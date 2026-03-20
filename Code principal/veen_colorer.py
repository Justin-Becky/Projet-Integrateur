"""
Diagramme de Venn à 3 ensembles — Architecture bitmask.

Chaque zone est un bit :
    A=64  B=32  C=16  AB=8  AC=4  BC=2  ABC=1

Toutes les 127 combinaisons possibles sont couvertes automatiquement.
Clic gauche : colorier une zone. Clic droit : effacer.
Bouton "Calculer" : affiche la notation simplifiée + stocke toutes les équivalences.
"""

import sys
from itertools import product as cartesian_product

from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QPainterPath, QColor, QPen, QBrush,
    QFont, QMouseEvent
)
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)


# ──────────────────────────────────────────────────────────────────────────────
# Bitmasks — chaque zone est un bit unique
# ──────────────────────────────────────────────────────────────────────────────
BIT = {
    "A": 64,
    "B": 32,
    "C": 16,
    "AB": 8,
    "AC": 4,
    "BC": 2,
    "ABC": 1,
}

# Masques pour les ensembles complets
A_FULL = BIT["A"] | BIT["AB"] | BIT["AC"] | BIT["ABC"]  # 77
B_FULL = BIT["B"] | BIT["AB"] | BIT["BC"] | BIT["ABC"]  # 43
C_FULL = BIT["C"] | BIT["AC"] | BIT["BC"] | BIT["ABC"]  # 23

# Masques dérivés utiles
A_SANS_B = BIT["A"] | BIT["AC"]  # A∩B'
A_SANS_C = BIT["A"] | BIT["AB"]  # A∩C'
A_INTER_BUNIONC = BIT["AB"] | BIT["AC"] | BIT["ABC"]  # A∩(B∪C)
A_SANS_ABC_msk = BIT["A"] | BIT["AB"] | BIT["AC"]  # A sans le centre
A_SANS_AB_msk = BIT["A"] | BIT["AC"] | BIT["ABC"]  # A sans la zone AB
A_SANS_AC_msk = BIT["A"] | BIT["AB"] | BIT["ABC"]  # A sans la zone AC

B_SANS_A = BIT["B"] | BIT["BC"]
B_SANS_C = BIT["B"] | BIT["AB"]
B_INTER_AUNIONC = BIT["AB"] | BIT["BC"] | BIT["ABC"]
B_SANS_ABC_msk = BIT["B"] | BIT["AB"] | BIT["BC"]
B_SANS_AB_msk = BIT["B"] | BIT["BC"] | BIT["ABC"]
B_SANS_BC_msk = BIT["B"] | BIT["AB"] | BIT["ABC"]

C_SANS_A = BIT["C"] | BIT["BC"]
C_SANS_B = BIT["C"] | BIT["AC"]
C_INTER_AUNIONB = BIT["AC"] | BIT["BC"] | BIT["ABC"]
C_SANS_ABC_msk = BIT["C"] | BIT["AC"] | BIT["BC"]
C_SANS_AC_msk = BIT["C"] | BIT["BC"] | BIT["ABC"]
C_SANS_BC_msk = BIT["C"] | BIT["AC"] | BIT["ABC"]

A_B_C_SANS_ABC = BIT["A"] | BIT["B"] | BIT["C"] | BIT["AB"] | BIT["AC"] | BIT["BC"]
A_B_C_ET_ABC = BIT["A"] | BIT["B"] | BIT["C"] | BIT["ABC"]

FULL = BIT["A"] | BIT["AB"] | BIT["AC"] | BIT["ABC"] | BIT["BC"] | BIT["B"] | BIT["C"]
FULL_SANS_AB = BIT["A"] | BIT["AC"] | BIT["ABC"] | BIT["BC"] | BIT["B"] | BIT["C"]
FULL_SANS_AC = BIT["A"] | BIT["AB"] | BIT["ABC"] | BIT["BC"] | BIT["B"] | BIT["C"]
FULL_SANS_BC = BIT["A"] | BIT["AB"] | BIT["AC"] | BIT["ABC"] | BIT["B"] | BIT["C"]
FULL_SANS_AB_AC = BIT["A"] | BIT["ABC"] | BIT["BC"] | BIT["B"] | BIT["C"]
FULL_SANS_AB_BC = BIT["A"] | BIT["AC"] | BIT["ABC"] | BIT["B"] | BIT["C"]
FULL_SANS_AC_BC = BIT["A"] | BIT["AB"] | BIT["ABC"] | BIT["B"] | BIT["C"]

