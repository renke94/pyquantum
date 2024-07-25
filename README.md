# PyQuantum

This package provides wrapper classes around PyQt, bringing enhanced functionality and ease of use to your PyQt applications. With this package, you can enjoy the following advantages:

- __Seamless Integration__: Easily integrate these wrapper classes into your existing PyQt projects without any hassle.
- __Reactive UI Elements__: Create dynamic and responsive user interfaces with reactive UI elements that adapt to changes effortlessly.
- __Concise Code__: Write clean and concise code, similar to the style of Flutter, making your development process more efficient and enjoyable.

## Examples

```python
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox

from pyquantum.ui import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Wrap variables in observables
        self.name = Value("")

        # Initialize UI
        self.resize(320, 100)
        self.setWindowTitle("PyQuantum Example")
        self.setCentralWidget(
            TabView(
                parent=self,
                tabs={
                    'User Form': Widget(
                        parent=self,
                        layout=Column([
                            Input(
                                parent=self,
                                binding=self.name
                            ),
                            Row([
                                Spacer(1),
                                Button(
                                    parent=self,
                                    value="Say Hello",
                                    enabled=self.name.map(lambda n: len(n) > 0),  # reactive enabling
                                    on_click=lambda: QMessageBox.information(self, "", f"Hello {self.name.data}")
                                ),
                            ]),
                            Spacer(1),
                        ])
                    ),
                    'Settings': Widget(parent=self),
                }
            )
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```
