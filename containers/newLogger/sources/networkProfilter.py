import iperf3
from typing import Tuple

Address = Tuple[str, int]


class NetProfiler:

    def __init__(
            self,
            serverBindAddr: Address = ('127.0.0.1', 10000)
    ):
        self._serverAddr: Address = serverBindAddr

        self.__server = iperf3.Server()
        self.__server.bind_address = self._serverAddr[0]
        self.__server.port = self._serverAddr[1]
        self.__client = iperf3.Client()
        self.__client.bind_address = self._serverAddr[0]

    def receive(self):
        result = self.__server.run()
        return result.received_bps

    def send(
            self,
            serverAddr: Tuple[str, int] = None):
        if serverAddr is None:
            serverAddr = self._serverAddr
        self.__client.server_hostname = serverAddr[0]
        self.__client.port = serverAddr[1]
        result = self.__client.run()
        return result.sent_bps


if __name__ == '__main__':
    test = NetProfiler()
    # print(test.receive())
    print(test.send())
