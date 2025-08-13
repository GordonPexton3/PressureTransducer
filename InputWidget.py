from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit
from PyQt5.QtCore import pyqtSlot

class InputWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.layout = QGridLayout()

        self.layout.addWidget(QLabel("Duration H:M"),0,0)
        self.layout.addWidget(QLabel("Interval H:M"),1,0)
        self.layout.addWidget(QLabel("File Name"),2,0)
        
        self.duration_input_box = QLineEdit()
        self.interval_input_box = QLineEdit()
        self.file_name_input_box = QLineEdit()

        self.layout.addWidget(self.duration_input_box,0,1)
        self.layout.addWidget(self.interval_input_box,1,1)
        self.layout.addWidget(self.file_name_input_box,2,1)
        
        self.setLayout(self.layout)
