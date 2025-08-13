from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLineEdit
from PyQt5.QtCore import pyqtSlot
import serial
import time
import random

class ConnectionWidgit(QWidget):

    silly_silly_haha_list = ["nope", "no pressure for you", "sorry did you need a pressure reading?", "meh", "oops", "battery boy", "are you confused", "Your lucy I didn't break"]

    def __init__(self, input, go, message = "Status Box"):
        super().__init__()

        self.input_widget = input
        self.go_widget = go
        self.disable_app()

        self.status_message = message
        
        self.layout = QVBoxLayout()

        self.COM_input_box = QLineEdit()
        self.COM_input_box.setPlaceholderText("Enter COM Port Number and Press ENTER")
        self.COM_input_box.returnPressed.connect(self.COM_connect_action)
        self.layout.addWidget(self.COM_input_box)

        self.status_box = QTextEdit()
        self.status_box.setText(self.status_message)
        self.status_box.setReadOnly(True)
        self.status_box.setFixedSize(400, 80)
        self.layout.addWidget(self.status_box)

        self.setLayout(self.layout)

    def COM_connect_action(self):
        try:
            COM_num: int = self.get_COM_input()
            self.arduino_serial = self.get_serial_connection(COM_num)
            self.varify_is_correct_hardware()
            self.status_box.setText("Serial Connection Success")
            self.enable_app()
        except Exception as a:
            self.status_box.setText(f"Serial Connection to Arduino Failed: {a}")
            self.disable_app()
            try:
                self.arduino_serial.close()
            except:
                ...
    
    def get_COM_input(self):
        try:
            return int(self.COM_input_box.text())
        except:
            raise Exception("That is not an integer")
    
    def get_serial_connection(self, COM_num):
        try:
            return serial.Serial(f"COM{COM_num}", 9600, timeout=1.5)
        except:
            raise Exception("Connection not available")
    
    def varify_is_correct_hardware(self):
        time.sleep(1)
        line_list = self.read_line().split()
        if line_list == [] or line_list[0] != "ARDU":
            raise Exception("Not a pressure sensor")
        
    def enable_app(self):
        self.input_widget.setEnabled(True)
        self.go_widget.go_button.setEnabled(True)
    
    def disable_app(self):
        self.go_widget.go_button.setEnabled(False)
        self.input_widget.setEnabled(False)

    def read_line(self) -> str:
        self.arduino_serial.read_all()
        return self.arduino_serial.readline().decode('utf-8').strip()
    
    def read_pressure(self) -> str:
        # string_list = self.read_line().split()
        #         return string_list[1])
        # Sometimes the string list is empty, happens rarely, so this catched the error. 
        # return self.silly_silly_haha_list[random.randint(0,len(self.silly_silly_haha_list)-1)]
        pressure = self.read_line().split()[1]
        while( pressure == ""):
            pressure = self.read_line().split()[1]
        return pressure

