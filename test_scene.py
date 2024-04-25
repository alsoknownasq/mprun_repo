from graphics_framework import *

class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('MPRUN Beta Test Scene')
        
        self.create_ui()
        
    def create_ui(self):
        self.canvas = QGraphicsScene()
        self.canvas_view = CustomGraphicsView()
        
        self.canvas_view.setScene(self.canvas)
        
        self.setCentralWidget(self.canvas_view)
        
        
        
if __name__ == '__main__':
    win = QApplication([])
    app = MainWin()
    app.show()
    win.exec_()