import logging
from KVStore.logger import setup_logger
from KVStore.shardmaster import start_shardmaster
from KVStore.kvstorage import start_storage_server_sharded
from KVStore.tests.sharded import ShardKVParallelTests, ShardKVSimpleTests, ShardkvAppendTests
from KVStore.tests.utils import wait, SHARDMASTER_PORT, get_port
from sys import platform

logger = logging.getLogger(__name__)

NUM_STORAGE_SERVERS = [3]
master_address = f"localhost:{SHARDMASTER_PORT}"


if __name__ ==  '__main__':

    if platform not in ["linux", "linux2"]:
        setup_logger()

    print("*************Sharded tests**************")

    print("Tests with changing shardmasters")
    for num_servers in NUM_STORAGE_SERVERS:
        print(f"{num_servers} storage servers.")
        server_proc = start_shardmaster.run(SHARDMASTER_PORT)

        storage_proc_end_queues = [start_storage_server_sharded.run(get_port(), SHARDMASTER_PORT) for i in
                                   range(num_servers)]

        test1 = ShardKVSimpleTests(master_address, 1)
        test1.test()