# ──────────────────────────────────────────────────────────────────────────────
# Tables de notation
# ──────────────────────────────────────────────────────────────────────────────

# Notation atomique par zone : bit → (forme simple, forme étendue)
ZONE_NOTATION: dict[int, tuple[str, str]] = {
    BIT["A"]: ("A∩B'∩C'", "A/(B∪C)"),
    BIT["B"]: ("A'∩B∩C'", "B/(A∪C)"),
    BIT["C"]: ("A'∩B'∩C", "C/(A∪B)"),
    BIT["AB"]: ("A∩B∩C'", "(A∩B)/C"),
    BIT["AC"]: ("A∩B'∩C", "(A∩C)/B"),
    BIT["BC"]: ("A'∩B∩C", "(B∩C)/A"),
    BIT["ABC"]: ("A∩B∩C", "A∩B∩C"),
}

# Notation pour les formes composées : masque → [notation simple, notation étendue, ...]
COMPOSED_NOTATION: dict[int, list[str]] = {
    A_FULL: ["A", "(A∩B')∪(A∩B)"],
    B_FULL: ["B", "(A'∩B)∪(A∩B)"],
    C_FULL: ["C", "(A'∩C)∪(A∩C)"],
    A_SANS_B: ["A∩B'", "(A∩B'∩C') ∪ (A∩B'∩C)"],
    A_SANS_C: ["A∩C'", "(A∩B'∩C') ∪ (A∩B∩C')"],
    B_SANS_A: ["B∩A'", "(A'∩B∩C') ∪ (A'∩B∩C)"],
    B_SANS_C: ["B∩C'", "(A'∩B∩C') ∪ (A∩B∩C')"],
    C_SANS_A: ["C∩A'", "(A'∩B'∩C) ∪ (A'∩B∩C)"],
    C_SANS_B: ["C∩B'", "(A'∩B'∩C) ∪ (A∩B'∩C)"],
    A_INTER_BUNIONC: ["A∩(B∪C)", "(A∩B) ∪ (A∩C)"],
    B_INTER_AUNIONC: ["B∩(A∪C)", "(A∩B) ∪ (B∩C)"],
    C_INTER_AUNIONB: ["C∩(A∪B)", "(A∩C) ∪ (B∩C)"],
    A_SANS_ABC_msk: ["A∩(B∩C)'", "(A∩B') ∪ (A∩C')"],
    B_SANS_ABC_msk: ["B∩(A∩C)'", "(B∩A') ∪ (B∩C')"],
    C_SANS_ABC_msk: ["C∩(A∩B)'", "(C∩A') ∪ (C∩B')"],
    A_SANS_AB_msk: ["A∩(A∩B)'", "(A∩B'∩C') ∪ (A∩B'∩C) ∪ (A∩B∩C)"],
    A_SANS_AC_msk: ["A∩(A∩C)'", "(A∩B'∩C') ∪ (A∩B∩C') ∪ (A∩B∩C)"],
    B_SANS_AB_msk: ["B∩(A∩B)'", "(A'∩B∩C') ∪ (A'∩B∩C) ∪ (A∩B∩C)"],
    B_SANS_BC_msk: ["B∩(B∩C)'", "(A'∩B∩C') ∪ (A∩B∩C') ∪ (A∩B∩C)"],
    C_SANS_AC_msk: ["C∩(A∩C)'", "(A'∩B'∩C) ∪ (A'∩B∩C) ∪ (A∩B∩C)"],
    C_SANS_BC_msk: ["C∩(B∩C)'", "(A'∩B'∩C) ∪ (A∩B'∩C) ∪ (A∩B∩C)"],
    A_B_C_SANS_ABC: ["(A∪B∪C)∩(A∩B∩C)'", "(A∪B∪C)/(A∩B∩C)"],
    A_B_C_ET_ABC: ["(A∩B'∩C') ∪ (A'∩B∩C') ∪ (A'∩B'∩C) ∪ (A∩B∩C)"],
    FULL: ["A∪B∪C"],
    FULL_SANS_AB: ["(A∪B∪C)/(A∩B)"],
    FULL_SANS_AC: ["(A∪B∪C)/(A∩C)"],
    FULL_SANS_BC: ["(A∪B∪C)/(B∩C)"],
    FULL_SANS_AB_AC: ["(A∪B∪C)/((A∩B)∩(A∩C))"],
    FULL_SANS_AB_BC: ["(A∪B∪C)/((A∩B)∩(B∩C))"],
    FULL_SANS_AC_BC: ["(A∪B∪C)/((A∩C)∩(B∩C))"],
}

