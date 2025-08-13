from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSlot
from ThreadTab import ThreadTab

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



       