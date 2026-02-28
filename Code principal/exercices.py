
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QFont, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QToolButton, QMenu, \
    QScrollArea, QLabel, QHBoxLayout, QTextBrowser
from Aquarium import AquariumWidget
import json

STYLE_SHEET = """
/* Main Window */
QMainWindow {
    background-color: #D1E4D4;
}

/* Header */
QWidget#custom_header {
    background-color: #006482;
    border-bottom: 2px solid #00506b;
}

/* Header Title */
QLabel#header_title {
    color: #F0DFC4;
    font-weight: bold;
    font-size: 22px;
}

/* Burger MMenu button */
QToolButton.burger_button { 
    border: none;
    font-size: 30px; 
    color: white;
    background: transparent;
    border-radius: 5px;

}

QToolButton.burger_button:hover {
    background-color: rgba(255,255,255,0.2);
}

/* Burger Menu */
QMenu.burger_menu {
    background-color: #F0DFC4;
    border: 1px solid #A67B5B;
}

QMenu.burger_menu::item {
padding: 10px 20px;
color: #006482;
}

QMenu.burger_menu::item:selected {
background-color: #D1E4D4;
}

/* help button */
QToolButton.help_button {
    border: 2px solid #6BCED4; 
    border-radius: 25px;
    font-size: 24px; 
    font-weight: bold;
    color: #6BCED4;
    background: transparent;
}

QToolButton.help_button:hover {
    background-color: #6BCED4; 
    color: #006482;
}

/* Scroll Area */
QScrollArea {
    background-color: transparent;
    border: none;
    margin: 0px 50px;
}

/* The Content Page */
QWidget#content_widget {
    background-color: #F0DFC4;
    border-radius: 15px;
    border: 1px solid #E8C89C;
}

/* Action Buttons */
QPushButton.action_btn {
    padding: 10px;
    border-radius: 8px;
    border: 3px ridge grey;
    font-size: 14px;
    font-weight: bold;
}
QPushButton.action_btn:hover {
    color: black;
}

/* ScrollBar */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 14px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #70A599;
    min-height: 20px;
    border-radius: 7px;
}
QScrollBar::handle:vertical:hover {
    background-color: #0F665D;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

class ExercicesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exercices Module")
        self.setGeometry(100, 100, 800, 600)

        # Central Widget and Layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setCentralWidget(self.central_widget)

        # <editor-fold desc="header Setup">
        # Header Layout
        self.header_widget = QWidget()
        self.header_widget.setObjectName("custom_header")
        self.header_widget.setFixedHeight(80)

        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(15, 20, 15, 20)

        # Burger menu
        self.burger_button = QToolButton()
        self.burger_button.setText("☰")
        self.burger_button.setFixedSize(50, 50)
        self.burger_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.burger_button.setProperty("class", "burger_button")

        self.burger_menu = QMenu(self)
        self.burger_menu.setProperty("class", "burger_menu")

        self.burger_menu.addAction("Home", self.open_selector)
        self.burger_menu.addAction("Profile", lambda: print("Profile"))
        self.burger_menu.addAction("Settings", lambda: print("Settings"))
        self.burger_menu.addSeparator()
        self.burger_menu.addAction("Logout", lambda: print("Logout"))

        self.burger_button.clicked.connect(self.show_burger_menu)
        header_layout.addWidget(self.burger_button)

        # Moula
        self.moula_widget = QWidget()
        self.moula_widget.setStyleSheet("""
            QWidget { 
            background: black;
            border-radius: 20px;
            }
        """)
        header_layout.addWidget(self.moula_widget)
        self.moula_layout = QHBoxLayout()
        self.moula_widget.setLayout(self.moula_layout)

        self.aquarium_widget = AquariumWidget(self)
        self.moula_texte_label = self.aquarium_widget.moula_texte_label
        self.moula_texte_label.setFont(QFont("Arial", 15))

        self.moula_image_label = QLabel()
        self.moula_image = QPixmap("../images/moula.png").scaled(
            20, 20,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.moula_image_label.setPixmap(self.moula_image)

        self.moula_texte_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.moula_texte_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.moula_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.moula_image_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.moula_layout.addWidget(self.moula_texte_label)
        self.moula_layout.addWidget(self.moula_image_label)

        # Title
        self.header_title = QLabel("Sélection de modules")
        self.header_title.setObjectName("header_title")
        self.header_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.header_title, 1)

        # Aquarium button
        self.aquarium_button = QToolButton()
        self.aquarium_icon = QIcon("../images/aquarium.png")
        self.exercice_icon = QIcon("../images/exercice.png")
        self.aquarium_button.setIcon(self.aquarium_icon)
        self.aquarium_button.setFixedSize(50, 50)
        self.aquarium_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.aquarium_button.setStyleSheet("""
                    QToolButton { 
                        border: 2px solid #6BCED4; 
                        border-radius: 25px; /* Circle */
                        color: #6BCED4;
                        background: transparent;
                    }
                    QToolButton:hover { 
                        background-color: #6BCED4; 
                        color: #006482;
                    }
                """)
        self.aquarium_button.clicked.connect(self.switch_aquarium_excercie)
        header_layout.addWidget(self.aquarium_button)

        self.layout.addWidget(self.header_widget)

        # Help Button
        self.help_button = QToolButton()
        self.help_button.setText("?")
        self.help_button.setFixedSize(50, 50)
        self.help_button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.help_button.setProperty("class", "help_button")
        self.help_button.clicked.connect(lambda: print("Help clicked"))
        header_layout.addWidget(self.help_button)

        self.layout.addWidget(self.header_widget)
        # </editor-fold>

        # <editor-fold desc="scroll area and content Setup">
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.current_widget = self.scroll_area

        self.layout.addWidget(self.scroll_area)
        # </editor-fold>

        self.open_selector()

    def open_selector(self):
        self.header_title.setText("Sélection de modules")

        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")

        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(15)

        self.scroll_area.setWidget(self.content_widget)

        self.open_exercise()

    def switch_aquarium_excercie(self):
        if self.current_widget == self.scroll_area:
            self.aquarium_button.setIcon(self.exercice_icon)
            nouveau_widget = self.aquarium_widget
        else:
            self.aquarium_button.setIcon(self.aquarium_icon)
            nouveau_widget = self.scroll_area

        self.layout.removeWidget(self.current_widget)
        self.current_widget.hide()
        self.current_widget = nouveau_widget
        self.layout.addWidget(self.current_widget)
        nouveau_widget.show()

        # Redonner le focus à l’aquarium ou au scroll_area
        nouveau_widget.setFocus()

    def open_exercise(self):
        with open('./Exercices Files/Exercices_structure.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        for i in data:
            section_title = QLabel(f"<h1>{i['title']}</h1>")
            section_title.setStyleSheet("color: #A67B5B;")
            self.content_layout.addWidget(section_title)

            for j in i['content']:
                section_content = QWidget()
                section_layout = QVBoxLayout(section_content)
                section_layout.setContentsMargins(0, 0, 0, 0)
                section_layout.setSpacing(8)

                section_content.setStyleSheet("background-color: #F0DFC4;")

                collapsible = CollapsibleSection(j['title'], j['description'], section_content, color=j['color'][0]['title'], expanded=False)
                self.content_layout.addWidget(collapsible)

                button_section_holder = QWidget()

                section_layout.addWidget(button_section_holder)

                for idx, k in enumerate(j['content']):
                    row_widget = QWidget()
                    row_layout = QHBoxLayout(row_widget)
                    row_layout.setContentsMargins(0, 0, 0, 0)
                    row_layout.setSpacing(10)

                    background_color, border_color, text_color, hovered_color = j['color'][0]['button-background'], \
                    j['color'][0]['button-border'], j['color'][0]['button-text'], j['color'][0]['button-hovered-text']
                    btn_style = f"""
                                            QPushButton {{
                                                background-color: {background_color};
                                                border: 3px ridge {border_color};
                                                color: {text_color};
                                            }}
                                            QPushButton:hover {{
                                                color: {hovered_color};
                                            }}
                                        """

                    matiere_btn = QPushButton("Matière " + k['title'])
                    matiere_btn.setProperty("class", "action_btn")
                    matiere_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
                    matiere_btn.clicked.connect(lambda _, link="../Exercices/matiere_" + str(k['id']) + ".html", info = (j['title'], k['title']): self.open_matiere(link, info))
                    matiere_btn.setStyleSheet(btn_style)

                    exercices_btn = QPushButton("Exercices " + k['title'])
                    exercices_btn.setProperty("class", "action_btn")
                    exercices_btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
                    exercices_btn.clicked.connect(lambda _, link="../Exercices/exercice_" + str(k['id']) + ".json": self.open_exercises(link))
                    exercices_btn.setStyleSheet(btn_style)

                    row_layout.addWidget(matiere_btn, 1)
                    row_layout.addWidget(exercices_btn, 1)

                    section_layout.addWidget(row_widget)

                    if idx != len(j['content']) -1:
                        separator_line = QWidget()
                        separator_line.setFixedHeight(2)
                        separator_line.setStyleSheet("background-color: #E8C89C; margin: 15px 0;")
                        section_layout.addWidget(separator_line)

                section_layout.addStretch()
        self.content_layout.addStretch()

    def show_burger_menu(self):
        pos = self.burger_button.mapToGlobal(self.burger_button.rect().bottomLeft())

        self.burger_menu.exec(pos)

    def open_matiere(self, file_path, info):
        self.header_title.setText(f"{info[0]}, section {info[1]}")

        matiere_widget = QTextBrowser()
        matiere_widget.setObjectName("content_widget")
        self.scroll_area.setWidget(matiere_widget)

        matiere_widget.setSource(file_path)

    def open_exercises(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        print("e")


class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title: str, description: str, content_widget: QWidget = None, *, parent=None, color, expanded: bool = True):
        super().__init__(parent)

        self.arrow_btn = QtWidgets.QToolButton()
        self.arrow_btn.setCheckable(True)
        self.arrow_btn.setChecked(expanded)
        self.arrow_btn.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        self.arrow_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.arrow_btn.setStyleSheet("QToolButton { border: none; padding: 0 8px; }")

        self.title_label = QLabel(f"<span style='font-weight:bold; font-size:18px; color:{color}'>{title}</span> <span style='color:#555; font-size: 14px;'>{description}</span>")

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 6, 0, 0)
        header_layout.setSpacing(8)
        header_layout.addWidget(self.arrow_btn, 0)
        header_layout.addWidget(self.title_label, 1)

        def header_mouse_press(event):
            self.arrow_btn.toggle()
        header.mousePressEvent = header_mouse_press

        # Content area that will be collapsed/expanded
        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        # Ensure there is always a widget inside the scroll area
        if content_widget is None:
            content_widget = QWidget()
        self.content_area.setWidget(content_widget)

        # Animation for maximumHeight property on the content area
        self.toggle_animation = QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        self.toggle_animation.setDuration(180)
        self.toggle_animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(header)
        main_layout.addWidget(self.content_area)

        # Initialize collapsed/expanded state
        QtCore.QTimer.singleShot(0, lambda: self._set_initial_state(expanded))

        # Connect
        self.arrow_btn.toggled.connect(self.toggle)

    def _set_initial_state(self, expanded: bool):
        content_h = self._content_height()
        self.content_area.setMaximumHeight(content_h if expanded else 0)

    def _content_height(self) -> int:
        # Calculate the full height needed by the content widget
        cw = self.content_area.widget()
        cw.adjustSize()
        return cw.sizeHint().height()

    def toggle(self, checked: bool):
        self.arrow_btn.setArrowType(QtCore.Qt.ArrowType.DownArrow if checked else QtCore.Qt.ArrowType.RightArrow)
        start = self.content_area.maximumHeight()
        end = self._content_height() if checked else 0
        self.toggle_animation.stop()
        self.toggle_animation.setStartValue(start)
        self.toggle_animation.setEndValue(end)
        self.toggle_animation.start()


if __name__ == "__main__":
    app = QApplication()
    app.setStyleSheet(STYLE_SHEET)
    exercices = ExercicesWindow()
    exercices.show()
    app.exec()
