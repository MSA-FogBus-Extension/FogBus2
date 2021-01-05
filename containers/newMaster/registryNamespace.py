import logging
import socketio

from logger import get_logger
from message import Message
from masterSideRegistry import Registry


class RegistryNamespace(socketio.Namespace):

    def __init__(self, namespace=None, registry: Registry = None, logLevel=logging.DEBUG):
        super(RegistryNamespace, self).__init__(namespace=namespace)
        self.registry: Registry = registry
        self.logger = get_logger("MasterRegistryNamespace", logLevel)

    def on_register(self, socketID, message):
        messageDecrypted = Message.decrypt(message)
        role = messageDecrypted["role"]
        if role == "user":
            if 'userID' in messageDecrypted:
                userID = messageDecrypted['userID']
                self.registry.users[userID].socketID = socketID
            else:
                userID = self.registry.__addUser(registrySocketID=socketID)
            messageEncrypted = Message.encrypt(userID)
            self.emit('registered', room=socketID, data=messageEncrypted)

        elif role == "worker":
            nodeSpecs = messageDecrypted["nodeSpecs"]
            if 'workerID' in messageDecrypted:
                workerID = messageDecrypted['workerID']
                self.registry.workers[workerID].socketID = socketID
            else:
                workerID = self.registry.__addWorker(
                    workerSocketID=socketID,
                    nodeSpecs=nodeSpecs)

            messageEncrypted = Message.encrypt(workerID)
            self.emit('registered', room=socketID, data=messageEncrypted)
