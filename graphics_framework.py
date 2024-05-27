from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
from undo_commands import *
from OpenGL.GL import *
from OpenGL.GLU import *
import xml.etree.ElementTree as ET
import time
import json

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas,
                 button,
                 button2,
                 smooth_btn,
                 button4,
                 add_canvas_btn,
                 select_btn,
                 scale_btn,
                 pan_btn,
                 zoom_spin):
        super().__init__()
        self.points = []

        # Set flags
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Set widgets
        self.button = button
        self.button2 = button2
        self.pen_btn = smooth_btn
        self.text_btn = button4
        self.add_canvas_btn = add_canvas_btn
        self.select_btn = select_btn
        self.scale_btn = scale_btn
        self.pan_btn = pan_btn

        # Items
        self.canvas = canvas
        self.temp_path_item = None
        self.temp_canvas = None
        self.pen = None
        self.stroke_fill = None
        self.font = None
        self.layer_height = None
        self.path = None
        self.last_point = None

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 100]
        self.zoom_spin = zoom_spin

        # Canvas item
        self.canvas_item = None

    def update_pen(self, pen):
        self.pen = pen

    def update_stroke_fill_color(self, brush):
        self.stroke_fill = brush

    def update_font(self, font, color):
        self.font = font
        self.font_color = color

    def disable_item_flags(self):
        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsMovable, False)
                item.setFlag(QGraphicsItem.ItemIsSelectable, False)

    def disable_item_movement(self):
        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsMovable, False)

    def enable_item_flags(self):
        for item in self.scene().items():
            if isinstance(item, CanvasItem):
                pass

            elif isinstance(item, CanvasTextItem):
                pass

            else:
                item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                item.setFlag(QGraphicsItem.ItemIsMovable, True)

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.button.isChecked():
            self.on_path_draw_start(event)

        elif self.pen_btn.isChecked():
            self.on_smooth_path_draw_start(event)
            self.disable_item_flags()

        elif self.button2.isChecked():
            self.on_label_start(event)
            self.disable_item_flags()

        elif self.text_btn.isChecked():
            self.on_add_text(event)
            self.disable_item_movement()
            super().mousePressEvent(event)

        elif self.scale_btn.isChecked():
            self.on_scale_start(event)
            self.disable_item_movement()
            super().mousePressEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.on_add_canvas_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        else:
            super().mousePressEvent(event)

        self.on_add_canvas()
        
    def mouseMoveEvent(self, event):
        point = event.pos()
        p = self.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)
        QToolTip.showText(p, f'''x: {int(p.x())} 
y: {int(p.y())}''')

        if self.button.isChecked():
            self.on_path_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pen_btn.isChecked():
            self.on_smooth_path_draw_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)
            
        elif self.text_btn.isChecked():
            super().mouseMoveEvent(event)

        elif self.button2.isChecked():
            self.on_label(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.scale_btn.isChecked():
            self.on_scale(event)
            self.disable_item_movement()
            super().mouseMoveEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.on_add_canvas_drag(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pan_btn.isChecked():
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.button.isChecked():
            self.on_path_draw_end(event)

        elif self.pen_btn.isChecked():
            self.on_smooth_path_draw_end(event)
            
        elif self.text_btn.isChecked():
            super().mouseReleaseEvent(event)

        elif self.button2.isChecked():
            self.on_label_end(event)

        elif self.scale_btn.isChecked():
            self.on_scale_end(event)
            super().mouseReleaseEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.on_add_canvas_end(event)
            super().mouseReleaseEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_end(event)
            super().mouseReleaseEvent(event)

        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        self.zoom_spin.blockSignals(True)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # Calculate zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # Calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        # Deal with clamping!
        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

        self.zoom_spin.setValue(int(zoomFactor * 100))
        self.zoom_spin.blockSignals(False)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            if url.toLocalFile().endswith('.svg'):
                item = CustomSvgItem(url.toLocalFile())
                item.store_filename(url.toLocalFile())
                item.setToolTip('Imported SVG')

            else:
                pixmap = QPixmap(url.toLocalFile())
                item = CustomPixmapItem(pixmap)
                item.store_filename(url.toLocalFile())
                item.setToolTip('Imported Bitmap')

            # Set default attributes
            item.setPos(self.mapToScene(event.pos()) - item.boundingRect().center())
            item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
            item.setZValue(0)

            # Add item to scene
            add_command = AddItemCommand(self.canvas, item)
            self.canvas.addCommand(add_command)
            self.canvas.update()

    def fitInView(self, *args, **kwargs):
        super().fitInView(*args, **kwargs)
        self.applyZoom()

    def applyZoom(self):
        # Reset the transformation and apply the stored zoom level
        self.resetTransform()
        zoomFactor = self.zoomInFactor ** (self.zoom - 10)  # 15 is the initial zoom level
        self.scale(zoomFactor, zoomFactor)

    def on_path_draw_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create a new path
            self.path = QPainterPath()
            self.path.setFillRule(Qt.WindingFill)
            self.path.moveTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())

            # Set drag mode
            self.setDragMode(QGraphicsView.NoDrag)

        super().mousePressEvent(event)

    def on_path_draw(self, event):
        # Check the buttons
        if event.buttons() == Qt.LeftButton:
            self.path.lineTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())
            
            # Remove temporary path if it exists
            if self.temp_path_item:
                self.canvas.removeItem(self.temp_path_item)

            # Load temporary path as QGraphicsItem to view it while drawing
            self.temp_path_item = CustomPathItem(self.path)
            self.temp_path_item.setPen(self.pen)
            self.temp_path_item.setBrush(self.stroke_fill)
            self.temp_path_item.setZValue(0)
            self.canvas.addItem(self.temp_path_item)

            self.canvas.update()

    def on_path_draw_end(self, event):
        # Check the buttons
        if event.button() == Qt.LeftButton:
            self.path.lineTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())

            # Check if there is a temporary path (if so, remove it now)
            if self.temp_path_item:
                self.canvas.removeItem(self.temp_path_item)

            self.canvas.update()

            # Load main path as QGraphicsItem
            path_item = CustomPathItem(self.path)
            path_item.setPen(self.pen)
            path_item.setZValue(0)
            path_item.setBrush(self.stroke_fill)

            # Add item
            add_command = AddItemCommand(self.canvas, path_item)
            self.canvas.addCommand(add_command)

            # Set Flags
            path_item.setFlag(QGraphicsItem.ItemIsSelectable)
            path_item.setFlag(QGraphicsItem.ItemIsMovable)

            # Set Tooltip
            path_item.setToolTip('Path')

    def on_smooth_path_draw_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create a new path
            self.path = QPainterPath()
            self.path.setFillRule(Qt.WindingFill)
            self.path.moveTo(self.mapToScene(event.pos()))
            self.last_point = self.mapToScene(event.pos())

            # Set drag mode
            self.setDragMode(QGraphicsView.NoDrag)

            super().mousePressEvent(event)

    def on_smooth_path_draw_draw(self, event):
        if self.path is not None:
            # Check the buttons
            if event.buttons() == Qt.LeftButton:
                self.path.lineTo(self.mapToScene(event.pos()))
                self.last_point = self.mapToScene(event.pos())

                # Remove temporary path if it exists
                if self.temp_path_item is not None:
                    self.canvas.removeItem(self.temp_path_item)

                # Load temporary path as QGraphicsItem to view it while drawing
                self.path.setFillRule(Qt.WindingFill)
                self.temp_path_item = CustomPathItem(self.path)
                self.temp_path_item.path().setFillRule(Qt.WindingFill)
                self.temp_path_item.setPen(self.pen)
                self.temp_path_item.setBrush(self.stroke_fill)
                self.temp_path_item.setZValue(0)
                self.canvas.addItem(self.temp_path_item)

                try:
                    self.temp_path_item.setPath(self.temp_path_item.smooth_path(self.temp_path_item.path(), 0.75))

                except Exception:
                    pass

                self.canvas.update()

                super().mouseMoveEvent(event)

    def on_smooth_path_draw_end(self, event):
        if self.path is not None:
            if self.path.isEmpty():
                return

            else:
                # Check the buttons
                if event.button() == Qt.LeftButton:
                    self.path.lineTo(self.mapToScene(event.pos()))
                    self.last_point = self.mapToScene(event.pos())

                    # Check if there is a temporary path (if so, remove it now)
                    if self.temp_path_item is not None:
                        self.canvas.removeItem(self.temp_path_item)

                    self.canvas.update()

                    # Load main path as QGraphicsItem
                    path_item = CustomPathItem(self.path)
                    path_item.path().setFillRule(Qt.WindingFill)
                    path_item.setPen(self.pen)
                    path_item.setZValue(0)
                    path_item.setBrush(self.stroke_fill)
                    try:
                        path_item.setPath(path_item.smooth_path(path_item.path(), 0.1))
                    except Exception:
                        pass

                    # Add item
                    add_command = AddItemCommand(self.canvas, path_item)
                    self.canvas.addCommand(add_command)

                    # Set Flags
                    path_item.setFlag(QGraphicsItem.ItemIsSelectable)
                    path_item.setFlag(QGraphicsItem.ItemIsMovable)

                    # Set Tooltop
                    path_item.setToolTip('Path')

                    self.path = None
                    self.temp_path_item = None
                    self.last_point = None

                    super().mouseReleaseEvent(event)

    def on_label_start(self, event):
        # Check the button being pressed
        if event.button() == Qt.LeftButton:
            # Create the leader line
            self.leader_line = QPainterPath()  # Create a new QPainterPath
            self.leader_line.moveTo(self.mapToScene(event.pos()))
            self.setDragMode(QGraphicsView.NoDrag)
            self.clicked_label_point = self.mapToScene(event.pos())

            # Create the label text
            self.label_text = EditableTextBlock('An Editable Text Block')
            self.label_text.setFont(self.font)
            self.label_text.setPos(self.mapToScene(event.pos()))
            self.label_text.setDefaultTextColor(QColor('black'))
            self.label_text.setToolTip("Text")

            # Create path item
            self.pathg_item = LeaderLineItem(self.leader_line)
            self.pathg_item.setBrush(QBrush(QColor(Qt.transparent)))

            add_command2 = AddItemCommand(self.canvas, self.label_text)
            self.canvas.addCommand(add_command2)
            add_command3 = AddItemCommand(self.canvas, self.pathg_item)
            self.canvas.addCommand(add_command3)

            self.canvas.update()

    def on_label(self, event):
        # Check the buttons
        if event.button() == Qt.LeftButton:
            # Move line to current coords
            self.leader_line.lineTo(self.mapToScene(event.pos()))
            self.pathg_item.setPath(self.leader_line)
            self.pathg_item.update()

            self.canvas.update()

    def on_label_end(self, event):
        # Check buttons
        if event.button() == Qt.LeftButton:
            # Move line to current mouse coords
            self.leader_line.lineTo(self.mapToScene(event.pos()))
            self.pathg_item.setPath(self.leader_line)
            self.canvas.update()

            # Draw circle at the end of path
            scene_pos = self.mapToScene(event.pos())

            self.canvas.update()

            # Load path as QGraphicsItem, set parent items
            self.pathg_item.setPen(self.pen)
            self.pathg_item.setZValue(0)
            self.label_text.setParentItem(self.pathg_item)

            if self.leader_line.isEmpty():
                self.scene().removeItem(self.pathg_item)

            # Add items (no need to add rect, circle, and label because parent is path_item)
            add_command = AddItemCommand(self.canvas, self.pathg_item)
            self.canvas.addCommand(add_command)

            # Set flags
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.pathg_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.label_text.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

            # Set Tooltips for elements
            self.pathg_item.setToolTip('Leader Line')

    def on_add_text(self, event):
        if event.button() == Qt.LeftButton:
            pos = self.mapToScene(event.pos())

            self.text = EditableTextBlock('Lorem Ipsum')
            self.text.setFont(self.font)
            self.text.setDefaultTextColor(self.font_color)

            add_command = AddItemCommand(self.canvas, self.text)
            self.canvas.addCommand(add_command)

            self.text.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            self.text.setZValue(0)
            self.text.setPos(pos)

    def on_scale_start(self, event):
        try:
            self.initialScale = None
            if event.buttons() == Qt.LeftButton:
                self.startPos = self.mapToScene(event.pos())

                selected_items = self.scene().selectedItems()
                if selected_items:
                    item = selected_items[0]
                    self.initialScale = item.scale()
                    # Create the ScaleCommand with the initial scale
                    self.scalingCommand = ScaleCommand(item, self.initialScale, self.initialScale)

        except Exception as e:
            pass

    def on_scale(self, event):
        try:
            self.setDragMode(QGraphicsView.NoDrag)

            if event.buttons() == Qt.LeftButton and self.scalingCommand:
                delta = self.mapToScene(event.pos()) - self.startPos
                scale = 1 + delta.y() / 100.0

                item = self.scalingCommand.item
                if self.initialScale is not None:
                    if isinstance(item, CanvasItem):
                        pass
                    else:
                        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                        item.setTransformOriginPoint(item.boundingRect().center())
                        item.setScale(self.initialScale * scale)  # Update the scale directly

                        # Update the new scale in the command
                        self.scalingCommand.new_scale = self.initialScale * scale

        except Exception as e:
            pass

    def on_scale_end(self, event):
        try:
            self.setDragMode(QGraphicsView.RubberBandDrag)

            for item in self.scene().selectedItems():
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

            if self.scalingCommand and self.scalingCommand.new_scale != self.scalingCommand.old_scale:
                # Push the command to the undo stack
                self.canvas.addCommand(self.scalingCommand)
                self.scalingCommand = None

        except Exception as e:
            pass

    def on_add_canvas(self):
        if self.add_canvas_btn.isChecked():
            self.scene().setBackgroundBrush(QBrush(QColor('#737373')))

            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    for items in item.childItems():
                        items.setVisible(True)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, False)
                    item.setFlag(QGraphicsItem.ItemIsMovable, False)

        elif not self.add_canvas_btn.isChecked():
            self.scene().setBackgroundBrush(QBrush(QColor('#606060')))

            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    for items in item.childItems():
                        items.setVisible(False)
                        items.parentItem().setSelected(False)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
                        items.parentItem().setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.ItemIsMovable)

    def on_add_canvas_start(self, event):
        if event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            self.setDragMode(QGraphicsView.NoDrag)
            self.clicked_canvas_point = self.mapToScene(event.pos())
            self.canvas_item = CanvasItem(0, 0, 1, 1)
            self.canvas_item.setPos(self.clicked_canvas_point)
            self.scene().addItem(self.canvas_item)
            self.canvas_item_text = CanvasTextItem('Canvas', self.canvas_item)
            command = AddItemCommand(self.scene(), self.canvas_item)
            self.canvas.addCommand(command)

    def on_add_canvas_drag(self, event):
        if self.canvas_item is not None and event.buttons() & Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            current_pos = self.mapToScene(event.pos())
            self.canvas_item.setRect(0,
                                     0,
                                     current_pos.x() - self.clicked_canvas_point.x(),
                                     current_pos.y() - self.clicked_canvas_point.y())

    def on_add_canvas_end(self, event):
        if self.canvas_item is not None and event.button() == Qt.LeftButton and event.modifiers() & Qt.ShiftModifier:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            current_pos = self.mapToScene(event.pos())
            self.canvas_item.setRect(0,
                                     0,
                                     current_pos.x() - self.clicked_canvas_point.x(),
                                     current_pos.y() - self.clicked_canvas_point.y())

            self.canvas_item.setPos(self.clicked_canvas_point)
            self.canvas_item.setToolTip('Canvas')
            self.canvas_item.setZValue(-1)

            if self.canvas_item.rect().isEmpty():
                self.scene().removeItem(self.canvas_item)
                self.scene().removeItem(self.canvas_item_text)

            self.canvas_item = None
            self.clicked_canvas_point = None

            self.canvas.update()

    def on_pan_start(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)

    def on_pan_end(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)

