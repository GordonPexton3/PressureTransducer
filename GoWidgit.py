from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QTextEdit, QPushButton
from PyQt5.QtCore import pyqtSlot, QThreadPool, QThread, pyqtSignal
from InputWidget import InputWidget
from ConnectionWidgit import ConnectionWidgit
from DisplayPressureWidgit import DisplayPressureWidgit
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

    # this is to cancel a run after it has been started. 
    cancel = pyqtSignal(bool)

    seconds_in_hour = 3600
    seconds_in_minute = 60


    def __init__(self):
        super().__init__()

        ### Thread Setup
    
        self.thread_recorder = Recorder()
        self.thread_recorder.go_widget = self
        # this connects the cancel emitter to a slot in the recorder. 
        self.cancel.connect(self.thread_recorder.cancel)
        # This connects the display presure readings fucntion to an emitter in the thread such that 
        # pressure readings should be seen outside the thread. 
        self.thread_recorder.pressure_reading.connect(self.display_pressure_widgit.add_pressure_reading)
        self.thread_recorder.finished.connect(self.finished)

        ### GUI Setup
    
        self.layout = QGridLayout()

        self.thread_manager = QThreadPool()

        self.input_widget: InputWidget = None
        self.connection_widget: ConnectionWidgit = None
        self.display_pressure_widgit: DisplayPressureWidgit = None

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

    '''
    This is the action that takes place when the go button is pressed 
    which reads the inputs, 
    creats a file, 
    updates the GUI, 
    starts a thread, 
    connects the cancel button action with a signal and slot. etc 
    '''
    def go_button_action(self):
        try:
            self.read_inputs()
            self.create_file()
            self.display_pressure_widgit.clear_widgit()
            # Time calculations for the sampling period. 
            current_time = datetime.now()
            self.end_time = current_time + timedelta(seconds=self.duration_sec)
            self.start_time_label.setText(f"Start Time is {self.format_time_string(current_time)}")
            self.end_time_label.setText(f"End Time is {self.format_time_string(self.end_time)}")
            # Enabling and disabling things for running
            self.go_button.setEnabled(False)
            self.input_widget.setEnabled(False)
            self.cancel_button.setDisabled(False)
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
        try:
            self.thread_recorder.duration_sec = self.read_time_to_seconds(self.input_widget.duration_input_box.text())
        except:
            raise Exception("Duration Input Invalid")
        try:
            self.thread_recorder.interval_sec = self.read_time_to_seconds(self.input_widget.interval_input_box.text())
        except:
            raise Exception("Interval Input Invalid")
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
        self.connection_widget.arduino_serial.close()
        self.connection_widget.disable_app()
        self.cancel_button.setDisabled(True)
        self.connection_widget.COM_input_box.clear()
        self.start_time_label.setText("Start Time is ")
        self.end_time_label.setText("End Time is ")

    '''
    Reconnect and go should be called after a fatal error during data logging 
    has occured. It should do the following 
    * 
    '''
    def reconnect_go_button_action():
        ...

    ############################################
    ### METHODS EXCLUSIVELY FOR RECORDER.RUN ###
    ############################################

    '''
    This function will cancel a session that started a reading
    '''
    def cancel_button_action(self):
        self.cancel.emit(True)
    
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

    # TODO Make all outbound information from the Recorder a pyqt signal
    # TODO make a pyqtSignal() that will emit if the arduino was disconnected. 
    # TODO make an external function that will enable the user to reconnect the arduino
    # TODO once connected make a signal get into the threat to modify the time stamp list and 
    # continue where it left off so that data can continue to be recorded on the same file. 
    finished = pyqtSignal()
    # this is en emitter that will carry pressure readings out of the thread to the main 
    pressure_reading = pyqtSignal(str)

    '''
    The display pressure widgit and go wigit instances are passed to the recorder class because it is
    the class that handles the thread. While the thread is executing it needs to communicate with the 
    instances of the go wigdit and the display pressure readings wigit
    '''
    def __init__(self):
        super().__init__()
        self.stop = False
        self.go_widget = None
        self.duration_sec = None
        self.interval_sec = None

    '''
    This will handel all the data recording 
    '''
    def run(self):
        # This value represents the number of samples to take during the collection period
        samples_in_duration = int(self.duration_sec / self.interval_sec)
        start_time = time.perf_counter()
        # this is a list of all the time intervals where a sample should be collected
        time_intervals = [start_time + (i*self.interval_sec) for i in range(samples_in_duration)]
        # for ever upcoming interval in intervals. 
        for next_interval in time_intervals:
            # wait until the current time has passed the time of the interval 
            while (time.perf_counter() < next_interval) and not self.stop:
                time.sleep(1)
            if self.stop:
                self.stop = False
                break
            time_stamp = self.go_widget.format_time_string(datetime.now())
            '''
            If the arduino gets disconnected then ...read_pressure() will throw an error
            This will catch the error, report that the arduino is disconnected, enable
            a button to reconnect it, verify that it is reconnected, and then resume once
            a connection is established. 
            '''
            '''
            Locate all the things that can throw an error in this loop
            '''
            try:
                pressure = self.go_widget.connection_widget.read_pressure()
            except:
                # TODO redirect to a waiting state (fucntion) to complete the taks described above. 
                # emitting the pressure reading to be put in the displayPressureWidgit
                ...
            # This emission is connected to self.display_pressure_widgit.add_pressure_reading
            # that in turn interacts with the GUI, therefore it must be a singal and slot 
            # to communicate safely. 
            self.pressure_reading.emit(pressure)
            # GPT Says "If the method only does pure Python math, 
            # parsing, or logic → safe, because Python code itself doesn’t care what thread it runs in."
            # Therefore this function call can work. 
            '''
            No race conditions should exist when calling this function from the logging thread 
            because this function is exclusively used by the logging thread
            '''
            self.go_widget.write_to_file([time_stamp, pressure])
            
        self.finished.emit()

    def cancel(self, bool):
        self.stop = True


