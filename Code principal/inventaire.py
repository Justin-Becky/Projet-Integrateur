from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QGridLayout, QHBoxLayout
from market import RoundedWidget

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

        # ── Sélecteur de quantité ──
        self.quantite_sortie = 1  # valeur par défaut

        selecteur_layout = QHBoxLayout()
        selecteur_layout.setContentsMargins(8, 0, 8, 4)
        selecteur_layout.setSpacing(4)

        style_btn_inactif = """
            QLabel {
                color: #006482;
                font-size: 11px;
                font-weight: bold;
                background: rgba(255,255,255,0.1);
                border-radius: 6px;
                padding: 2px;
            }
            QLabel:hover { background: rgba(255,255,255,0.25); color: white; }
        """
        style_btn_actif = """
            QLabel {
                color: white;
                font-size: 11px;
                font-weight: bold;
                background: #006482;
                border-radius: 6px;
                padding: 2px;
            }
        """

        self.btn_1 = QLabel("×1")
        self.btn_5 = QLabel("×5")
        self.btn_tous = QLabel("tous")

        for btn in [self.btn_1, self.btn_5, self.btn_tous]:
            btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btn.setFixedHeight(24)
            btn.setStyleSheet(style_btn_inactif)
            selecteur_layout.addWidget(btn)

        # Activer ×1 par défaut
        self.btn_1.setStyleSheet(style_btn_actif)

        def selectionner(valeur, btn_actif):
            self.quantite_sortie = valeur
            for b in [self.btn_1, self.btn_5, self.btn_tous]:
                b.setStyleSheet(style_btn_inactif)
            btn_actif.setStyleSheet(style_btn_actif)

        self.btn_1.mousePressEvent = lambda e: selectionner(1, self.btn_1)
        self.btn_5.mousePressEvent = lambda e: selectionner(5, self.btn_5)
        self.btn_tous.mousePressEvent = lambda e: selectionner(-1, self.btn_tous)  # -1 = tous

        conteneur_layout.addLayout(selecteur_layout)

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

        # ── Bouton "Tout sortir" ──
        btn_tout_sortir = QLabel("⬆ Tout sortir")
        btn_tout_sortir.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_tout_sortir.setFixedHeight(35)
        btn_tout_sortir.setStyleSheet("""
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
        btn_tout_sortir.mousePressEvent = lambda e: self.aquarium.tout_sortir_inventaire()
        conteneur_layout.addWidget(btn_tout_sortir)

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

        self.grille = QGridLayout()
        self.grille.setSpacing(6)

        # dictionnaire ordonné pour préserver l'ordre d'apparition dans l'inventaire
        compteur = {}
        for niveau in self.poissons_int_lst:
            compteur[niveau] = compteur.get(niveau, 0) + 1

        self.slots = {}  # niveau → SlotPoisson

        for i, (niveau, quantite) in enumerate(compteur.items()):
            nom = self.poisson_lst[niveau]
            slot = SlotPoisson(aquarium, niveau, nom, quantite)
            self.grille.addWidget(slot, i, 0)
            self.slots[niveau] = slot

            self.grille.addWidget(slot, i, 0)

        self.contenu_layout.addLayout(self.grille)

        scroll.setWidget(contenu)

        conteneur_layout.addWidget(scroll)

        main_layout.addWidget(conteneur)

    def mettre_a_jour_slot(self, niveau, nouvelle_quantite):
        slot = self.slots.get(niveau)
        if slot is None:
            if nouvelle_quantite > 0:
                self.ajouter_slot(niveau, nouvelle_quantite)
            return
        slot.quantite = nouvelle_quantite
        slot.badge.setText(f"×{nouvelle_quantite}")
        slot.badge.setVisible(nouvelle_quantite > 1)
        slot.repositionner_badge()
        slot.setEnabled(nouvelle_quantite > 0)
        slot.setStyleSheet("""
            QLabel {
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.1);
            }
        """ if nouvelle_quantite == 0 else """
            QLabel {
                background: rgba(255,255,255,0.1);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.2);
            }
            QLabel:hover { background: rgba(255,255,255,0.25); }
        """)

    def ajouter_slot(self, niveau, quantite):
        """Crée et ajoute un nouveau slot pour un niveau qui n'existait pas encore."""
        nom = self.poisson_lst[niveau]
        slot = SlotPoisson(self.aquarium, niveau, nom, quantite)
        ligne = len(self.slots)
        self.grille.addWidget(slot, ligne, 0)
        self.slots[niveau] = slot
        slot.show()

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
    def __init__(self, aquarium, index, nom_poisson, quantite=1, parent=None):
        super().__init__(parent)
        self.aquarium = aquarium
        self.index = index  # = niveau
        self.nom_poisson = nom_poisson
        self.quantite = quantite
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

        # Badge quantité
        self.badge = QLabel(f"×{self.quantite}", self)
        self.badge.setStyleSheet("""
            background: rgba(0,0,0,0.6);
            color: white;
            font-size: 9px;
            border-radius: 4px;
            padding: 1px 3px;
        """)
        self.badge.adjustSize()
        self.badge.move(self.width() - self.badge.width() - 2, 2)
        self.badge.setVisible(self.quantite > 1)

    def repositionner_badge(self):
        self.badge.adjustSize()
        self.badge.move(self.width() - self.badge.width() - 2, 2)

    def showEvent(self, event):
        super().showEvent(event)
        self.repositionner_badge()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.aquarium.commencer_drag_inventaire(self.index, self._pixmap)
        