class CustomGraphicsScene(QGraphicsScene):
    itemMoved = pyqtSignal(QGraphicsItem, QPointF)

    def __init__(self, undoStack):
        super().__init__()
        self.file_name = None
        self.mpversion = '1.0.0'
        self.undo_stack = undoStack
        self.scale_btn = None

        width = 64000
        height = 64000
        self.setSceneRect(-width // 2, -height // 2, width, height)
        self.setBackgroundBrush(QBrush(QColor('#606060')))

        self.movingItem = None
        self.oldPos = QPointF()
        self.itemMoved.connect(self.on_move_item)

    def set_widget(self, w):
        self.scale_btn = w

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.RightButton:
            mousePos = event.buttonDownScenePos(Qt.RightButton)
            list = self.items(mousePos)
            for item in list:
                item.setSelected(True)

        else:
            if self.scale_btn is not None:
                if self.scale_btn.isChecked():
                    pass

                else:
                    mousePos = event.buttonDownScenePos(Qt.LeftButton)
                    itemList = self.items(mousePos)
                    self.movingItem = None if not itemList else itemList[0]

                    if self.movingItem and event.button() == Qt.LeftButton:
                        self.oldPos = self.movingItem.pos()

                self.clearSelection()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if self.scale_btn is not None:
            if self.scale_btn.isChecked():
                pass

            else:
                if self.movingItem and event.button() == Qt.LeftButton:
                    if self.oldPos != self.movingItem.pos():
                        self.itemMoved.emit(self.movingItem, self.oldPos)
                    self.movingItem = None

        super().mouseReleaseEvent(event)

    def on_move_item(self, movedItem, oldPos):
        command = MoveItemCommand(movedItem, oldPos)
        self.addCommand(command)

    def undo(self):
        self.undo_stack.undo()

    def redo(self):
        self.undo_stack.redo()

    def addCommand(self, command):
        self.undo_stack.push(command)

    def selectedItemsBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        return bounding_rect

    def update(self, rect=None):
        super().update()

        for item in self.items():
            item.update()

    def loadSvg(self, fileName):
        try:
            tree = ET.parse(fileName)
            root = tree.getroot()

            ns = {'svg': 'http://www.w3.org/2000/svg'}

            # Load rectangles
            for elem in root.findall('.//svg:rect', ns):
                x = float(elem.get('x', 0))
                y = float(elem.get('y', 0))
                width = float(elem.get('width', 0))
                height = float(elem.get('height', 0))
                rect_item = CustomRectangleItem(QRectF(x, y, width, height))
                self.addItem(rect_item)

            # Load text
            for elem in root.findall('.//svg:text', ns):
                x = float(elem.get('x', 0))
                y = float(elem.get('y', 0))
                text = elem.text
                text_item = EditableTextBlock(text)
                text_item.setPos(QPointF(x, y))
                self.addItem(text_item)

        except Exception as e:
            print(e)

    def open(self, parent):
        fileName, _ = QFileDialog.getOpenFileName(self.parent(), "Open File", "", "MPRUN SVG (*.svg)")

        if fileName:
            self.clear()
            self.loadSvg(fileName)
            self.file_name = fileName
            parent.setWindowTitle(f'MPRUN - {fileName}')
            self.file_name = fileName

    def save(self, parent):
        if self.file_name is not None:
            svgGenerator = QSvgGenerator()
            svgGenerator.setFileName(self.file_name)
            svgGenerator.setSize(self.sceneRect().size().toSize())
            svgGenerator.setViewBox(self.sceneRect())
            svgGenerator.setTitle("SVG Document")
            svgGenerator.setDescription("Generated by PyQt QGraphicsScene")

            painter = QPainter(svgGenerator)
            self.render(painter, target=self.sceneRect(), source=self.sceneRect())
            painter.end()

        else:
            fileName, _ = QFileDialog.getSaveFileName(self.parent(), "Save File", "", "MPRUN SVG (*.svg)")
            if fileName:
                svgGenerator = QSvgGenerator()
                svgGenerator.setFileName(fileName)
                svgGenerator.setSize(self.sceneRect().size().toSize())
                svgGenerator.setViewBox(self.sceneRect())
                svgGenerator.setTitle("SVG Document")
                svgGenerator.setDescription("Generated by PyQt QGraphicsScene")

                painter = QPainter(svgGenerator)
                self.render(painter, target=self.sceneRect(), source=self.sceneRect())
                painter.end()

                self.file_name = fileName
                parent.setWindowTitle(f'MPRUN - {fileName}')






