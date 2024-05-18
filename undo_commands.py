from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *

class AddItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class EditTextCommand(QUndoCommand):
    def __init__(self, item, old_text, new_text):
        super().__init__()
        self.item = item
        self.old_text = old_text
        self.new_text = new_text

    def redo(self):
        self.item.setPlainText(self.new_text)

    def undo(self):
        self.item.setPlainText(self.old_text)

class RemoveItemCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
        self.removed = False

    def redo(self):
        if not self.removed:
            self.scene.removeItem(self.item)
            self.removed = True

    def undo(self):
        if self.removed:
            self.scene.addItem(self.item)
            self.removed = False

class GraphicsEffectCommand(QUndoCommand):
    def __init__(self, item, amount, og_effect, effect):
        super().__init__()

        self.item = item
        self.amount = amount
        self.og_effect = og_effect
        self.choosenEffect = effect


    def redo(self):
        effect = None

        if self.choosenEffect == 'blur':
            effect = QGraphicsBlurEffect()
            effect.setBlurRadius(self.amount)

        elif self.choosenEffect == 'dropShadow':
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(self.amount)

        self.item.setGraphicsEffect(effect)


    def undo(self):
        self.item.setGraphicsEffect(self.og_effect)

class SmoothPathCommand(QUndoCommand):
    def __init__(self, scene, item, new_path, old_path):
        super().__init__()
        self.scene = scene
        self.item = item
        self.new_path = new_path
        self.old_path = old_path

    def redo(self):
        self.item.setPath(self.new_path)

    def undo(self):
        self.item.setPath(self.old_path)

class ScaleCommand(QUndoCommand):
    def __init__(self, item, old_scale, new_scale):
        super().__init__()
        self.item = item
        self.old_scale = old_scale
        self.new_scale = new_scale

    def redo(self):
        self.item.setScale(self.new_scale)

    def undo(self):
        self.item.setScale(self.old_scale)

class TransformScaleCommand(QUndoCommand):
    def __init__(self, item, x, y, old_scalex, old_scaley):
        super().__init__()
        self.item = item
        self.old_scalex = old_scalex
        self.old_scaley = old_scaley
        self.x = x
        self.y = y

    def redo(self):
        transform = QTransform()
        transform.scale(self.x, self.y)
        self.item.setTransform(transform)

    def undo(self):
        transform = QTransform()
        transform.scale(self.old_scaley, self.old_scalex)
        self.item.setTransform(transform)

class RotateCommand(QUndoCommand):
    def __init__(self, item, old_rotation, new_rotation):
        super().__init__()
        self.item = item
        self.old_value = old_rotation
        self.new_value = new_rotation

    def redo(self):
        self.item.setRotation(self.new_value)

    def undo(self):
        self.item.setRotation(self.old_value)

class MoveItemCommand(QUndoCommand):
    def __init__(self, item, oldPos):
        super().__init__()
        self.item = item
        self.oldPos = oldPos
        self.newPos = item.pos()

    def mergeWith(self, command):
        moveCommand = command
        item = moveCommand.item

        if self.item != item:
            return False

        self.newPos = item.pos()

        return True

    def undo(self):
        self.item.setPos(self.oldPos)

    def redo(self):
        self.item.setPos(self.newPos)

class OpacityCommand(QUndoCommand):
    def __init__(self, item, old_opacity, new_opacity):
        super().__init__()
        self.item = item
        self.old_value = old_opacity
        self.new_value = new_opacity

    def redo(self):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(self.new_value)
        self.item.setGraphicsEffect(effect)

    def undo(self):
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(self.old_value)
        self.item.setGraphicsEffect(effect)

class HideCommand(QUndoCommand):
    def __init__(self, item, old_visible, new_visible):
        super().__init__()
        self.item = item
        self.old_value = old_visible
        self.new_value = new_visible

    def redo(self):
        self.item.setVisible(self.new_value)

    def undo(self):
        self.item.setVisible(self.old_value)

class NameCommand(QUndoCommand):
    def __init__(self, item, old_name, new_name):
        super().__init__()
        self.item = item
        self.old_value = old_name
        self.new_value = new_name

    def redo(self):
        self.item.setToolTip(self.new_value)

    def undo(self):
        self.item.setToolTip(self.old_value)

class CloseSubpathCommand(QUndoCommand):
    def __init__(self, item, scene):
        super().__init__()
        self.item = item
        self.scene = scene
        self.oldPath = self.item.path()
        self.newPath = QPainterPath(self.oldPath)

    def redo(self):
        if self.newPath.elementCount() > 0:
            self.newPath.closeSubpath()
            self.item.setPath(self.newPath)

    def undo(self):
        self.item.setPath(self.oldPath)

class AddTextToPathCommand(QUndoCommand):
    def __init__(self, path, widget, og_value, new_value):
        super().__init__()
        self.item = path
        self.widget = widget
        self.og = og_value
        self.new = new_value

    def redo(self):
        self.item.add_text = self.new
        self.widget.setChecked(self.new)
        self.item.update()

    def undo(self):
        self.item.add_text = self.og
        self.widget.setChecked(self.og)
        self.item.update()

class PathTextChangedCommand(QUndoCommand):
    def __init__(self, item, og, new):
        super().__init__()

        self.item = item
        self.og = og
        self.new = new

    def redo(self):
        self.item.setTextAlongPath(self.new)
        self.item.update()

    def undo(self):
        self.item.setTextAlongPath(self.og)
        self.item.update()

class PathTextSpacingChangedCommand(QUndoCommand):
    def __init__(self, item, og, new):
        super().__init__()

        self.item = item
        self.og = og
        self.new = new

    def redo(self):
        self.item.setTextAlongPathSpacingFromPath(self.new)
        self.item.update()

    def undo(self):
        self.item.setTextAlongPathSpacingFromPath(self.og)
        self.item.update()

class FontChangeCommand(QUndoCommand):
    def __init__(self, item, oldf, newf):
        super().__init__()

        self.item = item
        self.old = oldf
        self.new = newf

    def redo(self):
        self.item.setFont(self.new)
        self.item.update()

    def undo(self):
        self.item.setFont(self.old)
        self.item.update()
