from PyQt5 import uic

import Internal.Client as Client
import Internal.GameOptions as GameOptions
from Internal.Util import *
from Internal.PlayerTableWidget import PlayerTableWidget
from Internal.ServerSettings import ServerSettingsWidget
from Internal.ClientConnector import ClientConnector
from Internal.RunGame import runLocally, runHosting


localPlayerWidget = None
serverSettingsWidget = None
mainWidget = None
youSuffix = ' (You)'


def gObj():
    return Client.gameObject


def handleLocalPlayerCountChanged():
    mainWidget.button_addPlayer.setVisible(localPlayerWidget.rowCount() < gObj().maxPlayerCount)


def handleLocalPlayerAdded():
    i = localPlayerWidget.rowCount() + 1
    players = localPlayerWidget.getPlayers()
    while 'player ' + str(i) in players:
        i += 1
    localPlayerWidget.appendPlayer('player ' + str(i))


def handleConnected():
    Client.connector.host(gObj())
    serverPlayerWidget.setOverlayLabel(None)
    serverPlayerWidget.appendPlayer(Client.serverSettings.name + youSuffix)
    mainWidget.label_error.show()
    Client.connector.playerJoined.connect(handlePlayerJoined)
    Client.connector.playerDisjoined.connect(handlePlayerDisjoined)


def handlePlayerJoined(player):
    serverPlayerWidget.appendPlayer(player)
    if serverPlayerWidget.rowCount() >= gObj().minPlayerCount:
        mainWidget.label_error.hide()
        mainWidget.button_start.setEnabled(True)


def handlePlayerDisjoined(player):
    serverPlayerWidget.removePlayer(player)
    if serverPlayerWidget.rowCount() < gObj().minPlayerCount:
        mainWidget.label_error.show()
        mainWidget.button_start.setEnabled(False)


def handleHostButtonToggled(host):
    mainWidget.stackedWidget.setCurrentIndex(1 if host else 0)
    if host:
        if Client.connector is None:
            serverSettingsWidget.lock()
            Client.connector = ClientConnector()
            Client.connector.connected.connect(handleConnected)
            mainWidget.button_start.setEnabled(False)
    else:
        mainWidget.button_start.setEnabled(True)


def handleStartButtonClicked():
    ptw = serverPlayerWidget if mainWidget.button_host.isChecked() else localPlayerWidget
    gObj().players = list(map(lambda x: x[:-len(youSuffix)] if x.endswith(youSuffix) else x, ptw.getPlayers()))
    if gObj().playerTitles is not None:
        gObj().playerTitles = ptw.getTitles()
    gObj().hostGame = mainWidget.button_host.isChecked()
    if not gObj().hostGame:
        if Client.connector is not None:
            Client.connector.disconnect()
            Client.connector = None
        runLocally()
    else:
        mainWidget.setDisabled(True)
        runHosting()


def startGame():
    global mainWidget, localPlayerWidget, serverPlayerWidget, serverSettingsWidget
    mainWidget = QWidget()
    Client.setMainWidget(mainWidget)
    mainWidget.show()
    uic.loadUi('Internal/FormStartGame.ui', mainWidget)
    serverSettingsWidget = ServerSettingsWidget()
    fillGroupBox(mainWidget.groupBox_serverSettings, serverSettingsWidget)
    if GameOptions.empty():
        mainWidget.groupBox_gameSettings.hide()
    else:
        fillGroupBox(mainWidget.groupBox_gameSettings, GameOptions.Widget())
    localPlayerWidget = PlayerTableWidget(
        players=gObj().players,
        titles=gObj().playerTitles,
        minPlayerCount=gObj().minPlayerCount,
        playersAreMovable=True,
        playersAreEditable=True,
        playersAreRemovable=True,
        titlesAreChoosable=gObj().titlesAreChoosable,
    )
    mainWidget.page_local.layout().insertWidget(0, localPlayerWidget)
    localPlayerWidget.rowCountChanged.connect(handleLocalPlayerCountChanged)
    handleLocalPlayerCountChanged()
    mainWidget.button_addPlayer.clicked.connect(handleLocalPlayerAdded)

    serverPlayerWidget = PlayerTableWidget(
        players=[],
        titles=gObj().playerTitles,
        minPlayerCount=gObj().minPlayerCount,
        playersAreMovable=True,
        playersAreRemovable=True,
        titlesAreChoosable=gObj().titlesAreChoosable,
    )
    serverPlayerWidget.setOverlayLabel('Connecting ...')
    mainWidget.label_error.hide()
    mainWidget.label_error.setText('Minimum player count of {} not yet reached!'.format(gObj().minPlayerCount))

    mainWidget.button_host.toggled.connect(handleHostButtonToggled)
    mainWidget.page_server.layout().insertWidget(0, serverPlayerWidget)
    mainWidget.button_start.clicked.connect(handleStartButtonClicked)
    if gObj().hostGame:
        mainWidget.button_host.setChecked(True)