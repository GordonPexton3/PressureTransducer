import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget,QVBoxLayout
from PyQt5.QtCore import pyqtSlot
from Tabs import Tabs
from ThreadTab import ThreadTab
from time import time

width = 500
height = 300

class PressureTransducerApps(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'PressureTransducers'
        self.left = 0
        self.top = 0
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, width, height)
        
        self.main_widget = PressureTransducerWidgit(self)
        self.setCentralWidget(self.main_widget)
        
        self.show()
    
class PressureTransducerWidgit(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout()

        self.layout.addWidget(Tabs())

        self.setLayout(self.layout)

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = PressureTransducerApps()
        sys.exit(app.exec_())
    except Exception as a:
        print(a)
        while(True):
            time.sleep(1)


# python -m auto_py_to_exe 
# command to make this an executable

# python -m auto_py_to_exe 
# python -m pip install pyinstaller --upgrade

