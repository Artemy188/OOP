import sys
import abc
from abc import ABC, abstractmethod
from typing import Dict, Any, List

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (QAction, QColor, QPen, QBrush, QPainter,
                         QUndoCommand, QUndoStack, QImage)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
                             QToolBar, QColorDialog, QGraphicsRectItem,
                             QGraphicsEllipseItem, QGraphicsItem,
                             QGraphicsItemGroup, QFileDialog)




class Serializable(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass


class GraphicsCompositeMeta(type(QGraphicsItemGroup), abc.ABCMeta):
    pass




class AddCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, item: QGraphicsItem):
        super().__init__("Добавить объект")
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.item.setSelected(False)
        self.scene.removeItem(self.item)


class DeleteCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: List[QGraphicsItem]):
        super().__init__("Удалить")
        self.scene = scene
        self.items = items

    def redo(self):
        for item in self.items:
            item.setSelected(False)
            self.scene.removeItem(item)

    def undo(self):
        for item in self.items:
            self.scene.addItem(item)


class MoveCommand(QUndoCommand):
    def __init__(self, items_map: Dict[QGraphicsItem, QPointF]):
        super().__init__("Перемещение")
        self.items_map = items_map
        self.new_positions = {item: item.pos() for item in items_map.keys()}

    def redo(self):
        for item, pos in self.new_positions.items():
            item.setPos(pos)

    def undo(self):
        for item, pos in self.items_map.items():
            item.setPos(pos)


class GroupCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: List[QGraphicsItem]):
        super().__init__("Группировка")
        self.scene = scene
        self.items = items
        self.group = ShapeGroup()

    def redo(self):
        self.scene.addItem(self.group)
        for item in self.items:
            item.setSelected(False)
            self.group.addToGroup(item)
        self.scene.clearSelection()
        self.group.setSelected(True)

    def undo(self):
        self.group.setSelected(False)
        for item in self.items:
            self.group.removeFromGroup(item)
        self.scene.removeItem(self.group)
        for item in self.items:
            item.setSelected(True)


class ChangeColorCommand(QUndoCommand):
    def __init__(self, items: List[QGraphicsItem], new_color: QColor):
        super().__init__("Изменить цвет")
        self.new_brush = QBrush(new_color)
        self.affected_items = []

        for item in items:
            self._collect_shapes(item)

    def _collect_shapes(self, item):
        if isinstance(item, QGraphicsItemGroup):
            for child in item.childItems():
                self._collect_shapes(child)
        # Вместо абстрактного класса проверяем наличие метода setBrush
        elif hasattr(item, 'setBrush') and hasattr(item, 'brush'):
            self.affected_items.append((item, item.brush()))

    def redo(self):
        for item, _ in self.affected_items:
            item.setBrush(self.new_brush)

    def undo(self):
        for item, old_brush in self.affected_items:
            item.setBrush(old_brush)



class Tool(ABC):
    @abstractmethod
    def mousePress(self, event, editor): pass

    @abstractmethod
    def mouseMove(self, event, editor): pass

    @abstractmethod
    def mouseRelease(self, event, editor): pass


class SelectTool(Tool):
    def __init__(self):
        self.initial_positions = {}

    def mousePress(self, event, editor):
        self.initial_positions = {item: item.pos() for item in editor.scene().selectedItems()}
        QGraphicsView.mousePressEvent(editor, event)

    def mouseMove(self, event, editor):
        QGraphicsView.mouseMoveEvent(editor, event)

    def mouseRelease(self, event, editor):
        QGraphicsView.mouseReleaseEvent(editor, event)
        if self.initial_positions:
            moved = any(item.pos() != old_pos for item, old_pos in self.initial_positions.items())
            if moved:
                editor.undo_stack.push(MoveCommand(self.initial_positions))
        self.initial_positions = {}


class CreationTool(Tool):
    def __init__(self, shape_type: str):
        self.shape_type = shape_type
        self.temp_item = None

    def mousePress(self, event, editor):
        editor.scene().clearSelection()
        editor.start_point = editor.mapToScene(event.pos())
        pen = QPen(Qt.GlobalColor.black, 2)
        brush = QBrush(editor.current_color)

        if self.shape_type == "rect":
            self.temp_item = QGraphicsRectItem()
        elif self.shape_type == "ellipse":
            self.temp_item = QGraphicsEllipseItem()

        if self.temp_item:
            self.temp_item.setPen(pen)
            self.temp_item.setBrush(brush)
            editor.scene().addItem(self.temp_item)

    def mouseMove(self, event, editor):
        if self.temp_item:
            current_point = editor.mapToScene(event.pos())
            rect = QRectF(editor.start_point, current_point).normalized()
            self.temp_item.setRect(rect)

    def mouseRelease(self, event, editor):
        if self.temp_item:
            item = self.temp_item
            editor.scene().removeItem(item)
            item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                          QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            editor.undo_stack.push(AddCommand(editor.scene(), item))
            self.temp_item = None


