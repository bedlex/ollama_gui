import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class Worker(QThread):
    # Define a signal that the main thread can emit when it wants to stop the worker thread
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        while self.running:
            print("Worker thread is running...")
            import time
            time.sleep(1)  # Simulate a long-running task

    def stop(self):
        self.running = False

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a label to display the status of the worker thread
        self.label = QLabel("Press the button to start the worker thread")

        # Create a button that will start and stop the worker thread when clicked
        self.button = QPushButton("Start/Stop Thread")
        self.button.clicked.connect(self.start_stop_thread)

        # Create a layout to hold the label and button
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        # Create a central widget and set its layout to the created layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create a worker thread object
        self.worker = Worker()

    def start_stop_thread(self):
        if self.worker.isRunning():
            # If the worker thread is already running, stop it
            self.worker.stop()
            self.label.setText("Press the button to start the worker thread")
        else:
            # If the worker thread is not running, start it
            self.worker.start()
            self.label.setText("Worker thread is running...")

def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()