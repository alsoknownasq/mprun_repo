from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *
from custom_classes import *
class AddCanvasDialog(QWidget):
    def __init__(self, canvas, og_rect):
        super().__init__()

        self.canvas = canvas
        self.paper = og_rect

        self.setWindowTitle('Add Canvas')
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setFixedWidth(300)

        self.create_ui()
    def create_ui(self):
        layout = QVBoxLayout()

        button_layout = QVBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width")

        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Canvas Name")

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_canvas)

        # Add widgets, set layout
        button_layout.addWidget(self.width_input)
        button_layout.addWidget(self.height_input)
        button_layout.addWidget(self.name_input)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def create_canvas(self):
        paper_rect = self.paper.boundingRect()

        try:
            width = float(self.width_input.text())
            height = float(self.height_input.text())
            canvas_name = self.name_input.text()
            if width <= 0 or height <= 0:
                QMessageBox.critical(self, 'Incorrect Value', 'Please enter positive number values for width and height.')

            else:
                rect_item = CanvasItem(0, 0, width, height)

                brush = QBrush(QColor('white'))
                pen = QPen(QColor('white'), 2, Qt.SolidLine)
                rect_item.setBrush(brush)
                rect_item.setPen(pen)

                self.canvas.addItem(rect_item)

                rect_item.setZValue(-2)
                rect_item.setPos(paper_rect.width() + 10, 0)
                rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                rect_item.setToolTip(canvas_name)

                self.close()

        except ValueError as e:
            QMessageBox.critical(self, 'Incorrect Value', f'Please enter a correct value: {e}')

class CanvasItemSelector(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Canvas Item")
        self.setWindowIcon(QIcon('logos and icons/MPRUN_logo_rounded_corners_version.png'))
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        self.comboBox = QComboBox()
        layout.addWidget(self.comboBox)

        self.exportButton = QPushButton("Export")
        layout.addWidget(self.exportButton)

    def add_canvas_item(self, itemName, itemKey):
        values = {itemName: itemKey}
        for name, key in values.items():
            self.comboBox.addItem(name, key)



