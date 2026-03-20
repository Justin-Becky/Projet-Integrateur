import random

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsDropShadowEffect
from PySide6.QtGui import QPixmap, QTransform, QColor
from Animations import AnimationScale
from config import IMG_DIR, PIXEL_ART_DIR, MARGE, LARGEUR_INVENTAIRE, EVOLUTION_POISSON
from outils import clamper_position


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


# ===================================================
# Image cliquable
# ===================================================
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


# ===================================================
# Chum (nourriture)
# ===================================================
class Chum(QGraphicsPixmapItem):
    """Morceau de nourriture qui descend vers le sable."""

    # Zones de profondeur — détermine quels poissons peuvent manger ce chum
    ZONE_SURFACE = "surface"   # mouettes (n==22)
    ZONE_MILIEU = "milieu"    # poissons tropicaux
    ZONE_FOND = "fond"      # crabes (n==23), poissons des profondeurs (n>=24)

    def __init__(self, pos_depart: QPointF, y_sable: float):
        super().__init__()

        self.est_mange = False   # verrou anti-double-collision
        self.zone = None    # assignée à la fin de la descente
        self.y_sable = y_sable
        self.y_depart = pos_depart.y()

        chemin = IMG_DIR / "chum.png"
        pixmap = QPixmap(str(chemin)).scaled(
            24, 24,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(pixmap)
        self.setTransformOriginPoint(pixmap.width() / 2, pixmap.height() / 2)
        self.setZValue(-10)
        self.setPos(pos_depart)

    def zone_depuis_y(self, y: float, hauteur_scene: float) -> str:
        """Détermine la zone du chum selon sa position Y finale."""
        tiers = hauteur_scene / 3
        if y < tiers:
            return self.ZONE_SURFACE
        elif y < 2 * tiers:
            return self.ZONE_MILIEU
        else:
            return self.ZONE_FOND
