import time
import random
from typing import Dict, Union, List
import logging
import grpc
from KVStore.protos.kv_store_pb2 import *
from KVStore.protos.kv_store_pb2_grpc import KVStoreServicer, KVStoreStub
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
from KVStore.protos.kv_store_shardmaster_pb2 import Role
from multiprocessing import Manager
EVENTUAL_CONSISTENCY_INTERVAL: int = 2

logger = logging.getLogger("KVStore")

from typing import Dict, Optional


class KVStorageService:
    def __init__(self):
        self.manager = Manager()
        self.data: Dict[int, str] = self.manager.dict()

    def get(self, key: int) -> Optional[str]:
        return self.data.get(key)

    def l_pop(self, key: int) -> Optional[str]:
        if key not in self.data:
            return None
        value = self.data[key]
        if len(value) > 0:
            popped_char = value[0]
            self.data[key] = value[1:]
            return popped_char
        return ""

    def r_pop(self, key: int) -> Optional[str]:
        if key not in self.data:
            return None
        value = self.data[key]
        if len(value) > 0:
            popped_char = value[-1]
            self.data[key] = value[:-1]
            return popped_char
        return ""

    def put(self, key: int, value: str):
        self.data[key] = value

    def append(self, key: int, value: str):
        if key not in self.data:
            self.data[key] = value
        else:
            self.data[key] = self.data[key] + value

    def redistribute(self, destination_server: str, lower_val: int, upper_val: int):
        keys_to_transfer = []
        for key in self.data.keys():
            if lower_val <= key <= upper_val:
                keys_to_transfer.append(key)

        for key in keys_to_transfer:
            value = self.data[key]
            del self.data[key]
            # Transfer the key-value pair to the destination server using the appropriate logic

    def transfer(self, keys_values: list):
        for key, value in keys_values:
            self.data[key] = value

    def add_replica(self, server: str):
        # Add the replica server using the appropriate logic
        pass

    def remove_replica(self, server: str):
        # Remove the replica server using the appropriate logic
        pass


class KVStorageSimpleService(KVStorageService):

    def __init__(self):
        self.storage_service = KVStorageService()
        """
        To fill with your code
        """

    def get(self, key: int) -> Union[str, None]:
        return self.storage_service.get(key)
        """
        To fill with your code
        """

    def l_pop(self, key: int) -> Union[str, None]:
        return self.storage_service.l_pop(key)
        """
        To fill with your code
        """

    def r_pop(self, key: int) -> Union[str, None]:
        return self.storage_service.r_pop(key)
        """
        To fill with your code
        """

    def put(self, key: int, value: str):
        return self.storage_service.put(key, value)
        """
        To fill with your code
        """

    def append(self, key: int, value: str):
        return self.storage_service.append(key, value)
        """
        To fill with your code
        """

    def redistribute(self, destination_server: str, lower_val: int, upper_val: int):
        return self.storage_service.redistribute(destination_server, lower_val, upper_val)
        """
        To fill with your code
        """

    def transfer(self, keys_values: List[KeyValue]):
        return self.storage_service.transfer(keys_values)
        """
        To fill with your code
        """


class KVStorageReplicasService(KVStorageSimpleService):
    role: Role

    def __init__(self, consistency_level: int):
        super().__init__()
        self.consistency_level = consistency_level
        """
        To fill with your code
        """

    def l_pop(self, key: int) -> str:
        """
        To fill with your code
        """

    def r_pop(self, key: int) -> str:
        """
        To fill with your code
        """

    def put(self, key: int, value: str):
        """
        To fill with your code
        """

    def append(self, key: int, value: str):
        """
        To fill with your code
        """

    def add_replica(self, server: str):
        """
        To fill with your code
        """

    def remove_replica(self, server: str):
        """
        To fill with your code
        """

    def set_role(self, role: Role):
        logger.info(f"Got role {role}")
        self.role = role


class KVStorageServicer(KVStoreServicer):

    def __init__(self, service: KVStorageService):
        self.storage_service = service
        """
        To fill with your code
        """

    def Get(self, request: GetRequest, context) -> GetResponse:
        response = GetResponse(value=self.storage_service.get(request.key))
        if response.value is None or response.value == "":
            response = GetResponse(value=None)
        else:
            response = GetResponse(value=response.value)

        return response

    def LPop(self, request: GetRequest, context) -> GetResponse:
        response= GetResponse (value=self.storage_service.l_pop(request.key))
        if response.value is None or response.value == "":
            response = GetResponse(value=None)
        else:
            response = GetResponse(value=response.value)

        return response

    def RPop(self, request: GetRequest, context) -> GetResponse:
        response =  GetResponse(value=self.storage_service.r_pop(request.key))
        if response.value is None or response.value == "":
            response = GetResponse(value=None)
        else:
            response = GetResponse(value=response.value)
        return response
        """
        To fill with your code
        """

    def Put(self, request: PutRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        self.storage_service.put(request.key, request.value)
        return google_dot_protobuf_dot_empty__pb2.Empty()


    def Append(self, request: AppendRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        self.storage_service.append(request.key, request.value)
        return google_dot_protobuf_dot_empty__pb2.Empty()
        """
        To fill with your code
        """

    def Redistribute(self, request: RedistributeRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        self.storage_service.redistribute(request.key, request.value)
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def Transfer(self, request: TransferRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        self.storage_service.transfer(request.key, request.value)
        return google_dot_protobuf_dot_empty__pb2.Empty()

    def AddReplica(self, request: ServerRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        """
        To fill with your code
        """

    def RemoveReplica(self, request: ServerRequest, context) -> google_dot_protobuf_dot_empty__pb2.Empty:
        """
        To fill with your code
        """