# Ordre de priorité des simplifications : du plus grand masque au plus petit
SIMPLIFICATION_PRIORITY: list[int] = [
    FULL,
    FULL_SANS_AB, FULL_SANS_AC, FULL_SANS_BC,
    FULL_SANS_AB_AC, FULL_SANS_AB_BC, FULL_SANS_AC_BC,
    A_FULL, B_FULL, C_FULL,
    A_B_C_SANS_ABC, A_B_C_ET_ABC,
    A_SANS_B, A_SANS_C, A_SANS_ABC_msk, A_SANS_AB_msk, A_SANS_AC_msk,
    B_SANS_A, B_SANS_C, B_SANS_ABC_msk, B_SANS_AB_msk, B_SANS_BC_msk,
    C_SANS_A, C_SANS_B, C_SANS_ABC_msk, C_SANS_AC_msk, C_SANS_BC_msk,
    A_INTER_BUNIONC, B_INTER_AUNIONC, C_INTER_AUNIONB,
]


# ──────────────────────────────────────────────────────────────────────────────
# Moteur de simplification
# ──────────────────────────────────────────────────────────────────────────────

def _simplifier(mask: int) -> list[int]:
    """
    Décompose un masque en une liste de blocs simplifiés.
    Chaque bloc est soit un masque composé (dans COMPOSED_NOTATION),
    soit un bit atomique (dans ZONE_NOTATION).
    """
    blocs: list[int] = []
    remaining = mask

    for pattern in SIMPLIFICATION_PRIORITY:
        if remaining == 0:
            break
        if (remaining & pattern) == pattern:
            blocs.append(pattern)
            remaining &= ~pattern

    # Bits restants non couverts par une simplification
    for bit in [BIT["A"], BIT["B"], BIT["C"],
                BIT["AB"], BIT["AC"], BIT["BC"], BIT["ABC"]]:
        if remaining & bit:
            blocs.append(bit)

    return blocs


def _notations_pour_bloc(bloc: int) -> list[str]:
    """Retourne toutes les notations équivalentes pour un bloc."""
    if bloc in COMPOSED_NOTATION:
        return [n for n in COMPOSED_NOTATION[bloc] if n]
    if bloc in ZONE_NOTATION:
        simple, expanded = ZONE_NOTATION[bloc]
        return [simple] if simple == expanded else [simple, expanded]
    return [f"?({bloc})"]


def generer_notations(mask: int) -> list[str]:
    """
    Génère toutes les notations équivalentes pour un masque.
    Index 0 = forme la plus simple.
    """
    if mask == 0:
        return ["Aucune zone coloriée"]

    blocs = _simplifier(mask)
    listes_par_bloc = [_notations_pour_bloc(b) for b in blocs]

    toutes = []
    for combo in cartesian_product(*listes_par_bloc):
        toutes.append(" ∪ ".join(combo))

    return toutes


