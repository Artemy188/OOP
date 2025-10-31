import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QSpinBox, QCheckBox
)
import functools  # Для functools.lru_cache


class GameSolverBackend:
    def __init__(self):
        self.f_memo = {}

    def parse_moves(self, moves_str, is_increasing_game):
        moves = []
        for part in moves_str.split(','):
            part = part.strip()
            if not part:
                continue

            if is_increasing_game:
                if part.startswith('+'):
                    n = int(part[1:])
                    moves.append(lambda s, val=n: s + val)
                elif part.startswith('*'):
                    n = int(part[1:])
                    moves.append(lambda s, val=n: s * val)
                else:
                    raise ValueError(f"Неверный формат хода: '{part}'. Используйте +N или *N для увеличения кучи.")
            else:
                if part.startswith('-'):
                    n = int(part[1:])
                    moves.append(lambda s, val=n: s - val)
                elif part.startswith('/'):
                    n = int(part[1:])
                    moves.append(lambda s, val=n: s // val if s // val >= 1 else -1)
                else:
                    raise ValueError(f"Неверный формат хода: '{part}'. Используйте -N или /N для уменьшения кучи.")
        return moves

    def get_next_states(self, s, moves, is_increasing_game):
        states = []
        for move in moves:
            next_s = move(s)
            if not is_increasing_game and next_s < 1:
                continue
            if is_increasing_game and next_s < 1:
                continue

            states.append(next_s)
        return states
    def f(self, s, m, s_end, game_moves, is_increasing_game):
        if (s, m) in self.f_memo:
            return self.f_memo[(s, m)]


        if is_increasing_game:
            if s >= s_end:
                result = (m % 2 == 0)
                self.f_memo[(s, m)] = result
                return result
        else:
            if s <= s_end:
                result = (m % 2 == 0)
                self.f_memo[(s, m)] = result
                return result

        if m == 0:
            self.f_memo[(s, m)] = False
            return False

        next_states = self.get_next_states(s, game_moves, is_increasing_game)


        if not next_states:
            self.f_memo[(s, m)] = False
            return False

        h = [self.f(next_s, m - 1, s_end, game_moves, is_increasing_game) for next_s in next_states]

        result = any(h) if m % 2 else all(h)
        self.f_memo[(s, m)] = result
        return result

    def solve_task_19(self, s_end, moves, s_range, is_increasing_game):
        self.f_memo = {}
        results = []
        for s in s_range:
            if not self.f(s, 1, s_end, moves, is_increasing_game) and self.f(s, 2, s_end, moves, is_increasing_game):
                results.append(s)
        return min(results) if results else None

    def solve_task_20(self, s_end, moves, s_range, is_increasing_game):
        self.f_memo = {}
        results = []
        for s in s_range:
            if not self.f(s, 1, s_end, moves, is_increasing_game) and self.f(s, 3, s_end, moves, is_increasing_game):
                results.append(s)
                if len(results) == 2:
                    break
        return results if results else None

    def solve_task_21(self, s_end, moves, s_range, is_increasing_game):
        self.f_memo = {}
        results = []
        for s in s_range:
            if not self.f(s, 1, s_end, moves, is_increasing_game):
                if not self.f(s, 2, s_end, moves, is_increasing_game):
                    if self.f(s, 4, s_end, moves, is_increasing_game):
                        results.append(s)
        return min(results) if results else None


class EGESolverApp(QWidget):
    def __init__(self):
        super().__init__()
        self.backend = GameSolverBackend()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ЕГЭ Задачи 19–21: Камни")
        self.resize(700, 600)
        layout = QVBoxLayout()

        game_group = QGroupBox("Параметры игры")
        game_layout = QVBoxLayout()

        self.increasing_game_checkbox = QCheckBox("Куча увеличивается (S ≥ S_end)")
        self.increasing_game_checkbox.setChecked(True)  # По умолчанию для вашего теста
        self.increasing_game_checkbox.stateChanged.connect(self.update_default_values)
        game_layout.addWidget(self.increasing_game_checkbox)

        s_end_label = QLabel("Порог (игра заканчивается при S {>= или <=} S_end):")
        self.s_end_input = QSpinBox()
        self.s_end_input.setRange(1, 1000)
        game_layout.addLayout(self.create_horizontal_layout(s_end_label, self.s_end_input))

        moves_label = QLabel("Ходы (через запятую):")
        self.moves_input = QLineEdit()
        game_layout.addLayout(self.create_horizontal_layout(moves_label, self.moves_input))

        game_group.setLayout(game_layout)
        layout.addWidget(game_group)

        range_group = QGroupBox("Диапазон начальных значений S")
        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel("От:"))
        self.s_from = QSpinBox()
        self.s_from.setRange(1, 10000)
        range_layout.addWidget(self.s_from)

        range_layout.addWidget(QLabel("До:"))
        self.s_to = QSpinBox()
        self.s_to.setRange(1, 10000)
        range_layout.addWidget(self.s_to)

        range_group.setLayout(range_layout)
        layout.addWidget(range_group)

        btn_layout = QHBoxLayout()
        self.btn_19 = QPushButton("Решить задачу 19")
        self.btn_19.clicked.connect(self.run_task_19)
        btn_layout.addWidget(self.btn_19)

        self.btn_20 = QPushButton("Решить задачу 20")
        self.btn_20.clicked.connect(self.run_task_20)
        btn_layout.addWidget(self.btn_20)

        self.btn_21 = QPushButton("Решить задачу 21")
        self.btn_21.clicked.connect(self.run_task_21)
        btn_layout.addWidget(self.btn_21)
        layout.addLayout(btn_layout)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.update_default_values()  # Установить начальные значения при старте

    def create_horizontal_layout(self, label, widget):
        h_layout = QHBoxLayout()
        h_layout.addWidget(label)
        h_layout.addWidget(widget)
        return h_layout

    def update_default_values(self):
        is_increasing = self.increasing_game_checkbox.isChecked()
        if is_increasing:
            self.s_end_input.setValue(471)  # Ваш тестовый порог
            self.moves_input.setText("+4,+7,*4")  # Ваши тестовые ходы
            self.s_from.setValue(1)
            self.s_to.setValue(470)  # S < S_end для начала игры
        else:
            self.s_end_input.setValue(30)
            self.moves_input.setText("-3,-5,/4")
            self.s_from.setValue(31)
            self.s_to.setValue(200)

    def get_params(self):
        try:
            s_end = self.s_end_input.value()
            is_increasing_game = self.increasing_game_checkbox.isChecked()
            moves = self.backend.parse_moves(self.moves_input.text(), is_increasing_game)
            s_range = range(self.s_from.value(), self.s_to.value() + 1)
            return s_end, moves, s_range, is_increasing_game
        except Exception as e:
            self.output.setText(f"Ошибка ввода: {e}")
            return None, None, None, None

    def run_task_19(self):
        self.output.clear()
        s_end, moves, s_range, is_increasing_game = self.get_params()
        if s_end is None:
            return
        result = self.backend.solve_task_19(s_end, moves, s_range, is_increasing_game)
        if result is not None:
            self.output.append(f"Задача 19: {result}")
        else:
            self.output.append("Задача 19: решение не найдено.")

    def run_task_20(self):
        self.output.clear()
        s_end, moves, s_range, is_increasing_game = self.get_params()
        if s_end is None:
            return
        results = self.backend.solve_task_20(s_end, moves, s_range, is_increasing_game)
        if results and len(results) == 2:
            self.output.append(f"Задача 20: {results[0]} {results[1]}")
        elif results and len(results) == 1:
            self.output.append(f"Задача 20: найдено только одно значение: {results[0]}")
        else:
            self.output.append("Задача 20: решение не найдено.")

    def run_task_21(self):
        self.output.clear()
        s_end, moves, s_range, is_increasing_game = self.get_params()
        if s_end is None:
            return
        result = self.backend.solve_task_21(s_end, moves, s_range, is_increasing_game)
        if result is not None:
            self.output.append(f"Задача 21: {result}")
        else:
            self.output.append("Задача 21: решение не найдено.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EGESolverApp()
    window.show()
    sys.exit(app.exec())