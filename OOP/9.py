import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QSpinBox, QHBoxLayout
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt


class PerformanceTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.lines_count = 1000
        self.last_draw_time = 0

    def set_lines_count(self, count):
        self.lines_count = count
        self.update()

    def paintEvent(self, event):
        start_time = time.time()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        for i in range(self.lines_count):
            color = QColor(
                (i * 50) % 255,
                (i * 30) % 255,
                (i * 70) % 255
            )
            pen = QPen(color, 1)
            painter.setPen(pen)

            x1 = (i * 10) % width
            y1 = (i * 5) % height
            x2 = ((i + 1) * 10) % width
            y2 = ((i + 1) * 8) % height

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        self.last_draw_time = time.time() - start_time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест производительности рисования линий")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.test_widget = PerformanceTestWidget()
        layout.addWidget(self.test_widget)

        control_layout = QHBoxLayout()

        self.count_label = QLabel("Количество линий:")
        control_layout.addWidget(self.count_label)

        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 1000000)
        self.spin_box.setValue(1000)
        self.spin_box.valueChanged.connect(self.test_widget.set_lines_count)
        control_layout.addWidget(self.spin_box)

        self.test_button = QPushButton("Запустить тест")
        self.test_button.clicked.connect(self.run_test)
        control_layout.addWidget(self.test_button)

        self.result_label = QLabel("Время рисования: 0.000 сек")
        control_layout.addWidget(self.result_label)

        self.fps_label = QLabel("FPS: 0")
        control_layout.addWidget(self.fps_label)

        layout.addLayout(control_layout)

        info_layout = QHBoxLayout()
        self.info_label = QLabel("Изменяйте количество линий и наблюдайте за производительностью")
        info_layout.addWidget(self.info_label)
        layout.addLayout(info_layout)

        self.test_widget.update()

    def run_test(self):
        self.test_widget.update()
        draw_time = self.test_widget.last_draw_time
        fps = 1.0 / draw_time if draw_time > 0 else 0

        self.result_label.setText(f"Время рисования: {draw_time:.3f} сек")
        self.fps_label.setText(f"FPS: {fps:.1f}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())