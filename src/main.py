import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView

from pyquantum.ui import *


class MainView(View):
    def __init__(self):
        super(MainView, self).__init__()
        self.model.path = None
        self.model.receiver = ""
        self.model.subject = ""
        self.model.email_text = ""

        receiver_not_empty = self.model.receiver.map(lambda s: len(s.strip())) > 0
        subject_not_empty = self.model.subject.map(lambda s: len(s.strip())) > 0
        preview_enabled = self.model.email_text.map(lambda s: len(s.strip())) > 0

        path_alt_string = "Keine Datei ausgewählt"
        path_string = self.model.path.map(lambda p: path_alt_string if p is None else str(p))

        def open_file_dialog():
            path = FileDialog.save_file(self, "Test")
            if path is None:
                return
            self.model.path = path

        self.setLayout(Column([
            Splitter(
                parent = self,
                orientation = 'vertical',
                children = [
                    Column([
                        (Row([
                            (Button(self, "Datei auswählen", on_click=open_file_dialog), 0),
                            (Label(self, path_string), 1)
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
        self.setWindowTitle("PyQuantum")

        widget = MainView()
        self.setCentralWidget(widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())