'''
GOOD PRACTICE FOR ME TO REMEMBER
* Safe pattern:
Set thread attributes in the main thread before .start().
Treat them as “frozen configuration” once the worker starts.
* If you need to change variables dynamically while the thread runs, better practice is:
Use signals/slots to push new values into the worker safely.
Or add proper thread synchronization (lock/queue).
'''            

# Old Bacup Code
# # This value represents the number of samples to take during the collection period
#         samples_in_duration = int(self.duration_sec / self.interval_sec)
#         start_time = time.perf_counter()
#         # this is a list of all the time intervals where a sample should be collected
#         time_intervals = [start_time + (i*self.interval_sec) for i in range(samples_in_duration)]
#         # for ever upcoming interval in intervals. 
#         for next_interval in time_intervals:
#             # wait until the current time has passed the time of the interval 
#             while (time.perf_counter() < next_interval) and not self.stop:
#                 time.sleep(1)
#             if self.stop:
#                 self.stop = False
#                 break
#             time_stamp = self.go_widget.format_time_string(datetime.now())
#             '''
#             If the arduino gets disconnected then ...read_pressure() will throw an error
#             This will catch the error, report that the arduino is disconnected, enable
#             a button to reconnect it, verify that it is reconnected, and then resume once
#             a connection is established. 
#             '''
#             '''
#             Locate all the things that can throw an error in this loop
#             '''
#             try:
#                 pressure = self.go_widget.connection_widget.read_pressure()
#             except:
#                 # TODO redirect to a waiting state (fucntion) to complete the taks described above. 
#                 # emitting the pressure reading to be put in the displayPressureWidgit
#                 ...
#             # This emission is connected to self.display_pressure_widgit.add_pressure_reading
#             # that in turn interacts with the GUI, therefore it must be a singal and slot 
#             # to communicate safely. 
#             self.pressure_reading.emit(pressure)
#             # GPT Says "If the method only does pure Python math, 
#             # parsing, or logic → safe, because Python code itself doesn’t care what thread it runs in."
#             # Therefore this function call can work. 
#             '''
#             No race conditions should exist when calling this function from the logging thread 
#             because this function is exclusively used by the logging thread
#             '''
#             self.go_widget.write_to_file([time_stamp, pressure])
            
#         self.finished.emit()
