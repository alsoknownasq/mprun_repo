import os.path

from src.scripts.imports import *
from src.gui.custom_dialogs import *
from src.framework.undo_commands import *
from src.framework.custom_classes import *
from src.scripts.app_internal import *
from src.framework.tools import *

class CustomViewport(QOpenGLWidget):
    def __init__(self):
        super().__init__()

        format = QSurfaceFormat()
        format.setSamples(4)
        format.setRenderableType(QSurfaceFormat.OpenGL)
        self.setFormat(format)

class CustomGraphicsView(QGraphicsView):
    def __init__(self, canvas, actions: list, zoom_spin):
        super().__init__()
        self.points = []

        # Set flags
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.TextAntialiasing)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Set widgets
        self.select_btn = actions[0]
        self.pan_btn = actions[1]
        self.path_btn = actions[2]
        self.pen_btn = actions[3]
        self.sculpt_btn = actions[4]
        self.line_and_label_btn = actions[5]
        self.text_btn = actions[6]
        self.scale_btn = actions[7]
        self.add_canvas_btn = actions[8]
        self.grid_checkbtn = actions[9]

        # Items
        self.canvas = canvas
        self.temp_path_item = None
        self.pen = None
        self.stroke_fill = None
        self.font = None
        self.layer_height = None
        self.path = None
        self.last_point = None

        # Tools
        self.pathDrawingTool = PathDrawerTool(self.canvas, self)
        self.penDrawingTool = PenDrawerTool(self.canvas, self)
        self.labelingTool = LineAndLabelTool(self.canvas, self)
        self.scalingTool = MouseScalingTool(self.canvas, self)
        self.sculptingTool = PathSculptingTool(self.canvas, self)
        self.canvasTool = AddCanvasTool(self.canvas, self)

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [0, 100]
        self.zoom_spin = zoom_spin

    def update_pen(self, pen):
        self.pen = pen

    def update_brush(self, brush):
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

    def show_tooltip(self, event):
        point = event.pos()
        p = self.mapToGlobal(point)
        p.setY(p.y())
        p.setX(p.x() + 10)
        QToolTip.showText(p, f'''x: {int(self.mapToScene(point).x())} 
y: {int(self.mapToScene(point).y())}''')

    def mousePressEvent(self, event):
        # Check if the path tool is turned on
        if self.path_btn.isChecked():
            self.pathDrawingTool.on_path_draw_start(event)

        elif self.pen_btn.isChecked():
            self.penDrawingTool.on_draw_start(event)
            self.disable_item_flags()

        elif self.line_and_label_btn.isChecked():
            self.labelingTool.on_label_start(event)
            self.disable_item_flags()

        elif self.text_btn.isChecked():
            self.on_add_text(event)
            self.disable_item_movement()
            super().mousePressEvent(event)

        elif self.scale_btn.isChecked():
            self.scalingTool.on_scale_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.canvasTool.on_add_canvas_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_start(event)
            self.disable_item_flags()
            super().mousePressEvent(event)

        elif self.sculpt_btn.isChecked():
            self.sculptingTool.on_sculpt_start(event)
            self.disable_item_flags()

        else:
            super().mousePressEvent(event)

        self.on_add_canvas_trigger()
        
    def mouseMoveEvent(self, event):
        if self.path_btn.isChecked():
            self.pathDrawingTool.show_tooltip(event)
            self.pathDrawingTool.on_path_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pen_btn.isChecked():
            self.penDrawingTool.show_tooltip(event)
            self.penDrawingTool.on_draw(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)
            
        elif self.text_btn.isChecked():
            self.show_tooltip(event)
            super().mouseMoveEvent(event)

        elif self.line_and_label_btn.isChecked():
            self.show_tooltip(event)
            self.labelingTool.on_label(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.scale_btn.isChecked():
            self.show_tooltip(event)
            self.scalingTool.on_scale(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.canvasTool.on_add_canvas_drag(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.pan_btn.isChecked():
            self.show_tooltip(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        elif self.sculpt_btn.isChecked():
            self.show_tooltip(event)
            self.sculptingTool.on_sculpt(event)
            self.disable_item_flags()
            super().mouseMoveEvent(event)

        else:
            self.show_tooltip(event)
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.path_btn.isChecked():
            self.pathDrawingTool.on_path_draw_end(event)

        elif self.pen_btn.isChecked():
            self.penDrawingTool.on_draw_end(event)
            
        elif self.text_btn.isChecked():
            super().mouseReleaseEvent(event)

        elif self.line_and_label_btn.isChecked():
            self.labelingTool.on_label_end(event)
            super().mouseReleaseEvent(event)

        elif self.scale_btn.isChecked():
            self.scalingTool.on_scale_end(event)
            super().mouseReleaseEvent(event)

        elif self.add_canvas_btn.isChecked():
            self.canvasTool.on_add_canvas_end(event)
            super().mouseReleaseEvent(event)

        elif self.pan_btn.isChecked():
            self.on_pan_end(event)
            super().mouseReleaseEvent(event)

        elif self.sculpt_btn.isChecked():
            self.sculptingTool.on_sculpt_end(event)
            self.disable_item_flags()

        else:
            super().mouseReleaseEvent(event)

        self.parent().update_transform_ui()

    def mouseDoubleClickEvent(self, event):
        if self.sculpt_btn.isChecked():
            self.sculptingTool.on_sculpt_double_click(event)

        if self.scale_btn.isChecked():
            self.scalingTool.on_scale_double_click(event)
            
        else:
            super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        try:
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

            current_zoom_percentage = self.transform().m11() * 100
            self.zoom_spin.setValue(int(current_zoom_percentage))
            self.zoom_spin.blockSignals(False)

        except Exception:
            pass

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
                item.store_filename(os.path.abspath(url.toLocalFile()))
                item.setToolTip('Imported SVG')

            elif url.toLocalFile().endswith(('.txt', '.csv')):
                with open(url.toLocalFile(), 'r') as f:
                    item = CustomTextItem(f.read())
                    item.setToolTip('Imported Text')

            elif url.toLocalFile().endswith('.md'):
                with open(url.toLocalFile(), 'r') as f:
                    item = CustomTextItem(f.read())
                    item.setToolTip('Imported Text')
                    item.toMarkdown()

            else:
                pixmap = QPixmap(url.toLocalFile())
                item = CustomPixmapItem(pixmap)
                item.store_filename(os.path.abspath(url.toLocalFile()))
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

    def on_add_text(self, event):
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            i = self.scene().itemAt(self.mapToScene(event.pos()), self.transform())

            if i and isinstance(i, CustomTextItem):
                i.set_active()

            else:
                for item in self.canvas.items():
                    if isinstance(item, CustomTextItem):
                        if item.hasFocus():
                            item.clearFocus()
                            return

                pos = self.mapToScene(event.pos())

                self.text = CustomTextItem('Lorem Ipsum')
                self.text.setFont(self.font)
                self.text.setDefaultTextColor(self.font_color)

                add_command = AddItemCommand(self.canvas, self.text)
                self.canvas.addCommand(add_command)

                self.text.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                self.text.setZValue(0)
                self.text.setPos(pos)
                self.text.select_text_and_set_cursor()

    def on_add_canvas_trigger(self):
        if self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(True)

        elif not self.add_canvas_btn.isChecked():
            for item in self.canvas.items():
                if isinstance(item, CanvasItem):
                    item.setCanvasActive(False)

                else:
                    item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                    item.setFlag(QGraphicsItem.ItemIsMovable, True)

            self.canvas.setBackgroundBrush(QBrush(QColor('#606060')))

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
    itemsMoved = pyqtSignal(object, object)

    def __init__(self, undoStack):
        super().__init__()
        self.file_name = None
        self.mpversion = '1.0.0'
        self.canvas_count = 1
        self.undo_stack = undoStack
        self.scale_btn = None
        self.modified = False
        self.parentWindow = None

        width = 64000
        height = 64000
        self.setSceneRect(-width // 2, -height // 2, width, height)
        self.setBackgroundBrush(QBrush(QColor('#606060')))

        # Grid
        self.gridEnabled = False
        self.gridSize = 10
        self.gridSquares = 5

        # Item Movement
        self.oldPositions = {}
        self.movingItem = None
        self.oldPos = QPointF()
        self.itemsMoved.connect(self.on_move_item)

        # Managers
        self.manager = SceneManager(self)
        self.importManager = ImportManager(self)
        self.exportManager = ExportManager(self)

    def set_widget(self, w):
        self.scale_btn = w

    def setParentWindow(self, parent: QMainWindow):
        self.parentWindow = parent

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.oldPositions = {i: i.pos() for i in self.selectedItems()}

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and self.oldPositions:
            newPositions = {i: i.pos() for i in self.oldPositions.keys()}
            if any(self.oldPositions[i] != newPositions[i] for i in self.oldPositions.keys()):
                self.itemsMoved.emit(self.oldPositions, newPositions)
            self.oldPositions = {}

    def on_move_item(self, oldPositions, newPositions):
        self.addCommand(ItemMovedUndoCommand(oldPositions, newPositions))

    def undo(self):
        if self.undo_stack.canUndo():
            self.undo_stack.undo()
            self.modified = True
            self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        self.parentWindow.update_transform_ui()
        self.parentWindow.update_appearance_ui()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def redo(self):
        if self.undo_stack.canRedo():
            self.undo_stack.redo()
            self.modified = True
            self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        self.parentWindow.update_transform_ui()
        self.parentWindow.update_appearance_ui()

        for item in self.items():
            if isinstance(item, CustomTextItem):
                if isinstance(item.parentItem(), LeaderLineItem):
                    item.parentItem().updatePathEndPoint()

    def addCommand(self, command):
        self.undo_stack.push(command)
        self.modified = True
        self.parentWindow.setWindowTitle(f'{os.path.basename(self.manager.filename)}* - MPRUN')

        print(command)

    def selectedItemsBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.boundingRect())
        return bounding_rect

    def selectedItemsSceneBoundingRect(self):
        bounding_rect = QRectF()
        for item in self.selectedItems():
            bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        return bounding_rect

    def update(self, rect=None):
        super().update()

        for item in self.items():
            item.update()

    def setGridEnabled(self, enabled: bool):
        self.gridEnabled = enabled

    def setGridSize(self, grid_size: int):
        self.gridSize = grid_size
        self.update()

    def drawBackground(self, painter, rect):
        try:
            super().drawBackground(painter, rect)

            if self.gridEnabled:
                # settings
                self._color_light = QColor("#a3a3a3")
                self._color_dark = QColor("#b8b8b8")

                self._pen_light = QPen(self._color_light)
                self._pen_light.setWidth(1)
                self._pen_dark = QPen(self._color_dark)
                self._pen_dark.setWidth(1)

                # here we create our grid
                left = int(math.floor(rect.left()))
                right = int(math.ceil(rect.right()))
                top = int(math.floor(rect.top()))
                bottom = int(math.ceil(rect.bottom()))

                first_left = left - (left % self.gridSize)
                first_top = top - (top % self.gridSize)

                # compute all lines to be drawn
                lines_light, lines_dark = [], []
                for x in range(first_left, right, self.gridSize):
                    if (x % (self.gridSize * self.gridSquares) != 0):
                        lines_light.append(QLine(x, top, x, bottom))
                    else:
                        lines_dark.append(QLine(x, top, x, bottom))

                for y in range(first_top, bottom, self.gridSize):
                    if (y % (self.gridSize * self.gridSquares) != 0):
                        lines_light.append(QLine(left, y, right, y))
                    else:
                        lines_dark.append(QLine(left, y, right, y))

                # draw the lines
                painter.setPen(self._pen_light)
                painter.drawLines(*lines_light)

                painter.setPen(self._pen_dark)
                painter.drawLines(*lines_dark)

        except Exception:
            pass

    def addItem(self, item):
        super().addItem(item)

        if isinstance(item, CanvasItem):
            self.canvas_count += 1

        if self.gridEnabled:
            for item in self.items():
                if isinstance(item, CanvasTextItem):
                    pass

                else:
                    item.gridEnabled = True

class SceneManager:
    def __init__(self, scene):
        self.scene = scene
        self.filename = 'Untitled'
        self.parent = None
        self.repair_needed = False

    def reset_to_default_scene(self):
        self.scene.clear()
        self.scene.modified = False
        self.filename = 'Untitled'
        self.scene.parentWindow.setWindowTitle(f'{self.filename} - MPRUN')
        self.scene.parentWindow.create_default_objects()

    def restore(self):
        if self.scene.modified:
            # Display a confirmation dialog
            confirmation_dialog = QMessageBox(self.scene.parentWindow)
            confirmation_dialog.setWindowTitle('Close Document')
            confirmation_dialog.setIcon(QMessageBox.Warning)
            confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
            confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
            confirmation_dialog.setDefaultButton(QMessageBox.Save)

            # Get the result of the confirmation dialog
            result = confirmation_dialog.exec_()

            if result == QMessageBox.Discard:
                self.reset_to_default_scene()

            elif result == QMessageBox.Save:
                success = self.scene.parentWindow.save()

                if success:
                    self.reset_to_default_scene()

        else:
            self.reset_to_default_scene()

    def load(self, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.modified:
                # Display a confirmation dialog
                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                confirmation_dialog.setWindowTitle('Close Document')
                confirmation_dialog.setIcon(QMessageBox.Warning)
                confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
                confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
                confirmation_dialog.setDefaultButton(QMessageBox.Save)

                # Get the result of the confirmation dialog
                result = confirmation_dialog.exec_()

                if result == QMessageBox.Discard:
                    filename, _ = QFileDialog.getOpenFileName(self.scene.parent(), 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()
                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

                elif result == QMessageBox.Save:
                    parent.save()

                    filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                              'MPRUN files (*.mp)')

                    if filename:
                        self.scene.undo_stack.clear()
                        self.scene.clear()

                        with open(filename, 'rb') as f:
                            items_data = pickle.load(f)
                            self.deserialize_items(items_data)

                            self.filename = filename
                            parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                            if self.repair_needed:
                                # Display a confirmation dialog
                                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                                confirmation_dialog.setWindowTitle('Open Document Error')
                                confirmation_dialog.setIcon(QMessageBox.Warning)
                                confirmation_dialog.setText(
                                    f"The document has file directories that could not be found. Do you want to do a file repair?")
                                confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                                confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                                # Get the result of the confirmation dialog
                                result = confirmation_dialog.exec_()

                                if result == QMessageBox.Yes:
                                    self.repair_file()

            else:
                filename, _ = QFileDialog.getOpenFileName(self.scene.parentWindow, 'Open File', '',
                                                          'MPRUN files (*.mp)')

                if filename:
                    self.scene.undo_stack.clear()
                    self.scene.clear()

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow,
                                 'Open File Error',
                                 'The document you are attempting to open has been corrupted. '
                                 'Please open a different document, or repair any changes.')

            print(e)

    def load_from_file(self, filename, parent):
        try:
            self.scene.parentWindow.use_exit_add_canvas()

            if self.scene.modified:
                # Display a confirmation dialog
                confirmation_dialog = QMessageBox(self.scene.parentWindow)
                confirmation_dialog.setWindowTitle('Close Document')
                confirmation_dialog.setIcon(QMessageBox.Warning)
                confirmation_dialog.setText("The document has been modified. Do you want to save your changes?")
                confirmation_dialog.setStandardButtons(QMessageBox.Discard | QMessageBox.Save | QMessageBox.Cancel)
                confirmation_dialog.setDefaultButton(QMessageBox.Save)

                # Get the result of the confirmation dialog
                result = confirmation_dialog.exec_()

                if result == QMessageBox.Discard:
                    self.scene.undo_stack.clear()
                    self.scene.clear()
                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                        self.scene.modified = False

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

                elif result == QMessageBox.Save:
                    self.scene.undo_stack.clear()
                    self.scene.clear()

                    with open(filename, 'rb') as f:
                        items_data = pickle.load(f)
                        self.deserialize_items(items_data)

                        self.filename = filename
                        parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                        self.scene.modified = False

                        if self.repair_needed:
                            # Display a confirmation dialog
                            confirmation_dialog = QMessageBox(self.scene.parentWindow)
                            confirmation_dialog.setWindowTitle('Open Document Error')
                            confirmation_dialog.setIcon(QMessageBox.Warning)
                            confirmation_dialog.setText(
                                f"The document has file directories that could not be found. Do you want to do a file repair?")
                            confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                            confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                            # Get the result of the confirmation dialog
                            result = confirmation_dialog.exec_()

                            if result == QMessageBox.Yes:
                                self.repair_file()

            else:
                self.scene.undo_stack.clear()
                self.scene.clear()

                with open(filename, 'rb') as f:
                    items_data = pickle.load(f)
                    self.deserialize_items(items_data)

                    self.filename = filename
                    parent.setWindowTitle(f'{os.path.basename(self.filename)} - MPRUN')
                    self.scene.modified = False

                    if self.repair_needed:
                        # Display a confirmation dialog
                        confirmation_dialog = QMessageBox(self.scene.parentWindow)
                        confirmation_dialog.setWindowTitle('Open Document Error')
                        confirmation_dialog.setIcon(QMessageBox.Warning)
                        confirmation_dialog.setText(
                            f"The document has file directories that could not be found. Do you want to do a file repair?")
                        confirmation_dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                        confirmation_dialog.setDefaultButton(QMessageBox.Yes)

                        # Get the result of the confirmation dialog
                        result = confirmation_dialog.exec_()

                        if result == QMessageBox.Yes:
                            self.repair_file()

        except Exception as e:
            QMessageBox.critical(self.scene.parentWindow,
                                 'Open File Error',
                                 'The document you are attempting to open has been corrupted. '
                                 'Please open a different document, or repair any changes.')

            print(e)

    def serialize_items(self):
        items_data = []

        items_data.append({
            'mpversion': self.scene.mpversion,
            'copyright': copyright_message,
        })

        for item in self.scene.items():
            if isinstance(item, CanvasItem):
                items_data.append(self.serialize_canvas(item))

            elif isinstance(item, CustomTextItem):
                if item.parentItem():
                    pass

                else:
                    items_data.append({
                        'type': 'CustomTextItem',
                        'markdown': True if item.markdownEnabled else False,
                        'text': item.old_text if item.markdownEnabled else item.toPlainText(),
                        'font': self.serialize_font(item.font()),
                        'color': self.serialize_color(item.defaultTextColor()),
                        'attr': self.serialize_item_attributes(item),
                        'locked': True if item.markdownEnabled else False,
                    })

            elif isinstance(item, CustomPathItem):
                if item.parentItem():
                    pass

                else:
                    path_data = {
                        'type': 'CustomPathItem',
                        'pen': self.serialize_pen(item.pen()),
                        'brush': self.serialize_brush(item.brush()),
                        'attr': self.serialize_item_attributes(item),
                        'elements': self.serialize_path(item.path()),
                        'smooth': True if item.smooth else False,
                        'addtext': True if item.add_text else False,
                        'textalongpath': item.text_along_path if item.add_text else '',
                        'textfont': self.serialize_font(item.text_along_path_font) if item.add_text else self.serialize_font(QFont('Arial', 20)),
                        'textcolor': self.serialize_color(item.text_along_path_color) if item.add_text else self.serialize_color(QColor('black')),
                        'textspacing': item.text_along_path_spacing if item.add_text else 3,
                        'starttextfrombeginning': item.start_text_from_beginning if item.add_text else False,
                    }

                    items_data.append(path_data)

            elif isinstance(item, CustomGraphicsItemGroup):
                if item.parentItem():
                    pass

                else:
                    items_data.append({
                        'type': 'CustomGraphicsItemGroup',
                        'attr': self.serialize_item_attributes(item),
                        'children': self.serialize_group(item)
                    })

            elif isinstance(item, LeaderLineItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'LeaderLineItem',
                        'pen': self.serialize_pen(item.pen()),
                        'brush': self.serialize_brush(item.brush()),
                        'attr': self.serialize_item_attributes(item),
                        'elements': self.serialize_path(item.path()),
                        'text': item.text_element.toPlainText(),
                        'textcolor': self.serialize_color(item.text_element.defaultTextColor()),
                        'textfont': self.serialize_font(item.text_element.font()),
                        'textposx': item.text_element.pos().x(),
                        'textposy': item.text_element.pos().y(),
                        'textzval': item.text_element.zValue(),
                        'texttransform': self.serialize_transform(item.text_element.transform()),
                        'textscale': item.text_element.scale(),
                        'texttransformorigin': self.serialize_point(item.transformOriginPoint()),
                        'textrotation': item.text_element.rotation(),
                        'textvisible': item.text_element.isVisible(),
                    }

                    items_data.append(data)

            elif isinstance(item, CustomSvgItem):
                if item.parentItem():
                    pass

                else:
                    data = {
                        'type': 'CustomSvgItem',
                        'attr': self.serialize_item_attributes(item),
                        'filename': item.source() if
                        os.path.exists(item.source() if item.source() is not None else '') else None,
                        'raw_svg_data': self.serialize_file(item.source()) if
                        os.path.exists(item.source() if item.source() is not None else '') else item.svgData(),
                    }

                    items_data.append(data)

            elif isinstance(item, CustomPixmapItem):
                if item.parentItem():
                    pass

                else:
                    pixmap = item.pixmap()
                    buffer = QBuffer()
                    buffer.open(QIODevice.WriteOnly)
                    pixmap.save(buffer, "PNG")
                    pixmap_data = buffer.data().data()

                    data = {
                        'type': 'CustomPixmapItem',
                        'attr': self.serialize_item_attributes(item),
                        'filename': item.return_filename() if
                        os.path.exists(item.return_filename() if item.return_filename() is not None else '') else None,
                        'data': pixmap_data,
                    }

                    items_data.append(data)

        return items_data

    def serialize_item_attributes(self, item):
        return [{
            'rotation': item.rotation(),
            'transform': self.serialize_transform(item.transform()),
            'scale': item.scale(),
            'transformorigin': self.serialize_point(item.transformOriginPoint()),
            'x': item.pos().x(),
            'y': item.pos().y(),
            'name': item.toolTip(),
            'zval': item.zValue(),
            'visible': item.isVisible(),
        }]

    def serialize_color(self, color: QColor):
        return {
            'red': color.red(),
            'green': color.green(),
            'blue': color.blue(),
            'alpha': color.alpha(),
        }

    def serialize_pen(self, pen: QPen):
        return {
            'width': pen.width(),
            'color': self.serialize_color(pen.color()),
            'style': pen.style(),
            'capstyle': pen.capStyle(),
            'joinstyle': pen.joinStyle()
        }

    def serialize_brush(self, brush: QBrush):
        return {
            'color': self.serialize_color(brush.color()),
            'style': brush.style()
        }

    def serialize_font(self, font: QFont):
        return {
            'family': font.family(),
            'pointsize': font.pixelSize(),
            'letterspacing': font.letterSpacing(),
            'bold': font.bold(),
            'italic': font.italic(),
            'underline': font.underline(),
        }

    def serialize_transform(self, transform: QTransform):
        return {
            'm11': transform.m11(),
            'm12': transform.m12(),
            'm13': transform.m13(),
            'm21': transform.m21(),
            'm22': transform.m22(),
            'm23': transform.m23(),
            'm31': transform.m31(),
            'm32': transform.m32(),
            'm33': transform.m33()
        }

    def serialize_point(self, point: QPointF):
        return {'x': point.x(), 'y': point.y()}

    def serialize_canvas(self, canvas: CanvasItem):
        return {
            'type': 'CanvasItem',
            'rect': [0, 0, canvas.rect().width(), canvas.rect().height()],
            'name': canvas.name(),
            'x': canvas.pos().x(),
            'y': canvas.pos().y(),
        }

    def serialize_path(self, path: QPainterPath):
        elements = []
        for i in range(path.elementCount()):
            element = path.elementAt(i)
            if element.isMoveTo():
                elements.append({'type': 'moveTo', 'x': element.x, 'y': element.y})
            elif element.isLineTo():
                elements.append({'type': 'lineTo', 'x': element.x, 'y': element.y})
            elif element.isCurveTo():
                elements.append({'type': 'curveTo', 'x': element.x, 'y': element.y})
        return elements

    def serialize_group(self, group: CustomGraphicsItemGroup):
        children = []
        for child in group.childItems():
            if isinstance(child, CustomTextItem):
                children.append({
                    'type': 'CustomTextItem',
                    'markdown': True if child.markdownEnabled else False,
                    'text': child.toPlainText(),
                    'font': self.serialize_font(child.font()),
                    'color': self.serialize_color(child.defaultTextColor()),
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'locked': True if child.markdownEnabled else False,
                    'visible': child.isVisible(),
                })
            elif isinstance(child, CustomPathItem):
                path_data = {
                    'type': 'CustomPathItem',
                    'pen': self.serialize_pen(child.pen()),
                    'brush': self.serialize_brush(child.brush()),
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'elements': self.serialize_path(child.path()),
                    'visible': child.isVisible(),
                }

                if child.add_text:
                    path_data.update({
                        'addtext': child.add_text,
                        'text': child.text_along_path,
                        'textfont': self.serialize_font(child.text_along_path_font),
                        'textcolor': self.serialize_color(child.text_along_path_color),
                        'textspacing': child.text_along_path_spacing,
                        'starttextfrombeginning': child.start_text_from_beginning,
                    })

                children.append(path_data)
            elif isinstance(child, CustomSvgItem):
                data = {
                    'type': 'CustomSvgItem',
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'filename': child.source(),
                    'visible': child.isVisible(),
                }

                children.append(data)
            elif isinstance(child, CustomPixmapItem):
                data = {
                    'type': 'CustomPixmapItem',
                    'rotation': child.rotation(),
                    'transform': self.serialize_transform(child.transform()),
                    'x': child.pos().x(),
                    'y': child.pos().y(),
                    'name': child.toolTip(),
                    'zval': child.zValue(),
                    'filename': child.return_filename(),
                    'visible': child.isVisible(),
                }

                children.append(data)

        return children

    def serialize_file(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            return f.read()

    def deserialize_items(self, items_data):
        # Handle metadata
        metadata = items_data.pop(0)
        self.scene.mpversion = metadata.get('mpversion', 'unknown')

        for item_data in items_data:
            item = None
            if item_data['type'] == 'CanvasItem':
                item = self.deserialize_canvas(item_data)
            elif item_data['type'] == 'CustomTextItem':
                item = self.deserialize_custom_text_item(item_data)
            elif item_data['type'] == 'CustomPathItem':
                item = self.deserialize_custom_path_item(item_data)
            elif item_data['type'] == 'CustomGraphicsItemGroup':
                item = self.deserialize_custom_group_item(item_data)
            elif item_data['type'] == 'LeaderLineItem':
                item = self.deserialize_leader_line_item(item_data)
            elif item_data['type'] == 'CustomSvgItem':
                item = self.deserialize_custom_svg_item(item_data)
            elif item_data['type'] == 'CustomPixmapItem':
                item = self.deserialize_custom_pixmap_item(item_data)

            if item is not None:
                self.scene.addItem(item)

        self.scene.parentWindow.use_exit_add_canvas()

    def deserialize_color(self, color):
        return QColor(color['red'], color['green'], color['blue'], color['alpha'])

    def deserialize_pen(self, data):
        pen = QPen()
        pen.setWidth(data['width'])
        pen.setColor(self.deserialize_color(data['color']))
        pen.setStyle(data['style'])
        pen.setCapStyle(data['capstyle'])
        pen.setJoinStyle(data['joinstyle'])
        return pen

    def deserialize_brush(self, data):
        brush = QBrush()
        brush.setColor(self.deserialize_color(data['color']))
        brush.setStyle(data['style'])
        return brush

    def deserialize_font(self, data):
        font = QFont()
        font.setFamily(data['family'])
        font.setPixelSize(data['pointsize'])
        font.setLetterSpacing(QFont.AbsoluteSpacing, data['letterspacing'])
        font.setBold(data['bold'])
        font.setItalic(data['italic'])
        font.setUnderline(data['underline'])
        return font

    def deserialize_transform(self, data):
        transform = QTransform(
            data['m11'], data['m12'], data['m13'],
            data['m21'], data['m22'], data['m23'],
            data['m31'], data['m32'], data['m33']
        )
        return transform

    def deserialize_point(self, data):
        return QPointF(data['x'], data['y'])

    def deserialize_canvas(self, data):
        rect = QRectF(*data['rect'])
        canvas = CanvasItem(rect, data['name'])
        canvas.setPos(data['x'], data['y'])
        return canvas

    def deserialize_custom_text_item(self, data):
        text_item = CustomTextItem(data['text'])
        text_item.setFont(self.deserialize_font(data['font']))
        text_item.setDefaultTextColor(self.deserialize_color(data['color']))
        text_item.locked = data['locked']

        for attr in data['attr']:
            text_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            text_item.setRotation(attr['rotation'])
            text_item.setTransform(self.deserialize_transform(attr['transform']))
            text_item.setScale(attr['scale'])
            text_item.setPos(attr['x'], attr['y'])
            text_item.setToolTip(attr['name'])
            text_item.setZValue(attr['zval'])
            text_item.setVisible(attr['visible'])

        if data.get('markdown', True):
            text_item.toMarkdown()

        return text_item

    def deserialize_custom_path_item(self, data):
        sub_path = QPainterPath()
        for element in data['elements']:
            if element['type'] == 'moveTo':
                sub_path.moveTo(element['x'], element['y'])
            elif element['type'] == 'lineTo':
                sub_path.lineTo(element['x'], element['y'])
            elif element['type'] == 'curveTo':
                sub_path.cubicTo(element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'])

        path_item = CustomPathItem(sub_path)
        path_item.setPen(self.deserialize_pen(data['pen']))
        path_item.setBrush(self.deserialize_brush(data['brush']))

        for attr in data['attr']:
            path_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            path_item.setRotation(attr['rotation'])
            path_item.setTransform(self.deserialize_transform(attr['transform']))
            path_item.setScale(attr['scale'])
            path_item.setPos(attr['x'], attr['y'])
            path_item.setToolTip(attr['name'])
            path_item.setZValue(attr['zval'])
            path_item.setVisible(attr['visible'])

        if data.get('smooth', True):
            path_item.smooth = True

        else:
            path_item.smooth = False

        if data.get('addtext', True):
            path_item.add_text = True
            path_item.setTextAlongPath(data['textalongpath'])
            path_item.setTextAlongPathColor(self.deserialize_color(data['textcolor']))
            path_item.setTextAlongPathFont(self.deserialize_font(data['textfont']))
            path_item.setTextAlongPathSpacingFromPath(data['textspacing'])
            path_item.setTextAlongPathFromBeginning(data['starttextfrombeginning'])

        else:
            path_item.add_text = False

        return path_item

    def deserialize_custom_group_item(self, data):
        group_item = CustomGraphicsItemGroup()

        for attr in data['attr']:
            group_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            group_item.setRotation(attr['rotation'])
            group_item.setTransform(self.deserialize_transform(attr['transform']))
            group_item.setScale(attr['scale'])
            group_item.setPos(attr['x'], attr['y'])
            group_item.setToolTip(attr['name'])
            group_item.setZValue(attr['zval'])
            group_item.setVisible(attr['visible'])

        for child_data in data['children']:
            if child_data['type'] == 'CustomTextItem':
                child = self.deserialize_custom_text_item(child_data)
            elif child_data['type'] == 'CustomPathItem':
                child = self.deserialize_custom_path_item(child_data)
            elif child_data['type'] == 'CustomPixmapItem':
                child = self.deserialize_custom_pixmap_item(child_data)
            elif child_data['type'] == 'CustomSvgItem':
                child = self.deserialize_custom_svg_item(child_data)

            group_item.addToGroup(child)

        return group_item

    def deserialize_leader_line_item(self, data):
        sub_path = QPainterPath()
        for element in data['elements']:
            if element['type'] == 'moveTo':
                sub_path.moveTo(element['x'], element['y'])
            elif element['type'] == 'lineTo':
                sub_path.lineTo(element['x'], element['y'])
            elif element['type'] == 'curveTo':
                sub_path.cubicTo(element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'],
                                 element['x'],
                                 element['y'])

        path_item = LeaderLineItem(sub_path, data['text'])
        path_item.setPen(self.deserialize_pen(data['pen']))
        path_item.setBrush(self.deserialize_brush(data['brush']))
        path_item.text_element.setZValue(data['textzval'])
        path_item.text_element.setDefaultTextColor(self.deserialize_color(data['textcolor']))
        path_item.text_element.setFont(self.deserialize_font(data['textfont']))
        path_item.text_element.setTransformOriginPoint(self.deserialize_point(data['texttransformorigin']))
        path_item.text_element.setTransform(self.deserialize_transform(data['texttransform']))
        path_item.text_element.setScale(data['textscale'])
        path_item.text_element.setPos(data['textposx'], data['textposy'])
        path_item.text_element.setRotation(data['textrotation'])
        path_item.text_element.setVisible(data['textvisible'])

        for attr in data['attr']:
            path_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            path_item.setRotation(attr['rotation'])
            path_item.setTransform(self.deserialize_transform(attr['transform']))
            path_item.setScale(attr['scale'])
            path_item.setPos(attr['x'], attr['y'])
            path_item.setToolTip(attr['name'])
            path_item.setZValue(attr['zval'])
            path_item.setVisible(attr['visible'])

        path_item.updatePathEndPoint()

        return path_item

    def deserialize_custom_svg_item(self, data):
        try:
            svg_item = CustomSvgItem()
            svg_item.store_filename(data['filename'])
            svg_item.loadFromData(data['raw_svg_data'])

            for attr in data['attr']:
                svg_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
                svg_item.setRotation(attr['rotation'])
                svg_item.setTransform(self.deserialize_transform(attr['transform']))
                svg_item.setScale(attr['scale'])
                svg_item.setPos(attr['x'], attr['y'])
                svg_item.setToolTip(attr['name'])
                svg_item.setZValue(attr['zval'])
                svg_item.setVisible(attr['visible'])

            return svg_item

        except Exception as e:
            print(e)

    def deserialize_custom_pixmap_item(self, data):
        pixmap = QPixmap(data['filename'])
        pixmap_item = CustomPixmapItem(pixmap)
        pixmap_item.store_filename(data['filename'])
        pixmap_item.loadFromData(data['data'])

        for attr in data['attr']:
            pixmap_item.setTransformOriginPoint(self.deserialize_point(attr['transformorigin']))
            pixmap_item.setRotation(attr['rotation'])
            pixmap_item.setTransform(self.deserialize_transform(attr['transform']))
            pixmap_item.setScale(attr['scale'])
            pixmap_item.setPos(attr['x'], attr['y'])
            pixmap_item.setToolTip(attr['name'])
            pixmap_item.setZValue(attr['zval'])
            pixmap_item.setVisible(attr['visible'])

        pixmap = pixmap_item.pixmap()
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        pixmap.save(buffer, "PNG")
        pixmap_data = buffer.data().data()
        pixmap_item.loadFromData(pixmap_data)

        return pixmap_item

    def repair_file(self):
        try:
            with open(self.filename, 'rb') as f:
                items_data = pickle.load(f)

            # Handle metadata
            metadata = items_data.pop(0)
            self.scene.mpversion = metadata.get('mpversion', 'unknown')

            repaired_items_data = []
            removed_files = []
            for item_data in items_data:
                if item_data['type'] in ('CustomPixmapItem', 'CustomSvgItem') and not os.path.exists(
                        item_data['filename']):
                    removed_files.append(item_data['filename'])
                else:
                    repaired_items_data.append(item_data)

            with open(self.filename, 'wb') as f:
                pickle.dump(repaired_items_data, f)

                QMessageBox.information(self.scene.parentWindow, 'File Repair', f"""File repair completed: 
Removed missing items with filenames: {', '.join(removed_files)}""")

        except Exception as e:
            print(f"Error repairing file: {e}")

class ImportManager:
    def __init__(self, scene):
        self.canvas = scene

    def importFile(self):
        # Deactivate the add canvas tool
        self.canvas.parentWindow.use_exit_add_canvas()

        file_path, _ = QFileDialog().getOpenFileName(self.canvas.parentWindow, "Insert Element", "", supported_file_importing)

        if file_path:
            if file_path.endswith('.svg'):
                svg_item = CustomSvgItem(file_path)
                svg_item.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, svg_item)
                self.canvas.addCommand(add_command)
                svg_item.setToolTip('Imported SVG')

                self.create_item_attributes(svg_item)

            elif file_path.endswith(('.txt', '.csv')):
                with open(file_path, 'r') as f:
                    item = CustomTextItem(f.read())

                    add_command = AddItemCommand(self.canvas, item)
                    self.canvas.addCommand(add_command)

                    self.create_item_attributes(item)

            elif file_path.endswith('.md'):
                with open(file_path, 'r') as f:
                    item = CustomTextItem(f.read())
                    item.toMarkdown()
                    item.set_locked()

                    add_command = AddItemCommand(self.canvas, item)
                    self.canvas.addCommand(add_command)

                    self.create_item_attributes(item)

            else:
                image1 = QPixmap(file_path)
                image2 = CustomPixmapItem(image1)
                image2.store_filename(file_path)

                add_command = AddItemCommand(self.canvas, image2)
                self.canvas.addCommand(add_command)
                image2.setToolTip('Imported Pixmap')

                self.create_item_attributes(image2)

    def importMPBUILDFile(self):
        pass

    def create_item_attributes(self, item):
        item.setFlag(QGraphicsItem.ItemIsMovable)
        item.setFlag(QGraphicsItem.ItemIsSelectable)

        item.setZValue(0)

class ExportManager:
    def __init__(self, canvas):
        self.canvas = canvas


    def normalExport(self):
        # Exit add canvas tool if active
        self.canvas.parentWindow.use_exit_add_canvas()

        # Create a custom dialog to with a dropdown to select which canvas to export
        selector = CanvasItemSelector(self.canvas, self.canvas.parentWindow)
        selector.show()

        for item in self.canvas.items():
            if isinstance(item, CanvasItem):
                # Add the canvas items to the selector
                selector.add_canvas_item(itemName=item.toolTip(), itemKey=item)

        # Create a function to choose the selected item
        def export():
            index = selector.canvas_chooser_combo.currentIndex()
            data = selector.canvas_chooser_combo.itemData(index)
            selected_item = selector.canvas_chooser_combo.itemData(index)

            if selected_item:
                if selector.transparent_check_btn.isChecked():
                    self.canvas.setBackgroundBrush(QBrush(QColor(Qt.transparent)))

                    for item in self.canvas.items():
                        if isinstance(item, CanvasItem):
                            item.setTransparentMode()

                self.filterSelectedCanvasForExport(selected_item)

            else:
                QMessageBox.warning(self.canvas.parentWindow,
                                    'Export Selected Canvas',
                                    'No canvas elements found within the scene. '
                                    'Please create a canvas element to export.',
                                    QMessageBox.Ok)

        selector.export_btn.clicked.connect(export)

    def multipleExport(self):
        selector = AllCanvasExporter(self.canvas, self.canvas.parentWindow)
        selector.show()

    def exportAsBitmap(self, filename, selected_item):
        # Create a QImage with the size of the selected item (QGraphicsRectItem)
        rect = selected_item.sceneBoundingRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)

        print(rect)

        # Render the QGraphicsRectItem onto the image
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.canvas.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        try:
            # Save the image to file
            success = image.save(filename)

            if success:
                # If saving was successful, show a notification
                QMessageBox.information(self.canvas.parentWindow, "Export Finished", "Export completed successfully.")

                # Open the image with the default image viewer
                QDesktopServices.openUrl(QUrl.fromLocalFile(filename))

        except Exception as e:
            # If saving failed, show an error notification
            QMessageBox.critical(self.canvas.parentWindow, "Export Error", f"Failed to export canvas to file: {e}")

    def exportAsSVG(self, file_path, selected_item):
        try:
            # Get the bounding rect
            rect = selected_item.sceneBoundingRect()

            # Export as SVG
            svg_generator = QSvgGenerator()
            svg_generator.setFileName(file_path)
            svg_generator.setSize(rect.size().toSize())
            svg_generator.setViewBox(rect)

            # Clear selection
            self.canvas.clearSelection()

            # Create a QPainter to paint onto the QSvgGenerator
            painter = QPainter()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.begin(svg_generator)

            # Render the scene onto the QPainter
            self.canvas.render(painter, target=rect, source=rect)

            # End painting
            painter.end()

            # Show export finished notification
            QMessageBox.information(self.canvas.parentWindow, 'Export Finished', 'Export completed successfully.',
                                    QMessageBox.Ok)

            # Open the image with the default image viewer
            QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

        except Exception as e:
            # Show export error notification
            QMessageBox.information(self.canvas.parentWindow, 'Export Failed', f'Export failed: {e}',
                                    QMessageBox.Ok)

    def exportAsPDF(self, file_path, selected_item):
        try:
            printer = QPrinter()
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            painter = QPainter()
            painter.begin(printer)

            # Render your content directly onto the painter
            self.canvas.render(painter, source=selected_item.sceneBoundingRect(),
                               target=selected_item.sceneBoundingRect())

            painter.end()

        except Exception as e:
            print(e)

        # Show export finished notification
        QMessageBox.information(self.canvas.parentWindow, 'Export Finished', 'Export completed successfully.',
                                QMessageBox.Ok)

        # Open the image with the default image viewer
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def filterSelectedCanvasForExport(self, selected_item):
        self.canvas.parentWindow.use_exit_add_canvas()
        self.canvas.parentWindow.select_btn.trigger()

        # File dialog, filepath
        file_dialog = QFileDialog()

        file_path, selected_filter = file_dialog.getSaveFileName(self.canvas.parentWindow, 'Export Canvas', '',
                                                                 supported_file_exporting)

        if file_path:
            selected_extension = filter_extensions.get(selected_filter, '.png')

            # Ensure the file_path has the selected extension
            if not file_path.endswith(selected_extension):
                file_path += selected_extension

            if selected_extension == '.svg':
                self.exportAsSVG(file_path, selected_item)

            elif selected_extension == '.pdf':
                self.exportAsPDF(file_path, selected_item)

            else:
                try:
                    self.canvas.clearSelection()
                    self.exportAsBitmap(file_path, selected_item)

                except Exception as e:
                    print(e)

            self.canvas.parentWindow.use_exit_add_canvas()
