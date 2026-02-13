from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QEasingCurve, QObject, \
    QVariantAnimation, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QMenuBar, \
    QMenu
from PySide6.QtGui import QPixmap, QAction, QColorConstants, QLinearGradient


class AquariumApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vue = QGraphicsView()
        self.vue.setFixedSize(800, 600)

        self.setCentralWidget(self.vue)
        self.jardin = Aquarium()
        self.poisson = Poisson()
        self.bulle = Bulles(self.poisson)
        self.jardin.addItem(self.poisson)
        self.jardin.addItem(self.bulle)
        self.vue.setScene(self.jardin)

        self.barre_menu = QMenuBar()
        self.menu = QMenu("Menu")
        self.action_ajouter = QAction("Ajouter", parent=self)
        self.menu.addAction(self.action_ajouter)

        self.action_changer = QAction("Changer", parent=self)
        self.menu.addAction(self.action_changer)

        self.menu_math = QMenu("Math Discète")
        self.action_chapitre_1 = QAction("Chapitre 1", parent=self)
        self.action_chapitre_2 = QAction("Chapitre 2", parent=self)
        self.action_chapitre_3 = QAction("Chapitre 3", parent=self)
        self.action_chapitre_4 = QAction("Chapitre 4", parent=self)
        self.action_chapitre_5 = QAction("Chapitre 5", parent=self)
        self.action_chapitre_6 = QAction("Chapitre 6", parent=self)
        self.menu_math.addActions([self.action_chapitre_1, self.action_chapitre_2, self.action_chapitre_3,
                                   self.action_chapitre_4, self.action_chapitre_5, self.action_chapitre_6])

        self.barre_menu.addMenu(self.menu)
        self.barre_menu.addMenu(self.menu_math)
        self.setMenuBar(self.barre_menu)

        self.animation_bulle = AnimationBulle(self.bulle, self.bulle.start, self.bulle.end, duration=2500,
                                              easing=QEasingCurve.Type.InOutCubic, bulle=True)
        self.animation_bulle.play()

        self.animation_poisson = AnimationBulle(self.poisson, self.poisson.start, self.poisson.end, duration=2500,
                                                easing=QEasingCurve.Type.InOutCubic, poisson=True)
        QTimer.singleShot(2000, self.animation_poisson.play)

        QTimer.singleShot(4000, lambda: self.jardin.removeItem(self.poisson))


class Aquarium(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.setSceneRect(QRectF(0, 0, 800, 600))

        gradient = QLinearGradient(0, 0, 0, 600)
        gradient.setColorAt(0, QColorConstants.Cyan)
        gradient.setColorAt(0.5, QColorConstants.DarkCyan)
        gradient.setColorAt(1, QColorConstants.DarkBlue)
        self.setBackgroundBrush(gradient)

        for i in range(int(self.width() / 5) + (self.width() % 5 > 0)):
            floor = QGraphicsPixmapItem(QPixmap("../../Images/img_3.png"))
            floor.setScale(1)
            floor.setPos(QPoint((i-1)*320, 500))
            self.addItem(floor)


class AnimationBulle(QObject):
    def __init__(self, item: QGraphicsPixmapItem, position_debut: QPointF, position_fin: QPointF,
                 duration: int = 2000, easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic, bulle: bool = False,
                 poisson: bool = False):
        super().__init__()
        self.item = item
        self.debut = QPointF(position_debut)
        self.fin = QPointF(position_fin)
        self.anim = QVariantAnimation(self)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setDuration(duration)
        self.anim.setEasingCurve(QEasingCurve(easing))
        self.anim.valueChanged.connect(self._on_value)
        self.bulle = bulle
        self.poisson = poisson

    def _on_value(self, v):
        x = self.debut.x() + (self.fin.x() - self.debut.x()) * float(v)
        y = self.debut.y() + (self.fin.y() - self.debut.y()) * float(v)
        self.item.setPos(QPointF(x, y))

        if self.bulle and v < 0.25:
            self.item.setScale(2 * v)

    def play(self):
        self.anim.start()


class Bulles(QGraphicsPixmapItem):
    def __init__(self, poisson):
        super().__init__()
        poisson = poisson
        bulle = QPixmap("../Images/fsdfgS/Bubble.png").scaled(
            50,
            50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(bulle)
        self.setTransformOriginPoint(bulle.width() / 2, bulle.height() / 2)
        self.setScale(0.1)

        self.start = QPointF(poisson.start.x() + poisson.poisson.width() / 2, (400 - bulle.height()) / 2)
        self.end = QPointF(poisson.start.x() + poisson.poisson.width() / 2, -bulle.height())


class Poisson(QGraphicsPixmapItem):
    def __init__(self):
        super().__init__()
        self.poisson = QPixmap("../Images/pixel-art/martin.png").scaled(
            50,
            50,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(self.poisson)
        self.setTransformOriginPoint(self.poisson.width() / 2, self.poisson.height() / 2)

        self.start = QPointF(250, (400 - self.poisson.height()) / 2)
        self.end = QPointF(600 + self.poisson.width(), (400 - self.poisson.height()) / 2)
        self.setPos(self.start)

        #
        # move_menu_button = QGraphicsEllipseItem(730, 550, 30, 30)
        # move_menu_button_brush = QBrush
        # button_colour = QColor(40,80,180)
        # move_menu_button_brush.(button_colour)
        # self.addItem(move_menu_button)




    def add_feesh(self):
        pass

    def add_deco(self):
        pass



app = QApplication()
a = AquariumApp()
a.show()
app.exec()
