import sys
from itertools import permutations
from typing import Optional, List, Dict, Tuple

from PySide6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene,
                               QGraphicsItem, QGraphicsEllipseItem,
                               QGraphicsLineItem, QGraphicsTextItem,
                               QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QPushButton, QMessageBox, QLabel,
                               QTextEdit)
from PySide6.QtCore import Qt, QRectF, QLineF, QPointF, Signal, QObject, QThread
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPathStroker, QAction


# ==========================================
# 1. Конфигурация
# ==========================================
class GraphConfig:
    NODE_DIAMETER = 30
    NODE_RADIUS = NODE_DIAMETER / 2
    EDGE_WIDTH = 3
    MIN_DISTANCE = 50

    COLOR_BG = QColor(40, 40, 40)
    COLOR_NODE = QColor(0, 255, 255)  # Голубой (Циан)
    COLOR_NODE_ACTIVE = QColor(255, 0, 255)  # Маджента (выбран для соединения)
    COLOR_EDGE = QColor(200, 200, 200)
    COLOR_TEXT = QColor(0, 0, 0)

    # Цвета для таблицы
    TABLE_BG = QColor(50, 50, 50)
    TABLE_TEXT = QColor(255, 255, 255)
    TABLE_DIAGONAL = QColor(80, 80, 80)

    STYLE_SHEET = f"""
        QTableWidget {{
            background-color: {TABLE_BG.name()};
            color: {TABLE_TEXT.name()};
            gridline-color: #666;
            font-size: 14px;
        }}
        QHeaderView::section {{
            background-color: #333;
            color: white;
            padding: 4px;
            border: 1px solid #666;
        }}
        QLineEdit {{ color: white; background-color: #444; }}
        QTextEdit {{ background-color: #333; color: #0f0; font-family: Consolas; font-size: 13px; }}
    """


# ==========================================
# 2. Элементы Графа (Визуализация)
# ==========================================
class EdgeItem(QGraphicsLineItem):
    def __init__(self, source_item, dest_item):
        super().__init__()
        self.source = source_item
        self.dest = dest_item
        self.setPen(QPen(GraphConfig.COLOR_EDGE, GraphConfig.EDGE_WIDTH))
        self.setZValue(0)  # Ребра под узлами
        self.update_geometry()

    def update_geometry(self):
        line = QLineF(self.source.scenePos(), self.dest.scenePos())
        self.setLine(line)

    def shape(self):
        # Расширяем область клика, чтобы по тонкой линии было легче попасть
        path = super().shape()
        stroker = QPainterPathStroker()
        stroker.setWidth(10)
        return stroker.createStroke(path)


class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name: str, x: float, y: float):
        rect = QRectF(-GraphConfig.NODE_RADIUS, -GraphConfig.NODE_RADIUS,
                      GraphConfig.NODE_DIAMETER, GraphConfig.NODE_DIAMETER)
        super().__init__(rect)
        self.name = name
        self.edges: List[EdgeItem] = []
        self.setBrush(QBrush(GraphConfig.COLOR_NODE))
        self.setPen(QPen(Qt.NoPen))
        self.setPos(x, y)
        self.setZValue(1)  # Узлы над ребрами
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self._create_label(name)

    def _create_label(self, text: str):
        self.label = QGraphicsTextItem(text, self)
        self.label.setDefaultTextColor(GraphConfig.COLOR_TEXT)
        font = self.label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.label.setFont(font)
        # Центрирование текста внутри круга
        br = self.label.boundingRect()
        self.label.setPos(-br.width() / 2, -br.height() / 2)

    def set_highlighted(self, is_active: bool):
        color = GraphConfig.COLOR_NODE_ACTIVE if is_active else GraphConfig.COLOR_NODE
        self.setBrush(QBrush(color))

    def add_connection(self, edge: EdgeItem):
        self.edges.append(edge)

    def remove_connection(self, edge: EdgeItem):
        if edge in self.edges:
            self.edges.remove(edge)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged and self.scene():
            for edge in self.edges:
                edge.update_geometry()
        return super().itemChange(change, value)