# Précalcul de toutes les 127 combinaisons au démarrage
TOUTES_NOTATIONS: dict[int, list[str]] = {
    mask: generer_notations(mask) for mask in range(1, 128)
}


# ──────────────────────────────────────────────────────────────────────────────
# Couleurs disponibles
# ──────────────────────────────────────────────────────────────────────────────
COULEURS = [
    QColor(255, 100, 100, 160),  # rouge
    QColor(100, 180, 255, 160),  # bleu
    QColor(100, 220, 100, 160),  # vert
    QColor(255, 200,  50, 160),  # jaune
    QColor(200, 100, 255, 160),  # violet
    QColor(255, 150,  50, 160),  # orange
    QColor(50, 220, 200, 160),  # turquoise
]

def creer_chemin_ellipse(rect: QRectF) -> QPainterPath:
    p = QPainterPath()
    p.addEllipse(rect)
    return p


# ──────────────────────────────────────────────────────────────────────────────
# Widget Venn
# ──────────────────────────────────────────────────────────────────────────────
class VennWidget(QWidget):
    """
    Widget principal du diagramme de Venn.
    Utilise des bitmasks pour représenter et simplifier les zones actives.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 500)

        self.index_couleur_active = 0
        self.lst_solutions: list[str] = []

        self.couleurs_zones: dict[str, QColor | None] = {z: None for z in BIT}
        self.chemins: dict[str, QPainterPath] = {}
        self._texte_resultat: str | None = None

        self._calculer_chemins()

    # ── Géométrie ─────────────────────────────────────────────────────────────
    def _rects_ellipses(self):
        w, h = self.width(), self.height()
        rx, ry = w * 0.30, h * 0.28
        cx, cy = w / 2, h / 2
        dx, dy = rx * 0.55, ry * 0.45

        def rect(c: QPointF) -> QRectF:
            return QRectF(c.x() - rx, c.y() - ry, 2 * rx, 2 * ry)

        return (
            rect(QPointF(cx - dx, cy - dy)),
            rect(QPointF(cx + dx, cy - dy)),
            rect(QPointF(cx,      cy + dy)),
        )

    def _calculer_chemins(self):
        ra, rb, rc = self._rects_ellipses()
        pa = creer_chemin_ellipse(ra)
        pb = creer_chemin_ellipse(rb)
        pc = creer_chemin_ellipse(rc)

        self.chemins = {
            "A": pa.subtracted(pb).subtracted(pc),
            "B": pb.subtracted(pa).subtracted(pc),
            "C": pc.subtracted(pa).subtracted(pb),
            "AB": pa.intersected(pb).subtracted(pc),
            "AC": pa.intersected(pc).subtracted(pb),
            "BC": pb.intersected(pc).subtracted(pa),
            "ABC": pa.intersected(pb).intersected(pc),
        }
        self._chemin_A_complet = pa
        self._chemin_B_complet = pb
        self._chemin_C_complet = pc

    # ── Bitmask ───────────────────────────────────────────────────────────────
    def _masque_actif(self) -> int:
        mask = 0
        for nom, couleur in self.couleurs_zones.items():
            if couleur is not None:
                mask |= BIT[nom]
        return mask

    # ── Événements Qt ─────────────────────────────────────────────────────────
    def resizeEvent(self, event):
        self._calculer_chemins()
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        pt = QPointF(event.position())
        for nom, chemin in self.chemins.items():
            if chemin.contains(pt):
                if event.button() == Qt.MouseButton.RightButton:
                    self.couleurs_zones[nom] = None
                else:
                    self.couleurs_zones[nom] = COULEURS[self.index_couleur_active]
                if self._texte_resultat is not None:
                    self._mettre_a_jour_notation()
                self.update()
                return

    # ── Logique de notation ───────────────────────────────────────────────────
    def _mettre_a_jour_notation(self):
        mask = self._masque_actif()
        if mask == 0:
            self._texte_resultat = "Aucune zone coloriée"
            self.lst_solutions = []
            return
        self.lst_solutions = TOUTES_NOTATIONS[mask]
        self._texte_resultat = self.lst_solutions[0]

    def calculer(self):
        """Déclenché par le bouton Calculer."""
        self._mettre_a_jour_notation()
        self.update()

    def tout_effacer(self):
        for k in self.couleurs_zones:
            self.couleurs_zones[k] = None
        self._texte_resultat = None
        self.lst_solutions = []
        self.update()

    def set_couleur_active(self, index: int):
        self.index_couleur_active = index % len(COULEURS)

    # ── Dessin ────────────────────────────────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        for nom, chemin in self.chemins.items():
            couleur = self.couleurs_zones[nom]
            if couleur:
                painter.fillPath(chemin, QBrush(couleur))

        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for ch in (self._chemin_A_complet, self._chemin_B_complet, self._chemin_C_complet):
            painter.drawPath(ch)

        ra, rb, rc = self._rects_ellipses()
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(QColor(30, 30, 30))
        painter.drawText(QPointF(ra.left() + 8, ra.top() + 20), "A")
        painter.drawText(QPointF(rb.right() - 20, rb.top() + 20), "B")
        painter.drawText(QPointF(rc.center().x() - 5, rc.bottom() + 20), "C")

        if self._texte_resultat is not None:
            self._dessiner_resultat(painter)

        painter.end()

    def _dessiner_resultat(self, painter: QPainter):
        texte = f"= {self._texte_resultat}"
        rect_bandeau = QRectF(0, self.height() - 45, self.width(), 45)

        painter.fillRect(rect_bandeau, QColor(240, 240, 240, 220))
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawLine(
            QPointF(0, self.height() - 45),
            QPointF(self.width(), self.height() - 45)
        )
        painter.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        painter.setPen(QColor(30, 30, 30))
        painter.drawText(rect_bandeau, Qt.AlignmentFlag.AlignCenter, texte)


# ──────────────────────────────────────────────────────────────────────────────
# Fenêtre principale
# ──────────────────────────────────────────────────────────────────────────────
class VennColorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagramme de Venn — Colorier")
        self.resize(600, 620)

        self.venn = VennWidget()

        barre = QHBoxLayout()
        barre.addWidget(QLabel("Couleur active :"))

        self.boutons_couleur: list[QPushButton] = []
        for i, c in enumerate(COULEURS):
            btn = QPushButton()
            btn.setFixedSize(32, 32)
            btn.setStyleSheet(
                f"background-color: rgba({c.red()},{c.green()},{c.blue()},200);"
                f"border: 2px solid #555; border-radius: 4px;"
            )
            btn.clicked.connect(lambda _, idx=i: self._choisir_couleur(idx))
            barre.addWidget(btn)
            self.boutons_couleur.append(btn)

        barre.addStretch()

        btn_calculer = QPushButton("Calculer")
        btn_calculer.setFixedHeight(32)
        btn_calculer.clicked.connect(self.venn.calculer)
        barre.addWidget(btn_calculer)

        btn_effacer = QPushButton("Tout effacer")
        btn_effacer.setFixedHeight(32)
        btn_effacer.clicked.connect(self.venn.tout_effacer)
        barre.addWidget(btn_effacer)

        layout = QVBoxLayout(self)
        layout.addLayout(barre)
        layout.addWidget(self.venn)

        self._choisir_couleur(0)

    def _choisir_couleur(self, index: int):
        self.venn.set_couleur_active(index)
        for i, btn in enumerate(self.boutons_couleur):
            c = COULEURS[i]
            bordure = "#000" if i == index else "#555"
            epaisseur = "3px" if i == index else "2px"
            btn.setStyleSheet(
                f"background-color: rgba({c.red()},{c.green()},{c.blue()},200);"
                f"border: {epaisseur} solid {bordure}; border-radius: 4px;"
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = VennColorer()
    fenetre.show()
    sys.exit(app.exec())
