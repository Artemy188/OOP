import sys
import re
import math
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QMessageBox, QScrollArea, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush

class LogicSolver:
    @staticmethod
    def parse_interval(s):
        try:
            s = s.strip().replace('[', '').replace(']', '')
            parts = re.split(r'[;,]', s)
            return int(parts[0]), int(parts[1])
        except:
            return None

    @staticmethod
    def prepare_expression(expr):
        expr = expr.replace('and', ' and ')
        expr = expr.replace('or', ' or ')
        expr = expr.replace('not', ' not ')
        expr = expr.replace(' → ', ' <= ')
        expr = expr.replace('→', ' <= ')
        expr = expr.replace('xor', ' ^ ')
        expr = expr.replace('∧', ' and ')
        expr = expr.replace('∨', ' or ')
        expr = expr.replace('≡', ' == ')
        expr = expr.replace('¬', ' 1- ')
        expr = expr.replace('∈', ' in ')
        pattern = r'\b([a-zA-Z0-9_]+)\s+in\s+([a-zA-Z0-9_]+)\b'

        def replace_in(match):
            var, interval_name = match.group(1), match.group(2)
            if interval_name == 'A':
                return 'in_A'
            return f"check({var}, '{interval_name}')"

        expr = re.sub(pattern, replace_in, expr)
        return expr

    @staticmethod
    def solve(intervals_map, expr_raw, mode='max'):
        scale = 10  # Точность (1/10)
        all_coords = []
        for start, end in intervals_map.values():
            all_coords.extend([start, end])

        if not all_coords:
            return "Нет заданных интервалов", []

        min_x = (min(all_coords) - 20) * scale
        max_x = (max(all_coords) + 20) * scale
        def check(val, name):
            if name not in intervals_map: return 0
            start, end = intervals_map[name]
            return 1 if start <= val <= end else 0

        py_expr = LogicSolver.prepare_expression(expr_raw)
        valid_points = []
        try:
            for k in range(min_x, max_x + 1):
                x = k / scale

                if mode == 'max':
                    in_A = 1
                    if eval(py_expr, {"x": x, "check": check, "in_A": in_A}):
                        valid_points.append(x)

                else:
                    in_A = 0
                    if not eval(py_expr, {"x": x, "check": check, "in_A": in_A}):
                        valid_points.append(x)

        except Exception as e:
            return f"Ошибка в формуле: {e}", []

        if not valid_points:
            return 0, (0, 0), []
        if mode == 'min':
            start = valid_points[0]
            end = valid_points[-1]
            length = round(end - start)
            ui_start = round(start * 2) / 2
            ui_end = round(end * 2) / 2
            return length, (ui_start, ui_end), [(ui_start, ui_end)]
        else:
            max_len = -1
            best_segment = None
            all_segments = []

            current_start = valid_points[0]
            prev_x = valid_points[0]
            threshold = 1.1 / scale

            def close_segment(s, e):
                nonlocal max_len, best_segment
                l = round(e - s)
                ui_s = round(s * 2) / 2
                ui_e = round(e * 2) / 2
                seg = (ui_s, ui_e)
                all_segments.append(seg)

                if l >= max_len:
                    max_len = l
                    best_segment = seg

            for x in valid_points[1:]:
                if x - prev_x > threshold:  # Разрыв
                    close_segment(current_start, prev_x)
                    current_start = x
                prev_x = x

            close_segment(current_start, prev_x)  # Закрыть последний

            return max_len, best_segment, all_segments


class SetInputWidget(QWidget):
    def __init__(self, parent_layout, name="", interval=""):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 2, 0, 2)
        self.parent_layout_ref = parent_layout

        self.name_edit = QLineEdit(name)
        self.name_edit.setPlaceholderText("Буква")
        self.name_edit.setFixedWidth(50)
        self.name_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.interval_edit = QLineEdit(interval)
        self.interval_edit.setPlaceholderText("[10; 20]")

        self.del_btn = QPushButton("✕")
        self.del_btn.setFixedWidth(30)
        self.del_btn.setStyleSheet("color: white; background-color: #ff4444; font-weight: bold; border-radius: 3px;")
        self.del_btn.clicked.connect(self.delete_self)

        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.interval_edit)
        self.layout.addWidget(self.del_btn)

    def delete_self(self):
        self.parent_layout_ref.removeWidget(self)
        self.deleteLater()

    def get_data(self):
        return self.name_edit.text().strip(), self.interval_edit.text().strip()


