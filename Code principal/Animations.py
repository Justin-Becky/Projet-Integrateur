import random
import math
from PySide6.QtCore import QObject, QVariantAnimation, QEasingCurve, QPointF
from PySide6.QtWidgets import QGraphicsPixmapItem

# ===================================================
# Classes d'animation pour l'aquarium
# Chaque classe gère un type d'animation spécifique :
#   - Position (déplacement A → B)
#   - Bulle (montée naturelle avec ondulation fluide)
#   - Rotation (inclinaison angulaire)
#   - Scale (zoom avec rebond réaliste pour grab/release)
# ===================================================


class AnimationPosition(QObject):

    def __init__(self, item: QGraphicsPixmapItem, debut: QPointF, fin: QPointF,
                 duration: int = 2000, easing: QEasingCurve.Type = QEasingCurve.Type.Linear,
                 on_wall=None):
        super().__init__()
        self.item = item
        self.debut = QPointF(debut)
        self.fin = QPointF(fin)
        self.on_wall = on_wall  # callback appelé si la destination est un mur

        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve(easing))
        self.anim.valueChanged.connect(self._on_value)

    def _on_value(self, v):
        x = self.debut.x() + (self.fin.x() - self.debut.x()) * v
        y = self.debut.y() + (self.fin.y() - self.debut.y()) * v
        self.item.setPos(QPointF(x, y))

    def play(self):
        self.anim.start()

    def stop(self):
        self.anim.stop()


