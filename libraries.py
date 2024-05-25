from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtOpenGL import *
from PyQt5.QtSvg import *
from PyQt5.Qt import *
from graphics_framework import *
from custom_classes import *
from custom_widgets import *
import sys
import os


class DragDropListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(item.data(Qt.UserRole))])
            drag.setMimeData(mime_data)

            # Optional: set a drag image
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.transparent)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.CopyAction | Qt.MoveAction)

class LibraryWidget(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)

        self.current_folder_path = ""

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(HorizontalSeparator())

        self.canvas = canvas

        # Label
        label = QLabel('Libraries (local)')

        # List widget for the library
        self.library_list_widget = DragDropListWidget()
        self.library_list_widget.setStyleSheet('border: none')

        # Library button
        self.open_library_button = QPushButton("Open Library")
        self.reload_library_button = QPushButton("Reload Library")

        # Connect button to the method
        self.open_library_button.clicked.connect(self.open_library)
        self.reload_library_button.clicked.connect(self.reload_library)

        self.layout.addWidget(label)
        self.layout.addWidget(self.open_library_button)
        self.layout.addWidget(self.reload_library_button)
        self.layout.addWidget(self.library_list_widget)

    def open_library(self):
        # Open file dialog to select a folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select Library Folder")

        if folder_path:
            self.current_folder_path = folder_path
            self.load_svg_library(folder_path)

    def reload_library(self):
        if self.current_folder_path:
            self.load_svg_library(self.current_folder_path)

    def load_svg_library(self, folder_path):
        # Clear existing items in the list widget
        self.library_list_widget.clear()

        # List all SVG files in the selected folder
        svg_files = [f for f in os.listdir(folder_path) if f.endswith('.svg')]

        # Check if no SVG files are found
        if not svg_files:
            list_item = QListWidgetItem('No SVG elements found within this folder')
            self.library_list_widget.addItem(list_item)

        else:
            # Add each SVG file to the list widget
            for svg_file in svg_files:
                list_item = QListWidgetItem(svg_file)
                list_item.setData(Qt.UserRole, os.path.join(folder_path, svg_file))
                self.library_list_widget.addItem(list_item)
