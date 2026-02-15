import random
import math

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QEasingCurve, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QMenuBar, \
    QMenu, QGraphicsRectItem, QWidget
from PySide6.QtGui import QPixmap, QAction, QColorConstants, QLinearGradient, QPainterPath, QBrush, QPen, QFont, \
    QTransform
from Animations import AnimationBulle, AnimationPosition, AnimationRotation, AnimationScale


# ===================================================
# Liste d'évolution des poissons
# Chaque entrée correspond à un sprite dans le dossier
# Images/pixel-art/. L'index dans la liste représente
# le niveau d'évolution du poisson.
# ===================================================

# les poissons spéciaux ou qui ne fonctionne pas avec les bulles
# "mouette",
# "crabe",
# "koi_debout",
# "meduse",
# "puff",
# "doris_rose",
# "poisson_mauve",
# "goldfish_jolie",
# "hippocampe",
# "raie_manta",
# "dauphin",
# "baleine",
# "poisson_lion_fluo",
# "preuves",
# "preuve_complexe"

EVOLUTION_POISSON = [
    "basic_rouge",
    "poisson_jaune",
    "poisson_rayé",
    "green_bass",
    "saumon_bleu",
    "martin",
    "goldfish",
    "goldfish_long",
    "dore",
    "preuve_moyenne",
    "gros_rouge",
    "doris_sans_rayure",
    "doris_jaune",
    "doris_kawaii",
    "doris_oeil_aubernoir",
    "doris_og",
    "doris_bleu",
    "doris_brun",
    "doris_rouge",
    "doris_vert",
    "doris_shaded",
    "doris_skinny",
    "crevette",
    "anguille_cute",
    "poisson_chirurgien",
    "george_bleu",
    "beta_bleu",
    "Gill",
    "poisson_tournesol",
    "sunfish",
    "poisson_lune",
    "poisson_lune_bleu",
    "poisson_globe_bleu",
    "ton",
    "espadon",
    "espadon_croche",
    "poisson_lumiere",
    "poisson_lumiere2",
    "requin_baleine",
    "pokemon",
    "pokemon_licorne",
    "pokemon_magikarp",
]

# --- Constantes de la scène ---
SCENE_W = 800
SCENE_H = 600
MARGE = 0
SOL_Y = 525

# --- Multiplicateur de vitesse des animations ---
# Plus la valeur est grande, plus les animations sont lentes
FACTEUR_LENTEUR = 3.0


# --- Garde une position dans les limites de la scène ---
def clamper_position(x, y, largeur_poisson, hauteur_poisson):
    """
    Empêche un poisson de sortir des limites visibles de l'aquarium.
    Retourne les coordonnées clampées (x, y).
    """
    x = max(MARGE, min(x, SCENE_W - largeur_poisson - MARGE))
    y = max(MARGE, min(y, SOL_Y - hauteur_poisson))
    return x, y


# ===================================================
# Fenêtre principale de l'application Aquarium
# ===================================================
class AquariumApp(QMainWindow):
    """
    Fenêtre principale de l'application.
    Gère :
        - l'interface graphique (vue, menus)
        - la scène de l'aquarium
    """

    # --- Initialise la fenêtre principale ---
    def __init__(self):
        super().__init__()

        # <editor-fold desc="Configuration de la vue graphique">
        self.n = 0
        self.vue = QGraphicsView()
        self.vue.setFixedSize(804, 604)
        self.setCentralWidget(self.vue)
        # </editor-fold>

        # <editor-fold desc="Création de la scène">
        self.jardin = Aquarium(self)
        self.vue.setScene(self.jardin)
        # </editor-fold>

        # <editor-fold desc="Création des menus">
        self.barre_menu = QMenuBar()

        # --- Menu principal ---
        self.menu = QMenu("Menu")
        self.action_ajouter = QAction("Ajouter", parent=self)
        self.menu.addAction(self.action_ajouter)

        self.action_changer = QAction("Changer", parent=self)
        self.menu.addAction(self.action_changer)

        # --- Menu Math Discrète ---
        self.menu_math = QMenu("Math Discète")
        self.action_chapitre_1 = QAction("Chapitre 1", parent=self)
        self.action_chapitre_2 = QAction("Chapitre 2", parent=self)
        self.action_chapitre_3 = QAction("Chapitre 3", parent=self)
        self.action_chapitre_4 = QAction("Chapitre 4", parent=self)
        self.action_chapitre_5 = QAction("Chapitre 5", parent=self)
        self.action_chapitre_6 = QAction("Chapitre 6", parent=self)
        self.menu_math.addActions([self.action_chapitre_1, self.action_chapitre_2, self.action_chapitre_3,
                                   self.action_chapitre_4, self.action_chapitre_5, self.action_chapitre_6])

        # Ajout des menus à la barre
        self.barre_menu.addMenu(self.menu)
        self.barre_menu.addMenu(self.menu_math)
        self.setMenuBar(self.barre_menu)
        # </editor-fold>

    def keyPressEvent(self, event, /):
        if event.key() == Qt.Key.Key_N:
            self.jardin.creer_poisson(niveau=self.n)
            self.n += 1
        else:
            # pour que les autres événements soient gérés normalement
            super().keyPressEvent(event)


