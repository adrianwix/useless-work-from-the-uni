import getpass
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

import Internal.Client as Client
from Internal.Server import sessionServer as defaultAddress


class ServerSettings:
    def __init__(self, address=None, name=None, secret=None, locked=False):
        storedSettings = Client.storedSettings
        self.address = address if address is not None else storedSettings.value('server_address', defaultAddress)
        self.name    = name    if name    is not None else storedSettings.value('name', getpass.getuser())
        self.secret  = secret  if secret  is not None else storedSettings.value('secret', '')
        self.locked = locked


class ServerSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('Internal/FormServerSettings.ui', self)
        if Client.serverSettings is None:
            Client.serverSettings = ServerSettings()
        self.lineEdit_address.setText(Client.serverSettings.address)
        self.lineEdit_name.setText(Client.serverSettings.name)
        self.lineEdit_secret.setText(Client.serverSettings.secret)
        self.setDisabled(Client.serverSettings.locked)

    def lock(self):
        settings = ServerSettings(
            address=self.lineEdit_address.text(),
            name=self.lineEdit_name.text(),
            secret=self.lineEdit_secret.text(),
            locked=not self.isEnabled()
        )
        if settings.address != Client.serverSettings.address:
            Client.storedSettings.setValue('server_address', settings.address)
        if settings.name != Client.serverSettings.name:
            Client.storedSettings.setValue('name', settings.name)
        if settings.secret != Client.serverSettings.secret:
            Client.storedSettings.setValue('secret', settings.secret)
        Client.serverSettings = settings
        self.setDisabled(True)

    def unlock(self):
        self.setDisabled(False)
