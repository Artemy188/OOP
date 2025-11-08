import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPoint, QPointF


class DrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)


        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(50, 50, 100, 100)


        painter.setBrush(QBrush())
        painter.setPen(QPen(Qt.GlobalColor.blue, 3))
        painter.drawEllipse(200, 50, 100, 100)


        painter.setBrush(QBrush(QColor(0, 255, 0)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        triangle_points = [
            QPoint(400, 50),
            QPoint(350, 150),
            QPoint(450, 150)
        ]
        painter.drawPolygon(triangle_points)


        painter.setBrush(QBrush())
        painter.setPen(QPen(QColor(255, 165, 0), 3))
        triangle_points2 = [
            QPoint(550, 50),
            QPoint(500, 150),
            QPoint(600, 150)
        ]
        painter.drawPolygon(triangle_points2)


        painter.setBrush(QBrush(QColor(128, 0, 128)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawRect(50, 200, 100, 80)


        painter.setBrush(QBrush())
        painter.setPen(QPen(QColor(0, 128, 128), 3))
        painter.drawRect(200, 200, 100, 80)


        painter.setBrush(QBrush(QColor(255, 255, 0)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(350, 200, 120, 80)

        painter.setBrush(QBrush(QColor(255, 192, 203)))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        star_points = [
            QPoint(600, 200), QPoint(620, 250), QPoint(670, 250), QPoint(630, 280),
            QPoint(640, 330), QPoint(600, 300), QPoint(560, 330), QPoint(570, 280),
            QPoint(530, 250), QPoint(580, 250)
        ]
        painter.drawPolygon(star_points)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фигуры")
        self.setGeometry(100, 100, 800, 600)

        drawing_widget = DrawingWidget()
        self.setCentralWidget(drawing_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())