# ===================================================
# Scène graphique de l'aquarium
# Gère :
#   - le décor (fond dégradé, sol)
#   - la création et suppression de poissons
#   - les animations automatiques (nage, bulles)
#   - la fusion de poissons de même niveau
# ===================================================
class Aquarium(QGraphicsScene):
    """
    Scène graphique représentant l'aquarium.
    Contient :
        - le fond dégradé (cyan → bleu foncé)
        - les éléments de sol
        - les poissons et leurs animations
        - le bouton pour ajouter des poissons
    """

    # --- Initialise la scène de l'aquarium ---
    def __init__(self, application: AquariumApp):
        super().__init__()
        self.app = application
        self.setSceneRect(QRectF(0, 0, SCENE_W, SCENE_H))
        self.poissons = []
        self._animations_bulles = []

        # <editor-fold desc="Dessin du fond dégradé">
        gradient = QLinearGradient(0, 0, 0, SCENE_H)
        gradient.setColorAt(0, QColorConstants.Cyan)
        gradient.setColorAt(0.5, QColorConstants.DarkCyan)
        gradient.setColorAt(1, QColorConstants.DarkBlue)
        self.setBackgroundBrush(gradient)
        # </editor-fold>

        # <editor-fold desc="Dessin du sol">
        for i in range(int(self.width() / 5) + (self.width() % 5 > 0)):
            floor = QGraphicsPixmapItem(QPixmap("../../Images/img_3.png"))
            floor.setScale(1)
            floor.setPos(QPoint((i - 1) * 320, 500))
            self.addItem(floor)
        # </editor-fold>

        # --- Bouton pour ajouter un poisson ---
        bouton_custom = BoutonArrondi(self.app, 350, 500, 150, 40, "Nouveau Poisson", radius=20)
        self.addItem(bouton_custom)

    # --- Crée un nouveau poisson dans l'aquarium ---
    def creer_poisson(self, pos: QPointF = None, niveau: int = 0):
        """
        Crée un poisson à une position donnée (ou aléatoire) :
            - instancie un objet Poisson avec le niveau spécifié
            - l'ajoute à la scène et à la liste des poissons
            - lance une animation aléatoire après un délai
        Retourne le poisson créé.
        """
        if niveau > 42:
            return

        # Position aléatoire si aucune n'est spécifiée
        if pos is None:
            x = random.randint(50, 700)
            y = random.randint(50, 400)
            pos = QPointF(x, y)

        poisson = Poisson(niveau, pos)
        poisson.aquarium = self
        self.addItem(poisson)
        self.poissons.append(poisson)

        # Lancer une animation après un délai aléatoire
        delai = random.randint(500, 2000)
        QTimer.singleShot(delai, lambda: self.lancer_animation_aleatoire(poisson))

        return poisson

    # --- Supprime un poisson de l'aquarium ---
    def supprimer_poisson(self, poisson):
        """
        Retire un poisson :
            - de la liste interne des poissons
            - de la scène graphique
        """
        if poisson in self.poissons:
            self.poissons.remove(poisson)
        if poisson.scene():
            self.removeItem(poisson)

    # --- Lance une animation aléatoire sur un poisson ---
    def lancer_animation_aleatoire(self, poisson):
        """
        Choisit aléatoirement une animation parmi :
            - nage horizontale
            - nage diagonale
            - bulles

        Ne fait rien si le poisson n'existe plus ou est attrapé par l'utilisateur.
        """

        if poisson not in self.poissons or poisson.pris:
            return

        # Liste des animations possibles (pondérée : plus de nage que de bulles)
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

    # --- Anime un poisson en déplacement horizontal ---
    def animation_nager_horizontal(self, poisson):
        """
        Déplace le poisson horizontalement :
            - choisit une distance aléatoire (gauche ou droite)
            - clampe la position finale dans les limites
            - flip l'image si le poisson va à gauche
            - lance une AnimationPosition avec durée ralentie
            - enchaîne sur une nouvelle animation aléatoire à la fin
        """

        distance = random.randint(100, 400)
        if random.random() < 0.5:
            distance = -distance

        larg = poisson.poisson.width()
        haut = poisson.poisson.height()

        # Calcul de la position finale clampée
        pos_finale_x = poisson.pos().x() + distance
        pos_finale_y = poisson.pos().y()
        pos_finale_x, pos_finale_y = clamper_position(pos_finale_x, pos_finale_y, larg, haut)

        # Distance réelle après clamping
        distance_reelle = pos_finale_x - poisson.pos().x()

        # Si pas assez de place, relancer une autre animation
        if abs(distance_reelle) < 5:
            QTimer.singleShot(500, lambda: self.lancer_animation_aleatoire(poisson))
            return

        va_a_gauche = distance_reelle < 0

        # Remettre l'inclinaison à 0 (le poisson nage droit)
        poisson.setRotation(0)

        # Flip horizontal pour la direction
        poisson.appliquer_direction(va_a_gauche)

        # Calcul de la durée (ralentie par FACTEUR_LENTEUR)
        pos_finale = QPointF(pos_finale_x, pos_finale_y)
        duree = int(abs(distance_reelle) * 10 * FACTEUR_LENTEUR)
        duree = max(duree, 1500)  # Durée minimum de 1.5 secondes

        # Création et lancement de l'animation
        animation = AnimationPosition(
            poisson, poisson.pos(), pos_finale,
            duration=duree, easing=QEasingCurve.Type.InOutQuad
        )

        # Enchaîner sur une nouvelle animation après un délai aléatoire
        animation.anim.finished.connect(
            lambda: QTimer.singleShot(random.randint(500, 4000),
                                      lambda: self.lancer_animation_aleatoire(poisson))
        )

        animation.play()
        poisson.animation_actuelle = animation

    # ──────────────────────────────────────────────
    #  NAGE DIAGONALE — avec inclinaison du poisson
    # ──────────────────────────────────────────────

    # --- Anime un poisson en déplacement diagonal avec rotation ---
    def animation_nager_diagonal(self, poisson):
        """
        Déplace le poisson en diagonale avec une inclinaison réaliste :
            - Phase 1 : incliner le poisson vers l'angle de déplacement (500ms)
            - Phase 2 : déplacement diagonal (l'angle RESTE pendant tout le trajet)
            - Phase 3 : remettre l'inclinaison à 0° en douceur (600ms)

        L'angle est calculé avec atan2 et limité à ±35° pour rester naturel.
        La direction gauche/droite est gérée par flip horizontal du pixmap.
        """

        distance_x = random.randint(100, 300)
        distance_y = random.randint(-150, 150)

        if random.random() > 0.5:
            distance_x = -distance_x

        larg = poisson.poisson.width()
        haut = poisson.poisson.height()

        # Calcul de la position finale clampée
        pos_finale_x = poisson.pos().x() + distance_x
        pos_finale_y = poisson.pos().y() + distance_y
        pos_finale_x, pos_finale_y = clamper_position(pos_finale_x, pos_finale_y, larg, haut)

        # Distances réelles après clamping
        dx = pos_finale_x - poisson.pos().x()
        dy = pos_finale_y - poisson.pos().y()

        # Si pas assez de déplacement, relancer
        if abs(dx) < 5 and abs(dy) < 5:
            QTimer.singleShot(500, lambda: self.lancer_animation_aleatoire(poisson))
            return

        va_a_gauche = dx < 0

        # Flip horizontal pour la direction
        poisson.appliquer_direction(va_a_gauche)

        # ── Calcul de l'angle d'inclinaison ──
        # On utilise abs(dx) car le flip gère déjà la direction horizontale
        angle_rad = math.atan2(dy, abs(dx))
        angle_deg = math.degrees(angle_rad)
        angle_deg = max(-35, min(35, angle_deg))  # Limiter l'inclinaison

        # Si l'image est flippée (gauche), l'angle visuel s'inverse
        if va_a_gauche:
            angle_deg = -angle_deg

        # ── Phase 1 : Incliner le poisson (500ms) ──
        duree_rotation = int(500 * FACTEUR_LENTEUR)
        anim_rotation_debut = AnimationRotation(
            poisson, poisson.rotation(), angle_deg,
            duration=duree_rotation, easing=QEasingCurve.Type.InOutQuad
        )
        poisson._anim_rot_debut = anim_rotation_debut

        # ── Phase 2 : Déplacement diagonal (l'angle ne change PAS) ──
        pos_finale = QPointF(pos_finale_x, pos_finale_y)
        duree_deplacement = int(math.sqrt(dx * dx + dy * dy) * 15 * FACTEUR_LENTEUR)
        duree_deplacement = max(duree_deplacement, 2000)  # Minimum 2 secondes

        animation = AnimationPosition(
            poisson, poisson.pos(), pos_finale,
            duration=duree_deplacement, easing=QEasingCurve.Type.InOutQuad
        )

        # Lancer la rotation d'abord, puis le déplacement une fois l'inclinaison terminée
        anim_rotation_debut.play()
        QTimer.singleShot(duree_rotation, animation.play)

        def fin_deplacement():
            """Phase 3 : Remettre l'angle à 0° en douceur après le déplacement"""

            duree_retour = int(600 * FACTEUR_LENTEUR)
            anim_rotation_fin = AnimationRotation(
                poisson, poisson.rotation(), 0,
                duration=duree_retour, easing=QEasingCurve.Type.InOutQuad
            )
            poisson._anim_rot_fin = anim_rotation_fin
            anim_rotation_fin.play()

            # Enchaîner sur une nouvelle animation après un délai
            QTimer.singleShot(random.randint(1500, 5000),
                              lambda: self.lancer_animation_aleatoire(poisson))

        animation.anim.finished.connect(fin_deplacement)
        poisson.animation_actuelle = animation

    # ──────────────────────────────────────────────
    #  ANIMATION DE BULLES — 3 phases réalistes
    # ──────────────────────────────────────────────

    # --- Lance une série de bulles depuis la bouche du poisson ---
    def animation_faire_bulles(self, poisson):
        """
        Crée entre 2 et 6 bulles espacées dans le temps :
            - chaque bulle sort de la bouche du poisson
            - suit un trajet en 3 phases (horizontal → diagonal → vertical)
            - après toutes les bulles, relance une animation aléatoire
        """

        nb_bulles = random.randint(2, 6)
        intervalle_bulles = int(600 * FACTEUR_LENTEUR)

        for i in range(nb_bulles):
            QTimer.singleShot(i * intervalle_bulles, lambda p=poisson: self.creer_bulle(p))

        # Relancer une animation après que toutes les bulles soient créées
        delai_total = nb_bulles * intervalle_bulles + 2000
        QTimer.singleShot(delai_total, lambda: self.lancer_animation_aleatoire(poisson))

    # --- Crée une bulle qui sort de la bouche du poisson ---
    def creer_bulle(self, poisson):
        """
        Instancie une bulle à la bouche du poisson :
            - calcule la position EXACTE de la bouche
            - crée la bulle ET la positionne tout de suite
            - lance une AnimationBulle en montée fluide avec ondulation

        CLÉE : setPos() doit être appelé AVANT de créer l'animation.
        """

        # Vérification : le poisson existe encore
        if poisson not in self.poissons:
            return

        # ── Calcul EXACT de la position de la bouche ──
        # La bouche est au CENTRE vertical du poisson,
        # à l'avant du poisson (gauche ou droite selon sa direction)

        pos_poisson = poisson.pos()  # Position du poisson (coin haut-gauche de son bounding box)
        largeur_poisson = poisson.poisson.width()
        hauteur_poisson = poisson.poisson.height()

        # Centre vertical du poisson
        centre_y = pos_poisson.y() + poisson.poisson.height() / 4

        # Avant du poisson selon sa direction
        if poisson.regarde_gauche:
            # Poisson regarde à gauche : la bouche est à gauche (x = pos_x)
            bouche_x = pos_poisson.x()
        else:
            # Poisson regarde à droite : la bouche est à droite (x = pos_x + largeur)
            bouche_x = pos_poisson.x() + 2 * largeur_poisson / 3

        pos_bouche = QPointF(bouche_x, centre_y)

        # ── Créer la bulle ──
        bulle = Bulles()
        # ⭐ TRÈS IMPORTANT : positionner la bulle à la bouche du poisson IMMÉDIATEMENT
        bulle.setPos(pos_bouche)
        self.addItem(bulle)

        # ── Durée totale ralentie ──
        duree_bulle = int(6000 * FACTEUR_LENTEUR)

        # ── Création de l'animation ──
        # Passer la position de la bouche à l'animation
        animation = AnimationBulle(
            bulle, pos_bouche, poisson.regarde_gauche,
            duration=duree_bulle
        )

        def nettoyer_bulle():
            """Supprime la bulle de la scène et libère la référence de l'animation"""
            if bulle.scene():
                self.removeItem(bulle)
            if animation in self._animations_bulles:
                self._animations_bulles.remove(animation)

        # La fin de l'animation déclenche le nettoyage
        animation.anim.finished.connect(nettoyer_bulle)

        # ⭐ GARDER LA RÉFÉRENCE — sinon Python détruit l'animation immédiatement
        self._animations_bulles.append(animation)
        animation.play()

    # ──────────────────────────────────────────────
    #  FUSION DE POISSONS
    # ──────────────────────────────────────────────

    # --- Fusionne deux poissons de même niveau en un poisson évolué ---
    def fusionner_poissons(self, poisson1, poisson2):
        """
        Fusionne deux poissons si :
            - ils sont au même niveau d'évolution
            - le niveau n'est pas le maximum

        Résultat :
            - les deux poissons sont supprimés
            - un nouveau poisson de niveau + 1 apparaît entre les deux
        """

        # Vérifications
        if poisson1.n != poisson2.n:
            return
        if poisson1.n >= len(EVOLUTION_POISSON) - 1:
            return

        # Position moyenne entre les deux poissons
        pos_x = (poisson1.pos().x() + poisson2.pos().x()) / 2
        pos_y = (poisson1.pos().y() + poisson2.pos().y()) / 2
        nouvelle_position = QPointF(pos_x, pos_y)

        # Suppression des deux poissons originaux
        self.supprimer_poisson(poisson1)
        self.supprimer_poisson(poisson2)

        # Création du poisson évolué
        nouveau_poisson = self.creer_poisson(nouvelle_position, poisson1.n + 1)
        return nouveau_poisson


