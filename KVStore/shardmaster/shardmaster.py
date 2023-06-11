import logging
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


class ShardMasterService:
    def __init__(self):
        self.manager = Manager()
        self.keys: Dict[str, Tuple[int, int]] = self.manager.dict()
        self.servers = self.manager.list()
        self.total_keys = 100

    def recalculate_keys(self):
        num_servers = len(self.servers)
        min_key = 1
        max_key = -1
        for i, server_name in enumerate(self.servers):
            min_key = max_key + 1
            max_key = min_key + (self.total_keys // num_servers) - 1
            if i < (self.total_keys % num_servers):
                max_key += 1
            self.keys[server_name] = (min_key, max_key)

    def join(self, server: str):
        self.servers.append(server)
        num_servers = len(self.servers)
        keys_per_server = self.total_keys // num_servers
        remaining_keys = self.total_keys % num_servers
        start_key = 1
        for i, server in enumerate(self.servers):
            end_key = start_key + keys_per_server - 1
            if remaining_keys > 0:
                end_key += 1
                remaining_keys -= 1
            if i == num_servers - 1:
                # Asegurarse de que el último servidor obtenga las claves restantes
                end_key = self.total_keys
            self.keys[server] = (start_key, end_key)
            start_key = end_key + 1


    def leave(self, server: str):
        if server in self.servers:
            del self.servers[server]

    def query(self, key: int) -> str:
        num_servers = len(self.servers)
        if num_servers == 0:
            return ''

        shard = key % num_servers
        servers = list(self.servers.keys())
        return servers[shard]

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
        # self.storage_service.Redistribute(server, KEYS_LOWER_THRESHOLD, KEYS_UPPER_THRESHOLD)

    def leave(self, server: str):
        super().leave(server)
        # self.storage_service.Redistribute(server, KEYS_LOWER_THRESHOLD, KEYS_UPPER_THRESHOLD)

    def query(self, key: int) -> str:
        return super().query(key)


class ShardMasterReplicasService(ShardMasterSimpleService):
    def __init__(self, number_of_shards: int):
        super().__init__()
        self.storage_service = ShardMasterSimpleService()
        """
        To fill with your code
        """

    def leave(self, server: str):
        """
        To fill with your code
        """

    def join_replica(self, server: str) -> Role:
        """
        To fill with your code
        """

    def query_replica(self, key: int, op: Operation) -> str:
        """
        To fill with your code
        """


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