# ==========================================
# 3. Логика Графа (ИСПРАВЛЕНО)
# ==========================================
class ChainBuilder:
    def __init__(self):
        self.active_node: Optional[NodeItem] = None

    def start_or_continue(self, node: NodeItem) -> Optional[NodeItem]:
        prev_node = self.active_node

        # Если кликнули на тот же узел — ничего не делаем (или сбрасываем)
        if self.active_node == node:
            return None

        if self.active_node:
            self.active_node.set_highlighted(False)

        self.active_node = node
        self.active_node.set_highlighted(True)
        return prev_node

    def reset(self):
        if self.active_node:
            self.active_node.set_highlighted(False)
            self.active_node = None


class GraphManager(QObject):
    node_count_changed = Signal(int)

    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene

    def reset(self):
        self.scene.clear()
        self.node_count_changed.emit(0)

    def generate_name(self) -> str:
        """
        Ищет первое свободное имя в алфавитной последовательности (A, B, C...).
        Если B удалено, вернет B.
        """
        # Собираем все занятые имена
        existing_names = set()
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                existing_names.add(item.name)

        counter = 0
        while True:
            # Генерация имени: 0->A, 1->B, ..., 26->AA
            n = counter
            name = ""
            while n >= 0:
                name = chr(ord('A') + (n % 26)) + name
                n = n // 26 - 1

            if name not in existing_names:
                return name
            counter += 1

    def create_node(self, pos: QPointF, name: str = None) -> NodeItem:
        if name is None:
            name = self.generate_name()

        node = NodeItem(name, pos.x(), pos.y())
        self.scene.addItem(node)
        self.node_count_changed.emit(self.get_node_count())
        return node

    def create_edge(self, u: NodeItem, v: NodeItem):
        if u == v: return
        # Проверка на дубликаты
        for edge in u.edges:
            if (edge.source == u and edge.dest == v) or (edge.source == v and edge.dest == u):
                return
        edge = EdgeItem(u, v)
        self.scene.addItem(edge)
        u.add_connection(edge)
        v.add_connection(edge)

    def delete_item(self, item: QGraphicsItem):
        if isinstance(item, NodeItem):
            # Удаляем все ребра, связанные с узлом
            for edge in list(item.edges):
                self.delete_item(edge)
            self.scene.removeItem(item)
            self.node_count_changed.emit(self.get_node_count())
        elif isinstance(item, EdgeItem):
            item.source.remove_connection(item)
            item.dest.remove_connection(item)
            self.scene.removeItem(item)

    def get_node_count(self) -> int:
        return sum(1 for item in self.scene.items() if isinstance(item, NodeItem))

    def is_position_valid(self, pos: QPointF) -> bool:
        for item in self.scene.items():
            if isinstance(item, NodeItem):
                distance = QLineF(pos, item.scenePos()).length()
                if distance < GraphConfig.MIN_DISTANCE:
                    return False
        return True

    def get_adjacency_matrix(self) -> Tuple[List[List[bool]], List[str]]:
        nodes = [item for item in self.scene.items() if isinstance(item, NodeItem)]
        # Сортируем по имени, чтобы порядок был A, B, C... даже если создавали хаотично
        nodes.sort(key=lambda x: x.name)

        count = len(nodes)
        matrix = [[False] * count for _ in range(count)]
        node_map = {node: i for i, node in enumerate(nodes)}

        for node in nodes:
            u_idx = node_map[node]
            for edge in node.edges:
                other = edge.dest if edge.source == node else edge.source
                v_idx = node_map.get(other)
                if v_idx is not None:
                    matrix[u_idx][v_idx] = True
                    matrix[v_idx][u_idx] = True

        return matrix, [n.name for n in nodes]


# ==========================================
# 4. Таблица (Виджет)
# ==========================================
class DigitalMatrixWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(0)
        self.setRowCount(0)
        self.setStyleSheet(GraphConfig.STYLE_SHEET)
        self.itemChanged.connect(self.on_item_changed)

        self.horizontalHeader().setDefaultSectionSize(40)
        self.verticalHeader().setDefaultSectionSize(40)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def update_size(self, node_count: int):
        current_rows = self.rowCount()
        if current_rows == node_count:
            return

        self.setRowCount(node_count)
        self.setColumnCount(node_count)
        headers = [str(i + 1) for i in range(node_count)]
        self.setHorizontalHeaderLabels(headers)
        self.setVerticalHeaderLabels(headers)

        self.blockSignals(True)
        for r in range(node_count):
            for c in range(node_count):
                item = self.item(r, c)
                if not item:
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(r, c, item)

                if r == c:
                    item.setFlags(Qt.ItemIsEnabled)
                    item.setBackground(QBrush(GraphConfig.TABLE_DIAGONAL))
                    item.setText("-")
                else:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable)
                    item.setBackground(QBrush(GraphConfig.TABLE_BG))
        self.blockSignals(False)

    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        if row == col: return
        text = item.text()

        # Обеспечиваем симметрию матрицы
        self.blockSignals(True)
        symmetric_item = self.item(col, row)
        if symmetric_item:
            symmetric_item.setText(text)
        self.blockSignals(False)

    def get_data(self) -> List[List[str]]:
        rows = self.rowCount()
        data = []
        for r in range(rows):
            row_data = []
            for c in range(rows):
                item = self.item(r, c)
                text = item.text().strip() if item else ""
                if text == "0" or text == "-": text = ""
                row_data.append(text)
            data.append(row_data)
        return data


