import sys
from typing import List, Optional, Union, Set, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, \
    QLayout, QLineEdit, QSplitter, QFrame, QGridLayout, QPlainTextEdit, QTableView, QTextEdit

from src.value import Observer, Value


class Label(QLabel):
    def __init__(
            self,
            parent: QWidget,
            value: Union[Value, str],
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None
    ):
        super(Label, self).__init__(parent=parent)
        if isinstance(value, Value):
            self.setText(value.data)
            self._value_observer = Observer([value])
            self._value_observer.on_update(self.setText)
        else:
            self.setText(value)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)


class Button(QPushButton):
    def __init__(
            self,
            parent: QWidget,
            value: Union[Value, str],
            on_click=None,
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None
    ):
        super(Button, self).__init__(parent=parent)

        if isinstance(value, Value):
            self.setText(value.data)
            self._text_observer = Observer([value])
            self._text_observer.on_update(self.setText)
        else:
            self.setText(value)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if on_click is not None:
            self.clicked.connect(on_click)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)


class Input(QLineEdit):
    def __init__(
            self,
            parent: QWidget,
            binding: Value,
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None
    ):
        super(Input, self).__init__(parent=parent)
        self.setText(binding.data)
        self.textEdited.connect(binding.set_data)
        self._binding_observer = Observer([binding])
        self._binding_observer.on_update(self.setText)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        if max_width is not None:
            self.setMaximumWidth(max_width)


class MultiLineInput(QPlainTextEdit):
    def __init__(
            self,
            parent: QWidget,
            binding: Value,
            enabled: Union[Value, bool] = True,
            min_width: int = None,
            max_width: int = None,
    ):
        super(MultiLineInput, self).__init__(parent=parent)
        self.setPlainText(binding.data)
        def set_data():
            binding.set_data(self.toPlainText())

        self.textChanged.connect(set_data)

        if isinstance(enabled, Value):
            self.setEnabled(enabled.data)
            self._enabled_observer = Observer([enabled])
            self._enabled_observer.on_update(self.setEnabled)
        else:
            self.setEnabled(enabled)

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
            if isinstance(value, Value):
                value = value.data
            self.__dict__[key].set_data(value)
        else:
            self.__dict__[key] = Value(value)

class View(QWidget):
    def __init__(self):
        super(View, self).__init__()
        self.model = ViewModel()


class MainView(View):
    def __init__(self):
        super(MainView, self).__init__()
        self.model.receiver = ""
        self.model.subject = ""
        self.model.email_text = ""

        receiver_not_empty = self.model.receiver.map(lambda s: len(s.strip())) > 0
        subject_not_empty = self.model.subject.map(lambda s: len(s.strip())) > 0
        preview_enabled = self.model.email_text.map(lambda s: len(s.strip())) > 0

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
                            (Button(self, "Vorschau", min_width=100, enabled=preview_enabled), 0)
                        ]), 0),
                        (MultiLineInput(self, self.model.email_text), 1),
                        (Row([
                            (Button(self, "Einstellungen", min_width=100), 0),
                            Spacer(1),
                            (Button(
                                self,
                                "Alle senden",
                                enabled=receiver_not_empty & subject_not_empty & preview_enabled,
                                min_width=100,
                            ), 0),
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