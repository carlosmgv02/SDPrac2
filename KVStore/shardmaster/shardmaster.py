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


class ShardMasterService:
    def __init__(self):
        self.manager = Manager()
        self.node_dict = self.manager.dict()

    def join(self, server):
        if len(self.node_dict) >= 100:
            print("No se pueden agregar más nodos. El límite de claves se ha alcanzado.")
            return

        min_key = 0
        max_key = 0

        if len(self.node_dict) > 0:
            total_nodes = len(self.node_dict) + 1
            avg_keys_per_node = 100 // total_nodes

            # Calcular el rango de claves para el nuevo nodo
            min_key = 100 // total_nodes * len(self.node_dict) + 1
            max_key = min_key + avg_keys_per_node - 1

        # Asignar el rango de claves al nuevo nodo
        new_node = (min_key, max_key, server)
        self.node_dict[server] = new_node
        print(f"Total nodes: {len(self.node_dict)}")
        print(f"Joined node: {new_node}")

        # Redistribuir las claves existentes al nuevo nodo
        self.redistribute_keys()

    def leave(self, server: str):
        if server in self.node_dict:
            del self.node_dict[server]
            print(f"Left node: {server}")

            self.redistribute_keys()

    def query(self, key: int) -> str:
        for node in self.node_dict.values():
            if node[0] <= key <= node[1]:
                return node[2]

        return "Key not found"

    def redistribute_keys(self):
        if len(self.node_dict) == 0:
            return

        total_keys = 100
        total_nodes = len(self.node_dict)
        avg_keys_per_node = total_keys // total_nodes

        # Verificar si hay nodos con claves por debajo del promedio
        for node in self.node_dict.items():
            keys_count = node[1][1] - node[1][0] + 1
            if keys_count < avg_keys_per_node:
                # Encontrar nodos con exceso de claves para realizar transferencias
                nodes_to_transfer = []
                for other_node in self.node_dict.items():
                    if other_node[1][1] - other_node[1][0] + 1 > avg_keys_per_node:
                        nodes_to_transfer.append(other_node)

                # Ordenar los nodos con exceso de claves de mayor a menor
                nodes_to_transfer.sort(key=lambda x: x[1][1] - x[1][0], reverse=True)

                # Calcular cuántas claves transferir
                keys_to_transfer = avg_keys_per_node - keys_count

                # Transferir las claves
                for transfer_node in nodes_to_transfer:
                    transfer_count = min(keys_to_transfer, transfer_node[1][1] - transfer_node[1][0] + 1)
                    new_node = (node[1][0], node[1][1] + transfer_count, node[1][2])
                    self.node_dict[node[0]] = new_node

                    transfer_node_range = (transfer_node[1][0] + transfer_count, transfer_node[1][1])
                    new_transfer_node = (transfer_node_range[0], transfer_node_range[1], transfer_node[1][2])
                    self.node_dict[transfer_node[0]] = new_transfer_node
                    print(f"Source node keys: {node[1]}, Destination node keys: {new_node}")
                    print(f"Transferred {transfer_count} keys from {transfer_node[1][2]} to {node[1][2]}")

                    # Llamada gRPC para redistribuir las claves
                    self.grpc_redistribute(transfer_node[1][2], node[1][2], transfer_node_range)

                    keys_to_transfer -= transfer_count

                    if keys_to_transfer == 0:
                        break

    def grpc_redistribute(self, source_server: str, destination_server: str, keys: list):
        # Crear la instancia de la clase RedistributeRequest con los valores adecuados
        redistribute_request = RedistributeRequest()
        redistribute_request.destination_server = destination_server
        redistribute_request.lower_val = min(keys)
        redistribute_request.upper_val = max(keys)

        # Realizar la llamada gRPC a la función redistribute en el nodo fuente
        with grpc.insecure_channel(source_server) as channel:
            stub = KVStoreStub(channel)
            response = stub.Redistribute(redistribute_request)

        print(f"Redistributed keys: {keys}"
              f" from {source_server} to {destination_server}")

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
