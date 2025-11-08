import sys
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QSlider)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

import math



def transform_sirius_coordinates(input_file="roads.txt", output_file="transformed_roads.txt"):
    lat_sirius = 40.0
    lon_scale_factor = 1 / math.cos(math.radians(lat_sirius))

    print(f"Коэффициент преобразования долготы: {lon_scale_factor:.6f}")

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    nodes_section, edges_section = content.split("Рёбра графа (с названиями улиц):")

    transformed_nodes = []
    nodes_lines = nodes_section.split("ID: ")[1:]  # Пропускаем заголовок

    for node_line in nodes_lines:
        if not node_line.strip():
            continue

        parts = node_line.split(", координаты: ")
        node_id = parts[0].strip()
        coords = parts[1].strip()

        lon, lat = map(float, coords.split(", "))
        lon_transformed = lon * lon_scale_factor

        transformed_nodes.append(f"ID: {node_id}, координаты: {lat:.7f}, {lon_transformed:.7f}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Узлы графа (преобразованные):\n")
        f.write("\n".join(transformed_nodes))
        f.write(f"\n\nРёбра графа (с названиями улиц):\n{edges_section}")

    print(f"Преобразованные координаты сохранены в {output_file}")
    return output_file


transformed_file = transform_sirius_coordinates()

class RoadNetworkWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.edges = []
        self.scale = 5000  # Масштаб для визуализации
        self.offset_x = 0
        self.offset_y = 0
        self.load_data()
        self.calculate_viewport()

    def load_data(self):
        try:
            with open("transformed_roads.txt", 'r', encoding='utf-8') as f:
                content = f.read()
            nodes_section, edges_section = content.split("Рёбра графа (с названиями улиц):")
            nodes_lines = nodes_section.split("ID: ")[1:]

            for node_line in nodes_lines:
                if not node_line.strip():
                    continue

                parts = node_line.split(", координаты: ")
                node_id = parts[0].strip()
                coords = parts[1].strip()
                lat, lon = map(float, coords.split(", "))

                self.nodes[node_id] = (lon, lat)
            edge_lines = edges_section.strip().split('\n')
            for edge_line in edge_lines[:200]:
                if '->' in edge_line:
                    parts = edge_line.split('->')
                    if len(parts) == 2:
                        node_part, rest = parts
                        node1 = node_part.strip()
                        if ':' in rest:
                            node2_part, street = rest.split(':', 1)
                            node2 = node2_part.strip()
                            if node1 in self.nodes and node2 in self.nodes:
                                self.edges.append((node1, node2, street.strip()))

            print(f"Загружено узлов: {len(self.nodes)}, ребер: {len(self.edges)}")

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def calculate_viewport(self):
        if not self.nodes:
            return

        lons = [coord[0] for coord in self.nodes.values()]
        lats = [coord[1] for coord in self.nodes.values()]

        self.min_lon, self.max_lon = min(lons), max(lons)
        self.min_lat, self.max_lat = min(lats), max(lats)

        self.center_lon = (self.min_lon + self.max_lon) / 2
        self.center_lat = (self.min_lat + self.max_lat) / 2

        print(f"Границы: lon[{self.min_lon:.3f}, {self.max_lon:.3f}], "
              f"lat[{self.min_lat:.3f}, {self.max_lat:.3f}]")

    def lon_lat_to_pixel(self, lon, lat):
        x = (lon - self.center_lon) * self.scale + self.width() / 2 + self.offset_x
        y = (self.center_lat - lat) * self.scale + self.height() / 2 + self.offset_y
        return x, y

    def paintEvent(self, event):
        if not self.nodes:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        edge_pen = QPen(QColor(100, 100, 200, 150))
        edge_pen.setWidth(1)
        painter.setPen(edge_pen)

        for node1_id, node2_id, street in self.edges:
            if node1_id in self.nodes and node2_id in self.nodes:
                lon1, lat1 = self.nodes[node1_id]
                lon2, lat2 = self.nodes[node2_id]

                x1, y1 = self.lon_lat_to_pixel(lon1, lat1)
                x2, y2 = self.lon_lat_to_pixel(lon2, lat2)

                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        node_pen = QPen(QColor(255, 0, 0, 200))
        node_pen.setWidth(3)
        painter.setPen(node_pen)

        for lon, lat in self.nodes.values():
            x, y = self.lon_lat_to_pixel(lon, lat)
            painter.drawPoint(int(x), int(y))
        info_pen = QPen(QColor(0, 0, 0))
        painter.setPen(info_pen)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(10, 20, f"Узлов: {len(self.nodes)} | Ребер: {len(self.edges)} | Масштаб: {self.scale}")
        painter.drawText(10, 40, f"Сдвиг: X:{self.offset_x}, Y:{self.offset_y}")

    def wheelEvent(self, event):
        old_scale = self.scale
        if event.angleDelta().y() > 0:
            self.scale *= 1.2
        else:
            self.scale /= 1.2
        self.scale = max(100, min(50000, self.scale))
        if old_scale != self.scale:
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'last_mouse_pos'):
            delta = event.pos() - self.last_mouse_pos
            self.offset_x += delta.x()
            self.offset_y += delta.y()
            self.last_mouse_pos = event.pos()
            self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Дорожная сеть Сириуса")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        control_layout = QHBoxLayout()

        self.scale_label = QLabel("Масштаб:")
        control_layout.addWidget(self.scale_label)

        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setMinimum(100)
        self.scale_slider.setMaximum(50000)
        self.scale_slider.setValue(5000)
        self.scale_slider.valueChanged.connect(self.on_scale_changed)
        control_layout.addWidget(self.scale_slider)

        self.reset_btn = QPushButton("Сброс")
        self.reset_btn.clicked.connect(self.reset_view)
        control_layout.addWidget(self.reset_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)
        self.map_widget = RoadNetworkWidget()
        layout.addWidget(self.map_widget)

    def on_scale_changed(self, value):
        self.map_widget.scale = value
        self.map_widget.update()

    def reset_view(self):
        self.map_widget.scale = 5000
        self.map_widget.offset_x = 0
        self.map_widget.offset_y = 0
        self.scale_slider.setValue(5000)
        self.map_widget.update()


def main():
    transform_sirius_coordinates()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()