from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot
import serial
import time

class DisplayPressureWidgit(QWidget):

    '''
    the display pressure widget will display the pressure for the last n readings in a box below the
    go widget
    '''
    def __init__(self):
        super().__init__()
        
        # used to store the n last pressure readings and display them in GUI
        self.n_readings = 30
        self.last_pressure_readings = []

        self.layout = QVBoxLayout()

        self.pressure_readings_box = QTextEdit()
        self.pressure_readings_box.setReadOnly(True)
        self.pressure_readings_box.setFixedSize(400, 400)
        self.layout.addWidget(self.pressure_readings_box)

        self.setLayout(self.layout)


    '''
    Used to add a pressure to the self.last_pressure_readings list. Takes in a number for the pressure. 
    '''
    def add_pressure_reading(self, pressure_reading):
        self.last_pressure_readings.append(pressure_reading)
        if len(self.last_pressure_readings) > self.n_readings:
            self.last_pressure_readings.pop(0)
        self.display_pressure_readings()

    '''
    Will display the current readings of pressure in the pressure readinds box
    '''
    def display_pressure_readings(self):
        self.pressure_readings_box.setPlainText(self.lst_to_str(self.last_pressure_readings))

    def clear_widgit(self):
        self.pressure_readings_box.clear()
        self.last_pressure_readings = []

    '''
    Converts the pressure readings list into a well formatted string. 
    '''
    def lst_to_str(self, lst):
        result_string = ""
        for pressure in lst:
            result_string += str(pressure) + "\n"
        result_string = result_string[:-1]
        return result_string

