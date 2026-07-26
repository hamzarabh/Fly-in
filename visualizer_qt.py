from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsObject,
    QGraphicsLineItem
)

from PySide6.QtGui import QBrush, QColor, QPen, QPainter, QPixmap
from PySide6.QtCore import Qt, QRectF
import sys


class ZoneItem(QGraphicsObject):
    def __init__(self, scene, x, y,name, color):
        super().__init__()
        self.name = name
        self.color = QColor(color)
        self.connections = []
        self.setPos(x,y)
        scene.addItem(self)
    def boundingRect(self):
        return QRectF(0,0,80,100)

    def center(self):
        return(
            self.scenePos().x() + 40,
            self.scenePos().y() + 40,
        )

    def paint(self, painter, option, widget):
        painter.setBrush(self.color)
        painter.drawEllipse(0,0,80,80)
        painter.drawText(
            QRectF(0,80,80,20),
            Qt.AlignCenter,
            self.name
        )
        # return super().paint(painter, option, widget)

    def setPos(self, x, y):
        super().setPos(x, y)
        for connections in self.connections:
            connections.update()


class ConnectionItem(QGraphicsLineItem):
    def __init__(self, scene, zone_1: ZoneItem, zone_2: ZoneItem):
        super().__init__()
        self.zone_1 = zone_1
        self.zone_2 = zone_2

        zone_1.connections.append(self)
        zone_2.connections.append(self)
        x1, y1 = zone_1.center()
        x2, y2 = zone_2.center()
        self.setPen(QPen(Qt.red, 2))
        self.setLine(x1, y1, x2, y2)
        # self.line = scene.addLine(x1, y1, x2, y2,QPen(Qt.red, 2))
        self.setZValue(-1)
        self.update()
        scene.addItem(self)

    def update(self):
        x1, y1 = self.zone_1.center()
        x2, y2 = self.zone_2.center()
        self.setLine(x1, y1, x2, y2)

class DroneItem(QGraphicsObject):
    def __init__(self, scene, image_path):
        super().__init__()
        self.pixmap = QPixmap(image_path)
        print(self.pixmap.width(), self.pixmap.height())
        scene.addItem(self)
        self.setTransformOriginPoint(self.boundingRect().center())
        self.setRotation(90)
        self.setScale(0.1)
        


    def boundingRect(self):
        return QRectF(self.pixmap.rect())

    def paint(self, painter, option, widget):
        painter.drawPixmap(0,0, self.pixmap)

class MapView(QGraphicsView):
    def __init__(self,scene):

        self.camera_x = 0
        self.camera_y = 0
        self.zoom  = 1.0
        self.dragging = False
        self.last_pos = None
        super().__init__(scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    def UpdateCamera(self):
        self.resetTransform()
        self.scale(self.zoom, self.zoom)
        self.centerOn(self.camera_x, self.camera_y)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom *= 1.15
        else:
            self.zoom /= 1.15
        self.UpdateCamera()
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_pos = event.position()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.position() - self.last_pos
            self.camera_x -= delta.x() / self.zoom
            self.camera_y -= delta.y() / self.zoom
            self.UpdateCamera()
            self.last_pos = event.position()
            event.accept()
            return
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)




class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fly-in Visualizer")
        self.resize(1400, 900)
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        toolbar = QHBoxLayout()
        main_layout.addLayout(toolbar)
        self.combo = QComboBox()
        self.combo.addItems(["map1","map2","map3","map4","map5"])
        toolbar.addWidget(self.combo)
        self.run_button = QPushButton("Run")
        self.step_button = QPushButton("Run setep")
        self.reload_button = QPushButton("Reload")
        self.close_button = QPushButton("Close")
        toolbar.addWidget(self.run_button)
        toolbar.addWidget(self.step_button)
        toolbar.addWidget(self.reload_button)
        toolbar.addWidget(self.close_button)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        self.view = MapView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        main_layout.addWidget(self.view)

        self.start = ZoneItem(
            self.scene,200,200, "Start","red"
        )
        self.end = ZoneItem(
            self.scene,200,400, "End","green"
        )
        self.conect = ConnectionItem(self.scene,self.start, self.end)

        self.drone = DroneItem(
            self.scene,
            "Copilot_20260630_104836.png"
        )
        self.drone.setPos(300,300)
        
       


app = QApplication(sys.argv)
window = MainWindow()
window.end.setPos(0,10)
window.start.setPos(900,10)
# window.view.scale(1.2, 1.2)
window.show()
sys.exit(app.exec())