# ==========================================
# 5. Логика Решения
# ==========================================
class SolverWorker(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, digital_matrix_str, graph_matrix_bool, letter_names):
        super().__init__()
        self.digital = digital_matrix_str
        self.graph_bool = graph_matrix_bool
        self.headers = letter_names

    def run(self):
        n = len(self.digital)
        if len(self.graph_bool) != n:
            self.finished_signal.emit(False, "Ошибка: Количество вершин в таблице и графе не совпадает!")
            return

        perms = permutations(range(n))
        results = []
        limit_counter = 0
        MAX_CHECKS = 2_000_000

        for perm in perms:
            limit_counter += 1
            if limit_counter > MAX_CHECKS:
                self.finished_signal.emit(False, "Слишком сложный граф (превышен лимит вычислений).")
                return

            if self.check_structural_isomorphism(perm):
                mapping = {}
                for digit_idx in range(n):
                    digit_name = str(digit_idx + 1)
                    letter_idx = perm[digit_idx]
                    letter_name = self.headers[letter_idx]
                    mapping[digit_name] = letter_name
                results.append(mapping)

        if results:
            text = f"Найдено вариантов: {len(results)}\n"
            text += "-" * 30 + "\n"
            for idx, mapping in enumerate(results, 1):
                text += f"ВАРИАНТ {idx}:\n"
                sorted_map = sorted(mapping.items(), key=lambda x: int(x[0]))
                pairs = [f"{k} -> {v}" for k, v in sorted_map]
                # Форматирование вывода в колонки
                for i in range(0, len(pairs), 4):
                    text += ",  ".join(pairs[i:i + 4]) + "\n"
                text += "\n"
            self.finished_signal.emit(True, text)
        else:
            self.finished_signal.emit(False,
                                      "Решения не найдены.\nПроверьте, правильно ли заполнены связи\nв таблице и на графе.")

    def check_structural_isomorphism(self, p):
        """
        Проверяем, соответствует ли структура связей при перестановке p.
        digital[i][j] - связь в таблице (цифры)
        graph[p[i]][p[j]] - связь в графе (буквы) после перестановки
        """
        n = len(self.digital)
        for i in range(n):
            for j in range(i + 1, n):
                has_digit_link = bool(self.digital[i][j])
                has_graph_link = self.graph_bool[p[i]][p[j]]

                if has_digit_link != has_graph_link:
                    return False
        return True


