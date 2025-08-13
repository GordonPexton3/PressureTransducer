from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot
from ConnectionWidgit import ConnectionWidgit
from InputWidget import InputWidget
from GoWidgit import GoWidgit
from DisplayPressureWidgit import DisplayPressureWidgit


class ThreadTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.input_widget = InputWidget()
        self.go_widget = GoWidgit()
        self.connection_widget = ConnectionWidgit(self.input_widget, self.go_widget)
        self.display_pressure_widgit = DisplayPressureWidgit()

        '''Go wiget needs these instance of the other widgets to manage them while running the thread'''
        self.go_widget.status_box = self.connection_widget.status_box
        self.go_widget.input_widget = self.input_widget
        self.go_widget.connection_widget = self.connection_widget
        self.go_widget.display_pressure_widgit = self.display_pressure_widgit

        # This is the organization of each tab of the GUI. 
        # There is a connection section, a input section, a section to get the program going, and a section to 
        # view the pressure readings, all in that order. 
        self.layout.addWidget(self.connection_widget)
        self.layout.addWidget(self.input_widget)
        self.layout.addWidget(self.go_widget)
        self.layout.addWidget(self.display_pressure_widgit)
        
        self.setLayout(self.layout)

    

    