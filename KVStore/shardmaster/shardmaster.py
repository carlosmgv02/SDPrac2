import logging
import threading

from KVStore.tests.utils import KEYS_LOWER_THRESHOLD, KEYS_UPPER_THRESHOLD
from KVStore.protos.kv_store_pb2 import RedistributeRequest, ServerRequest
from KVStore.protos.kv_store_pb2_grpc import KVStoreStub
from KVStore.protos.kv_store_shardmaster_pb2_grpc import ShardMasterServicer
from KVStore.protos.kv_store_shardmaster_pb2 import *

# from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
logger = logging.getLogger(__name__)
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import grpc
from multiprocessing import Manager

from typing import Dict, Tuple


def grpc_redistribute(source_server: str, destination_server: str, keys: Tuple[int, int]):
    redistribute_request = RedistributeRequest()
    redistribute_request.destination_server = destination_server
    redistribute_request.lower_val = keys[0]
    redistribute_request.upper_val = keys[1]
    print(f"Source server: {source_server}, Destination server: {destination_server}, Keys: {keys}")
    with grpc.insecure_channel(source_server) as channel:
        stub = KVStoreStub(channel)
        response = stub.Redistribute(redistribute_request)

    print(f"Redistributed keys: {keys} from {source_server} to {destination_server}")


class ShardMasterService:
    def __init__(self):
        self.manager = Manager()
        self.node_dict = self.manager.dict()
        self.servers = self.manager.list()
        self.lock = threading.Lock()

    def join(self, server: str):
        with self.lock:
            if server not in self.servers:
                self.servers.append(server)
                self.recalculate_shards()
                self.redistribute_keys(server)
                print(f"New Join ({server}), Servers -> {self.servers}")
                print(f"Shards -> {self.node_dict}")

    def leave(self, server: str):
        if server in self.servers:
            self.lock.acquire()
            try:
                self.servers.remove(server)
                del self.node_dict[server]
                if len(self.servers) >= 1:
                    self.recalculate_shards()
                    destination = self.servers[0]
                    grpc_redistribute(server, destination, (0, 99))
                    self.redistribute_keys(server)
            finally:
                self.lock.release()
            print(f"New Leave ({server}), Servers -> {self.servers}")
            print(f"Shards -> {self.node_dict}")

    def recalculate_shards(self):
        total_servers = len(self.servers)
        total_keys = 100

        if total_servers == 0:
            return

        avg_keys_per_server = total_keys // total_servers
        remaining_keys = total_keys % total_servers

        lower_val = 0
        for i, server in enumerate(self.servers):
            keys_count = avg_keys_per_server + (1 if i < remaining_keys else 0)
            upper_val = lower_val + keys_count - 1
            self.node_dict[server] = (lower_val, upper_val)
            lower_val = upper_val + 1

    def query(self, key):
        # self.lock.acquire()
        for address in self.servers:
            print(f"Key: {str(key)} Range: {str(self.node_dict.get(address))} Server: {address}")
            if self.node_dict.get(address)[0] <= key <= self.node_dict.get(address)[1]:
                return address
        # self.lock.release()
        return None

    def redistribute_keys(self, server):
        #with self.lock:
        if server in self.servers:
            server_index = self.servers.index(server)
            prev_server = self.servers[server_index - 1] if server_index > 0 else None
            next_server = self.servers[server_index + 1] if server_index < len(self.servers) - 1 else None

            if prev_server:
                shard = self.node_dict[prev_server]
                if shard[1] != 99:
                    destination = server
                    keys = (shard[1] + 1, 99)
                    print(f"Redistributing keys: {keys} from {prev_server} to {destination}")
                    grpc_redistribute(prev_server, destination, keys)

            if next_server:
                shard = self.node_dict[next_server]
                if shard[0] != 0:
                    destination = server
                    keys = (0, shard[0])
                    print(f"Redistributing keys: {keys} from {next_server} to {destination}")
                    grpc_redistribute(next_server, destination, keys)
        else:
            print(f"Server {server} not in servers list")

    def join_replica(self, server: str) -> Role:
        pass

    def query_replica(self, key: int, op: Operation) -> str:
        pass


class ShardMasterSimpleService(ShardMasterService):
    def __init__(self):
        super().__init__()
        self.storage_service = KVStoreStub(grpc.insecure_channel("localhost:50051"))

    def join(self, server: str):
        super().join(server)

    def leave(self, server: str):
        super().leave(server)

    def query(self, key: int) -> str:
        return super().query(key)


class ShardMasterReplicasService(ShardMasterSimpleService):
    def __init__(self, number_of_shards: int):
        super().__init__()
        self.storage_service = ShardMasterSimpleService()


    def leave(self, server: str):
        super().leave(server)

    def join_replica(self, server: str) -> Role:
        response = super().join_replica(server)
        if response == "MASTER":
            return Role.MASTER
        elif response == "REPLICA":
            return Role.REPLICA
        else:
            raise ValueError("Invalid role")

    def query_replica(self, key: int, op: Operation) -> str:
        response = super().query_replica(key, op)
        return response


class ShardMasterServicer(ShardMasterServicer):
    def __init__(self, shard_master_service: ShardMasterService):
        self.shard_master_service = shard_master_service
        """
        To fill with your code
        """

    def Join(self, request: JoinRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        self.shard_master_service.join(request.server)
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Leave(self, request: LeaveRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        self.shard_master_service.leave(request.server)
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Query(self, request: QueryRequest, context) -> QueryResponse:
        response = self.shard_master_service.query(request.key)
        toReturn: QueryResponse = QueryResponse(server=response)
        if response == "":
            return QueryResponse(server=None)
        else:
            return toReturn

    def JoinReplica(self, request: JoinRequest, context) -> JoinReplicaResponse:
        return JoinReplicaResponse(role=self.shard_master_service.join_replica(request.server))

    def QueryReplica(self, request: QueryReplicaRequest, context) -> QueryResponse:
        return QueryResponse(server=self.shard_master_service.query_replica(request.key, request.operation))
