from PySide6.QtCore import QPoint
from PySide6.QtGui import QPainter, QColorConstants
from PySide6.QtWidgets import QWidget, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsView, \
    QVBoxLayout, QGraphicsScene, QGraphicsTextItem, QStyleOptionGraphicsItem


class Venn(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Diagramme de Venn")

        # Layout
        self.disposition = QVBoxLayout()
        self.setLayout(self.disposition)

        # Prep pour l'animation
        self.graphique_vue = QGraphicsView()
        self.graphique_vue.setStyleSheet("background-color:rgb(255,255,255);")
        self.graphique_scene = QGraphicsScene(0, 0, 600, 600)
        self.graphique_vue.setScene(self.graphique_scene)

        # Éllipse
        x = int(self.graphique_scene.width() / 4)
        y = int(self.graphique_scene.height() / 4)
        w = 200
        h = 200
        painter = QPainter()
        painter.setBackground(QColorConstants.White)
        painter.drawEllipse(QPoint(x, y), w, h)
        self.graphique_ellipse_2 = QGraphicsEllipseItem(x + 2 * w/3, y, w, h)
        self.graphique_ellipse_3 = QGraphicsEllipseItem(x + w/3, y + 3 * h/5, w, h)

        # Rectangle
        self.graphique_rec = QGraphicsRectItem(5, 5, self.graphique_scene.width() - 10, self.graphique_scene.height() -
                                               10)

        # Ensembles
        x = self.graphique_scene.width()/2
        y = 25
        self.ensemble_univers = QGraphicsTextItem("U")
        self.ensemble_univers.setPos(x, y)

        self.graphique_scene.addItem(self.graphique_rec)
        self.graphique_scene.addItem(self.graphique_ellipse_2)
        self.graphique_scene.addItem(self.graphique_ellipse_3)
        self.graphique_scene.addItem(self.ensemble_univers)

        self.disposition.addWidget(self.graphique_vue)
