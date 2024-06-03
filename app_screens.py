from PIL import Image
from PyQt5 import QtWidgets, QtGui, QtCore
from custom_widgets import *
import sys

class AboutWin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('About MPRUN')
        self.setWindowIcon(QtGui.QIcon('logos and icons/Main Logos/MPRUN_icon.ico'))
        self.setFixedSize(500, 900)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet('border-radius: 5px;')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.create_ui()

    def create_ui(self):
        # Create main layout
        layout = QtWidgets.QVBoxLayout()

        # App image and label
        mprun_img_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("logos and icons/Main Logos/MPRUN_logoV3.png").scaled(80, 80,
                                                                                                           QtCore.Qt.KeepAspectRatio)
        mprun_img_label.setPixmap(pixmap)
        mprun_img_label.move(20, 20)

        # Text label
        text = '''ABOUT:
        
MPRUN is a proof of concept that computer software can be useful for 
Snowboard and Ski Athletes to help plan competition runs, tricks, or even goals.

Development started in late January 2024, when athlete Keller Hydle realized the 
power of building apps. 

Keller saw a missed opportunity when it came to Snowboard Competitions, there was really no way to create a solid plan for any event. That's when he came up with MPRUN, a software that would assist athletes in creating comp runs. 

Some athletes (including Keller) struggle with creating good plans, especially for big events like Rev-Tour, and that's where MPRUN comes in. 

MPRUN allows users to visualize comp runs on computer and paper, quickly and easily. It includes a proper toolset to create documents that match course setups, draw lines, and label tricks along the course. 

LICENCE:

This program is free software and is distributed under the GNU General Public License, version 3. In short, this means you are free to use and distribute MPRUN for any purpose, commercial or non-commercial, without any restrictions. 

You are also free to modify the program as you wish, with the only restriction that if you distribute the modified version, you must provide access to its source code.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. For more details about the license, check the LISCENSE.txt file included with this distribution.


FILES MADE USING MPRUN:

All files either saved or exported from MPRUN in any format (SVG, PNG, JPG, etc.) are owned by the creators of the work (that's you!) and/or the original authors in case you use derivative works. 
You are responsible for publishing your work under a license of your choosing and for tracking your use of derivative works in the software.
        '''
        label = QtWidgets.QLabel(text, self)
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.move(20, 190)

        credits_label = QLinkLabel('Credits', 'https://docs.google.com/document/d/1r-HFww2g-71McWNktCsRq363_n6Pjlog89ZnsTmf3ec/edit?usp=sharing')
        contact_label = QLinkLabel('Contact Us', 'mailto:ktechindustries2019@gmail.com')

        # Add widgets to layout
        layout.addWidget(mprun_img_label)
        layout.addWidget(label)
        layout.addWidget(credits_label)
        layout.addWidget(contact_label)

        # Set layout to the main window
        self.setLayout(layout)

    def mousePressEvent(self, event):
        self.close()

class VersionWin(QtWidgets.QWidget):
    def __init__(self, version):
        super().__init__()

        self.setWindowTitle('MPRUN Version')
        self.setWindowIcon(QtGui.QIcon('logos and icons/Main Logos/MPRUN_icon.ico'))
        self.setFixedSize(500, 250)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.version = version

        self.create_ui()

    def create_ui(self):
        # Create main layout
        layout = QtWidgets.QVBoxLayout()

        # App image and label
        mprun_img_label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("logos and icons/Main Logos/MPRUN_logoV3.png").scaled(80, 80,
                                                                                                           QtCore.Qt.KeepAspectRatio)
        mprun_img_label.setPixmap(pixmap)
        mprun_img_label.move(20, 20)

        # Text label
        text = f'''
{self.version}

Copyright © K-TECH Industries 2024, All rights reserved.

If you encounter any issues or have suggestions for improvements, contact us at:
        '''
        label = QtWidgets.QLabel(text, self)
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft)
        label.move(20, 190)

        email_label = QLinkLabel('K-TECH Industries', 'mailto:ktechindustries2019@gmail.com')

        # Add widgets to layout
        layout.addWidget(mprun_img_label)
        layout.addWidget(label)
        layout.addWidget(email_label)

        # Set layout to the main window
        self.setLayout(layout)

    def mousePressEvent(self, e):
        self.close()

class FindActionWin(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowIcon(QIcon('logos and icons/Main Logos/MPRUN_icon.ico'))
        self.setWindowTitle('Find Action')
        self.setFixedHeight(500)
        self.setFixedWidth(300)

        # Create a QVBoxLayout and set it as the layout for the QWidget
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Create a QLineEdit for searching
        self.searchInput = QtWidgets.QLineEdit()
        self.searchInput.setObjectName('modernLineEdit')
        self.searchInput.setPlaceholderText("Search actions...")

        # Create a QListWidget
        self.listWidget = QtWidgets.QListWidget()

        # Add some items to the QListWidget
        self.actions = ['Action 1', 'Action 2', 'Action 3', 'Action 4']
        self.listWidget.addItems(self.actions)

        # Add the search input and the QListWidget to the layout
        layout.addWidget(self.searchInput)
        layout.addWidget(self.listWidget)

        # Connect the textChanged signal of the search input to the search method
        self.searchInput.textChanged.connect(self.searchActions)

    def searchActions(self):
        # Get the search text
        searchText = self.searchInput.text().lower()

        # Clear the QListWidget
        self.listWidget.clear()

        # Filter actions based on search text and add them back to the QListWidget
        filteredActions = [action for action in self.actions if searchText in action.lower()]
        self.listWidget.addItems(filteredActions)



if __name__ == '__main__':
    app = VersionWin()
    app.mainloop()
