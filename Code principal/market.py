from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QPainter, QPainterPath, QColor, QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QPushButton

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "../Images"
PIXEL_ART_DIR = IMG_DIR / "pixel-art"


class Market(QWidget):

    def __init__(self, aquarium, poissons_lst, moula):
        super().__init__()
        self.aquarium = aquarium
        self.poissons_lst = poissons_lst
        self.moula = moula

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── RoundedWidget contient TOUT ──
        conteneur = RoundedWidget()
        conteneur.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        conteneur_layout = QVBoxLayout(conteneur)
        conteneur_layout.setContentsMargins(0, 0, 0, 0)
        conteneur_layout.setSpacing(0)

        # ── Bouton fermer à l'intérieur du RoundedWidget ──
        btn_fermer = QLabel("✕")
        btn_fermer.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_fermer.setFixedHeight(30)
        btn_fermer.setStyleSheet("""
            QLabel {
                color: #006482;
                font-size: 20px;
                font-weight: bold;
                padding-right: 8px;
                background: transparent;
            }
            QLabel:hover { color: #DA2C38; }
        """)
        btn_fermer.mousePressEvent = lambda e: self.aquarium.fermer_market()
        conteneur_layout.addWidget(btn_fermer)

        # ── ScrollArea à l'intérieur du RoundedWidget ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setViewportMargins(0, 0, 0, 0)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; margin: 0px; padding: 0px; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #A98467;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        scroll.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        scroll.viewport().setAutoFillBackground(False)

        # ── Contenu de la scroll ──
        contenu = QWidget()
        contenu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        contenu.setAutoFillBackground(False)
        self.contenu_layout = QVBoxLayout(contenu)
        self.contenu_layout.setContentsMargins(6, 0, 6, 10)
        self.contenu_layout.setSpacing(4)
        self.contenu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for i, poisson in enumerate(self.poissons_lst):
            section = self.creer_sections_achat(poisson, (i + 1))
            self.contenu_layout.addWidget(section)

            if i < len(self.poissons_lst) - 1:
                separateur = QWidget()
                separateur.setFixedHeight(1)
                separateur.setStyleSheet("background-color: rgba(169, 132, 103, 0.4);")
                self.contenu_layout.addWidget(separateur)

        scroll.setWidget(contenu)
        conteneur_layout.addWidget(scroll)

        main_layout.addWidget(conteneur)

    def creer_sections_achat(self, poisson: str, index):
        section = QWidget()
        section.setFixedHeight(100)
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        row = QHBoxLayout(section)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # Image du poisson
        label_image = QLabel()
        label_image.setFixedSize(70, 70)
        label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chemin_poisson = PIXEL_ART_DIR / f"{poisson}.png"
        image = QPixmap(str(chemin_poisson)).scaled(
            70, 70,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label_image.setPixmap(image)
        row.addWidget(label_image)

        # Description
        layout_description = QVBoxLayout()
        layout_description.setContentsMargins(0, 0, 0, 0)
        layout_description.setSpacing(2)
        layout_description.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        nom = poisson.replace("_", " ")
        label_nom = QLabel(nom)
        font = QFont("Arial", 11)
        font.setBold(True)
        label_nom.setFont(font)
        label_nom.setWordWrap(True)
        label_nom.setMaximumWidth(120)
        label_nom.setToolTip(poisson)
        layout_description.addWidget(label_nom)

        label_niveau = QLabel(f"Niveau: {index}")
        label_niveau.setFont(QFont("Arial", 9))
        layout_description.addWidget(label_niveau)

        row.addLayout(layout_description, 1)  # stretch=1
        row.addStretch()

        # Boutons pour acheter 1 ou 5 poissons
        layout_bouton = QVBoxLayout()
        layout_bouton.setContentsMargins(0, 0, 4, 0)
        layout_bouton.setSpacing(4)
        layout_bouton.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        coins = IMG_DIR / "moula.png"

        style = """
            QPushButton {
                background-color: #226F54;
                color: white;
                border: 2px solid transparent;
                border-radius: 10px;
                font-family: Arial;
                font-weight: bold;
                font-size: 11px;
                padding: 0px 2px;
                min-height: 24px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #1a5a43;
                border: 2px solid transparent;
            }
            QPushButton:pressed {
                background-color: #144332;
                border: 2px solid transparent;
                padding-top: 2px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
                border: 2px solid transparent;
            }
        """

        bouton_1 = QPushButton("1X: 100")
        bouton_1.setIcon(QIcon(str(coins)))
        bouton_1.setFlat(True)
        bouton_1.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        bouton_1.clicked.connect(lambda: self.creer_un_poisson(index))
        bouton_1.setStyleSheet(style)
        layout_bouton.addWidget(bouton_1)

        bouton_5 = QPushButton("5X: 500")
        bouton_5.setIcon(QIcon(str(coins)))
        bouton_5.setFlat(True)
        bouton_5.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        bouton_5.clicked.connect(lambda: self.creer_cinq_poisson(index))
        bouton_5.setStyleSheet(style)
        layout_bouton.addWidget(bouton_5)

        row.addLayout(layout_bouton)

        return section

    def creer_un_poisson(self, index):
        self.aquarium.creer_poisson(niveau=index - 1)

    def creer_cinq_poisson(self, index):
        for _ in range(5):
            self.aquarium.creer_poisson(niveau=index - 1)

# ===========================
# QWidget avec border-radius
# ===========================
class RoundedWidget(QWidget):

    def __init__(self, radius=20, color="#F0DFC4", parent=None):
        super().__init__(parent)
        self.radius = radius
        self.color = QColor(color)
        # Fond transparent pour que les coins arrondis soient visibles
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)

        painter.fillPath(path, self.color)
        painter.end()