class ShapeGroup(QGraphicsItemGroup, Serializable, metaclass=GraphicsCompositeMeta):
    def __init__(self):
        super().__init__()
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

    def to_dict(self) -> Dict[str, Any]:
        return {"type": "group", "pos_x": self.x(), "pos_y": self.y()}



class VectorEditor(QGraphicsView):
    def __init__(self, scene, undo_stack):
        super().__init__(scene)
        self.undo_stack = undo_stack
        self.current_tool = SelectTool()
        self.current_color = QColor("#3498db")
        self.start_point = QPointF()

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

    def set_tool(self, tool: Tool):
        self.current_tool = tool
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag if isinstance(tool, SelectTool)
                         else QGraphicsView.DragMode.NoDrag)

    def mousePressEvent(self, event):
        self.current_tool.mousePress(event, self)

    def mouseMoveEvent(self, event):
        self.current_tool.mouseMove(event, self)

    def mouseReleaseEvent(self, event):
        self.current_tool.mouseRelease(event, self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
        else:
            super().keyPressEvent(event)

    def delete_selected(self):
        items = self.scene().selectedItems()
        if items:
            self.undo_stack.push(DeleteCommand(self.scene(), items))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Vector Editor Pro")
        self.resize(1100, 800)

        self.undo_stack = QUndoStack(self)
        self.scene = QGraphicsScene(0, 0, 2000, 2000)
        self.view = VectorEditor(self.scene, self.undo_stack)
        self.setCentralWidget(self.view)

        self._create_toolbar()

    def _create_toolbar(self):
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        actions = [
            ("Курсор", lambda: self.view.set_tool(SelectTool())),
            ("Прямоугольник", lambda: self.view.set_tool(CreationTool("rect"))),
            ("Эллипс", lambda: self.view.set_tool(CreationTool("ellipse"))),
        ]
        for name, callback in actions:
            act = QAction(name, self)
            act.triggered.connect(callback)
            toolbar.addAction(act)

        toolbar.addSeparator()
        color_act = QAction("Цвет заливки", self)
        color_act.triggered.connect(self.choose_color)
        toolbar.addAction(color_act)

        toolbar.addSeparator()
        toolbar.addAction(self.undo_stack.createUndoAction(self, "Назад"))
        toolbar.addAction(self.undo_stack.createRedoAction(self, "Вперед"))

        toolbar.addSeparator()
        group_act = QAction("Группировать", self)
        group_act.triggered.connect(self.group_items)
        toolbar.addAction(group_act)

        ungroup_act = QAction("Разгруппировать", self)
        ungroup_act.triggered.connect(self.ungroup_items)
        toolbar.addAction(ungroup_act)

        toolbar.addSeparator()
        del_act = QAction("Удалить", self)
        del_act.triggered.connect(self.view.delete_selected)
        toolbar.addAction(del_act)

    def choose_color(self):
        selected_items = self.scene.selectedItems()
        initial_color = self.view.current_color


        if selected_items:
            item = selected_items[0]
            if hasattr(item, 'brush'):
                initial_color = item.brush().color()
            elif isinstance(item, QGraphicsItemGroup) and item.childItems():
                child = item.childItems()[0]
                if hasattr(child, 'brush'):
                    initial_color = child.brush().color()

        color = QColorDialog.getColor(initial_color, self, "Выберите цвет")
        if color.isValid():
            if selected_items:
                self.undo_stack.push(ChangeColorCommand(selected_items, color))
            self.view.current_color = color

    def group_items(self):
        items = self.scene.selectedItems()
        if len(items) > 1:
            self.undo_stack.push(GroupCommand(self.scene, items))

    def ungroup_items(self):
        items = self.scene.selectedItems()
        for item in items:
            if isinstance(item, QGraphicsItemGroup):
                children = item.childItems()
                item.setSelected(False)
                self.scene.destroyItemGroup(item)
                for child in children:
                    child.setSelected(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())