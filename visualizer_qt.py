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
)
import sys
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
        self.run_button = QPushButton("Run")
        self.step_button = QPushButton("Run setep")
        self.reload_button = QPushButton("Reload")
        self.close_button = QPushButton("Close")
        toolbar.addWidget(self.run_button)
        toolbar.addWidget(self.step_button)
        toolbar.addWidget(self.reload_button)
        toolbar.addWidget(self.close_button)
        self.combo = QComboBox()
        self.combo.addItems(["map1","map2","map3","map4","map5"])
        toolbar.addWidget(self.combo)
        self.screen = QGraphicsScene()
        self.view = QGraphicsView(self.screen)
        main_layout.addWidget(self.view)
       


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())