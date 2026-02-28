from pathlib import Path
from PySide6.QtCore import Qt, QMimeData, QByteArray
from PySide6.QtGui import QPixmap, QDrag
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QGridLayout
from market import RoundedWidget
from collections import Counter

BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "../Images"
PIXEL_ART_DIR = IMG_DIR / "pixel-art"


class Inventaire(QWidget):

    def __init__(self, aquarium, poissons_int_lst, poisson_lst):
        super().__init__()
        self.i = 0
        self.j = 0
        self.aquarium = aquarium
        self.poissons_int_lst = poissons_int_lst
        self.poisson_lst = poisson_lst

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
        btn_fermer.mousePressEvent = lambda e: self.aquarium.fermer_inventaire()
        conteneur_layout.addWidget(btn_fermer)

        # ── Bouton "Tout ranger" ──
        btn_tout_ranger = QLabel("⬇ Tout ranger")
        btn_tout_ranger.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_tout_ranger.setFixedHeight(30)
        btn_tout_ranger.setStyleSheet("""
            QLabel {
                color: #006482;
                font-size: 11px;
                font-weight: bold;
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                margin: 0px 8px 4px 8px;
            }
            QLabel:hover { background: rgba(255,255,255,0.25); color: white; }
        """)
        btn_tout_ranger.mousePressEvent = lambda e: self.aquarium.tout_mettre_en_inventaire()
        conteneur_layout.addWidget(btn_tout_ranger)

        # ── ScrollArea à l'intérieur du RoundedWidget ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
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
        self.contenu_layout.setContentsMargins(10, 0, 10, 10)
        self.contenu_layout.setSpacing(8)
        self.contenu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        grille = QGridLayout()
        grille.setSpacing(6)

        compteur = Counter(self.poissons_int_lst)

        for i, (niveau, quantite) in enumerate(compteur.items()):
            nom = self.poisson_lst[niveau]
            slot = SlotPoisson(aquarium, niveau, nom)  # ← passer niveau au lieu de i

            badge = QLabel(f"×{quantite}", slot)
            badge.setStyleSheet("""
                background: rgba(0,0,0,0.6);
                color: white;
                font-size: 9px;
                border-radius: 4px;
                padding: 1px 3px;
            """)
            badge.adjustSize()
            badge.move(slot.width() - badge.width() - 2, 2)

            grille.addWidget(slot, i, 0)

        self.contenu_layout.addLayout(grille)

        scroll.setWidget(contenu)

        conteneur_layout.addWidget(scroll)

        main_layout.addWidget(conteneur)

    def creer_sections_inventaire(self, poisson):
        layout = QGridLayout()

        # Image du poisson
        label_image = QLabel()
        label_image.setFixedSize(100, 100)
        label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chemin_poisson = PIXEL_ART_DIR / f"{poisson}.png"
        image = QPixmap(str(chemin_poisson)).scaled(
            100, 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        label_image.setPixmap(image)

        layout.addWidget(label_image, self.i, self.j)

        if self.i % 2 == 0:
            self.j += 1
        else:
            self.i += 1

        return layout

    

class SlotPoisson(QLabel):
    def __init__(self, aquarium, index, nom_poisson, parent=None):
        super().__init__(parent)
        self.aquarium = aquarium
        self.index = index  # = niveau
        self.nom_poisson = nom_poisson
        self.setFixedSize(90, 90)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        chemin = PIXEL_ART_DIR / f"{nom_poisson}.png"
        self._pixmap = QPixmap(str(chemin)).scaled(
            70, 70,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(self._pixmap)
        self.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            QLabel:hover { background: rgba(255,255,255,0.25); }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Demander à l'aquarium de créer un poisson fantôme qui suit la souris
            self.aquarium.commencer_drag_inventaire(self.index, self._pixmap)
        