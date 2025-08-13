from PyQt5.QtWidgets import QWidget, QPushButton 
from PyQt5.QtCore import pyqtSlot


class DisplayPressureWidgit(QWidget):

    def __init__(self):
        super().__init__()
    
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_btn_action)
