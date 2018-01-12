import sys
import mne
import logging
import threading
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from pylsl import StreamInlet, resolve_stream
from PyQt5.QtGui import QIcon, QFont


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

        initbtn = QPushButton("Initilize", self)
        initbtn.move(30, 100)

        plotbtn = QPushButton("Plot", self)
        plotbtn.move(150, 100)

        startbtn.clicked.connect(self.start_recording)
        stopbtn.clicked.connect(self.stop_recording)
        initbtn.clicked.connect(self.init_recording)
        plotbtn.clicked.connect(self.plot_signals)

        self.statusBar()
        self.statusBar().showMessage('Click Init')

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Recorder 1.0')
        self.setWindowIcon(QIcon("./Static/Images/icon.jpg"))
        self.show()

        #init Variables
        self.recordFlag = True

    def start_recording(self):
        self.flag_event.set()
        self.statusBar().showMessage('Starting the Recording')
        startThread = threading.Thread(name='record', target=self.record)
        # startThread.setDaemon(True)
        startThread.start()
        self.statusBar().showMessage('Recording')

    def stop_recording(self):
        self.flag_event.clear()
        self.statusBar().showMessage('Recording Stopped')
        print('boo ya')

    def init_recording(self):
        self.statusBar().showMessage('Initialising...')
        self.streams = resolve_stream('type', 'EEG')
        self.inlet = StreamInlet(self.streams[0])
        self.timeObj = []
        self.sampleObj = []

    def record(self):
        n_channels = 32
        sampling_rate = 500
        channel_types = 'eeg'
        info = mne.create_info(ch_names=n_channels, sfreq=sampling_rate, ch_types=channel_types)

        while self.flag_event.is_set():
            sample, timestamp = self.inlet.pull_sample()
            self.timeObj.append(timestamp)
            self.sampleObj.append(sample)
            self.data = np.array(self.sampleObj).reshape((n_channels, -1)) * 1e-6
            custom_raw = mne.io.RawArray(self.data, info)
            custom_raw.save("./Data/sample_raw.fif", overwrite=True)

            # print(self.data.shape)
            # if (self.data.shape[1]+1) % sampling_rate == 0:
            #     # custom_raw = mne.io.RawArray(self.data, info)
            #     # custom_raw.plot()
            #     # plt.plot(self.timeObj, data.T * 1e-6)
            #     # plt.pause(0.05)
            #     # plt.show()
            #     ani = animation.FuncAnimation(fig, self.animate, interval=10)
            #     plt.pause(0.05)
            #     plt.show()

    # def animate(self, i):
    #     # xar = self.timeObj
    #     yar = self.data.T[0, :]
    #     ax1.clear()
    #     ax1.plot(yar)

    def plot_signals(self):
        # TODO: Change the info attribute later. Find a way to automatically set it
        # n_channels = 32
        # sampling_rate = 500
        # channel_types = 'eeg'
        # info = mne.create_info(ch_names=n_channels, sfreq=sampling_rate, ch_types=channel_types)
        #
        # print("Plot!!!")
        #
        # while self.flag_event.is_set():
        #     data = np.array(self.sampleObj).reshape((n_channels, -1))
        #     custom_raw = mne.io.RawArray(data, info)
        #     custom_raw.plot()

        # Currently showing saved data
        raw = mne.io.read_raw_fif("./Data/sample_raw.fif")
        raw.plot()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())