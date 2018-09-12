import pickle, sys, inspect
from tempfile import TemporaryDirectory
from PyQt5.QtCore import QFileInfo, QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

import Internal.Client as Client
from Internal.GameWidget import openGameWindow
from Internal.GameObject import GameObject
from Internal.Util import getModuleAttrDict, getModuleFilePath
import GamePlayer


def initGame():
    initGameFunc = getModuleAttrDict(Client.gameObject.module).get('initGame')
    if initGameFunc:
        initGameFunc()


def runLocally():
    Client.gameObject.hostGame = False
    initGame()
    gameWindow = openGameWindow()
    def handleMoveDone():
        if Client.gameObject.currentPlayerIndex >= 0:
            Client.gameObject.thisPlayerIndex = Client.gameObject.currentPlayerIndex
    gameWindow.moveDone.connect(handleMoveDone)



def showMessageLater(title, text, sendToOthers):
    if sendToOthers and Client.connector:
        Client.connector.sendMessage(title, text)
    QTimer.singleShot(0, lambda: handleMessageReceived(title, text))


messages = []
showingMessage = False
def handleMessageReceived(title, text):
    global messages, showingMessage
    if showingMessage:
        messages.append((title, text))
    else:
        messageBox = QMessageBox(QMessageBox.Information, title, text, QMessageBox.Ok, Client.mainWidget)
        def whenFinished():
            global messages, showingMessage
            showingMessage = False
            if len(messages) > 0:
                [title, text] = messages.pop(0)
                handleMessageReceived(title, text)
        messageBox.finished.connect(whenFinished)
        messageBox.show()


def disconnect():
    Client.connector.errorOccurred.disconnect(handleError)
    Client.connector.disconnect()


def handleUpdateReceived(finished, state):
    if finished:
        disconnect()
    applyState(state)
    Client.mainWidget.updateStatusBar()
    Client.mainWidget.update()


def handleError(error):
    QMessageBox.critical(Client.mainWidget, 'Error Occurred', 'The following error ocurred:\n\n' + error)


def runGame():
    Client.connector.updateReceived.connect(handleUpdateReceived)
    Client.connector.messageReceived.connect(handleMessageReceived)
    Client.connector.errorOccurred.connect(handleError)
    gameWindow = openGameWindow()
    def handleMoveDone(res):
        finished = (res == -1)
        Client.connector.sendUpdate(finished, getState())
        if finished:
            disconnect()
    gameWindow.moveDone.connect(handleMoveDone)


modules = None


def getPathsAndModules():
    module = Client.gameObject.module
    normalizePath = lambda x: QFileInfo(x).absoluteFilePath()
    moduleFile = normalizePath(getModuleFilePath(module))
    path = moduleFile[:(moduleFile.rfind('/') + 1)]
    pathLen = len(path)
    modules = [[moduleFile[pathLen:], module]]
    stack = [module]
    while len(stack) > 0:
        module = stack.pop()
        for name, var in getModuleAttrDict(module).items():
            if var not in modules and var != GamePlayer and inspect.ismodule(var) and hasattr(var, '__file__'):
                moduleFile = normalizePath(var.__file__)
                if moduleFile.startswith(path):
                    modules.append([moduleFile[pathLen:], var])
                    stack.append(var)
    return modules


def getState():
    mstates = []
    for module in modules:
        vars = dict()
        for name, var in getModuleAttrDict(module).items():
            if not name.startswith('__') and not name.endswith('__') and not inspect.ismodule(var) \
                    and not inspect.isfunction(var) and not inspect.isclass(var):
                vars[name] = var
        mstates.append(vars)
    return pickle.dumps([Client.gameObject.currentPlayerIndex, mstates])


def applyState(state):
    [currentPlayerIndex, mstates] = pickle.loads(state)
    Client.gameObject.currentPlayerIndex = currentPlayerIndex
    for module, vars in zip(modules, mstates):
        getModuleAttrDict(module).update(vars)


def runHosting():
    Client.connector.gameDataRequested.connect(handleGameDataRequested)
    Client.connector.startSession()


def handleGameDataRequested():
    global modules
    initGame()
    pathsAndModules = getPathsAndModules()
    modules = list(map(lambda x: x[1], pathsAndModules))
    # read modules
    for pathAndModule in pathsAndModules:
        pathAndModule[1] = open(getModuleFilePath(pathAndModule[1]), 'rb').read()
    gObj = Client.gameObject
    data = pickle.dumps([gObj.players, gObj.playerTitles, pathsAndModules])
    Client.connector.sendGameData(data, getState())
    gObj.thisPlayerIndex = gObj.players.index(Client.serverSettings.name)
    gObj.hostGame = True
    runGame()


def runClient(data, state):
    global tempDir, modules
    tempDir = TemporaryDirectory()
    tempPath = QFileInfo(tempDir.name).absoluteFilePath()+ '/'
    sys.path = [tempPath] + sys.path
    QApplication.instance().aboutToQuit.connect(tempDir.cleanup)
    [players, playerTitles, pathsAndModules] = pickle.loads(data)
    fullPaths = []
    paths = []
    for path, module in pathsAndModules:
        fullPath = tempPath + path
        open(fullPath, 'wb').write(module)
        fullPaths.append(fullPath)
        paths.append(path)
    Client.gameObject = GameObject(GameObject.LoadAsClient, moduleFile=fullPaths[0])
    Client.gameObject.execModule()
    Client.gameObject.players = players
    Client.gameObject.playerTitles = playerTitles
    Client.gameObject.thisPlayerIndex = players.index(Client.serverSettings.name)
    Client.gameObject.hostGame = True

    modules = [None] * len(pathsAndModules)
    for path, module in getPathsAndModules():
        modules[paths.index(path)] = module

    applyState(state)
    runGame()

