import logging
import threading
import struct
import socket

from logger import get_logger
from queue import Queue
from time import time


class DataManager:

    def __init__(self, host: str, port: int, logLevel=logging.DEBUG):
        self.dataID = 0
        self.host: str = host
        self.port: int = port
        self.receivingQueue: Queue[bytes] = Queue()
        self.sendingQueue: Queue[bytes] = Queue()
        self.clientSocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.logger = get_logger('User-DataManager', logLevel)

    def run(self):
        self.clientSocket.connect((self.host, self.port))

        threading.Thread(target=self.__readData).start()
        threading.Thread(target=self.__writeData).start()
        self.logger.info("[*] Connected to %s:%d over tcp.", self.host, self.port)

    def __readData(self):
        while True:
            data = self.__receivePackage(self.clientSocket)
            self.receivingQueue.put(data)

    def __writeData(self):
        while True:
            data = self.sendingQueue.get()
            print('sending', time())
            self.__sendPackage(self.clientSocket, data)

    @staticmethod
    def __receivePackage(clientSocket: socket.socket) -> bytes:
        data = b''
        payloadSize = struct.calcsize(">L")
        while len(data) < payloadSize:
            data += clientSocket.recv(4096)

        packedDataSize = data[:payloadSize]
        data = data[payloadSize:]
        dataSize = struct.unpack(">L", packedDataSize)[0]

        while len(data) < dataSize:
            data += clientSocket.recv(4096)

        data = data[:dataSize]
        return data

    @staticmethod
    def __sendPackage(clientSocket: socket.socket, data: bytes):
        clientSocket.sendall(struct.pack(">L", len(data)) + data)
        print('sent', time())


if __name__ == '__main__':
    dataManager = DataManager(host='0.0.0.0',
                              port=5000,
                              logLevel=logging.DEBUG)
    dataManager.run()