class NumberLineWidget(QWidget):
    """Рисование отрезков"""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(250)
        self.intervals_map = {}
        self.result_seg = None
        self.all_segments = []
        self.colors = {}

    def set_data(self, intervals_map, result_seg, all_segments):
        self.intervals_map = intervals_map
        self.result_seg = result_seg
        self.all_segments = all_segments

        # Генерируем цвета для множеств
        keys = list(intervals_map.keys())
        self.colors = {}
        for i, key in enumerate(keys):
            hue = int((i * 137.5) % 360)  # Золотое сечение для разброса цветов
            self.colors[key] = QColor.fromHsv(hue, 180, 200)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        margin = 50

        points = []
        for s, e in self.intervals_map.values():
            points.extend([s, e])
        if self.result_seg:
            points.extend([self.result_seg[0], self.result_seg[1]])

        if not points:
            painter.drawText(w // 2 - 50, h // 2, "Нет данных")
            return

        min_val, max_val = min(points) - 10, max(points) + 10
        val_range = max_val - min_val if max_val != min_val else 100

        def to_screen(val):
            return margin + (val - min_val) / val_range * (w - 2 * margin)
        axis_y = h // 2 + 30
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawLine(int(to_screen(min_val)), axis_y, int(to_screen(max_val)), axis_y)
        h_bar = 14
        spacing = 28

        for i, (name, (start, end)) in enumerate(self.intervals_map.items()):
            y_pos = axis_y - 20 - (i * spacing)
            col = self.colors.get(name, Qt.GlobalColor.gray)
            painter.setBrush(QBrush(col))
            painter.setPen(Qt.PenStyle.NoPen)
            x1, x2 = to_screen(start), to_screen(end)
            painter.drawRect(int(x1), y_pos - h_bar, int(x2 - x1), h_bar)
            painter.setPen(Qt.GlobalColor.black)
            painter.drawText(int(x1) - 10, y_pos - 2, f"{start}")
            painter.drawText(int(x2) + 2, y_pos - 2, f"{end}")
            painter.setPen(QPen(col.darker(150), 1))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(int((x1 + x2) / 2) - 5, y_pos - h_bar - 2, name)
        if self.result_seg:
            y_a = axis_y + 25
            if len(self.all_segments) > 1:
                painter.setBrush(QBrush(QColor(200, 200, 200, 100)))
                for seg in self.all_segments:
                    sx1, sx2 = to_screen(seg[0]), to_screen(seg[1])
                    painter.drawRect(int(sx1), y_a, int(sx2 - sx1), h_bar)

            painter.setBrush(QBrush(QColor(255, 0, 0, 180)))  # Ярко-красный
            ax1, ax2 = to_screen(self.result_seg[0]), to_screen(self.result_seg[1])
            painter.drawRect(int(ax1), y_a, int(ax2 - ax1), h_bar + 4)

            painter.setPen(QPen(Qt.GlobalColor.red, 2))
            painter.drawText(int(ax1), y_a + 35, f"{self.result_seg[0]}")
            painter.drawText(int(ax2), y_a + 35, f"{self.result_seg[1]}")

            length = round(self.result_seg[1] - self.result_seg[0])
            painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            painter.drawText(int((ax1 + ax2) / 2) - 30, y_a + 55, f"A (Len={length})")




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Решатель логических задач (ЕГЭ)")
        self.resize(850, 650)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        sets_group = QWidget()
        sets_layout = QVBoxLayout(sets_group)
        sets_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("<b>Исходные множества:</b>"))
        add_btn = QPushButton("+ Добавить")
        add_btn.setFixedWidth(100)
        add_btn.clicked.connect(self.add_set_row)
        header_layout.addWidget(add_btn)
        header_layout.addStretch()
        sets_layout.addLayout(header_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(160)
        self.scroll_content = QWidget()
        self.sets_container = QVBoxLayout(self.scroll_content)
        self.sets_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        sets_layout.addWidget(self.scroll)

        main_layout.addWidget(sets_group)
        self.add_set_row("P", "[10; 1000]")
        self.add_set_row("Q", "[27; 2222]")
        control_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Найти НАИБОЛЬШИЙ отрезок A", "Найти НАИМЕНЬШИЙ отрезок A"])
        self.mode_combo.setStyleSheet("font-size: 13px; padding: 5px;")
        control_layout.addWidget(QLabel("Режим:"))
        control_layout.addWidget(self.mode_combo, 1)

        main_layout.addLayout(control_layout)
        self.input_expr = QLineEdit("¬(x∈A)∨(((x∈P)≡(x∈Q))→¬(x∈A))")
        self.input_expr.setPlaceholderText("Пример: (x in P) <= (x in A)")
        self.input_expr.setStyleSheet("font-size: 14px; padding: 5px;")
        main_layout.addWidget(QLabel("Формула (используйте буквы множеств и 'A'):"))
        main_layout.addWidget(self.input_expr)
        solve_btn = QPushButton("РЕШИТЬ")
        solve_btn.setFixedHeight(45)
        solve_btn.setStyleSheet(
            "background-color: #0078d7; color: white; font-size: 16px; font-weight: bold; border-radius: 5px;")
        solve_btn.clicked.connect(self.run_solver)
        main_layout.addWidget(solve_btn)
        self.res_label = QLabel("Введите данные и нажмите Решить")
        self.res_label.setFont(QFont("Arial", 12))
        self.res_label.setStyleSheet("color: #333; margin-top: 10px;")
        main_layout.addWidget(self.res_label)
        self.canvas = NumberLineWidget()
        main_layout.addWidget(self.canvas, 1)

    def add_set_row(self, name="", interval=""):
        row = SetInputWidget(self.sets_container, name, interval)
        self.sets_container.addWidget(row)

    def run_solver(self):
        intervals = {}
        for i in range(self.sets_container.count()):
            widget = self.sets_container.itemAt(i).widget()
            if isinstance(widget, SetInputWidget):
                name, inter_str = widget.get_data()
                if not name or not inter_str: continue
                parsed = LogicSolver.parse_interval(inter_str)
                if parsed:
                    intervals[name] = parsed
                else:
                    QMessageBox.warning(self, "Ошибка", f"Ошибка в интервале {name}")
                    return

        if not intervals:
            QMessageBox.warning(self, "Ошибка", "Нужно задать хотя бы одно множество")
            return

        expr = self.input_expr.text()
        mode_text = self.mode_combo.currentText()
        mode = 'max' if "НАИБОЛЬШИЙ" in mode_text else 'min'

        res = LogicSolver.solve(intervals, expr, mode)

        if isinstance(res, tuple):
            length, best_seg, all_segments = res

            if mode == 'min':
                res_text = f"Наименьшая длина: <b>{length}</b>"
            else:
                res_text = f"Наибольшая длина: <b>{length}</b>"

            self.res_label.setText(f"{res_text} (Отрезок: {best_seg})")
            self.canvas.set_data(intervals, best_seg, all_segments)
        else:
            self.res_label.setText(f"Результат: {res}")
            self.canvas.set_data(intervals, None, [])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())