import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from pylsl import StreamInlet, resolve_stream
import logging
import threading

import matplotlib.pyplot as plt

class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.flag_event = threading.Event()

    def initUI(self):
        startbtn = QPushButton("Start Recroding", self)
        startbtn.move(30, 50)

        stopbtn = QPushButton("Stop Recording", self)
        stopbtn.move(150, 50)

        initbtn = QPushButton("Initilise", self)
        initbtn.move(30, 100)

        startbtn.clicked.connect(self.start_recording)
        stopbtn.clicked.connect(self.stop_recording)
        initbtn.clicked.connect(self.init_recording)

        self.statusBar()
        self.statusBar().showMessage('Click Init')

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Recorder 1.0')
        self.show()

        #init Variables
        self.recordFlag = True

    def start_recording(self):
        self.flag_event.set()
        self.statusBar().showMessage('Starting the Recording')
        startThread = threading.Thread(name='record',target=self.record)
        startThread.setDaemon(True)
        startThread.start()
        self.statusBar().showMessage('Recording')

    def stop_recording(self):
        self.flag_event.clear()
        self.statusBar().showMessage('Recording Stopped')
        plt.imshow(self.sampleObj)

        print('boo ya')

    def init_recording(self):
        self.statusBar().showMessage('Initialising...')
        self.streams = resolve_stream('type','EEG')
        self.inlet = StreamInlet(self.streams[0])
        self.timeObj = []
        self.sampleObj = []

    def record(self):
        while self.flag_event.is_set():
            sample, timestamp = self.inlet.pull_sample()
            self.timeObj.append(timestamp)
            self.sampleObj.append(sample)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())