class AnimationBulle(QObject):
    """
    Animation naturelle de bulle en montée fluide avec ondulation.

    Le trajet est calculé comme une courbe lisse :
        - La bulle sort de la bouche du poisson
        - Elle monte verticalement vers la surface
        - Elle oscille légèrement horizontalement (comme une vraie bulle)
        - Le scaling augmente graduellement (plus grande en montant)
        - L'opacité diminue légèrement vers la fin (disparition progressive)

    La clé pour la nature : utiliser des courbes easing fluides (InOutQuad)
    et des perturbations aléatoires qui suivent un pattern sinusoïdal.
    """

    # --- Initialise l'animation de bulle ---
    def __init__(self, bulle: QGraphicsPixmapItem,
                 pos_bouche: QPointF, regarde_gauche: bool,
                 duration: int = 6000):
        """
        Paramètres :
            bulle           → l'élément graphique de la bulle
            pos_bouche      → position de la bouche du poisson (coin haut-gauche de son bounding box)
            regarde_gauche  → True si le poisson regarde à gauche
            duration        → durée totale de l'animation
        """
        super().__init__()
        self.bulle = bulle
        self.regarde_gauche = regarde_gauche

        # ── Points clés du trajet ──

        # Point A : bouche du poisson (départ)
        self.pos_a = QPointF(pos_bouche)

        # Point B : position intermédiaire (1/4 du chemin) - pour courber le trajet
        # Petite déviation horizontale au début pour une sortie plus naturelle
        deviation_debut = random.randint(10, 25) * (-1 if regarde_gauche else 1)
        self.pos_b = QPointF(
            pos_bouche.x() + deviation_debut,
            pos_bouche.y() - 100  # Montée rapide initiale
        )

        # Point C : position intermédiaire (3/4 du chemin)
        # La bulle a déjà beaucoup monté, léger drift horizontal final
        deviation_fin = random.randint(-15, 15)
        self.pos_c = QPointF(
            self.pos_b.x() + deviation_fin,
            pos_bouche.y() - 450  # Presque en haut
        )

        # Point D : surface de l'eau (tout en haut, hors écran)
        self.pos_d = QPointF(
            self.pos_c.x() + random.randint(-10, 10),
            -50  # Hors écran en haut
        )

        # ── Amplitude et fréquence de l'ondulation ──
        # L'ondulation crée le mouvement naturel side-to-side
        self.amplitude_ondulation = random.uniform(8, 18)  # Pixels de déviation
        self.frequence_ondulation = random.uniform(0.008, 0.015)  # Cycles par millisecondes

        # ── Animation principale : interpolation fluide 0.0 → 1.0 ──
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(duration)
        # InOutQuad crée une montée fluide qui accélère puis décélère
        self.anim.setEasingCurve(QEasingCurve(QEasingCurve.Type.InOutQuad))
        self.anim.valueChanged.connect(self._on_value)

    # --- Callback appelé à chaque tick de l'animation ---
    def _on_value(self, v):
        """
        Met à jour la position et le scaling de la bulle en fonction
        de la progression v (0.0 → 1.0).

        Calcul du trajet :
            - utilise Bézier quadratique pour interpoler entre 4 points
            - ajoute une perturbation sinusoïdale pour l'ondulation
            - augmente le scale graduellement (grossit en montant)
        """

        # ── Interpolation sur la courbe de Bézier (A → B → C → D) ──
        # Pour une montée fluide, on utilise 2 courbes quadratiques consécutives

        if v < 0.5:
            # Première moitié : A → B → C (accélération initiale)
            t = v * 2  # Normaliser à [0, 1]
            # Bézier quadratique : (1-t)²·P0 + 2(1-t)t·P1 + t²·P2
            p1 = self._interpolation_quadratique(self.pos_a, self.pos_b, self.pos_c, t)
        else:
            # Deuxième moitié : C → D (décélération finale)
            t = (v - 0.5) * 2  # Normaliser à [0, 1]
            p1 = self._interpolation_quadratique(self.pos_c, self.pos_d, self.pos_d, t)

        # ── Perturbation sinusoïdale pour l'ondulation ──
        # Crée un mouvement side-to-side naturel basé sur la hauteur
        angle_onde = v * math.pi * 2 * self.amplitude_ondulation / 100
        deviation_x = math.sin(angle_onde) * self.amplitude_ondulation

        # ── Position finale avec ondulation ──
        pos_finale_x = p1.x() + deviation_x
        pos_finale_y = p1.y()

        self.bulle.setPos(QPointF(pos_finale_x, pos_finale_y))

        # ── Scaling : grossit graduellement (0.1 → 0.8) ──
        # La bulle commence très petite et grandit légèrement à mesure qu'elle monte
        scale = 0.1 + 0.7 * v
        self.bulle.setScale(scale)

    # --- Interpolation Bézier quadratique ──
    @staticmethod
    def _interpolation_quadratique(p0: QPointF, p1: QPointF, p2: QPointF, t: float) -> QPointF:
        """
        Interpole une courbe quadratique de Bézier :
            B(t) = (1-t)² * P0 + 2(1-t)t * P1 + t² * P2

        Crée une courbe fluide passant par P0 et P2, guidée par P1.
        Utilisé pour interpoler le trajet entre 3 points clés.
        """
        mt = 1 - t
        x = mt * mt * p0.x() + 2 * mt * t * p1.x() + t * t * p2.x()
        y = mt * mt * p0.y() + 2 * mt * t * p1.y() + t * t * p2.y()
        return QPointF(x, y)

    # --- Démarre l'animation ---
    def play(self):
        self.anim.start()

    # --- Arrête l'animation ---
    def stop(self):
        self.anim.stop()


class AnimationRotation(QObject):
    """
    Animation de rotation (inclinaison) d'un item graphique.
    Utilisée pour :
        - incliner le poisson quand il nage en diagonale
        - remettre l'inclinaison à 0° après un déplacement
    """

    # --- Initialise l'animation de rotation ---
    def __init__(self, item: QGraphicsPixmapItem, angle_debut: float, angle_fin: float,
                 duration: int = 2000, easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic):
        """
        Paramètres :
            item         → l'élément graphique à faire tourner
            angle_debut  → angle de départ (en degrés)
            angle_fin    → angle d'arrivée (en degrés)
            duration     → durée de l'animation
            easing       → courbe d'accélération
        """
        super().__init__()
        self.item = item
        self.angle_debut = angle_debut
        self.angle_fin = angle_fin

        # Configuration de l'animation via QVariantAnimation (0.0 → 1.0)
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve(easing))
        self.anim.valueChanged.connect(self._on_value)

    # --- Callback appelé à chaque tick de l'animation ---
    def _on_value(self, v):
        """Interpole l'angle entre angle_debut et angle_fin."""
        angle = self.angle_debut + (self.angle_fin - self.angle_debut) * v
        self.item.setRotation(angle)

    # --- Démarre l'animation ---
    def play(self):
        self.anim.start()

    # --- Arrête l'animation ---
    def stop(self):
        self.anim.stop()


