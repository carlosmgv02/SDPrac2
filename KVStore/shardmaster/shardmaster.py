import logging
from KVStore.tests.utils import KEYS_LOWER_THRESHOLD, KEYS_UPPER_THRESHOLD
from KVStore.protos.kv_store_pb2 import RedistributeRequest, ServerRequest
from KVStore.protos.kv_store_pb2_grpc import KVStoreStub
from KVStore.protos.kv_store_shardmaster_pb2_grpc import ShardMasterServicer
from KVStore.protos.kv_store_shardmaster_pb2 import *
# from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
logger = logging.getLogger(__name__)
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2

from multiprocessing import Manager

from typing import Dict


class ShardMasterService:
    def __init__(self):
        self.manager = Manager()
        self.servers: Dict[str, int] = self.manager.dict()

    def join(self, server: str):
        if server not in self.servers:
            self.servers[server] = 0

    def leave(self, server: str):
        if server in self.servers:
            del self.servers[server]

    def query(self, key: int) -> str:
        num_servers = len(self.servers)
        if num_servers == 0:
            return ""

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
        """
        To fill with your code
        """

    def join(self, server: str):
        """
        To fill with your code
        """

    def leave(self, server: str):
        """
        To fill with your code
        """

    def query(self, key: int) -> str:
        return super().query(key)
        """
        To fill with your code
        """


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
        if response == "":
            return QueryResponse(server=None)
        else:
            return QueryResponse(server=response)


    def JoinReplica(self, request: JoinRequest, context) -> JoinReplicaResponse:
        """
        To fill with your code
        """

    def QueryReplica(self, request: QueryReplicaRequest, context) -> QueryResponse:
        """
        To fill with your code
        """
