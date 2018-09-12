import inspect
from bisect import bisect_right
from PyQt5.QtCore import Qt, QSettings, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QToolButton, QVBoxLayout, \
                            QComboBox, QStyle, QHeaderView, QPushButton, QLabel, QGroupBox, QGridLayout, \
                            QCheckBox, QRadioButton


def getInspectMember(object, mem: str):
    for m in inspect.getmembers(object):
        if m[0] == mem:
            return m[1]
    else:
        return None

def getInspectMembers(object, mems: list):
    ret = [None] * len(mems)
    for m in inspect.getmembers(object):
        try:
            ret[mems.index(m[0])] = m[1]
        except ValueError:
            pass
    return ret


def makeToolButton(iconOrText):
    button = QToolButton()
    if type(iconOrText) == str:
        button.setText(iconOrText)
        button.setToolButtonStyle(Qt.ToolButtonTextOnly)
    else:
        button.setIcon(QApplication.instance().style().standardIcon(iconOrText))
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
    return button


def fillGroupBox(groupBox: QGroupBox, widget: QWidget):
    groupBox.setLayout(QVBoxLayout())
    groupBox.layout().addWidget(widget)


def makeTableWidgetItem(text, flags = Qt.ItemIsEnabled):
    item = QTableWidgetItem(text)
    item.setFlags(flags)
    return item


def getModuleAttrDict(module):
    return module if type(module) == dict else module.__dict__


def getModuleFilePath(module):
    return getModuleAttrDict(module)['__file__']