# ==========================================
# 6. Сцена Графа
# ==========================================
class GraphScene(QGraphicsScene):
    def __init__(self, manager: GraphManager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.chain_builder = ChainBuilder()
        self.setBackgroundBrush(QBrush(GraphConfig.COLOR_BG))
        self.setSceneRect(0, 0, 800, 600)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self.chain_builder.reset()
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        pos = event.scenePos()
        item = self.itemAt(pos, self.views()[0].transform())

        # Если кликнули по тексту (букве), переключаемся на родителя (сам узел)
        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ShiftModifier:
                if isinstance(item, NodeItem):
                    # Соединение узлов
                    prev_node = self.chain_builder.start_or_continue(item)
                    if prev_node:
                        self.manager.create_edge(prev_node, item)
                        self.chain_builder.reset()
                    event.accept()
                    return
                else:
                    self.chain_builder.reset()
            else:
                self.chain_builder.reset()

            if item is None:
                # Создание нового узла на пустом месте
                if self.manager.is_position_valid(pos):
                    self.manager.create_node(pos)
                event.accept()
                return

            super().mousePressEvent(event)

        elif event.button() == Qt.RightButton:
            # Удаление
            self.chain_builder.reset()
            if item:
                self.manager.delete_item(item)
                event.accept()


# ==========================================
# 7. Главное окно
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тренажер: Сопоставление Графа и Таблицы")
        self.resize(1300, 750)

        self.scene = QGraphicsScene()
        # Сначала создаем менеджер, потом сцену, передавая менеджер
        self.graph_manager = GraphManager(self.scene)
        self.scene = GraphScene(self.graph_manager, self)
        self.graph_manager.scene = self.scene  # Привязываем сцену обратно

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)

        self.digital_matrix = DigitalMatrixWidget()
        self.graph_manager.node_count_changed.connect(self.digital_matrix.update_size)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        # --- Левая панель (Таблица) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        lbl_table = QLabel("<b>1. Цифровая Таблица (из задания)</b>")
        lbl_table.setStyleSheet("font-size: 14px; color: #ddd;")
        left_layout.addWidget(lbl_table)

        lbl_help_table = QLabel("Введите длины дорог. Пустые ячейки = нет дороги.")
        lbl_help_table.setStyleSheet("color: #888; font-size: 11px;")
        left_layout.addWidget(lbl_help_table)

        left_layout.addWidget(self.digital_matrix)

        self.btn_solve = QPushButton("Найти соответствие")
        self.btn_solve.setStyleSheet("""
            QPushButton { background-color: #2a82da; color: white; height: 45px; font-weight: bold; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #3a92ea; }
            QPushButton:disabled { background-color: #555; color: #888; }
        """)
        self.btn_solve.clicked.connect(self.run_solver)
        left_layout.addWidget(self.btn_solve)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        self.result_area.setPlaceholderText("Здесь появится результат...")
        left_layout.addWidget(self.result_area)

        # --- Правая панель (Граф) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        lbl_graph = QLabel("<b>2. Буквенный Граф (рисунок)</b>")
        lbl_graph.setStyleSheet("font-size: 14px; color: #ddd;")
        right_layout.addWidget(lbl_graph)

        lbl_help_graph = QLabel("ЛКМ: создать узел. Shift+ЛКМ по двум узлам: соединить. ПКМ: удалить.")
        lbl_help_graph.setStyleSheet("color: #aaa; font-size: 12px;")
        right_layout.addWidget(lbl_help_graph)

        right_layout.addWidget(self.view)

        main_layout.addWidget(left_widget, 4)
        main_layout.addWidget(right_widget, 6)

        self.setCentralWidget(central_widget)
        self.create_menu()
        self.solver_worker = None

    def create_menu(self):
        menu = self.menuBar()
        file_menu = menu.addMenu("Меню")
        clear_action = QAction("Очистить всё", self)
        clear_action.triggered.connect(self.clear_all)
        file_menu.addAction(clear_action)

    def clear_all(self):
        self.graph_manager.reset()
        self.digital_matrix.update_size(0)
        self.result_area.clear()

    def run_solver(self):
        digital_data = self.digital_matrix.get_data()
        graph_bool_matrix, letter_names = self.graph_manager.get_adjacency_matrix()

        if len(digital_data) < 2:
            QMessageBox.warning(self, "Внимание", "Создайте хотя бы 2 узла для поиска решения.")
            return

        self.btn_solve.setEnabled(False)
        self.result_area.setText("Вычисление...")
        self.result_area.setStyleSheet("color: #FFFF00; background-color: #333;")

        self.solver_worker = SolverWorker(digital_data, graph_bool_matrix, letter_names)
        self.solver_worker.finished_signal.connect(self.on_solved)
        self.solver_worker.start()

    def on_solved(self, success, text):
        self.btn_solve.setEnabled(True)
        if success:
            self.result_area.setStyleSheet("color: #00FF00; background-color: #333;")
        else:
            self.result_area.setStyleSheet("color: #FF5555; background-color: #333;")
        self.result_area.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Настройка темной темы
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.WindowText, Qt.white)
    palette.setColor(palette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(palette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ToolTipBase, Qt.white)
    palette.setColor(palette.ColorRole.ToolTipText, Qt.white)
    palette.setColor(palette.ColorRole.Text, Qt.white)
    palette.setColor(palette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(palette.ColorRole.ButtonText, Qt.white)
    palette.setColor(palette.ColorRole.BrightText, Qt.red)
    palette.setColor(palette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(palette.ColorRole.HighlightedText, Qt.black)
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())