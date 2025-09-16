import sys
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel


class Worker(QObject):
    bool_changed = pyqtSignal(bool)  # Worker → Main

    def __init__(self):
        super().__init__()
        self._flag = False

    @pyqtSlot(bool)
    def set_flag(self, value):
        """Slot to safely update the worker's boolean"""
        self._flag = value
        print(f"[Worker] Flag updated to: {self._flag}")
        self.bool_changed.emit(self._flag)  # report back to main thread


class MainWindow(QWidget):
    update_worker_flag = pyqtSignal(bool)  # Main → Worker

    def __init__(self):
        super().__init__()

        # UI
        self.label = QLabel("Flag: False", self)
        self.button = QPushButton("Toggle Worker Flag", self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # Thread setup
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.button.clicked.connect(self.toggle_flag)                 # Button → Main
        self.update_worker_flag.c(self.worker.set_flag)         # Main → Worker
        self.worker.bool_changed.connect(self.update_label)           # Worker → Main

        # Start thread
        self.thread.start()

        self.current_flag = False

    def toggle_flag(self):
        """Called in main thread when button is clicked"""
        self.current_flag = not self.current_flag
        print(f"[Main] Sending flag={self.current_flag} to worker")
        self.update_worker_flag.emit(self.current_flag)  # emit to worker

    @pyqtSlot(bool)
    def update_label(self, value):
        """Update UI when worker confirms change"""
        self.label.setText(f"Flag: {value}")
        print(f"[Main] UI updated with {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
