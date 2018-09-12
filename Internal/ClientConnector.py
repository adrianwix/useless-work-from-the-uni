import base64
from PyQt5.QtCore import QObject, QIODevice, pyqtSignal
from PyQt5.QtNetwork import QSslSocket, QSslCertificate
import Internal.Client as Client
from Internal.ClientSocket import ClientSocket
from Internal.Server import listenPort, sessionProtocolVersion, sessionClientSecret, certificate
from Internal.SendStream import SendStream


class Session:
    def __init__(self, game, host, id):
        self.game = game
        self.host = host
        self.id   = id

    def __lt__(self, other):
        return (self.game.lower(), self.host.lower()) < (other.game.lower(), other.host.lower())


class ClientConnector(QObject):
    def __init__(self):
        super().__init__()
        self.clientSocket = ClientSocket(QSslSocket())
        self.socket = self.clientSocket.socket
        self.sendStream = self.clientSocket.sendStream
        self.clientSocket.setReceiveHandler(self.handleConnectorReceive)
        self.socket.setCaCertificates([QSslCertificate(base64.b64decode(certificate))])
        self.socket.encrypted.connect(self.handleConnected)
        self.socket.error.connect(self.handleError)
        self.socket.connectToHostEncrypted(Client.serverSettings.address, listenPort, QIODevice.ReadWrite,
                                           QSslSocket.IPv4Protocol)

    def disconnect(self):
        self.socket.disconnectFromHost()

    def handleConnected(self):
        self.socket.write(str(len(sessionClientSecret)).encode() + sessionClientSecret)
        self.sendStream.writeInt(sessionProtocolVersion)
        self.sendStream.writeString(Client.serverSettings.name)
        self.sendStream.writeString(Client.serverSettings.secret)
        self.sendStream.send()
        self.connected.emit()

    def host(self, returnId=False):
        self.sendStream.writeBytes(b'host')
        self.sendStream.writeString(Client.gameObject.gameName)
        self.sendStream.writeInt(Client.gameObject.minPlayerCount)
        self.sendStream.writeInt(Client.gameObject.maxPlayerCount)
        self.sendStream.writeBool(Client.gameObject.playerCanLeave)
        self.sendStream.writeBool(returnId)
        self.sendStream.send()

    def getSessions(self):
        self.sendStream.writeBytes(b'client')
        self.sendStream.send()

    def join(self, sessionId):
        self.sendStream.writeBytes(b'join')
        self.sendStream.writeInt(sessionId)
        self.sendStream.send()

    def disjoin(self):
        self.sendStream.writeBytes(b'disjoin')
        self.sendStream.send()

    def startSession(self):
        self.sendStream.writeBytes(b'start')
        self.sendStream.writeInt(0) # no files
        self.sendStream.send()

    def sendGameData(self, data, state):
        self.sendStream.writeBytes(b'data')
        self.sendStream.writeInt(0) # no files
        self.sendStream.writeBytes(data)
        self.sendStream.writeBytes(state)
        self.sendStream.send()

    def sendUpdate(self, finished, state):
        self.sendStream.writeBytes(b'update')
        self.sendStream.writeBool(finished)
        self.sendStream.writeBytes(state)
        self.sendStream.send()

    def sendMessage(self, title, text):
        self.sendStream.writeBytes(b'message')
        self.sendStream.writeString(title)
        self.sendStream.writeString(text)
        self.sendStream.send()


    connected = pyqtSignal()
    sessionIdReceived = pyqtSignal(int)
    sessionsAdded = pyqtSignal(list)
    sessionRemoved = pyqtSignal(int)
    sessionCanceled = pyqtSignal(str)
    playerJoined = pyqtSignal(str)
    playerDisjoined = pyqtSignal(str)
    playerLeft = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    gameDataRequested = pyqtSignal()
    gameDataReceived = pyqtSignal(bytes, bytes)
    updateReceived = pyqtSignal(bool, bytes)
    messageReceived = pyqtSignal(str, str)

    def handleError(self, error):
        self.socket.disconnectFromHost()
        if type(error) != str:
            if error == QSslSocket.SocketTimeoutError:
                error = 'A timeout error occurred.'
            elif error == QSslSocket.ConnectionRefusedError:
                error = 'The connection has been refused.'
            else:
                error = 'Socket error {} occurred.'.format(int(error))
        self.errorOccurred.emit(error)


    def handleConnectorReceive(self, stream: SendStream, socket: ClientSocket):
        command = stream.readBytes()
        if command == b'id':
            self.sessionIdReceived.emit(stream.readInt())
        elif command == b'error':
            self.handleError(stream.readString())
        elif command == b'join':
            self.playerJoined.emit(stream.readString())
        elif command == b'disjoin':
            self.playerDisjoined.emit(stream.readString())
        elif command == b'left':
            self.playerLeft.emit(stream.readString())
        elif command == b'cancel':
            self.sessionCanceled.emit(stream.readString())
        elif command == b'rmsession':
            self.sessionRemoved.emit(stream.readInt())
        elif command == b'addsessions':
            sessions = []
            for i in range(stream.readInt()):
                id = stream.readInt()
                host = stream.readString()
                game = stream.readString()
                sessions.append(Session(game, host, id))
            self.sessionsAdded.emit(sessions)
        elif command == b'start':
            fileMap = dict()
            for i in range(stream.readInt()):
                fileName = stream.readString()
                fileHash = stream.readBytes()
                fileMap[fileHash] = fileName
            # no file support
            self.sendStream.writeBytes(b'data')
            self.sendStream.writeInt(0)
            self.sendStream.send()
        elif command == b'missing':
            missingHashes = []
            for i in range(stream.readInt()):
                missingHashes.append(stream.readBytes())
            self.gameDataRequested.emit()
        elif command == b'data':
            files = []
            for i in range(stream.readInt()):
                files.append(stream.readBytes())
            data = stream.readBytes()
            state = stream.readBytes()
            self.gameDataReceived.emit(data, state)
        elif command == b'update':
            finished = stream.readBool()
            state = stream.readBytes()
            self.updateReceived.emit(finished, state)
        elif command == b'message':
            title = stream.readString()
            text = stream.readString()
            self.messageReceived.emit(title, text)
