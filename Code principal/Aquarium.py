import random
import math
from pathlib import Path

from PySide6 import QtWidgets
from PySide6.QtCore import QPointF, QRectF, Qt, QEasingCurve, QTimer
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QWidget,
                               QVBoxLayout, QLabel, QGraphicsColorizeEffect, QGraphicsDropShadowEffect)
from PySide6.QtGui import QPixmap, QColorConstants, QLinearGradient, QTransform, QColor
from Animations import AnimationBulle, AnimationPosition, AnimationRotation, AnimationScale
from market import Market
from inventaire import Inventaire

# ===================================================
# Liste d'évolution des poissons
# ===================================================
EVOLUTION_POISSON = [
    "basic_rouge", "poisson_jaune", "poisson_rayé", "green_bass", "saumon_bleu",
    "martin", "goldfish", "goldfish_long", "dore", "preuve_moyenne",
    "gros_rouge", "doris_sans_rayure", "doris_jaune", "doris_kawaii", "doris_oeil_aubernoir",
    "doris_og", "doris_bleu", "doris_brun", "doris_rouge", "doris_vert",
    "doris_rose", "hippocampe", "mouette", "crabe", "meduse",
    "puff", "poisson_mauve", "goldfish_jolie", "raie_manta", "dauphin",
    "baleine", "poisson_lion_fluo", "preuves", "preuve_complexe", "doris_shaded",
    "doris_skinny", "crevette", "anguille_cute", "poisson_chirurgien", "george_bleu",
    "beta_bleu", "Gill", "poisson_tournesol", "sunfish", "poisson_lune",
    "poisson_lune_bleu", "poisson_globe_bleu", "ton", "espadon", "espadon_croche",
    "poisson_lumiere", "poisson_lumiere2", "requin_baleine", "pokemon", "pokemon_licorne",
    "pokemon_magikarp",
]

# path
BASE_DIR = Path(__file__).parent
IMG_DIR = BASE_DIR / "../Images"
PIXEL_ART_DIR = IMG_DIR / "pixel-art"

# --- Constantes de la scène ---
MARGE = 0
MOULA = 10000
# --- Multiplicateur de vitesse des animations ---
# Plus la valeur est grande, plus les animations sont lentes
FACTEUR_LENTEUR = 1

# Constante pour la largeur du market
LARGEUR_MARKET = 500
LARGEUR_INVENTAIRE = 120

