import logging
import socketio
from logger import get_logger
from message import Message
from dataManagerClient import DataManagerClient
from typing import List
from datatype import ApplicationUserSide


class TaskNamespace(socketio.ClientNamespace):
    def __init__(
            self,
            namespace=None,
            appList=None,
            dataManager: DataManagerClient = None,
            logLevel=logging.DEBUG):
        super(TaskNamespace, self).__init__(namespace=namespace)
        if appList is None:
            appList = []
        self.isConnected = False
        self.canRegister = False
        self.isRegistered = False
        self.workerID = None
        self.appList: List[ApplicationUserSide] = appList
        self.dataManager = dataManager
        self.logger = get_logger("Worker-Task", logLevel)

    def on_connect(self):
        self.isConnected = True
        self.register()
        self.logger.info("[*] Connected.")

    def on_disconnect(self):
        self.isConnected = False
        self.logger.info("[!] Disconnected.")

    def updateWorkerID(self, workerID: int):
        self.workerID = workerID
        self.canRegister = True

    def register(self):
        while not self.canRegister:
            pass
        message = {'workerID': self.workerID, 'role': 'worker'}
        messageEncrypted = Message.encrypt(message)
        self.emit('register', data=messageEncrypted)

    def on_registered(self, message):
        messageDecrypted = Message.decrypt(message)
        workerID = messageDecrypted['workerID']
        if workerID == self.workerID:
            self.isRegistered = True

    def on_task(self, message):
        messageDecrypted = Message.decrypt(message)
        taskID = messageDecrypted["taskID"]
        appID = messageDecrypted["appID"]
        dataID = messageDecrypted["dataID"]
        self.logger.debug("Received Task-%d, appID: %d, dataID: %d", taskID, appID, dataID)
        if appID >= len(self.appList):
            messageDecrypted['resultID'] = dataID
        else:
            app = self.appList[appID]
            inputData = self.dataManager.receiveData(dataID=dataID)
            resultData = app.process(inputData)
            resultDataID = self.dataManager.sendData(resultData)
            messageDecrypted['resultID'] = resultDataID

        messageDecrypted['workerID'] = self.workerID
        messageEncrypted = Message.encrypt(messageDecrypted)
        return messageEncrypted