class AnimationScale(QObject):
    """
    Animation de mise à l'échelle réaliste avec effet de rebond (squash & stretch).

    Quand le poisson est attrapé (grab) :
        - Phase 1 : grossit légèrement au-delà de la cible (overshoot)
        - Phase 2 : revient à la taille cible avec un léger rebond
        Simule un effet "squish" comme si on pressait le poisson.

    Quand le poisson est relâché (release) :
        - Phase 1 : se comprime légèrement en-dessous de la taille normale
        - Phase 2 : rebondit et revient à la taille normale
        Simule un effet "bounce" comme si le poisson reprenait sa forme.
    """

    # --- Initialise l'animation de scale avec rebond ---
    def __init__(self, item: QGraphicsPixmapItem, scale_debut: float, scale_fin: float,
                 duration: int = 400, easing: QEasingCurve.Type = QEasingCurve.Type.OutBack):
        """
        Paramètres :
            item        → l'élément graphique à redimensionner
            scale_debut → échelle de départ (ex: 1.0)
            scale_fin   → échelle d'arrivée (ex: 1.15 pour grab, 1.0 pour release)
            duration    → durée totale de l'animation
            easing      → courbe d'accélération (OutBack donne un rebond naturel)
        """
        super().__init__()
        self.item = item
        self.scale_debut = scale_debut
        self.scale_fin = scale_fin

        # Configuration de l'animation via QVariantAnimation (0.0 → 1.0)
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve(easing))
        self.anim.valueChanged.connect(self._on_value)

    # --- Callback appelé à chaque tick de l'animation ---
    def _on_value(self, v):
        """Interpole le scale entre scale_debut et scale_fin avec le rebond de l'easing."""
        scale = self.scale_debut + (self.scale_fin - self.scale_debut) * v
        self.item.setScale(scale)

    # --- Démarre l'animation ---
    def play(self):
        self.anim.start()

    # --- Arrête l'animation ---
    def stop(self):
        self.anim.stop()

    # --- Crée une animation de grab (poisson attrapé) ---
    @staticmethod
    def grab(item: QGraphicsPixmapItem, duration: int = 300):
        """
        Crée et retourne une AnimationScale pour l'effet "grab" :
            - le poisson grossit de 1.0 → 1.15
            - courbe OutBack pour un léger overshoot réaliste
            - durée courte (300ms) pour un feedback instantané
        """
        return AnimationScale(
            item,
            scale_debut=item.scale(),
            scale_fin=1.15,
            duration=duration,
            easing=QEasingCurve.Type.OutBack
        )

    # --- Crée une animation de release (poisson relâché) ---
    @staticmethod
    def release(item: QGraphicsPixmapItem, duration: int = 400):
        """
        Crée et retourne une AnimationScale pour l'effet "release" :
            - le poisson revient de sa taille actuelle → 1.0
            - courbe OutBounce pour un rebond élastique
            - durée légèrement plus longue (400ms) pour un effet satisfaisant
        """
        return AnimationScale(
            item,
            scale_debut=item.scale(),
            scale_fin=1.0,
            duration=duration,
            easing=QEasingCurve.Type.OutBounce
        )

    # --- Crée une animation de fusion ---
    @staticmethod
    def fusion(item: QGraphicsPixmapItem, duration: int = 400):

        return AnimationScale(
            item,
            scale_debut=item.scale(),
            scale_fin=0.01,
            duration=duration,
            easing=QEasingCurve.Type.Linear
        )

    # --- Crée une animation de fusion ---
    @staticmethod
    def fusion_after(item: QGraphicsPixmapItem, duration: int = 400):

        return AnimationScale(
            item,
            scale_debut=0.01,
            scale_fin=item.scale(),
            duration=duration,
            easing=QEasingCurve.Type.Linear
        )
