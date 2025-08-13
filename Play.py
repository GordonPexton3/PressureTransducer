from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QCoreApplication
import sys
import time

class Worker(QObject):
    # Signal to send data back to main
    dataReady = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    @pyqtSlot(str)
    def receive_data(self, value):
        print(f"[Thread] Received from main: {value}")
        # Do something with value...
        time.sleep(2)
        self.dataReady.emit(f"Processed: {value}")

class MainController(QObject):
    sendToWorker = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.thread = QThread()
        self.worker = Worker()

        self.worker.moveToThread(self.thread)

        # Connect signal to slot
        self.sendToWorker.connect(self.worker.receive_data)
        self.worker.dataReady.connect(self.handle_result)

        self.thread.start()

    def handle_result(self, result):
        print(f"[Main] Got result from thread: {result}")

    def send_data_to_worker(self, value):
        print(f"[Main] Sending to thread: {value}")
        self.sendToWorker.emit(value)

if __name__ == "__main__":
    app = QCoreApplication(sys.argv)

    mc = MainController()
    mc.send_data_to_worker("BREH")

    sys.exit(app.exec_())
