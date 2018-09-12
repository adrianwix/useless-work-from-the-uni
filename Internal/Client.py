from PyQt5.QtCore import QSettings

# common data for client

mainWidget = None
gameObject = None
connector = None
serverSettings = None
storedSettings = QSettings('settings.ini', QSettings.IniFormat)


def setMainWidget(widget):
    global mainWidget
    if mainWidget is not None:
        mainWidget.deleteLater()
    mainWidget = widget