# <editor-fold desc="Clamping dynamique">
# --- Garde une position dans les limites de la scène ---
def clamper_position(x, y, largeur_poisson, hauteur_poisson, poisson):
    limite_gauche = LARGEUR_MARKET + 50 if poisson.aquarium and poisson.aquarium.proxy_market else MARGE
    limite_droite = poisson.aquarium.width() - LARGEUR_INVENTAIRE - largeur_poisson - 25 if \
        poisson.aquarium and poisson.aquarium.proxy_inventaire else poisson.aquarium.width() - largeur_poisson - MARGE
    if poisson.n == 22:
        x = max(limite_gauche, min(x, limite_droite))
        y = MARGE
    elif poisson.n == 23:
        x = max(limite_gauche, min(x, limite_droite))
        y = max(int(poisson.aquarium.height()) - 160 + 2 * hauteur_poisson // 3, min(
            y, poisson.aquarium.height() - 2 * hauteur_poisson // 3))
    else:
        # Décaler la limite gauche si le market est ouvert et décalé la limite de droite si l'inventaire est ouvert.
        x = max(limite_gauche, min(x, limite_droite))
        y = max(MARGE + 2 * hauteur_poisson // 3, min(y, poisson.aquarium.height() - 175))
    return x, y

# </editor-fold>


# ===================================================
# Fenêtre principale de l'application Aquarium
# ===================================================

class AquariumWidget(QWidget):

    def __init__(self, application):
        super().__init__()
        self.app = application
        self.n = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # <editor-fold desc="Vue graphique — Sans scrollbars">
        self.view = QGraphicsView()
        self.view.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                                QtWidgets.QSizePolicy.Policy.Expanding)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.wheelEvent = lambda event: None
        layout.addWidget(self.view)
        # </editor-fold>

        # Scène
        self.scene = Aquarium(self)
        self.view.setScene(self.scene)

        self.moula_texte_label = QLabel()
        self.moula_texte_label.setText(F"{MOULA}")

    def mise_a_jour_moula(self):
        self.moula_texte_label.setText(F"{MOULA}")

    def resizeEvent(self, event):
        """
        Met à jour la scène quand le widget se redimensionne.
        Force aussi le repositionnement de tous les poissons pour qu'ils restent dans les limites.
        """
        super().resizeEvent(event)
        w = self.view.width()
        h = self.view.height()

        # Mettre à jour la scène à la bonne taille
        self.scene.setSceneRect(0, 0, w, h)

        # Redessiner le sol
        self.scene.update_floor()

        # Redessiner le fond
        self.scene.update_background()

        # Redessiner l'icon d'inventaire
        self.scene.update_inventaire_icon()

        # Redessiner la sideBar du market et de l'inventaire
        self.scene.update_market()
        self.scene.update_inventaire()

    def keyPressEvent(self, event, /):
        if event.key() == Qt.Key.Key_N:

            self.scene.creer_poisson(niveau=self.n)
            self.n = (self.n + 1) % (len(EVOLUTION_POISSON) - 1)
            self.scene.nb += 1
        elif event.key() == Qt.Key.Key_F:
            for poisson in self.scene.poissons:
                poisson.appliquer_direction(-1)
        else:
            super().keyPressEvent(event)


# ===================================================
# Scène graphique de l'aquarium
# ===================================================
class Aquarium(QGraphicsScene):
    """
    Scène graphique représentant l'aquarium.
    """

    def __init__(self, application):
        super().__init__()
        self.est_nuit = False
        self.sparkles = []
        self.animation_fusion_lst = []
        self._original_mouse_release = None
        self._original_mouse_move = None
        self._icone_drop_item = None
        self.proxy_inventaire = None
        self.proxy_market = None
        self.bouton_inventaire = None
        self._drag_poisson_item = None  # pixmap fantôme pendant le drag
        self._drag_poisson_niveau = None
        self.nb = 0
        self.app = application
        self.setSceneRect(QRectF(0, 0, self.app.width(), self.app.height()))
        self.inventaire_poissons = []  # liste de niveaux (int)
        self.poissons = []  # liste des poissons
        self._animations_bulles = []

        # <editor-fold desc="Dessin du fond dégradé">
        gradient = QLinearGradient(0, 0, 0, self.app.width())
        gradient.setColorAt(0, QColorConstants.Cyan)
        gradient.setColorAt(0.5, QColorConstants.DarkCyan)
        gradient.setColorAt(1, QColorConstants.DarkBlue)
        self.setBackgroundBrush(gradient)

        # alterner entre le mode nuit et le mode jour à chaque 30 minutes
        self.timer_jour_nuit = QTimer()
        self.timer_jour_nuit.timeout.connect(self._basculer_jour_nuit)
        self.timer_jour_nuit.start(30 * 60 * 1000)  # 30 minutes en ms
        # </editor-fold>

        # --- Le sol en sable ---
        self.floors = []
        self.update_floor()

        # <editor-fold desc="Bouton pour le market et pour l'inventaire">
        chemin_market = IMG_DIR / "market.png"
        self.chemin_inventaire = IMG_DIR / "sac_a_dos.png"
        self.bouton_market = PixmapCliquable(
            chemin_image=str(chemin_market),
            x=5, y=5,
            scale=50,
            callback=self.market_clicked
        )

        self.update_inventaire_icon()
        self.addItem(self.bouton_market)
        # </editor-fold>

    def _basculer_jour_nuit(self):
        self.est_nuit = not self.est_nuit
        self.update_background()

    def _wheel_event_filtre(self, event):
        pos_scene = self.app.view.mapToScene(event.position().toPoint())

        if self.proxy_market is not None:
            pos_locale = self.proxy_market.mapFromScene(pos_scene)
            if self.proxy_market.boundingRect().contains(pos_locale):
                QGraphicsView.wheelEvent(self.app.view, event)
                return

        if self.proxy_inventaire is not None:
            pos_locale = self.proxy_inventaire.mapFromScene(pos_scene)
            if self.proxy_inventaire.boundingRect().contains(pos_locale):
                QGraphicsView.wheelEvent(self.app.view, event)
                return

    def market_clicked(self):
        if self.proxy_market is not None:
            self.fermer_market()
            return

        market = Market(self, EVOLUTION_POISSON, MOULA)
        market.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        market.setAutoFillBackground(False)

        self.proxy_market = self.addWidget(market)
        self.proxy_market.setZValue(1000)
        self.proxy_market.setPos(0, 0)
        self.update_market()

        self.app.view.wheelEvent = self._wheel_event_filtre

        # Pousser tous les poissons vers la droite
        self._repositionner_poissons(market=True)

    def fermer_market(self):
        if self.proxy_market is not None:
            self.removeItem(self.proxy_market)
            self.proxy_market = None
        self.app.view.wheelEvent = lambda event: None

        # Laisser les poissons revenir partout
        self._repositionner_poissons(market=False)

    def fermer_inventaire(self):
        if self.proxy_inventaire is not None:
            self.removeItem(self.proxy_inventaire)
            self.proxy_inventaire = None
        self.app.view.wheelEvent = lambda event: None

        # Laisser les poissons revenir partout
        self._repositionner_poissons(inventaire=False)

    def mettre_en_inventaire(self, poisson):
        """Retire le poisson de l'eau et le met dans l'inventaire."""
        self.inventaire_poissons.append(poisson.n)
        self.supprimer_poisson(poisson)
        self.refresh_inventaire_ui()

    def sortir_de_inventaire(self, niveau, nb, pos, collision: bool = True):
        """Remet un poisson de l'inventaire dans l'eau."""
        if niveau not in self.inventaire_poissons:
            return
        if nb == -1:
            n = self.inventaire_poissons.count(niveau)
        else:
            n = min(self.inventaire_poissons.count(niveau), nb)

        # Retirer n occurrence du niveau
        for i in range(n):
            self.inventaire_poissons.remove(niveau)  # ← enlève la première occurrence

        for i in range(n):
            self.creer_poisson(pos, niveau)
            if self.poissons:
                dernier = self.poissons[-1]
                dernier.setPos(pos.x() - dernier.pixmap().width() / 2, pos.y() - dernier.pixmap().height() / 2)
                if i == 0:
                    if collision:
                        dernier.verifier_collisions()
                delai = random.randint(500, 2000)
                QTimer.singleShot(delai, lambda: self.lancer_animation_aleatoire(dernier))

        self.refresh_inventaire_ui()

    def refresh_inventaire_ui(self):
        if self.proxy_inventaire is None:
            return

        compteur = {}
        for niveau in self.inventaire_poissons:
            compteur[niveau] = compteur.get(niveau, 0) + 1

        widget_inventaire = self.proxy_inventaire.widget()

        # Mettre à jour les slots existants ET créer les nouveaux
        tous_les_niveaux = set(widget_inventaire.slots.keys()) | set(compteur.keys())
        for niveau in tous_les_niveaux:
            widget_inventaire.mettre_a_jour_slot(niveau, compteur.get(niveau, 0))

    def inventaire_clicked(self):
        if self.proxy_inventaire is not None:
            self.fermer_inventaire()
            return

        inventaire = Inventaire(self, self.inventaire_poissons, EVOLUTION_POISSON)
        inventaire.setFixedSize(LARGEUR_INVENTAIRE, int(self.height()))
        inventaire.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        inventaire.setAutoFillBackground(False)

        self.proxy_inventaire = self.addWidget(inventaire)
        self.proxy_inventaire.setZValue(1000)
        self.proxy_inventaire.setPos(self.width() - LARGEUR_INVENTAIRE, 0)

        self.app.view.wheelEvent = self._wheel_event_filtre

        # Pousser tous les poissons vers la Gauche
        self._repositionner_poissons(inventaire=True)

    def commencer_drag_inventaire(self, niveau, pixmap):
        self._drag_poisson_niveau = niveau
        self._drag_poisson_item = QGraphicsPixmapItem(pixmap)
        self._drag_poisson_item.setOpacity(0.75)
        self._drag_poisson_item.setZValue(3000)
        self._drag_poisson_item.setTransformOriginPoint(
            pixmap.width() / 2, pixmap.height() / 2
        )
        self.addItem(self._drag_poisson_item)

        # ✅ Sauvegarder et remplacer
        self._original_mouse_move = self.app.view.mouseMoveEvent
        self._original_mouse_release = self.app.view.mouseReleaseEvent
        self.app.view.mouseMoveEvent = self._drag_inventaire_move
        self.app.view.mouseReleaseEvent = self._drag_inventaire_release

    def _drag_inventaire_move(self, event):
        if self._drag_poisson_item:
            pos = self.app.view.mapToScene(event.pos())
            self._drag_poisson_item.setPos(
                pos.x() - self._drag_poisson_item.pixmap().width() / 2,
                pos.y() - self._drag_poisson_item.pixmap().height() / 2
            )

    def _drag_inventaire_release(self, event):
        if self._drag_poisson_item is None:
            return

        pos = self.app.view.mapToScene(event.pos())

        # ✅ Restaurer les events souris originaux de QGraphicsView
        self.app.view.mouseMoveEvent = QGraphicsView.mouseMoveEvent.__get__(self.app.view)
        self.app.view.mouseReleaseEvent = QGraphicsView.mouseReleaseEvent.__get__(self.app.view)

        # Supprimer le fantôme
        self.removeItem(self._drag_poisson_item)
        self._drag_poisson_item = None

        niveau = self._drag_poisson_niveau
        self._drag_poisson_niveau = None

        if pos.x() < self.width() - LARGEUR_INVENTAIRE:
            self.sortir_de_inventaire(niveau, self.proxy_inventaire.widget().quantite_sortie, pos)

    def _repositionner_poissons(self, market: bool = False, inventaire: bool = False):
        """Arrête les animations et repositionne les poissons hors de la zone du market."""
        if market or inventaire:
            for poisson in self.poissons:

                # Arrêter l'animation en cours pour que le clamping prenne effet
                if poisson.animation_actuelle:
                    poisson.animation_actuelle.stop()
                    poisson.animation_actuelle = None

                x = poisson.pos().x()
                y = poisson.pos().y()
                larg = poisson.poisson.width()

                if market and x < LARGEUR_MARKET:
                    x = LARGEUR_MARKET + larg // 2
                    poisson.setPos(QPointF(x, y))

                if inventaire and x > self.width() - LARGEUR_INVENTAIRE - larg:
                    x = self.width() - LARGEUR_INVENTAIRE - larg - 25
                    poisson.setPos(QPointF(x, y))

                # Relancer une animation avec les nouvelles limites
                QTimer.singleShot(
                    random.randint(200, 800),
                    lambda p=poisson: self.lancer_animation_aleatoire(p)
                )

    def update_market(self):
        global LARGEUR_MARKET

        if self.proxy_market:
            if int(self.width()) >= 1000:
                LARGEUR_MARKET = 350
            else:
                LARGEUR_MARKET = int(self.width()) // 3
            self.proxy_market.widget().setFixedHeight(int(self.height()))
            self.proxy_market.widget().setFixedWidth(LARGEUR_MARKET)
            self.proxy_market.setPos(0, 0)

    def update_inventaire(self):
        global LARGEUR_INVENTAIRE

        if self.proxy_inventaire is not None:
            self.proxy_inventaire.widget().setFixedHeight(int(self.height()))
            self.proxy_inventaire.widget().setFixedWidth(LARGEUR_INVENTAIRE)
            self.proxy_inventaire.setPos(self.width() - LARGEUR_INVENTAIRE, 0)

    def tout_mettre_en_inventaire(self):
        """Met tous les poissons de l'eau dans l'inventaire."""
        # Copier la liste car on va la modifier pendant l'itération
        poissons_a_ranger = self.poissons.copy()
        for poisson in poissons_a_ranger:
            self.inventaire_poissons.append(poisson.n)
            self.supprimer_poisson(poisson)
        self.refresh_inventaire_ui()

    def tout_sortir_inventaire(self):
        x = self.width() // 2
        y = self.height() // 2
        pos = QPointF(x, y)

        niveaux = list(self.inventaire_poissons)

        for i, n in enumerate(niveaux):
            if len(niveaux) < 50:
                i *= 2

            QTimer.singleShot(
                i * 40,
                lambda niveau=n: self.sortir_de_inventaire(niveau, 1, pos, collision=False)
                if niveau in self.inventaire_poissons else None
            )

    def update_inventaire_icon(self):
        if self.bouton_inventaire is not None:
            self.removeItem(self.bouton_inventaire)

        self.bouton_inventaire = PixmapCliquable(
            chemin_image=str(self.chemin_inventaire),
            x=self.width() - 55, y=5,
            scale=50,
            callback=self.inventaire_clicked
        )
        self.addItem(self.bouton_inventaire)

    def afficher_icone_drop(self, visible: bool):
        if visible:
            if self._icone_drop_item is None:
                self._icone_drop_item = self.addText("＋")
                self._icone_drop_item.setDefaultTextColor(Qt.GlobalColor.white)
                self._icone_drop_item.setZValue(2000)
                font = self._icone_drop_item.font()
                font.setPointSize(36)
                font.setBold(True)
                self._icone_drop_item.setFont(font)
                x = self.width() - LARGEUR_INVENTAIRE + LARGEUR_INVENTAIRE / 2 - 20
                y = self.height() / 2 - 30
                self._icone_drop_item.setPos(x, y)
        else:
            if self._icone_drop_item is not None:
                self.removeItem(self._icone_drop_item)
                self._icone_drop_item = None

    def update_floor(self):
        """Redessine le sol en fonction de la taille actuelle de la scène."""
        for f in self.floors:
            self.removeItem(f)
        self.floors.clear()

        tile_width = 320
        y = self.height() - 160

        count = int(self.width() / tile_width) + 2

        for i in range(count):
            chemin_sol = IMG_DIR / "Sand_ground_melt.png"
            floor = QGraphicsPixmapItem(QPixmap(str(chemin_sol)))
            floor.setScale(1)
            floor.setPos(i * tile_width - tile_width, y)
            floor.setZValue(-10)
            self.addItem(floor)
            self.floors.append(floor)

    def update_background(self):
        """
        Redessine le dégradé du fond.
        soit en mode jour.
        soit en mode nuit.
        """
        if self.est_nuit:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColor(30, 25, 90))
            gradient.setColorAt(0.5, QColor(20, 15, 70))
            gradient.setColorAt(1, QColor(10, 5, 50))
            self.setBackgroundBrush(gradient)
        else:
            gradient = QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, QColorConstants.Cyan)
            gradient.setColorAt(0.5, QColorConstants.DarkCyan)
            gradient.setColorAt(1, QColorConstants.DarkBlue)
            self.setBackgroundBrush(gradient)

            self._appliquer_mode_nuit()

    def _appliquer_mode_nuit(self):
        # Assombrir les poissons
        for poisson in self.poissons:
            # Ne pas écraser le glow des poissons lumineux
            if poisson.n == 24:
                continue

            if self.est_nuit:
                effet = QGraphicsColorizeEffect()
                effet.setColor(QColor(30, 20, 80))  # teinte violette
                effet.setStrength(0.4)  # 0.0 = aucun effet, 1.0 = full
                poisson.setGraphicsEffect(effet)
            else:
                poisson.setGraphicsEffect(None)

        # Assombrir le sable
        for floor in self.floors:
            if self.est_nuit:
                effet = QGraphicsColorizeEffect()
                effet.setColor(QColor(30, 20, 80))
                effet.setStrength(0.5)
                floor.setGraphicsEffect(effet)
            else:
                floor.setGraphicsEffect(None)

    def clipper_poissons_au_resize(self):
        """
        Après un resize, force tous les poissons à rester dans les limites.
        Si un poisson sort de l'écran, il est ramené à l'intérieur.
        """
        for poisson in self.poissons:
            larg = poisson.poisson.width()
            haut = poisson.poisson.height()

            # Récupérer la position actuelle
            x = poisson.pos().x()
            y = poisson.pos().y()

            # Appliquer le clamping
            x, y = clamper_position(x, y, larg, haut, poisson)

            # Repositionner le poisson
            poisson.setPos(QPointF(x, y))

    def creer_poisson(self, pos: QPointF = None, niveau: int = 0):
        """Crée un poisson à une position donnée (ou aléatoire)."""
        if niveau > 55:
            return

        poisson = Poisson(niveau, pos)
        poisson.aquarium = self

        if pos is None:
            x = random.randint(0, int(self.width()))
            y = random.randint(0, int(self.height()))
            x, y = clamper_position(x, y, poisson.poisson.width(), poisson.poisson.height(), poisson)
            poisson.setPos(QPointF(x, y))

        poisson.setZValue(-1)
        self.addItem(poisson)
        self.poissons.append(poisson)
        self._appliquer_mode_nuit()

        delai = random.randint(500, 2000)
        QTimer.singleShot(delai, lambda: self.lancer_animation_aleatoire(poisson))

        return poisson

    def supprimer_poisson(self, poisson):
        """Retire un poisson de la liste et de la scène graphique."""
        if poisson in self.poissons:
            self.poissons.remove(poisson)
        if poisson.scene():
            self.removeItem(poisson)

    def lancer_animation_aleatoire(self, poisson):
        """Choisit aléatoirement une animation pour le poisson."""
        if poisson not in self.poissons or poisson.pris:
            return

        if 24 <= poisson.n <= 33:
            animations = [
                self.animation_nager_horizontal,
                self.animation_nager_diagonal,
            ]
        elif poisson.n == 22 or poisson.n == 23:
            animations = [
                self.animation_nager_horizontal,
                self.animation_nager_diagonal
            ]
        else:
            animations = [
                self.animation_nager_horizontal,
                self.animation_nager_horizontal,
                self.animation_nager_diagonal,
                self.animation_nager_diagonal,
                self.animation_faire_bulles
            ]

        animation_choisie = random.choice(animations)
        animation_choisie(poisson)

    # ──────────────────────────────────────────────
    #  NAGE HORIZONTALE
    # ──────────────────────────────────────────────

    def animation_nager_horizontal(self, poisson):
        """Déplace le poisson horizontalement."""
        distance = random.randint(100, int(self.width() - 100))
        if random.random() < 0.5:
            distance = -distance

        larg = poisson.poisson.width()
        haut = poisson.poisson.height()

        pos_finale_x = poisson.pos().x() + distance
        pos_finale_y = poisson.pos().y()
        pos_finale_x, pos_finale_y = clamper_position(pos_finale_x, pos_finale_y, larg, haut, poisson)

        distance_reelle = pos_finale_x - poisson.pos().x()

        if abs(distance_reelle) < 5:
            QTimer.singleShot(500, lambda: self.lancer_animation_aleatoire(poisson))
            return

        va_a_gauche = distance_reelle < 0

        poisson.setRotation(0)
        poisson.appliquer_direction(va_a_gauche)

        pos_finale = QPointF(pos_finale_x, pos_finale_y)
        duree = int(abs(distance_reelle) * 10 * FACTEUR_LENTEUR)
        duree = max(duree, 1500)

        animation = AnimationPosition(
            poisson, poisson.pos(), pos_finale,
            duration=duree, easing=QEasingCurve.Type.InOutQuad
        )

        animation.anim.finished.connect(
            lambda: QTimer.singleShot(random.randint(500, 4000),
                                      lambda: self.lancer_animation_aleatoire(poisson))
        )

        animation.play()
        poisson.animation_actuelle = animation

    # ──────────────────────────────────────────────
    #  NAGE DIAGONALE
    # ──────────────────────────────────────────────

    def animation_nager_diagonal(self, poisson):
        """Déplace le poisson en diagonale avec une inclinaison réaliste."""
        distance_x = random.randint(100, int(self.width() // 4))
        distance_y = random.randint(-int(self.height() // 2), int(self.height() // 2))

        if random.random() > 0.5:
            distance_x = -distance_x

        larg = poisson.poisson.width()
        haut = poisson.poisson.height()

        pos_finale_x = poisson.pos().x() + distance_x
        pos_finale_y = poisson.pos().y() + distance_y
        pos_finale_x, pos_finale_y = clamper_position(pos_finale_x, pos_finale_y, larg, haut, poisson)

        dx = pos_finale_x - poisson.pos().x()
        dy = pos_finale_y - poisson.pos().y()

        if abs(dx) < 5 and abs(dy) < 5:
            QTimer.singleShot(500, lambda: self.lancer_animation_aleatoire(poisson))
            return

        va_a_gauche = dx < 0

        poisson.appliquer_direction(va_a_gauche)

        angle_rad = math.atan2(dy, abs(dx))
        angle_deg = int(math.degrees(angle_rad))
        angle_deg = max(-35, min(35, angle_deg))

        if va_a_gauche:
            angle_deg = -angle_deg

        duree_rotation = int(500 * FACTEUR_LENTEUR)
        anim_rotation_debut = AnimationRotation(
            poisson, poisson.rotation(), angle_deg,
            duration=duree_rotation, easing=QEasingCurve.Type.InOutQuad
        )
        poisson._anim_rot_debut = anim_rotation_debut

        pos_finale = QPointF(pos_finale_x, pos_finale_y)
        duree_deplacement = int(math.sqrt(dx * dx + dy * dy) * 15 * FACTEUR_LENTEUR)
        duree_deplacement = max(duree_deplacement, 2000)

        animation = AnimationPosition(
            poisson, poisson.pos(), pos_finale,
            duration=duree_deplacement, easing=QEasingCurve.Type.InOutQuad
        )

        anim_rotation_debut.play()
        QTimer.singleShot(duree_rotation, animation.play)

        def fin_deplacement():
            duree_retour = int(600 * FACTEUR_LENTEUR)
            anim_rotation_fin = AnimationRotation(
                poisson, poisson.rotation(), 0,
                duration=duree_retour, easing=QEasingCurve.Type.InOutQuad
            )
            poisson._anim_rot_fin = anim_rotation_fin
            anim_rotation_fin.play()

            QTimer.singleShot(random.randint(1500, 5000),
                              lambda: self.lancer_animation_aleatoire(poisson))

        animation.anim.finished.connect(fin_deplacement)
        poisson.animation_actuelle = animation

    # ──────────────────────────────────────────────
    #  ANIMATION DE BULLES
    # ──────────────────────────────────────────────

    def animation_faire_bulles(self, poisson):
        """Crée une série de bulles depuis la bouche du poisson."""
        nb_bulles = random.randint(2, 6)
        intervalle_bulles = int(600 * FACTEUR_LENTEUR)

        for i in range(nb_bulles):
            QTimer.singleShot(i * intervalle_bulles, lambda p=poisson: self.creer_bulle(p))

        delai_total = nb_bulles * intervalle_bulles + 2000
        QTimer.singleShot(delai_total, lambda: self.lancer_animation_aleatoire(poisson))

    def creer_bulle(self, poisson):
        """Crée une bulle qui sort de la bouche du poisson."""
        if poisson not in self.poissons:
            return

        pos_poisson = poisson.pos()
        largeur_poisson = poisson.poisson.width()

        if poisson.regarde_gauche:
            bouche_x = pos_poisson.x() - largeur_poisson / 6
        else:
            bouche_x = pos_poisson.x() + 2 * largeur_poisson / 3

        if poisson.n == 20:
            centre_y = pos_poisson.y() + 2 * poisson.poisson.height() / 5
        elif poisson.n == 21:
            centre_y = pos_poisson.y() + poisson.poisson.height() / 8
            if poisson.regarde_gauche:
                bouche_x = pos_poisson.x() - largeur_poisson / 4
            else:
                bouche_x = pos_poisson.x() + largeur_poisson / 2
        else:
            centre_y = pos_poisson.y() + poisson.poisson.height() / 4

        pos_bouche = QPointF(bouche_x, centre_y)

        bulle = Bulles()
        bulle.setPos(pos_bouche)
        self.addItem(bulle)

        duree_bulle = int(6000 * FACTEUR_LENTEUR)

        animation = AnimationBulle(
            bulle, pos_bouche, poisson.regarde_gauche,
            duration=duree_bulle
        )

        def nettoyer_bulle():
            if bulle.scene():
                self.removeItem(bulle)
            if animation in self._animations_bulles:
                self._animations_bulles.remove(animation)

        animation.anim.finished.connect(nettoyer_bulle)
        self._animations_bulles.append(animation)
        animation.play()

    # ──────────────────────────────────────────────
    #  FUSION DE POISSONS
    # ──────────────────────────────────────────────

    def fusionner_poissons(self, poisson1, poisson2):
        if poisson1.n != poisson2.n:
            return
        if poisson1.n >= len(EVOLUTION_POISSON) - 1:
            return

        # Bloquer toute re-fusion pendant l'animation
        poisson1.pris = True
        poisson2.pris = True

        if poisson1.animation_actuelle:
            poisson1.animation_actuelle.stop()
        if poisson2.animation_actuelle:
            poisson2.animation_actuelle.stop()

        self.supprimer_poisson(poisson1)

        pos_x = (poisson1.pos().x() + poisson2.pos().x()) / 2
        pos_y = (poisson1.pos().y() + poisson2.pos().y()) / 2
        nouvelle_position = QPointF(pos_x, pos_y)

        animation_poisson_2 = AnimationScale.fusion(poisson2)
        self.animation_fusion_lst.append(animation_poisson_2)

        def apres_fusion():
            # Supprimer après la fin de l'animation
            self.supprimer_poisson(poisson2)

            if animation_poisson_2 in self.animation_fusion_lst:
                self.animation_fusion_lst.remove(animation_poisson_2)

            nouveau_poisson = self.creer_poisson(nouvelle_position, poisson1.n + 1)
            if nouveau_poisson:
                larg = nouveau_poisson.poisson.width()
                haut = nouveau_poisson.poisson.height()
                nouveau_poisson.setPos(QPointF(
                    nouvelle_position.x(),
                    nouvelle_position.y()
                ))

                animation_nouveau = AnimationScale.fusion_after(nouveau_poisson)
                self.animation_fusion_lst.append(animation_nouveau)
                animation_nouveau.anim.finished.connect(
                    lambda: self.animation_fusion_lst.remove(animation_nouveau)
                    if animation_nouveau in self.animation_fusion_lst else None
                )
                animation_nouveau.play()

                self.animation_sparkles(QPointF(
                    nouveau_poisson.pos().x() + larg / 2,
                    nouveau_poisson.pos().y() + haut / 2
                ))

        animation_poisson_2.anim.finished.connect(apres_fusion)
        animation_poisson_2.play()

    def animation_sparkles(self, pos_depart):
        for i in range(50):
            chemin = random.choice([IMG_DIR / "etoile_blanche.png", IMG_DIR / "etoile_bleu.png"])
            pix = Etoile(chemin)
            pix.setPos(pos_depart)  # position de départ
            self.addItem(pix)  # ajouter à la scène

            x_fin = pos_depart.x() + random.uniform(-60, 60)
            y_fin = pos_depart.y() + random.uniform(-60, 60)
            pos_fin = QPointF(x_fin, y_fin)

            animation_sparkles = AnimationPosition(pix, pos_depart, pos_fin, 500, QEasingCurve.Type.OutCubic)
            self.sparkles.append(animation_sparkles)

            # Nettoyer l'étoile et libérer l'animation_sparkles quand c'est fini
            def nettoyer(p=pix, a=animation_sparkles):
                if p.scene():
                    self.removeItem(p)
                if a in self.sparkles:
                    self.sparkles.remove(a)

            animation_sparkles.anim.finished.connect(nettoyer)
            self.sparkles.append(animation_sparkles)  # garder en mémoire
            animation_sparkles.play()


# ===================================================
# Bulle
# ===================================================
class Bulles(QGraphicsPixmapItem):
    """Bulle graphique dans l'aquarium."""

    def __init__(self):
        super().__init__()

        chemin_bulle = IMG_DIR / "fsdfgS" / "Bubble.png"
        bulle = QPixmap(str(chemin_bulle))

        self.setPixmap(bulle)
        self.setTransformOriginPoint(bulle.width() / 2, bulle.height() / 2)
        self.setScale(0.1)


# ===================================================
# Étoile
# ===================================================
class Etoile(QGraphicsPixmapItem):
    """Étoile graphique dans l'aquarium."""

    def __init__(self, chemin):
        super().__init__()

        scale = random.randint(5, 25)

        etoile = QPixmap(str(chemin))

        self.setPixmap(etoile.scaled(
            scale,
            scale,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.setTransformOriginPoint(etoile.width() / 2, etoile.height() / 2)


# ===================================================
# Poisson interactif
# ===================================================
class Poisson(QGraphicsPixmapItem):
    """Poisson interactif dans l'aquarium."""

    def __init__(self, niveau: int = 0, position: QPointF = None):
        super().__init__()

        self.animation_actuelle = None
        self._anim_rot_debut = None
        self._anim_rot_fin = None
        self._anim_scale = None

        self.aquarium = None
        self.n = niveau

        self.pris = False
        self.offset = QPointF(0, 0)

        self.regarde_gauche = False
        self._glow_item = None  # item séparé pour la lumière

        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)

        chemin_poisson = PIXEL_ART_DIR / f"{EVOLUTION_POISSON[self.n]}.png"
        self.poisson = QPixmap(str(chemin_poisson)).scaled(
            100, 100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self._pixmap_droite = self.poisson.copy()
        self._pixmap_gauche = self._pixmap_droite.transformed(QTransform().scale(-1, 1))

        self.setPixmap(self.poisson)

        self.setTransformOriginPoint(self.poisson.width() / 2, self.poisson.height() / 2)

        if self.n in (50, 51):  # poisson_lumiere et poisson_lumiere2
            self._creer_glow()

        if self.n == 24:
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(40)
            glow.setOffset(0, 0)  # centré sur le poisson
            glow.setColor(QColor(180, 0, 255))
            self.setGraphicsEffect(glow)

        if position:
            self.setPos(position)
        else:
            self.setPos(QPointF(250, 200))

    def _creer_glow(self):
        from PySide6.QtWidgets import QGraphicsEllipseItem
        from PySide6.QtGui import QRadialGradient, QBrush

        couleur = QColor(0, 200, 255) if self.n == 50 else QColor(255, 140, 0)

        # Cercle lumineux
        self._glow_item = QGraphicsEllipseItem(-20, -20, 40, 40, self)  # ← enfant du poisson

        # Dégradé radial : brillant au centre, transparent au bord
        gradient = QRadialGradient(0, 0, 20)
        gradient.setColorAt(0.0, QColor(couleur.red(), couleur.green(), couleur.blue(), 220))
        gradient.setColorAt(0.5, QColor(couleur.red(), couleur.green(), couleur.blue(), 80))
        gradient.setColorAt(1.0, QColor(couleur.red(), couleur.green(), couleur.blue(), 0))

        self._glow_item.setBrush(QBrush(gradient))
        self._glow_item.setPen(Qt.PenStyle.NoPen)
        self._glow_item.setZValue(5)

        # Positionner la boule lumineuse sur l'antenne du poisson
        if self.n == 50:
            self._glow_item.setPos(self.poisson.width() * 0.82, self.poisson.height() * 0.32)
        else:
            self._glow_item.setPos(self.poisson.width() * 0.92, self.poisson.height() * 0.25)

        # Ajouter un effet glow sur le cercle seulement
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(30)
        glow.setOffset(0, 0)
        glow.setColor(couleur)
        self._glow_item.setGraphicsEffect(glow)

    def appliquer_direction(self, vers_gauche: bool):
        """Change la direction du poisson via un flip horizontal."""
        if vers_gauche == self.regarde_gauche:
            return

        self.regarde_gauche = vers_gauche

        if vers_gauche:
            self.poisson = self._pixmap_gauche
            if self.n == 50:
                self._glow_item.setPos(self.poisson.width() * 0.18, self.poisson.height() * 0.32)
            if self.n == 51:
                self._glow_item.setPos(self.poisson.width() * 0.08, self.poisson.height() * 0.25)
        else:
            self.poisson = self._pixmap_droite
            if self.n == 50:
                self._glow_item.setPos(self.poisson.width() * 0.82, self.poisson.height() * 0.32)
            if self.n == 51:
                self._glow_item.setPos(self.poisson.width() * 0.92, self.poisson.height() * 0.25)

        self.setPixmap(self.poisson)
        self.setTransformOriginPoint(self.poisson.width() / 2, self.poisson.height() / 2)

    def verifier_collisions(self):
        """Vérifie les collisions avec d'autres poissons pour la fusion."""
        collisions = self.collidingItems()
        for item in collisions:
            if isinstance(item, Poisson) and item != self:
                if self.n == item.n and self.aquarium:
                    self.aquarium.fusionner_poissons(self, item)
                    break

    def mousePressEvent(self, event):
        """Gère le clic sur le poisson (début du drag)."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.pris = True
            self.offset = event.pos()

            if self.animation_actuelle:
                self.animation_actuelle.stop()

            self.setRotation(0)

            self._anim_scale = AnimationScale.grab(self)
            self._anim_scale.play()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Déplace le poisson en suivant la souris."""
        if self.pris:
            new_pos = event.pos() - self.offset + self.pos()
            larg = self.poisson.width()
            haut = self.poisson.height()

            # Si l'inventaire est ouvert, on permet d'aller dans sa zone pour le drop
            if self.aquarium and self.aquarium.proxy_inventaire:
                # Clamping sans limite droite → le poisson peut entrer dans l'inventaire
                x = max(MARGE, int(new_pos.x()))
                y = max(MARGE, min(int(new_pos.y()), self.aquarium.height() - haut))

                # Effet visuel quand on survole l'inventaire
                dans_zone = new_pos.x() + larg > self.aquarium.width() - LARGEUR_INVENTAIRE
                self.aquarium.proxy_inventaire.setOpacity(0.5 if dans_zone else 1.0)
                self.aquarium.afficher_icone_drop(dans_zone)
            else:
                x, y = clamper_position(new_pos.x(), new_pos.y(), larg, haut, self)

            self.setPos(QPointF(x, y))

    def mouseReleaseEvent(self, event):
        """Gère le relâchement du clic (fin du drag)."""
        if event.button() == Qt.MouseButton.LeftButton:

            # Remettre l'inventaire normal
            if self.aquarium and self.aquarium.proxy_inventaire:
                self.aquarium.proxy_inventaire.setOpacity(1.0)
                self.aquarium.afficher_icone_drop(False)

            larg = self.poisson.width()

            # Lâché sur l'inventaire ?
            if (self.aquarium and self.aquarium.proxy_inventaire and
                    self.pos().x() + larg > self.aquarium.width() - LARGEUR_INVENTAIRE):
                self.aquarium.mettre_en_inventaire(self)
                return  # ← le poisson est supprimé, on arrête là

            # Sinon comportement normal — reclamper au cas où
            larg = self.poisson.width()
            haut = self.poisson.height()
            x, y = clamper_position(self.pos().x(), self.pos().y(), larg, haut, self)
            self.setPos(QPointF(x, y))

            self.verifier_collisions()
            self.pris = False

            self._anim_scale = AnimationScale.release(self)
            self._anim_scale.play()

            if self.aquarium:
                QTimer.singleShot(random.randint(500, 2000),
                                  lambda: self.aquarium.lancer_animation_aleatoire(self))

        super().mouseReleaseEvent(event)


class PixmapCliquable(QGraphicsPixmapItem):
    def __init__(self, chemin_image, x, y, scale=100, callback=None):
        super().__init__()
        # Charger l'image
        self.scale = scale
        self.pos = QPointF(x, y)
        self.chemin_image = chemin_image
        self.pixmap = QPixmap(self.chemin_image).scaled(
            self.scale,
            self.scale,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.pixmap)
        self.setPos(self.pos)
        self.setAcceptHoverEvents(True)  # ← IMPORTANT !
        self.callback = callback

    def mousePressEvent(self, event):
        self.pixmap = self.pixmap.scaled(
            int(self.scale * 0.95),
            int(self.scale * 0.95),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPos(self.pos + QPointF(self.scale * 0.025, self.scale * 0.025))
        self.setPixmap(self.pixmap)

        if self.callback:
            self.callback()  # Appeler la fonction au clic

    def mouseReleaseEvent(self, event):
        self.pixmap = QPixmap(self.chemin_image).scaled(
            self.scale,
            self.scale,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPos(self.pos)
        self.setPixmap(self.pixmap)

    def hoverEnterEvent(self, event):
        self.setOpacity(0.7)  # Assombrir au survol

    def hoverLeaveEvent(self, event):
        self.setOpacity(1)   # Remet normal quand on ne survol plus
