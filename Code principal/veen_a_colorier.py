"""
Diagramme de Venn à 3 ensembles.
Clic gauche sur une zone pour la colorier et clic droit pour effacer.
Bouton "Calculer" : affiche la notation ensembliste des zones coloriées.
"""

import sys
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (
    QPainter, QPainterPath, QColor, QPen, QBrush,
    QFont, QMouseEvent
)
from PySide6.QtWidgets import (
    QWidget, QApplication, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from itertools import product


# ──────────────────────────────────────────────
# Couleurs disponibles
# ──────────────────────────────────────────────
COULEURS = [
    QColor(255, 100, 100, 160),   # rouge
    QColor(100, 180, 255, 160),   # bleu
    QColor(100, 220, 100, 160),   # vert
    QColor(255, 200, 50,  160),   # jaune
    QColor(200, 100, 255, 160),   # violet
    QColor(255, 150, 50,  160),   # orange
    QColor(50,  220, 200, 160),   # turquoise
]

# Notation ensembliste de chaque zone

NOTATION: dict[str, list[str]] = {
    "A_entier": ["A", "(A∩B')∪(A∩B)", "(A∩B')∪(A∩B∩C')∪(A∩B∩C)", "(A∩B')∪(A∩B)∪(A∩B∩C)"],
    "B_entier": ["B", "(A'∩B)∪(A∩B)"],
    "C_entier": ["C", "(A'∩C)∪(A∩C)"],
    "A": ["A∩B'∩C'", "A/(B∪C)"],
    "B": ["A'∩B∩C'", "B/(A∪C)"],
    "C": ["A'∩B'∩C", "C/(A∪B)"],
    "AB": ["A∩B", "A∩B∩C'", "(A∩B)/C"],
    "AC": ["A∩C", "A∩B'∩C", "(A∩C)/B"],
    "BC": ["B∩C", "A'∩B∩C", "(B∩C)/A"],
    "ABC": ["A∩B∩C"],
    "A_B_C_sans_ABC": ["(A∪B∪C)∩(A∩B∩C)'", "(A∪B∪C)/(A∩B∩C)"],
    "A_sans_C": ["A∩C'", "A/(B∪C) ∪ (A∩B)"],
    "A_sans_B": ["A∩B'", "A/(B∪C) ∪ (A∩C)"],
    "B_sans_C": ["B∩C'", "B/(A∪C) ∪ (A∩B)"],
    "B_sans_A": ["B∩A'", "B/(A∪C) ∪ (B∩C)"],
    "C_sans_A": ["C∩A'", "C/(A∪B) ∪ (B∩C)"],
    "C_sans_B": ["C∩B'", "C/(A∪B) ∪ (A∩C)"],
    "A_inter_BunionC": ["A∩(B∪C)", "(A∩B)∪(A∩C)"],
    "B_inter_AunionC": ["B∩(A∪C)", "(A∩B)∪(B∩C)"],
    "C_inter_AunionB": ["C∩(A∪B)", "(A∩C)∪(B∩C)"],
    "A_sans_ABC": ["A/(A∩B∩C)", "A∩B' ∪ A∩C'"],
    "B_sans_ABC": ["B/(A∩B∩C)", "A∩B' ∪ B∩C'"],
    "C_sans_ABC": ["C/(A∩B∩C)", "A∩C' ∪ B∩C'"],
    "A_sans_AB": ["A/(A∩B)"],
    "A_sans_AC": ["A/(A∩C)"],
    "B_sans_AB": ["B/(A∩B)"],
    "B_sans_BC": ["B/(B∩C)"],
    "C_sans_AC": ["C/(A∩C)"],
    "C_sans_BC": ["C/(B∩C)"],
}

def creer_chemin_ellipse(rect: QRectF) -> QPainterPath:
    p = QPainterPath()
    p.addEllipse(rect)
    return p


class VennWidget(QWidget):
    """
    Widget principal du diagramme de Venn.
    Gère 7 zones cliquables + affichage de la notation calculée.
    """

    def __init__(self):
        super().__init__()
        self.setMinimumSize(500, 500)

        self.index_couleur_active = 0

        self.lst_solutions = []

        self.couleurs_zones: dict[str, QColor | None] = {
            "A": None, "B": None, "C": None,
            "AB": None, "AC": None, "BC": None, "ABC": None,
        }

        self.chemins: dict[str, QPainterPath] = {}

        # Texte de résultat affiché en bas du diagramme (None = rien)
        self._texte_resultat: str | None = None

        self._calculer_chemins()

    # ──────────────────────────────────────────
    # Géométrie
    # ──────────────────────────────────────────

    def _rects_ellipses(self):
        w, h = self.width(), self.height()
        rx = w * 0.30
        ry = h * 0.28
        cx, cy = w / 2, h / 2
        dx = rx * 0.55
        dy = ry * 0.45

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
            "A":   pa.subtracted(pb).subtracted(pc),
            "B":   pb.subtracted(pa).subtracted(pc),
            "C":   pc.subtracted(pa).subtracted(pb),
            "AB":  pa.intersected(pb).subtracted(pc),
            "AC":  pa.intersected(pc).subtracted(pb),
            "BC":  pb.intersected(pc).subtracted(pa),
            "ABC": pa.intersected(pb).intersected(pc),
        }
        self._chemin_A_complet = pa
        self._chemin_B_complet = pb
        self._chemin_C_complet = pc

    # ──────────────────────────────────────────
    # Événements Qt
    # ──────────────────────────────────────────

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
                # Mise à jour automatique si la notation était déjà affichée
                if self._texte_resultat is not None:
                    self._texte_resultat = self._construire_notation()
                self.update()
                return

    # ──────────────────────────────────────────
    # Logique de notation ensembliste
    # ──────────────────────────────────────────

    def _construire_notation(self) -> str:
        zones_actives = {nom for nom, c in self.couleurs_zones.items() if c is not None}
        self.lst_solutions = []

        if not zones_actives:
            return "Aucune zone coloriée"

        # ── Simplifications ensemblistes ──────────────────────────────────
        # A/(B∪C) ∪ (A∩B) ∪ (A∩C) ∪ (A∩B∩C) = A
        if {"A", "AB", "AC", "ABC"}.issubset(zones_actives):
            zones_actives -= {"A", "AB", "AC", "ABC"}
            zones_actives.add("A_entier")

        # B/(A∪C) ∪ (A∩B) ∪ (B∩C) ∪ (A∩B∩C) = B
        if {"B", "AB", "BC", "ABC"}.issubset(zones_actives):
            zones_actives -= {"B", "AB", "BC", "ABC"}
            zones_actives.add("B_entier")

        # C/(A∪B) ∪ (A∩C) ∪ (B∩C) ∪ (A∩B∩C) = C
        if {"C", "AC", "BC", "ABC"}.issubset(zones_actives):
            zones_actives -= {"C", "AC", "BC", "ABC"}
            zones_actives.add("C_entier")

        # A ∪ B/(A∪C) ∪ (B∩C)
        if {"A_entier", "B", "BC"}.issubset(zones_actives):
            zones_actives -= {"B", "BC"}
            zones_actives.add("B_entier")

        # A ∪ C/(A∪B) ∪ (B∩C)
        if {"A_entier", "C", "BC"}.issubset(zones_actives):
            zones_actives -= {"C", "BC"}
            zones_actives.add("C_entier")

        # B ∪ C/(A∪B) ∪ (BA∩C)
        if {"B_entier", "C", "AC"}.issubset(zones_actives):
            zones_actives -= {"C", "AC"}
            zones_actives.add("C_entier")

        # A ∪ B ∪ C/(A∪B)
        if {"A_entier", "B_entier", "C"}.issubset(zones_actives):
            zones_actives -= {"C"}
            zones_actives.add("C_entier")

        # A/(B∪C) ∪ B/(A∪C) ∪ C/(A∪B) ∪ (A∩B) ∪ (A∩C) ∪ (B∩C)
        if {"A", "B", "C", "AB", "AC", "BC"}.issubset(zones_actives):
            zones_actives -= {"A", "B", "C", "AB", "AC", "BC"}
            zones_actives.add("A_B_C_sans_ABC")

        # A/(B∪C) ∪ (A∩B) = A∩C'   (A sans C)
        if {"A", "AB"}.issubset(zones_actives) and "AC" not in zones_actives and "ABC" not in zones_actives:
            zones_actives -= {"A", "AB"}
            zones_actives.add("A_sans_C")

        # A/(B∪C) ∪ (A∩C) = A∩B'   (A sans B)
        if {"A", "AC"}.issubset(zones_actives) and "AB" not in zones_actives and "ABC" not in zones_actives:
            zones_actives -= {"A", "AC"}
            zones_actives.add("A_sans_B")

        # (A∩B) ∪ (A∩C) ∪ (A∩B∩C) = A∩(B∪C)
        if {"AB", "AC", "ABC"}.issubset(zones_actives):
            zones_actives -= {"AB", "AC", "ABC"}
            zones_actives.add("A_inter_BunionC")

        # (A∩B) ∪ (B∩C) ∪ (A∩B∩C) = B∩(A∪C)
        if {"AB", "BC", "ABC"}.issubset(zones_actives):
            zones_actives -= {"AB", "BC", "ABC"}
            zones_actives.add("B_inter_AunionC")

        # (A∩C) ∪ (B∩C) ∪ (A∩B∩C) = C∩(A∪B)
        if {"AC", "BC", "ABC"}.issubset(zones_actives):
            zones_actives -= {"AC", "BC", "ABC"}
            zones_actives.add("C_inter_AunionB")

        # A sans le centre = A + AB + AC
        if {"A", "AB", "AC"}.issubset(zones_actives) and "ABC" not in zones_actives:
            zones_actives -= {"A", "AB", "AC"}
            zones_actives.add("A_sans_ABC")

        # B sans le centre = B + AB + BC
        if {"B", "AB", "BC"}.issubset(zones_actives) and "ABC" not in zones_actives:
            zones_actives -= {"B", "AB", "BC"}
            zones_actives.add("B_sans_ABC")

        # C sans le centre = C + AC + BC
        if {"C", "AC", "BC"}.issubset(zones_actives) and "ABC" not in zones_actives:
            zones_actives -= {"C", "AC", "BC"}
            zones_actives.add("C_sans_ABC")

        # A sans le coté AB = A + AC + ABC
        if {"A", "AC", "ABC"}.issubset(zones_actives) and "AB" not in zones_actives:
            zones_actives -= {"A", "AC", "ABC"}
            zones_actives.add("A_sans_AB")

        # B sans le cçoté AB = B + BC + ABC
        if {"B", "BC", "ABC"}.issubset(zones_actives) and "AB" not in zones_actives:
            zones_actives -= {"B", "BC", "ABC"}
            zones_actives.add("B_sans_AB")

        # C sans le côté AC = C + BC + ABC
        if {"C", "BC", "ABC"}.issubset(zones_actives) and "AC" not in zones_actives:
            zones_actives -= {"C", "BC", "ABC"}
            zones_actives.add("C_sans_AC")

        # A sans le coté AC = A + AB + ABC
        if {"A", "AB", "ABC"}.issubset(zones_actives) and "AC" not in zones_actives:
            zones_actives -= {"A", "AB", "ABC"}
            zones_actives.add("A_sans_AC")

        # B sans le cçoté BC = B + AB + ABC
        if {"B", "AB", "ABC"}.issubset(zones_actives) and "BC" not in zones_actives:
            zones_actives -= {"B", "AB", "ABC"}
            zones_actives.add("B_sans_BC")

        # C sans le côté BC = C + AC + ABC
        if {"C", "AC", "ABC"}.issubset(zones_actives) and "BC" not in zones_actives:
            zones_actives -= {"C", "AC", "ABC"}
            zones_actives.add("C_sans_BC")

        # ── Construction de la notation finale ───────────────────────────

        ordre = [
            # Ensembles entiers
            "A_entier", "B_entier", "C_entier",

            # A sans un autre
            "A_sans_B", "A_sans_C", "A_sans_ABC", "A_sans_AB", "A_sans_AC",
            "B_sans_A", "B_sans_C", "B_sans_ABC", "B_sans_AB", "B_sans_BC",
            "C_sans_A", "C_sans_B", "C_sans_ABC", "C_sans_AC", "C_sans_BC",

            # Intersections avec union
            "A_inter_BunionC", "B_inter_AunionC", "C_inter_AunionB",

            # Zones pures (sans aucune intersection)
            "A", "B", "C",

            # Intersections doubles
            "AB", "AC", "BC",

            # Centre
            "ABC",

            # Cas spécial tout sauf centre
            "A_B_C_sans_ABC",
        ]
        zones_triees = sorted(zones_actives, key=lambda z: ordre.index(z))

        # Génère toutes les combinaisons d'équivalences

        listes = [NOTATION[z] for z in zones_triees]
        for combo in product(*listes):  # produit cartésien
            notation = " ∪ ".join(combo)
            self.lst_solutions.append(notation)

        # La plus simple = toujours le premier élément de chaque zone
        e = " ∪ ".join(NOTATION[z][0] for z in zones_triees)
        print(e)
        return e

    # ──────────────────────────────────────────
    # Dessin
    # ──────────────────────────────────────────

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fond blanc
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        # 1) Zones coloriées
        for nom, chemin in self.chemins.items():
            couleur = self.couleurs_zones[nom]
            if couleur:
                painter.fillPath(chemin, QBrush(couleur))

        # 2) Contours des ellipses
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for chemin in (self._chemin_A_complet, self._chemin_B_complet, self._chemin_C_complet):
            painter.drawPath(chemin)

        # 3) Étiquettes A, B, C
        ra, rb, rc = self._rects_ellipses()
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(QColor(30, 30, 30))
        marge = 8
        painter.drawText(QPointF(ra.left() + marge,    ra.top() + 20),    "A")
        painter.drawText(QPointF(rb.right() - 20,      rb.top() + 20),    "B")
        painter.drawText(QPointF(rc.center().x() - 5,  rc.bottom() + 20), "C")

        # 4) Bandeau résultat (si calculé)
        if self._texte_resultat is not None:
            self._dessiner_resultat(painter)

        painter.end()

    def _dessiner_resultat(self, painter: QPainter):
        """Affiche la notation ensembliste dans un bandeau en bas du widget."""
        texte = f"= {self._texte_resultat}"
        rect_bandeau = QRectF(0, self.height() - 45, self.width(), 45)

        # Fond semi-transparent
        painter.fillRect(rect_bandeau, QColor(240, 240, 240, 220))
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawLine(
            QPointF(0, self.height() - 45),
            QPointF(self.width(), self.height() - 45)
        )

        # Texte centré
        painter.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        painter.setPen(QColor(30, 30, 30))
        painter.drawText(rect_bandeau, Qt.AlignmentFlag.AlignCenter, texte)

    def calculer(self):
        """Déclenché par le bouton Calculer — affiche la notation ensembliste."""
        self._texte_resultat = self._construire_notation()
        self.update()

    def tout_effacer(self):
        for k in self.couleurs_zones:
            self.couleurs_zones[k] = None
        self._texte_resultat = None
        self.update()

    def set_couleur_active(self, index: int):
        self.index_couleur_active = index % len(COULEURS)


# ──────────────────────────────────────────────
# Fenêtre principale
# ──────────────────────────────────────────────

class VennColorer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diagramme de Venn — Colorier")
        self.resize(600, 620)

        self.venn = VennWidget()

        # Barre de couleurs + boutons
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
