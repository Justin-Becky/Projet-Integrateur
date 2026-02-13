from PySide6.QtCore import QPoint, QPointF, QRectF
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QMenuBar, \
    QMenu, QDialog, QHBoxLayout, QPushButton, QVBoxLayout, QLabel
from PySide6.QtGui import QPainter, QPainterPath, QPixmap, QAction, QGradient, QColorConstants, QBrush, QLinearGradient


class Jardin(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(QRectF(0, 0, 800, 600))

        brush = QBrush()
        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0, QColorConstants.Cyan)
        gradient.setColorAt(0.5, QColorConstants.DarkCyan)
        gradient.setColorAt(1, QColorConstants.DarkBlue)
        self.setBackgroundBrush(gradient)

        for i in range(5):
            floor = QGraphicsPixmapItem(QPixmap("../images/img_3.png"))
            floor.setScale(1)
            floor.setPos(QPoint((i-1)*175, 500))
            self.addItem(floor)



    def ajouter(self):
        images = QGraphicsPixmapItem(QPixmap("../images/img_2.png"))
        images.setScale(0.1)
        images.setPos(QPoint(50, 50))
        self.addItem(images)


class JardinApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vue = QGraphicsView()
        self.vue.setFixedSize(800, 600)

        self.setCentralWidget(self.vue)
        self.jardin = Jardin()
        self.vue.setScene(self.jardin)

        self.barre_menu = QMenuBar()
        self.menu = QMenu("Allo")
        self.action_ajouter = QAction("Ajouter", parent=self)
        self.action_ajouter.triggered.connect(self.ajouter)
        self.menu.addAction(self.action_ajouter)

        self.action_changer = QAction("Changer", parent=self)
        self.action_changer.triggered.connect(self.changer)
        self.menu.addAction(self.action_changer)

        self.barre_menu.addMenu(self.menu)
        self.setMenuBar(self.barre_menu)

    def ajouter(self):
        self.jardin.addItem(Plante("../images/img_2.png", "../images/img_1.png", "../images/img.png"))
        lo = JardinAchat()
        lo.exec()

    def changer(self):
        #Plante.ETAT = 1
        Plante.mettre_a_jour()


class JardinAchat(QDialog):

    def __init__(self):
        super().__init__()
        self.plante_selectionne = QLabel()
        self.disposition = QVBoxLayout()
        self.setLayout(self.disposition)
        self.disposition.addLayout(BoutonPlante("../images/img.png", 55, self))
        self.disposition.addLayout(BoutonPlante("../images/img.png", 55, self))
        self.disposition.addLayout(BoutonPlante("../images/img.png", 55, self))


class BoutonPlante(QHBoxLayout):
    def __init__(self, image, prix, parent):
        super().__init__()
        self.parent = parent
        self.image = QLabel()
        self.image.setPixmap(QPixmap(image).scaled(15, 15))
        self.bouton_prix = QPushButton(str(prix))
        self.bouton_prix.clicked.connect(self.bouton_clicked)
        self.addWidget(self.image)
        self.addWidget(self.bouton_prix)

    def bouton_clicked(self):
        self.parent.plante_selectionne.setPixmap(QPixmap("../images/img.png"))


class Plante(QGraphicsPixmapItem):
    FANER = 0
    MOYENNE = 1
    BELLE = 2
    ETAT = 0

    def __init__(self, belle, moyenne, laide):
        super().__init__()
        self.etat = belle
        self.belle = QPixmap(belle)
        self.moyenne = QPixmap(moyenne)
        self.laide = QPixmap(laide)
        self.position = QPointF(50, 50)
        self.setPixmap(self.belle)

    def mettre_a_jour(self):

        if Plante.ETAT == Plante.FANER:
            self.setPixmap(self.laide)
        elif self.ETAT == Plante.MOYENNE:
            self.setPixmap(self.moyenne)
        else:
            self.setPixmap(self.belle)


app = QApplication()
j = JardinApp()
j.show()
app.exec()
