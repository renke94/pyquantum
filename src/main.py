import sys
from typing import List, Optional, Union

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QLayout, QLineEdit, QSplitter, QFrame, QGridLayout, QPlainTextEdit, QTableView


class Observable:
    def __init__(self, value):
        self.value = value
        self.subscribers = set()

    def set_value(self, value):
        self.value = value
        self.notify_subscribers()

    def notify_subscribers(self):
        for sub in self.subscribers:
            sub.value_update(self.value)

    def subscribe(self, observer):
        self.subscribers.add(observer)

    def unsubscribe(self, observer):
        self.subscribers.remove(observer)

    def map(self, mapping):
        return MappedValue(self, mapping)

    def __iadd__(self, other):
        self.set_value(self.value + other)
        return self

    def __isub__(self, other):
        self.set_value(self.value - other)
        return self

class Observer:
    def __init__(self, observable: Optional[Observable]):
        self.observable = observable
        if observable is not None:
            self.observable.subscribe(self)
        self.update_callbacks = []

    def on_update(self, callback):
        self.update_callbacks.append(callback)

    def value_update(self, value):
        for callback in self.update_callbacks:
            callback(value)

    def __del__(self):
        if self.observable is not None:
            self.observable.unsubscribe(self)


class MappedValue(Observer, Observable):
    def __init__(self, observable: Observable, mapping):
        super(MappedValue, self).__init__(observable=observable)    # 1. super class constructor (Observer)
        Observable.__init__(self, value=mapping(observable.value))  # 2. super class constructor (Observable)
        self.mapping = mapping

        def on_update(value):
            self.set_value(self.mapping(value))

        self.on_update(on_update)


class Label(QLabel, Observer):
    def __init__(
            self,
            parent: QWidget,
            value: Union[Observable, str],
            min_width: int = None,
            max_width: int = None
    ):
        if isinstance(value, Observable):
            super(Label, self).__init__(observable=value)
            self.setText(value.value)
        else:
            super(Label, self).__init__(observable=None)
            self.setText(value)
        self.setParent(parent)
        self.on_update(self.setText)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)


class Button(QPushButton, Observer):
    def __init__(
            self,
            parent: QWidget,
            value: Union[Observable, str],
            on_click=None,
            min_width: int = None,
            max_width: int = None
    ):
        if isinstance(value, Observable):
            super(Button, self).__init__(observable=value)
            self.setText(value.value)
            self.on_update(self.setText)
        else:
            super(Button, self).__init__(observable=None)
            self.setText(value)
        self.setParent(parent)

        if on_click is not None:
            self.clicked.connect(on_click)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)


class Input(QLineEdit, Observer):
    def __init__(
            self,
            parent: QWidget,
            binding: Observable,
            min_width: int = None,
            max_width: int = None
    ):
        super(Input, self).__init__(observable=binding)
        self.setParent(parent)
        self.setText(binding.value)
        self.textEdited.connect(binding.set_value)
        self.on_update(self.setText)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)


class Row(QHBoxLayout):
    def __init__(self, children: List = []):
        super(QHBoxLayout, self).__init__()
        for child in children:
            if isinstance(child, (tuple, list)):
                child, stretch = child
            else:
                child, stretch = child, 1

            if isinstance(child, QWidget):
                self.addWidget(child, stretch)
            elif isinstance(child, QLayout):
                self.addLayout(child, stretch)
            elif isinstance(child, Spacer):
                self.addStretch(child.stretch)


class Column(QVBoxLayout):
    def __init__(self, children: List = []):
        super(QVBoxLayout, self).__init__()
        for child in children:
            if isinstance(child, (tuple, list)):
                child, stretch = child
            else:
                child, stretch = child, 1

            if isinstance(child, QWidget):
                self.addWidget(child, stretch)
            elif isinstance(child, QLayout):
                self.addLayout(child, stretch)
            elif isinstance(child, Spacer):
                self.addStretch(child.stretch)


class GridLayout(QGridLayout):
    def __init__(self, children: List = []):
        super(GridLayout, self).__init__()
        for child, row, column in children:
            self.addWidget(child, row, column)


class Spacer:
    def __init__(self, stretch: int):
        self.stretch = stretch

class Splitter(QSplitter):
    def __init__(
            self,
            parent: Optional[QWidget] = None,
            orientation: str = 'horizontal',
            children: List = []
    ):
        if orientation == 'horizontal':
            orientation = Qt.Orientation.Horizontal
        elif orientation == 'vertical':
            orientation = Qt.Orientation.Vertical
        else:
            raise ValueError("Orientation must be either 'horizontal' or 'vertical'")

        super(Splitter, self).__init__(orientation=orientation, parent=parent)

        for i, child in enumerate(children):
            if isinstance(child, (tuple, list)):
                child, stretch = child
            else:
                child, stretch = child, 1

            if isinstance(child, QLayout):
                frame = QFrame()
                frame.setLayout(child)
                child = frame

            self.addWidget(child)
            self.setStretchFactor(i, stretch)



class ViewModel:
    def __setattr__(self, key, value):
        if key in self.__dict__:
            if isinstance(value, Observable):
                value = value.value
            self.__dict__[key].set_value(value)
        else:
            self.__dict__[key] = Observable(value)

class View(QWidget):
    def __init__(self):
        super(View, self).__init__()
        self.model = ViewModel()


class MainView(View):
    def __init__(self):
        super(MainView, self).__init__()
        self.model.count = 0
        self.model.receiver = ""
        self.model.subject = ""

        def increment():
            self.model.text = "Hallo"
            self.model.count += 1

        def decrement():
            self.model.count -= 1

        count_str = self.model.count.map(lambda x: f"clicked {x} times")

        self.setLayout(Column([
            Splitter(
                parent = self,
                orientation = 'vertical',
                children = [
                    Column([
                        (Row([
                            (Button(self, "Datei auswählen"), 0),
                            (Label(self, "keine Datei ausgewählt"), 1)
                        ]), 0),
                        (QTableView(self), 1),
                    ]),
                    Column([
                        (GridLayout([
                            (Label(self, "An:", max_width=100), 0, 0),
                            (Input(self, self.model.receiver), 0, 1),
                            (Label(self, "Betreff:", max_width=100), 1, 0),
                            (Input(self, self.model.subject), 1, 1),
                        ]), 0),
                        (Row([
                            (Label(self, "Email Text"), 0),
                            Spacer(1),
                            (Button(self, "Vorschau", min_width=100), 0)
                        ]), 0),
                        (QPlainTextEdit(parent=self), 1),
                        (Row([
                            (Button(self, "Einstellungen", min_width=100), 0),
                            Spacer(1),
                            (Button(self, "Alle senden", min_width=100), 0),
                        ]), 0)
                    ])
                ]
            )
        ]))


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(1280, 900)
        self.setWindowTitle("PyQt Compose")

        widget = MainView()
        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())