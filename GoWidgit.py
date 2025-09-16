from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import pyqtSlot, QThreadPool, QThread, pyqtSignal
from InputWidget import InputWidget
from ConnectionWidgit import ConnectionWidgit
from DisplayPressureWidget import DisplayPressureWidget
from datetime import datetime, timedelta
import csv
from PyQt5.QtCore import QThread, pyqtSignal
import time


'''
### Purpose 
The GoWidgit contains all the logic that runs the data looging operation and interacts with 
all the other widgits in the GUI to provide the complete UI experience for one tab/
program instance. 
### Important note
GoWidgit has been designated to hold all the widgets instatiated for the tab that was 
created. This is because GoWidgit contains the code that starts the independed thread, 
that thread must have access to the instances of the other coponents to update 
them real time. '''
class GoWidgit(QWidget):

    cancel = pyqtSignal()

    seconds_in_hour = 3600
    seconds_in_minute = 60

    def __init__(self, display_pressure_widget):
        super().__init__()

        ### GUI Setup
    
        self.layout = QGridLayout()

        self.input_widget: InputWidget = None
        self.connection_widget: ConnectionWidgit = None
        self.display_pressure_widget: DisplayPressureWidget = display_pressure_widget

        self.go_button = QPushButton("GO")
        self.go_button.clicked.connect(self.go_button_action)
        self.layout.addWidget(self.go_button,0,0)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_button_action)
        self.layout.addWidget(self.cancel_button,1,0)
        self.cancel_button.setDisabled(True)

        self.start_time_label = QLabel("Start Time")
        self.layout.addWidget(self.start_time_label,0,1)

        self.end_time_label = QLabel("End Time")
        self.layout.addWidget(self.end_time_label,1,1)

        self.reconnect_go_button = QPushButton("Reconnect and Go")
        self.reconnect_go_button.clicked.connect(self.reconnect_go_button_action)
        self.reconnect_go_button.setDisabled(True)
        self.layout.addWidget(self.reconnect_go_button,2,0)
        
        self.setLayout(self.layout)

        # Initially disabling go widget
        self.setEnabled(False)
        
        ### Thread Setup
    
        self.thread_recorder = Recorder()
        self.thread_recorder.go_widget = self
        # this connects the cancel emitter to a slot in the recorder. 
         # this is to cancel a run after it has been started. 
        
        self.cancel.connect(self.thread_recorder.cancel)
        # this connects the recorder_error_handle to the singal inside the thread if an error occured. 
        self.thread_recorder.error.connect(self.recorder_error_handle)
        # This connects the display presure readings fucntion to an emitter in the thread such that 
        # pressure readings should be seen outside the thread. 
        self.thread_recorder.pressure_reading.connect(self.display_pressure_widget.add_pressure_reading)
        self.thread_recorder.finished.connect(self.finished)


    '''
    This is the action that takes place when the go button is pressed 
    which reads the inputs, 
    creats a file, 
    updates the GUI, 
    starts a thread, 
    connects the cancel button action with a signal and slot. etc 
    '''
    def go_button_action(self):
        self.start_with_new_file()

    def start_without_new_file(self):
        try:
            self.start_general()
        except Exception as a:
            self.connection_widget.status_box.setText(f"Go Command Failed: {a}")

    def start_with_new_file(self):
        try:
            self.read_inputs()
            self.create_file()
            self.start_general()
        except Exception as a:
            self.connection_widget.status_box.setText(f"Go Command Failed: {a}")

    def start_general(self):
        try:
            self.display_pressure_widget.clear_widgit()
            # Time calculations for the sampling period. 
            current_time = datetime.now()
            self.end_time = current_time + timedelta(seconds=self.duration_sec)
            self.start_time_label.setText(f"Start Time is {self.format_time_string(current_time)}")
            self.end_time_label.setText(f"End Time is {self.format_time_string(self.end_time)}")
            # Enabling and disabling things for running
            self.enable_cancel_button_only(True)
            # START THREAD
            self.thread_recorder.start()
        except Exception as a:
            self.connection_widget.status_box.setText(f"Go Command Failed: {a}")

    def create_file(self):
        with open(self.file_name, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Time Stamps','Pressure (PSI)'])

    '''
    This reads the inputs from the inputs widgit and throws exceptions with appropriate
    error messages that eventually get put on the GUI outside of this fucntion
    '''
    def read_inputs(self):
        # Getting duration 
        try:
            self.duration_sec = self.read_time_to_seconds(self.input_widget.duration_input_box.text())
        except:
            raise Exception("Duration Input Invalid")
        # Getting interval 
        try:
            self.thread_recorder.interval_sec = self.read_time_to_seconds(self.input_widget.interval_input_box.text())
            # with both values calculated now give recorder the total number of samples. 
            self.thread_recorder.total_num_samples = int(self.duration_sec / self.thread_recorder.interval_sec)
        except:
            raise Exception("Interval Input Invalid")
        # Getting name
        self.file_name = self.input_widget.file_name_input_box.text()
        if self.file_name.strip() == "":
            raise Exception("Must provide a file name")        
    def read_time_to_seconds(self, text: str):
        split_list = text.split(":")
        return int((self.seconds_in_hour * float(split_list[0].strip())) + (self.seconds_in_minute * float(split_list[1].strip())))  


    '''
    This function is called at the end of the recording threats operation
    '''
    def finished(self):
        self.connection_widget.status_box.setText("DONE! Reconnect to Arduino to restart")
        self.thread_end_reset()

    '''
    The reconnect and go button action will do the following
    '''
    def reconnect_go_button_action(self):
        if self.connection_widget.COM_connect_action():
            self.start_without_new_file()
            self.connection_widget.status_box.append(f"{self.thread_recorder.total_num_samples} of {int(self.duration_sec / self.thread_recorder.interval_sec)} samples left")

    '''
    This is a helper function for go_widget.finished and cancel button action
    '''
    def thread_end_reset(self):
        self.connection_widget.arduino_serial.close()
        self.input_widget.setEnabled(False)
        self.setEnabled(False)
        self.connection_widget.COM_input_box.clear()
        self.start_time_label.setText("Start Time is ")
        self.end_time_label.setText("End Time is ") 

    def enable_go_button_and_input_only(self, state: bool):
        self.setEnabled(True)
        self.go_button.setEnabled(state)
        self.input_widget.setEnabled(state)
        self.cancel_button.setEnabled(not state)
        self.reconnect_go_button.setEnabled(not state)

    def enable_go_button_only(self, state: bool):
        self.setEnabled(True)
        self.go_button.setEnabled(state)
        self.input_widget.setEnabled(not state)
        self.cancel_button.setEnabled(not state)
        self.reconnect_go_button.setEnabled(not state)

    def enable_cancel_button_only(self, state: bool):
        self.go_button.setEnabled(not state)
        self.input_widget.setEnabled(not state)
        self.cancel_button.setEnabled(state)
        self.reconnect_go_button.setEnabled(not state)

    def enable_cancel_and_reconnect_buttons_only(self, state: bool):
        self.go_button.setEnabled(not state)
        self.input_widget.setEnabled(not state)
        self.cancel_button.setEnabled(state)
        self.reconnect_go_button.setEnabled(state)

    ############################################
    ### METHODS EXCLUSIVELY FOR RECORDER.RUN ###
    ############################################

    ### SLOT METHODS FOR RECORDER.RUN

    '''
    This function will cancel a session that started a reading
    '''
    def cancel_button_action(self):
        self.cancel.emit()
        self.connection_widget.status_box.setText("CANCELED! Reconnect to Arduino to restart")
        self.thread_end_reset()

    '''
    Reconnect and go should be called after a fatal error during data logging 
    has occured. At this point the thread has terminated and will need to be
    reset and restarted. 
    This function should do the following 
    * print to the status screen that recording has been interrupted 
    * State the progress in number of samples taken. 
    * State the error messsage. 
    '''
    def recorder_error_handle(self, info_lst: list):
        # print to the screen the status. 
        self.connection_widget.status_box.setText(f"Progress in samples ({info_lst[0]}/{self.thread_recorder.total_num_samples})\n ERROR {str(info_lst[1])}\n")
        self.enable_cancel_and_reconnect_buttons_only(True)
        # print("Total num samples" + str(self.thread_recorder.total_num_samples))
        # print(f"num samples taken {info_lst[0]}")
        # print(f"The subtraction of the two {self.thread_recorder.total_num_samples - info_lst[0]}")
        # print("Setting one to the other and dispaly")
        self.thread_recorder.total_num_samples = self.thread_recorder.total_num_samples - info_lst[0]
        print("error detected in main thread")
        print(self.thread_recorder.total_num_samples)
        

    ### METHODS USED BY THE THREAD !!! RACE CONDITION POSSIBLE ###
    
    '''
    No race conditions should exist when calling this function from the logging thread 
    because this function is exclusively used by the logging thread
    '''
    def format_time_string(self, time: datetime):
        return str(time.strftime('%Y-%m-%d %H:%M:%S'))
    
    '''
    No race conditions should exist when calling this function from the logging thread 
    because this function is exclusively used by the logging thread
    '''
    def write_to_file(self, data):
        with open(self.file_name, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(data)









'''
The recorder class is exactly that, it is a thread that loggs the data. 
It has the go widget passed to it, so by default it also has access to all other widget classes 
in this instance of the tread. 
'''
class Recorder(QThread):
    # This is used by the go widget to handle errors without failure. 
    error = pyqtSignal(list)
    # This is used by go widget to know when the thread is done. 
    finished = pyqtSignal()
    # This emitter is used by the diplay presure readings class
    pressure_reading = pyqtSignal(str)

    '''
    The display pressure widgit and go wigit instances are passed to the recorder class because it is
    the class that handles the thread. While the thread is executing it needs to communicate with the 
    instances of the go wigdit and the display pressure readings wigit
    '''
    def __init__(self):
        super().__init__()
        self.break_loop = False
        self.go_widget: GoWidgit = None
        self.interval_sec = None
        self.total_num_samples = None

    '''
    This will handel all the data recording 
    '''
    def run(self):
        next_time = time.perf_counter() + self.interval_sec
        for sample_num in range(self.total_num_samples):
            print(f"Number of samples {sample_num}")
            # Breaking loop
            if self.break_loop:
                self.break_loop = False
                return
            # Getting a reading
            try:
                pressure = self.go_widget.connection_widget.read_pressure()
                self.pressure_reading.emit(pressure)
                self.go_widget.write_to_file([self.go_widget.format_time_string(datetime.now()), pressure])
            except Exception as a:
                self.error.emit([sample_num, a])
                print("excetionp detected in recorder.run")
                return
            # Wait here until the next cycle 
            while time.perf_counter() < next_time:
                if self.break_loop:
                    self.break_loop = False
                    return
                QThread.msleep(50)  # sleep for 50 ms chunks instead of 1 sec
            next_time = time.perf_counter() + self.interval_sec 
        # Once Finishded
        self.finished.emit()

    @pyqtSlot()
    def cancel(self):
        self.break_loop = True
        


'''
GOOD PRACTICE FOR ME TO REMEMBER
* Safe pattern:
Set thread attributes in the main thread before .start().
Treat them as “frozen configuration” once the worker starts.
* If you need to change variables dynamically while the thread runs, better practice is:
Use signals/slots to push new values into the worker safely.
Or add proper thread synchronization (lock/queue).
'''            