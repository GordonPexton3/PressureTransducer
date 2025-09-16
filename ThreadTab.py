from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSlot
from ConnectionWidgit import ConnectionWidgit
from InputWidget import InputWidget
from GoWidgit import GoWidgit
from DisplayPressureWidget import DisplayPressureWidget

'''
This class initiates each tab in the GUI while also creating a unique instance of all the widgets 
that each tab uses. 
Then each tab will have it's own threat that will start when the loggin process is iniciated. 
Operation of each tab happens independently allowing the user
to connect as many pressure tranducers as needed to the computer and run them all 
simultaneously. 
'''

class ThreadTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        '''
        These are the funamental widgets that get added to each tab and through which all
        the programs functionality is run
        '''
        self.input_widget = InputWidget()
        self.display_pressure_widget = DisplayPressureWidget()
        # Getting Go-widget the dispay_pressure_widget at startup so that the thread 
        # can be linked immediatly. 
        self.go_widget = GoWidgit(self.display_pressure_widget)
        # Connection widget needs go widget in order to keep it disabled until all 
        # the parameters are right to start running it. 
        self.connection_widget = ConnectionWidgit(self.go_widget)
        
        '''
        Go wiget is the class and widget in which the program loggin thread is started
        and as such it needs the instance of the other widgets to interact with them
        and manage them while running the thread. 
        '''
        self.go_widget.input_widget = self.input_widget
        self.go_widget.connection_widget = self.connection_widget

        '''
        This is the organization of each tab of the GUI. 
        There is a connection section, a input section, a section to get 
        the program going, and a section to 
        view the pressure readings, all in that order. 
        '''
        self.layout.addWidget(self.connection_widget)
        self.layout.addWidget(self.input_widget)
        self.layout.addWidget(self.go_widget)
        self.layout.addWidget(self.display_pressure_widget)
        
        self.setLayout(self.layout)

    

    