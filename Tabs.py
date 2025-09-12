from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSlot
from ThreadTab import ThreadTab

'''
The tabs widget is the main occupying widget of the application. Everything is built off
it. From the Tabs widget, threadTabs are made. They are called thread tabs because 
they each will host a thread (which is the loggin process) and will act like a thread
because they will have unique instances of all the widgets in that tab so that
each tab can operate independently. 
This mainly controls the ability to click the plus (+) tab at the top of the 
applcation and create another tab. 
'''
class Tabs(QWidget):
    def __init__(self):
        super().__init__()

        self.num_sensors = 1

        self.layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tabs.addTab(ThreadTab(), f"Sensor {str(self.num_sensors)}")
        self.tabs.addTab(QWidget(), "+")

        self.tabs.currentChanged.connect(self.change_tab_event)

        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

    def change_tab_event(self, int):
        tabs_len = self.tabs.count() - 1
        if int == tabs_len:
            self.num_sensors += 1
            self.tabs.insertTab(tabs_len, ThreadTab(), f"Sensor {str(self.num_sensors)}")
            self.tabs.setCurrentIndex(tabs_len)



       