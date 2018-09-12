import inspect
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QCheckBox, QVBoxLayout, QRadioButton

from Internal.Util import getInspectMembers


options = []


def empty():
    return len(options) == 0


class Option:
    def __init__(self):
        self.value = None


def add(argTuple):
    option = Option()
    args = [option, argTuple[0]]
    f = inspect.stack()[2]
    [code, ann] = getInspectMembers(f.frame.f_globals[f.function], ['__code__', '__annotations__'])
    for i, varName in enumerate(code.co_varnames):
        arg = argTuple[i+1]
        argType = type(arg)
        errorStart = lambda: 'The parameter "{}" of function "{}" must '.format(varName, f.function)
        if type(arg) == tuple:
            if not hasattr(arg[0], '__iter__'):
                raise Exception(errorStart() + 'be a list but it has type <{}>'.format(type(arg[0]).__name__))
            for j, x in enumerate(arg[0]):
                xtype = type(x)
                if type(x) != arg[1]:
                    raise Exception((errorStart() + 'contain only elements of type <{}> but element {} has type <{}>!').
                                    format(arg[1].__name__, j, xtype.__name__))
            args.append(arg[0])
        else:
            varType = ann.get(varName)
            if varType is not None:
                if varType != argType:
                    raise Exception(errorStart() + 'have type <{}> but it is <{}>'.
                                    format(varType.__name__, argType.__name__))
            args.append(arg)
    options.append(args)
    return option


class Widget(QWidget):
    def __init__(self):
        global options
        super().__init__()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        for row, option in enumerate(options):
            [obj, optionType] = option[:2]
            if optionType == 'checkBox':
                [text, defaultValue] = option[2:]
                checkBox = QCheckBox(text)
                layout.addWidget(checkBox, row, 0, 1, 2)
                def handleToggled(checked):
                    obj.value = checked
                checkBox.toggled.connect(handleToggled)
                checkBox.setChecked(defaultValue)
            elif optionType == 'radioButtons':
                [values, text] = option[2:]
                groupBox = QGroupBox(text)
                layout.addWidget(groupBox, row, 0, 1, 2)
                groupBox.setLayout(QVBoxLayout())
                for i, value in enumerate(values):
                    radioButton = QRadioButton(value)
                    groupBox.layout().addWidget(radioButton)
                    def handleToggled(toggled):
                        if toggled:
                            obj.value = value
                    radioButton.toggled.connect(handleToggled)
                    radioButton.setChecked(i == 0)
        options = []
