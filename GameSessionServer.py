#!python3

import sys, signal, os, glob, re, base64, subprocess, traceback
from datetime import datetime
from PyQt5.QtCore import QCoreApplication, QTimerEvent
from PyQt5.QtNetwork import QHostAddress, QTcpServer, QSsl, QSslSocket, QSslCertificate, QSslKey
from Internal.Server import *
from Internal.SendStream import *
from Internal.ClientSocket import ClientSocket
from Internal.Session import Session
from Internal.ControlHandler import ControlHandler


signal.signal(signal.SIGINT, signal.SIG_DFL)


if os.path.exists(cacheFolder):
    for file in glob.glob(cacheFolder + '/[0-9a-f]*'):
        match = re.match('.*([0-9a-f]{40,40})$', file)
        if match:
            try:
                fileHashDict[match.group(1).encode()] = open(file, 'rb').read()
            except Exception as e:
                print("Could not read file '" + file + '": ' + str(e))
                sys.exit(1)
else:
    os.mkdir(cacheFolder)


app = QCoreApplication(sys.argv)


def handleValidatedReceive(stream : SendStream, socket : ClientSocket):
    socket.unregister()
    protocolVersion = stream.readInt()
    if protocolVersion != sessionProtocolVersion:
        if protocolVersion < sessionProtocolVersion:
            text = 'Client uses outdated protocol version. Please update the client.'
        else:
            text = 'Client uses newer protocol version. Please inform the server provider that the server is outdated.'
        stream = socket.sendStream
        stream.writeBytes(b'error')
        stream.writeString(text)
        stream.send()
        socket.disconnectWhenWritten()
        raise HandledError()
    socket.name = stream.readString()
    socket.secret = stream.readString()
    Session.startHandling(stream, socket)


class MyServer(QTcpServer):
    def __init__(self):
        super().__init__()
        self.timerDict = dict()
        self.lastLogMinute = datetime.now().minute // 10
        self.watchDogTimer = self.startTimer(30000)
        self.restartTimer = None
        self.testSocket = QSslSocket()
        self.testSocket.setCaCertificates([QSslCertificate(base64.b64decode(certificate))])
        def onTestSuccess():
            if self.restartTimer:
                self.killTimer(self.restartTimer)
                self.restartTimer = None
            minute = datetime.now().minute // 10
            if minute != self.lastLogMinute:
                log('server ok, tot: ' + str(Session.IdCounter) + ' open: ' + str(len(openSessions)) +
                    ' active: ' + str(len(activeSessions)) + ' unv: ' + str(len(unvalidatedSockets)) +
                    ' cached: ' + str(len(fileHashDict)) + ' join: ' + str(len(joiningClients)) +
                    ' blockd: ' + str(len(blockedAddresses)) + ' ctrl: ' + str(len(controlHandlers)))
                self.lastLogMinute = minute
            self.testSocket.disconnectFromHost()
        self.testSocket.encrypted.connect(onTestSuccess)
        self.newConnection.connect(self.handleNewConnection)

    def __del__(self):
        log('Server deleted - ' + traceback.format_exc())

    def restart(self):
        self.close()
        subprocess.Popen([sys.executable, os.path.normpath(sys.argv[0])], close_fds=True)
        app.exit(0)

    def timerEvent(self, event : QTimerEvent):
        id = event.timerId()
        if id == self.restartTimer:
            log('restarting server because test socket cannot connect')
            self.restart()
        elif id == self.watchDogTimer:
            if self.testSocket.state() == QSslSocket.UnconnectedState and not self.restartTimer:
                self.restartTimer = self.startTimer(30000)
                self.testSocket.connectToHostEncrypted('localhost', listenPort)
        else:
            self.killTimer(id)
            socket = self.timerDict[id]
            socket.close()
            socket.deleteLater()
            del self.timerDict[id]
            if socket in unvalidatedSockets:
                unvalidatedSockets.remove(socket)

    def incomingConnection(self, handle):
        socket = QSslSocket()
        if socket.setSocketDescriptor(handle):
            if blockedAddresses.get(socket.peerAddress(), 1) <= 0:
                socket.close()
                return
            def handleSslErrors(errors, socket = socket):
                address = socket.peerAddress().toString()
                log('SSL errors for peer ' + address + ' : ' + ', '.join([x.errorString() for x in errors]))
            socket.sslErrors.connect(handleSslErrors)
            socket.setLocalCertificate(QSslCertificate(base64.b64decode(certificate)))
            socket.setPrivateKey(QSslKey(base64.b64decode(privatekey), QSsl.Rsa))
            socket.startServerEncryption()
            self.addPendingConnection(socket)

    def handleNewConnection(self):
        while True:
            socket = self.nextPendingConnection()
            if not socket:
                return
            timerId = self.startTimer(30000)
            self.timerDict[timerId] = socket
            def handleNewEncryptedConnection(socket = socket, timerId = timerId):
                unvalidatedSockets.add(socket)
                def handleDisconnect(socket = socket):
                    unvalidatedSockets.remove(socket)
                socket.disconnected.connect(handleDisconnect)
                def handleReceive(socket = socket, timerId = timerId):
                    if timerId:
                        self.killTimer(timerId)
                    unvalidatedSockets.remove(socket)
                    socket.disconnected.disconnect(handleDisconnect)
                    def blockAddress():
                        address = socket.peerAddress()
                        remaining = blockedAddresses.setdefault(address, 3)
                        blockedAddresses[address] -= 1
                        if remaining == 1:  # was last trial
                            socket.write(b"your address '" + address.toString().encode() + b"' has been blocked\n")
                            log("block address '" + address.toString() + "'")
                        socket.disconnectFromHost()
                    try:
                        secretLen = int(socket.read(1))
                    except:
                        blockAddress()
                        return
                    secret = socket.read(secretLen)
                    if secret == b'ctrl4eip':
                        blockedAddresses.pop(socket.peerAddress(), None)
                        controlHandlers.add(ControlHandler(socket))
                        socket.readyRead.disconnect(handleReceive)
                    elif secret == sessionClientSecret:
                        blockedAddresses.pop(socket.peerAddress(), None)
                        clientSocket = ClientSocket(socket)
                        clientSocket.register(validatedSockets)
                        clientSocket.setReceiveHandler(handleValidatedReceive)
                        socket.readyRead.disconnect(handleReceive)
                        clientSocket.handleReceive()
                    else:
                        address = socket.peerAddress()
                        remaining = blockedAddresses.setdefault(address, 3)
                        blockedAddresses[address] -= 1
                        if remaining == 1: # was last trial
                            socket.write(b"your address '" + address.toString().encode() + b"' has been blocked\n")
                            log("block address '" + address.toString() + "'")
                        socket.disconnectFromHost()
                        return
                socket.readyRead.connect(handleReceive)

            if socket.isEncrypted():
                handleNewEncryptedConnection()
            else:
                socket.encrypted.connect(handleNewEncryptedConnection)

tcpServer = MyServer()

hostAddress = QHostAddress.Any if ('-a' in sys.argv or '--all-interfaces' in sys.argv) else QHostAddress.LocalHost

if not tcpServer.listen(hostAddress, listenPort):
    log('could not bind to port - exiting')
    print('Could not listen.')
    sys.exit(1)
else:
    log('server started')
    try:
        sys.exit(app.exec())
    except Exception as e:
        log('crash - ' + str(e) + ' - ' + traceback.format_exc())
        sys.exit(1)
