
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt, QTimer, QSize, QByteArray
from PySide6.QtGui import QIcon, QFont, QResizeEvent, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QToolButton, QMenu, \
    QScrollArea, QLabel, QHBoxLayout
from Aquarium import AquariumWidget
import json

# --- SEA INSPIRED PALETTE MAPPING ---
# Header Background: #006482 (Deep Blue)
# Window Background: #D1E4D4 (Light Sage)
# Page Background:   #F0DFC4 (Sand/Beige)
# Button Color:      #11BBAA (Teal)
# Text Color:        #0F665D (Dark Green/Teal)

STYLE_SHEET = """
/* 1. Main Window Background */
QMainWindow {
    background-color: #D1E4D4; /* Light Sage */
}

/* 2. The Custom Header Widget */
QWidget#custom_header {
    background-color: #006482; /* Deep Blue from palette bottom-right */
    border-bottom: 2px solid #00506b;
}

/* 3. Header Title Label */
QLabel#header_title {
    color: #F0DFC4; /* Sand color text */
    font-weight: bold;
    font-size: 22px;
}

/* 4. The Scroll Area (Transparent container) */
QScrollArea {
    background-color: transparent;
    border: none;
    margin: 0px 50px; /* Margins to show the Main Window color on sides */
}

/* 5. The Content Page (The visible paper) */
QWidget#content_widget {
    background-color: #F0DFC4; /* Sand/Beige from palette top-left */
    border-radius: 15px;
    border: 1px solid #E8C89C;
}

/* 6. Action Buttons in the page */
QPushButton.action_btn {
    background-color: #11BBAA; /* Teal from palette middle */
    color: white;
    padding: 10px;
    border-radius: 8px;
    border: none;
    font-size: 14px;
    font-weight: bold;
}
QPushButton.action_btn:hover {
    background-color: #008583; /* Darker Teal */
}

/* 7. ScrollBar Styling */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 14px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #70A599; /* Sage Green handle */
    min-height: 20px;
    border-radius: 7px;
}
QScrollBar::handle:vertical:hover {
    background-color: #0F665D; /* Darker Green handle */
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
        self.burger_button.setStyleSheet("""
                    QToolButton { 
                        border: none;
                        font-size: 30px; 
                        color: white;
                        background: transparent;
                        border-radius: 5px;
                    }
                    QToolButton:hover { background-color: rgba(255,255,255,0.2); }
                """)

        self.burger_menu = QMenu(self)
        self.burger_menu.setStyleSheet("""
                    QMenu { background-color: #F0DFC4; border: 1px solid #A67B5B; }
                    QMenu::item { padding: 10px 20px; color: #006482; }
                    QMenu::item:selected { background-color: #D1E4D4; }
                """)
        self.burger_menu.addAction("Profile", self.open_exercise)
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
        self.help_button.setStyleSheet("""
                    QToolButton { 
                        border: 2px solid #6BCED4; 
                        border-radius: 25px; /* Circle */
                        font-size: 24px; 
                        font-weight: bold;
                        color: #6BCED4;
                        background: transparent;
                    }
                    QToolButton:hover { 
                        background-color: #6BCED4; 
                        color: #006482;
                    }
                """)
        self.help_button.clicked.connect(lambda: print("Help clicked"))
        header_layout.addWidget(self.help_button)

        self.layout.addWidget(self.header_widget)
        # </editor-fold>

        # <editor-fold desc="scroll area and content Setup">
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.current_widget = self.scroll_area

        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")

        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(30, 30, 30, 30)
        self.content_layout.setSpacing(15)

        # # Add buttons
        # for i in range(1, 20):
        #     btn = QPushButton(f"typeshit {i}")
        #     btn.setProperty("class", "action_btn")
        #     self.content_layout.addWidget(btn)

        self.content_layout.addStretch()
        self.scroll_area.setWidget(self.content_widget)
        self.layout.addWidget(self.scroll_area)
        # </editor-fold>

        self.open_exercise()

    def switch_aquarium_excercie(self):
        if self.current_widget == self.scroll_area:
            self.aquarium_button.setIcon(self.exercice_icon)
            nouveau_widget = self.aquarium_widget

            # Désactiver scroll quand on est dans l’aquarium
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll_area.setEnabled(False)
            QTimer.singleShot(0, lambda: self.aquarium_widget.resizeEvent(
                QResizeEvent(self.aquarium_widget.size(), QSize(0, 0)
                             )))
        else:
            self.aquarium_button.setIcon(self.aquarium_icon)
            nouveau_widget = self.scroll_area

            # Réactiver le scroll quand on revient aux exercices
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.scroll_area.setEnabled(True)

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
                collapsible = CollapsibleSection(f"<span "
                                                 f"style='font-weight:bold; "
                                                 f"font-size:18px; "
                                                 f"color:#006482'>{j['title']}</span> {j['description']}",
                                                 section_content, expanded=False
                                                 )
                self.content_layout.addWidget(collapsible)

                section_desc = QLabel("test")
                section_desc.setStyleSheet("color: #555; font-size: 16px; margin-bottom: 20px;")
                section_desc.setWordWrap(True)

                section_layout.addWidget(section_desc)

                for k in j['content']:
                    bouton_holder = QHBoxLayout()

                    matiere_btn = QPushButton("Matière " + k['title'])
                    matiere_btn.setProperty("class", "action_btn")
                    matiere_btn.clicked.connect(lambda _, link=str(k['id']) + "_m": print(f"Open {link}"))

                    exercices_btn = QPushButton("Exercices " + k['title'])
                    exercices_btn.setProperty("class", "action_btn")
                    exercices_btn.clicked.connect(lambda _, link=str(k['id']) + "_e": print(f"Open {link}"))

                    bouton_holder.addWidget(matiere_btn)
                    bouton_holder.addWidget(exercices_btn)

                    self.content_layout.addLayout(bouton_holder)

                    if k != j['content'][-1]:
                        separator_line = QWidget()
                        separator_line.setFixedHeight(2)
                        separator_line.setStyleSheet("background-color: #E8C89C; margin: 15px 0;")
                        self.content_layout.addWidget(separator_line)

    def show_burger_menu(self):
        pos = self.burger_button.mapToGlobal(self.burger_button.rect().bottomLeft())

        self.burger_menu.exec(pos)


class CollapsibleSection(QtWidgets.QWidget):
    def __init__(self, title: str, content_widget: QWidget = None, *, parent=None, expanded: bool = True):
        super().__init__(parent)
        self.header_btn = QtWidgets.QToolButton()
        self.header_btn.setText(title)
        self.header_btn.setCheckable(True)
        self.header_btn.setChecked(expanded)
        self.header_btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.header_btn.setArrowType(QtCore.Qt.ArrowType.DownArrow if expanded else QtCore.Qt.ArrowType.RightArrow)
        self.header_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        # Content area that will be collapsed/expanded
        self.content_area = QtWidgets.QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        # Ensure there is always a widget inside the scroll area
        if content_widget is None:
            content_widget = QtWidgets.QWidget()
        self.content_area.setWidget(content_widget)

        # Animation for maximumHeight property on the content area
        self.toggle_animation = QtCore.QPropertyAnimation(self.content_area, QByteArray(b"maximumHeight"))
        self.toggle_animation.setDuration(180)
        self.toggle_animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutQuad)

        # Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.header_btn)
        main_layout.addWidget(self.content_area)

        # Initialize collapsed/expanded state
        QtCore.QTimer.singleShot(0, lambda: self._set_initial_state(expanded))

        # Connect
        self.header_btn.toggled.connect(self.toggle)

    def _set_initial_state(self, expanded: bool):
        content_h = self._content_height()
        self.content_area.setMaximumHeight(content_h if expanded else 0)

    def _content_height(self) -> int:
        # Calculate the full height needed by the content widget
        cw = self.content_area.widget()
        cw.adjustSize()
        return cw.sizeHint().height()

    def toggle(self, checked: bool):
        self.header_btn.setArrowType(QtCore.Qt.ArrowType.DownArrow if checked else QtCore.Qt.ArrowType.RightArrow)
        start = self.content_area.maximumHeight()
        end = self._content_height() if checked else 0
        self.toggle_animation.stop()
        self.toggle_animation.setStartValue(start)
        self.toggle_animation.setEndValue(end)
        self.toggle_animation.start()


app = QApplication()
app.setStyleSheet(STYLE_SHEET)
exercices = ExercicesWindow()
exercices.show()
app.exec()
