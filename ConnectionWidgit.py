from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLineEdit, QPushButton
import serial
import time

'''
This widgit in the GUI is responsible for interacting with the user to 
establish connection with the Arduino. 
It also hosts a read only bo which communicates a lot of information to the 
user. 
It also manages the continual connection with the Arduino and 
provides the functions necesary to read from it. 
'''

class ConnectionWidgit(QWidget):

    def __init__(self, go, message = "Status Box"):
        super().__init__()

        self.go_widget = go

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

    # The return value lets the caller know if it was sucessful. 
    def COM_connect_action(self) -> False:
        try:
            COM_num: int = self.get_COM_input()
            self.arduino_serial = self.get_serial_connection(COM_num)
            self.varify_is_correct_hardware()
            self.status_box.setText("Serial Connection Success")
            self.go_widget.enable_go_button_and_input_only(True)
            return True
        except Exception as a:
            self.status_box.setText(f"Serial Connection to Arduino Failed: {a}")
            try:
                self.arduino_serial.close()
            except:
                ...
            return False
    
    def get_COM_input(self):
        try:
            return int(self.COM_input_box.text())
        except:
            raise Exception("That is not an integer")
    
    def get_serial_connection(self, COM_num):
        try:
            return serial.Serial(f"COM{COM_num}", 9600, timeout=1)
        except:
            raise Exception("Connection not available")
    
    def varify_is_correct_hardware(self):
        time.sleep(1)
        line_list = self.read_line().split()
        if line_list == [] or line_list[0] != "ARDU":
            raise Exception("Not a pressure sensor")
        

    ############################################
    ### METHODS EXCLUSIVELY FOR RECORDER.RUN ###
    ############################################


    '''
    No race conditions should exist when calling this function from the logging thread 
    because this function is exclusively used by the logging thread
    '''
    def read_line(self) -> str: 
        # Errors here will be caught up in Recorder.run
        self.arduino_serial.read_all()
        return self.arduino_serial.readline().decode('utf-8').strip()
    
    '''
    No race conditions should exist when calling this function from the logging thread 
    because this function is exclusively used by the logging thread
    '''
    def read_pressure(self) -> str:
        # if there are little blips I want to try and catch them here so that the only important 
        # errors will require human intervention. 
        for i in range(3):
            error_message: str = None
            try:
                return self.read_line().split()[1]
            except Exception as a: 
                error_message = a
        raise Exception("Reading pressure sensor failed\n" + str(error_message))
            
            
