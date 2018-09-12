import inspect, importlib.util, sys
from PyQt5.QtCore import QFileInfo
import GamePlayer
from Internal.Util import getInspectMember


class GameObject:

    StartFromModule = 0
    LoadSelected = 1
    LoadAsClient = 2

    def specAndModuleFromFile(self, filename):
        self.moduleSpec = importlib.util.spec_from_file_location(QFileInfo(filename).completeBaseName(), filename)
        self.module = importlib.util.module_from_spec(self.moduleSpec)

    def execModule(self):
        self.moduleSpec.loader.exec_module(self.module)

    def __init__(self, loadType, moduleFile=None, settings=None):
        self.currentPlayerIndex = 0
        self.thisPlayerIndex = 0
        self.loadType = loadType
        self.module = None
        self.moduleSpec = None
        if loadType == self.StartFromModule: # retrieve module from stack
            gameFileName = getInspectMember(GamePlayer, '__file__')
            if gameFileName is None:
                raise ('Could not find Game module in stack!')
            gameFrameFound = False
            for info in inspect.stack():
                if info.filename == gameFileName:
                    gameFrameFound = True
                elif gameFrameFound:
                    self.module = info.frame.f_locals
                    self.moduleName = QFileInfo(info.filename).completeBaseName()
                    break
            if self.module is None:
                raise Exception('Game module could not be derived from stack!')
        else:
            if not moduleFile:
                raise Exception('Modulfile must be given for this load type')
            self.specAndModuleFromFile(moduleFile)
            self.moduleName = self.moduleSpec.name
        if settings:
            self.addAndCheckSettings(settings)

    def addAndCheckSettings(self, settings):
        for key, value in settings.items():
            setattr(self, key, value)
        if type(self.minPlayerCount) is not int:
            raise Exception('Parameter minPlayerCount for Game.run must be an integer!')
        if type(self.maxPlayerCount) is not int:
            raise Exception('Parameter maxPlayerCount for Game.run must be an integer!')
        if self.players is None:
            self.players = self.minPlayerCount
        if type(self.players) == int:
            if self.players < self.minPlayerCount or self.players > self.maxPlayerCount:
                raise Exception('players parameter for GamePlayer.run is not in [minPlayerCount, maxPlayerCount]!')
            self.players = ['player ' + str(i + 1) for i in range(self.maxPlayerCount)]
        elif type(self.players) != list or any(map(lambda x: type(x) != str, self.players)):
            raise Exception(
                'players parameter for GamePlayer.run is neither None, nor an integer, nor a list of strings!')
        elif len(self.players) < self.minPlayerCount or len(self.players) > self.maxPlayerCount:
            raise Exception(
                'len of players parameter for GamePlayer.run is not in [minPlayerCount, maxPlayerCount]!')
        if self.gameName is None:
            self.gameName = self.moduleName
        elif type(self.gameName) != str:
            raise Exception('gameName parameter for GamePlayer.run must be a string or None!')
        self.playerCanLeave = hasattr(self.module, 'playerLeftGame')

    def isMoving(self):
        return self.currentPlayerIndex == self.thisPlayerIndex

    def getPlayerCount(self):
        return len(self.players)