# ===================================================
# Représente une bulle dans l'aquarium
# La bulle est un simple pixmap sans position prédéfinie;
# la position et le trajet sont gérés par AnimationBulle.
# ===================================================
class Bulles(QGraphicsPixmapItem):
    """
    Bulle graphique dans l'aquarium.
    Contient uniquement le pixmap de la bulle (50x50).
    Le positionnement et le trajet sont gérés par AnimationBulle.
    """

    # --- Initialise le pixmap de la bulle ---
    def __init__(self):
        super().__init__()

        # Chargement de l'image de la bulle
        bulle = QPixmap("../../Images/fsdfgS/Bubble.png").scaled(
            50, 50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(bulle)
        self.setTransformOriginPoint(bulle.width() / 2, bulle.height() / 2)
        self.setScale(0.1)  # Commence très petite (l'animation la fera grossir)


# ===================================================
# Représente un poisson dans l'aquarium
# Gère :
#   - l'affichage du sprite (avec flip horizontal)
#   - les interactions souris (drag & drop)
#   - l'effet de scale au grab/release
#   - la détection de collision pour la fusion
# ===================================================
class Poisson(QGraphicsPixmapItem):
    """
    Poisson interactif dans l'aquarium.
    Chaque poisson possède :
        - un niveau d'évolution (détermine le sprite)
        - deux pixmaps pré-calculés (droite et gauche) pour éviter la dégradation
        - un état "pris" pour le drag & drop
        - un effet de scale réaliste quand on l'attrape/relâche
        - une référence à l'animation en cours
    """

    # --- Initialise un poisson avec son niveau et sa position ---
    def __init__(self, niveau: int = 0, position: QPointF = None):
        """
        Paramètres :
            niveau   → niveau d'évolution (index dans EVOLUTION_POISSON)
            position → position initiale (QPointF), aléatoire si None
        """
        super().__init__()

        # Référence aux animations en cours (pour éviter le garbage collector)
        self.animation_actuelle = None
        self._anim_rot_debut = None
        self._anim_rot_fin = None
        self._anim_scale = None  # Animation de scale au grab/release

        # Références
        self.aquarium = None
        self.n = niveau

        # État du drag & drop
        self.pris = False
        self.offset = QPointF(0, 0)

        # Direction actuelle du poisson
        self.regarde_gauche = False

        # Rendre l'item déplaçable à la souris
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)

        # Chargement du sprite selon le niveau
        self.poisson = QPixmap(f"../../Images/pixel-art/{EVOLUTION_POISSON[self.n]}.png").scaled(
            50, 50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # Pré-calcul des deux versions (droite et gauche)
        # Évite la dégradation d'image à chaque flip répété
        self._pixmap_droite = self.poisson.copy()
        self._pixmap_gauche = self._pixmap_droite.transformed(QTransform().scale(-1, 1))

        self.setPixmap(self.poisson)
        self.setTransformOriginPoint(self.poisson.width() / 2, self.poisson.height() / 2)

        # Position initiale
        if position:
            self.setPos(position)
        else:
            self.setPos(QPointF(250, 200))

    # --- Applique la direction (flip horizontal) sans rotation ---
    def appliquer_direction(self, vers_gauche: bool):
        """
        Change la direction du poisson via un flip horizontal du pixmap.
        Utilise des pixmaps pré-calculés pour éviter la dégradation d'image.

        Note : on ne fait PAS de setRotation(180) car ça mettrait
        le poisson à l'envers. Le flip horizontal est la bonne approche.
        """

        # Ne rien faire si déjà dans la bonne direction
        if vers_gauche == self.regarde_gauche:
            return

        self.regarde_gauche = vers_gauche

        # Utiliser le pixmap pré-calculé correspondant
        if vers_gauche:
            self.poisson = self._pixmap_gauche
        else:
            self.poisson = self._pixmap_droite

        self.setPixmap(self.poisson)
        self.setTransformOriginPoint(self.poisson.width() / 2, self.poisson.height() / 2)

    # --- Vérifie les collisions avec d'autres poissons pour la fusion ---
    def verifier_collisions(self):
        """
        Parcourt les items en collision :
            - si un autre Poisson de même niveau est trouvé
            - déclenche la fusion via l'aquarium
        """
        collisions = self.collidingItems()
        for item in collisions:
            if isinstance(item, Poisson) and item != self:
                if self.n == item.n and self.aquarium:
                    self.aquarium.fusionner_poissons(self, item)
                    break

    # --- Gère le clic gauche sur le poisson (début du drag) ---
    def mousePressEvent(self, event):
        """
        Au clic gauche :
            - active le mode "pris" (drag)
            - mémorise l'offset de la souris par rapport au poisson
            - arrête l'animation en cours
            - remet l'inclinaison à 0°
            - lance l'effet de scale "grab" (grossit avec overshoot)
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.pris = True
            self.offset = event.pos()

            # Arrêter l'animation automatique
            if self.animation_actuelle:
                self.animation_actuelle.stop()

            # Remettre l'angle à 0 (annuler toute inclinaison)
            self.setRotation(0)

            # Effet de scale "grab" : le poisson grossit légèrement (1.0 → 1.15)
            # avec un overshoot réaliste grâce à la courbe OutBack
            self._anim_scale = AnimationScale.grab(self)
            self._anim_scale.play()

        super().mousePressEvent(event)

    # --- Gère le déplacement de la souris pendant le drag ---
    def mouseMoveEvent(self, event):
        """
        Déplace le poisson en suivant la souris.
        La position est clampée pour empêcher le poisson de sortir de l'aquarium.
        """
        if self.pris:
            new_pos = event.pos() - self.offset + self.pos()
            larg = self.poisson.width()
            haut = self.poisson.height()
            x, y = clamper_position(new_pos.x(), new_pos.y(), larg, haut)
            self.setPos(QPointF(x, y))

    # --- Gère le relâchement du clic (fin du drag) ---
    def mouseReleaseEvent(self, event):
        """
        Au relâchement du clic gauche :
            - vérifie les collisions pour la fusion
            - désactive le mode "pris"
            - lance l'effet de scale "release" (rebond élastique vers 1.0)
            - relance une animation aléatoire après un délai
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.verifier_collisions()
            self.pris = False

            # Effet de scale "release" : le poisson rebondit vers sa taille normale
            # avec un effet élastique grâce à la courbe OutBounce
            self._anim_scale = AnimationScale.release(self)
            self._anim_scale.play()

            # Relancer une animation automatique après un délai
            if self.aquarium:
                QTimer.singleShot(random.randint(500, 2000),
                                  lambda: self.aquarium.lancer_animation_aleatoire(self))

        super().mouseReleaseEvent(event)


# ===================================================
# Bouton arrondi dessiné dans la scène graphique
# ===================================================
class BoutonArrondi(QGraphicsRectItem):
    """
    Bouton personnalisé avec coins arrondis, dessiné directement
    dans la QGraphicsScene (pas un QWidget standard).
    Gère :
        - le dessin avec QPainterPath (coins arrondis)
        - l'effet hover (changement de couleur)
        - le clic (ajout d'un poisson)
    """

    # --- Initialise le bouton arrondi ---
    def __init__(self, application: AquariumApp, x, y, width, height, texte: str, radius=15):
        super().__init__(0, 0, width, height)
        self.app = application
        self.setPos(x, y)
        self.radius = radius
        self.texte = texte

        # Rendre le bouton cliquable et réactif au hover
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.hovered = False

    # --- Dessine le bouton avec coins arrondis ---
    def paint(self, painter, option, widget: QWidget = None):
        """
        Dessin personnalisé :
            - fond cyan (plus foncé au hover)
            - bordure bleu foncé
            - texte centré en noir gras
        """
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)

        # Couleur de fond selon l'état hover
        if self.hovered:
            painter.fillPath(path, QBrush(QColorConstants.Cyan.darker(120)))
        else:
            painter.fillPath(path, QBrush(QColorConstants.Cyan))

        # Bordure
        painter.setPen(QPen(QColorConstants.DarkBlue, 2))
        painter.drawPath(path)

        # Texte centré
        painter.setPen(QColorConstants.Black)
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.texte)

    # --- Effet hover : entrée de la souris ---
    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()
        super().hoverEnterEvent(event)

    # --- Effet hover : sortie de la souris ---
    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    # --- Gère le clic sur le bouton ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked()
        super().mousePressEvent(event)

    # --- Action déclenchée au clic : crée un nouveau poisson ---
    def clicked(self):
        self.app.jardin.creer_poisson()


# ===================================================
# Point d'entrée de l'application
# ===================================================
app = QApplication()
a = AquariumApp()
a.show()
app.exec()