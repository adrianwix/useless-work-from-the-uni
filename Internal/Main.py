import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

import Internal.Client as Client
from Internal.Util import *
from Internal.GameObject import GameObject
from Internal.ServerSettings import *
from Internal.StartGame import startGame
from Internal.RunGame import showMessageLater as showMessageLaterInGame
import Internal.SelectGame as SelectGame
import Internal.GameOptions as GameOptions


app = QApplication(sys.argv)


def addOption(argTuple):
    GameOptions.add(argTuple)


def getGameObject():
    if Client.gameObject is None:
        raise Exception('You cannot call this function because the game has not yet started!')
    return Client.gameObject


def loadGame(gameFile, hostGame=None):
    try:
        Client.gameObject = GameObject(GameObject.LoadSelected, moduleFile=gameFile)
        Client.gameObject.execModule()
        if hostGame is not None:
            Client.gameObject.hostGame = hostGame
        return
    except Exception as e:
        QMessageBox.critical(Client.mainWidget, 'Error', 'The following error occurred:\n\n' + str(e))
    except:
        QMessageBox.critical(Client.mainWidget, 'Unknown Error', 'An unknown error occurred when loading the game.')
    Client.gameObject = None


def selectGame():
    SelectGame.selectGame(loadGame)
    exec()


def exec():
    sys.exit(app.exec())


def showMessageLater(title, message, all):
    showMessageLaterInGame(title, message, all)


def run(settings):
    hostingName = settings.pop('hostingName')
    sessionSecret = settings.pop('sessionSecret')
    if Client.serverSettings is None:
        Client.serverSettings = ServerSettings(name=hostingName, secret=sessionSecret)
    if Client.gameObject is not None:
        Client.gameObject.addAndCheckSettings(settings)
    else:
        try:
            Client.gameObject = GameObject(GameObject.StartFromModule, settings=settings)
        except Exception as e:
            QMessageBox.critical(None, 'Error', 'The following error occurred:\n\n' + str(e))
            return
    if Client.gameObject.loadType != GameObject.LoadAsClient:
        QTimer.singleShot(0, startGame)
        if Client.gameObject.loadType == GameObject.StartFromModule:
            exec()

