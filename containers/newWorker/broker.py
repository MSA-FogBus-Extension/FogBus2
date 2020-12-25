import logging
import socketio
import threading
from logger import get_logger
from registryNamespace import RegistryNamespace
from taskNamespace import TaskNamespace


class Broker:

    def __init__(self, host: str, port: int, logLevel=logging.DEBUG):
        self.logger = get_logger('Worker-Broker', logLevel)
        self.host = host
        self.port = port
        self.sio = socketio.Client()
        self.registryNamespace = RegistryNamespace('/registry', logLevel=logLevel)
        self.taskNamespace = TaskNamespace('/task', logLevel=logLevel)

    def run(self):
        threading.Thread(target=self.connect).start()
        while not self.registryNamespace.isRegistered:
            pass
        self.taskNamespace.updateWorkerID(self.registryNamespace.workerID)
        while not self.registryNamespace.isRegistered:
            pass
        self.logger.info("Got workerID-%d", self.taskNamespace.workerID)

    def connect(self):
        self.sio.register_namespace(self.registryNamespace)
        self.sio.register_namespace(self.taskNamespace)
        self.sio.connect('%s:%d' % (self.host, self.port))
        self.sio.wait()


if __name__ == '__main__':
    broker = Broker('http://127.0.0.1', 5000, logLevel=logging.DEBUG)
    broker.run()

