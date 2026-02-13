from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QWidget, QPushButton, QVBoxLayout


class HomeMenuApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Home Menu Example")

        disposition_central = QWidget()
        self.setCentralWidget(disposition_central)

        layout = QVBoxLayout()
        disposition_central.setLayout(layout)

        button = PersonalizedButton(
            position=QtCore.QPoint(50, 50),
            size=QSize(64, 64),
            image_path="../Images/Bouton/bouton.png",
            callback="new_file",
            parent=self
        )
        layout.addWidget(button)

    def new_file(self):
        print("New file action triggered")

    def open_file(self):
        print("Open file action triggered")


class PersonalizedButton(QPushButton):
    def __init__(self, position: QtCore.QPoint, size: QSize, image_path, callback, parent):
        super().__init__(parent)

        self.setIcon(QIcon(image_path))
        self.setIconSize(size)
        self.setText(callback)
        self.setGeometry(position.x(), position.y(), size.width(), size.height())
        self.setStyleSheet("border: none; background-color: transparent;")
        self.clicked.connect(parent.__getattribute__(callback))


app = QApplication()
home_menu = HomeMenuApp()
home_menu.show()
app.exec()
