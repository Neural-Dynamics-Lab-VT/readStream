import sys
import mne
import logging
import threading
import numpy as np
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication
from pylsl import StreamInlet, resolve_stream
from PyQt5.QtGui import QIcon, QFont


class ReadStream(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.flag_event = threading.Event()  # Used to check a running thread

    def initUI(self):
        """
        Initializes the app UI and display it.
        """
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

    def start_recording(self):
        """
        Event handler when the Start recording button is pressed.
        Launches a thread and starts receiving data from a EEG stream.
        """
        self.flag_event.set()
        self.statusBar().showMessage('Starting the Recording')
        startThread = threading.Thread(name='record', target=self.record)
        startThread.start()
        self.statusBar().showMessage('Recording')

    def stop_recording(self):
        """
        Event handler when Stop recording button is pressed.
        Currently does nothing but that.
        """
        self.flag_event.clear()
        self.statusBar().showMessage('Recording Stopped')
        print('boo ya')

    def init_recording(self):
        """
        Housekeeping before starting the EEG stream.
        :return:
        """
        self.statusBar().showMessage('Initialising...')
        self.streams = resolve_stream('type', 'EEG')
        self.inlet = StreamInlet(self.streams[0])
        self.timeObj = []
        self.sampleObj = []

    def record(self):
        """
        Start receiving and converting data to python-mne format and save it.
        """

        # TODO: Make the Metadata transmission automatic
        n_channels = 32
        sampling_rate = 500
        channel_types = 'eeg'

        # Info class required by mne
        info = mne.create_info(ch_names=n_channels, sfreq=sampling_rate, ch_types=channel_types)

        while self.flag_event.is_set():
            sample, timestamp = self.inlet.pull_sample()
            self.timeObj.append(timestamp)
            self.sampleObj.append(sample)
            self.data = np.array(self.sampleObj).reshape((n_channels, -1)) * 1e-6
            if (self.data.shape[1]+1) % sampling_rate == 0:
                custom_raw = mne.io.RawArray(self.data, info)
                custom_raw.save("./Data/sample_raw.fif", overwrite=True)

            # TODO: Finish real time data plotting
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    rS = ReadStream()
    sys.exit(app.exec_())