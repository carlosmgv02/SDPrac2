import time
import logging
from KVStore.clients.clients import ShardClient
from KVStore.logger import setup_logger
from KVStore.tests.utils import test_get, test_put, test_append, Test

logger = logging.getLogger(__name__)

"""
Tests on parallel storage requests on a single storage server.
"""

DATA = {
    0: "1.965.000.000",
    1: "75.000.000",
    2: "32.000.000",
    3: "24.000.000",
    4: "3.200.000"
}


class ShardKVParallelTests(Test):

    def _test(self, client_id: int):
        setup_logger()

        client = ShardClient(self.master_address)
        time.sleep(1)
        print("PARALEL PUT TESTS")
        assert (test_put(client, client_id * 20, DATA[client_id]))
        print("END PARALEL PUT TESTS")

        print("PARALEL GET TESTS")
        assert (test_get(client, client_id * 20, DATA[client_id]))
        print("END PARALEL GET TESTS")

        print("PARALEL APPEND TESTS")
        assert (test_append(client, client_id * 20, DATA[client_id]))
        print("END PARALEL APPEND TESTS")

        print("PARALEL GET2 TESTS")
        assert (test_get(client, client_id * 20, DATA[client_id] + DATA[client_id]))
        print("END PARALEL GET2 TESTS")

        assert (test_put(client, client_id * 20, ""))

        client.stop()

