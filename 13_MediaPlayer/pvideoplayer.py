#! coding:utf-8
import os
import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

Signal = pyqtSignal
Slot = pyqtSlot

__all__ = ["pVideoPlayer"]


class pVideoPlayer(QWidget):
    def __init__(self, url=None, parent=None):
        QWidget.__init__(self)
        self.setWindowTitle('Video Player')

        # Phonon Objects
        # ***************
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
        self.videoWidget.setMinimumHeight(128)

        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Timer
        # *****
        self.timer = QTimer()
        self.timer.setInterval(1000 / 30)
        self.timer.timeout.connect(self.tock)
        self.timer.start()

        # UI 生成
        # ***************
        self.setupUI()


        # 再生ファイル
        self.url = url
        if url is not None:
            self.set_url(self.url)

    def setupUI(self):

        """UI生成シーケンス.
        可視性を高めるため別に記述
        """


        # Ctrl UI
        self.btn_start = QPushButton('PLAY', self)
        self.btn_start.clicked.connect(self._handle_BtnStart)


        # Seek Bar
        # =========
        self.seek_slider = QSlider(Qt.Horizontal, self)
        # Seek
        self.mediaPlayer.positionChanged.connect(self.seek_slider.setValue)
        self.mediaPlayer.durationChanged.connect(self.seek_slider.setMaximum)
        self.seek_slider.sliderMoved.connect(self.mediaPlayer.setPosition)

        # Volume Bar
        # =========
        self.volume_slider = QSlider(Qt.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.mediaPlayer.setVolume(self.volume_slider.value())
        # Signal Connect
        self.volume_slider.sliderMoved.connect(self.mediaPlayer.setVolume)
        self.mediaPlayer.volumeChanged.connect(self.volume_slider.setValue)


        # Time Label
        self.time_label = QLabel(self)
        self.time_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)

        # Status Label
        self.status_label = QLabel(self)
        self.status_label.setAlignment(Qt.AlignRight | Qt.AlignCenter)
        self.status_label.setText("Status")

        # Layout
        layout = QGridLayout(self)
        # 一段目
        layout.addWidget(self.videoWidget, 0, 0, 1, 4)
        # 二段目
        layout.addWidget(self.btn_start, 1, 0)
        layout.addWidget(self.volume_slider, 1, 1)
        layout.addWidget(self.time_label, 1, 2)
        layout.addWidget(self.status_label, 1, 3)
        # 三段目
        layout.addWidget(self.seek_slider, 2, 0, 1, 4)

        # Signal
        self.mediaPlayer.stateChanged.connect(self._handle_StateChanged)

    def _handle_StateChanged(self, status):

        """MediaPlayerの状態遷移時のコールバック
        ボタンの文字を変更している．
        """

        if (status == QMediaPlayer.PlayingState):
            self.btn_start.setText('PAUSE')
        elif (status != QMediaPlayer.PausedState):
            self.btn_start.setText('PLAY')
        elif (status != QMediaPlayer.StoppedState):
            self.btn_start.setText('PLAY')
        if status == QMediaPlayer.LoadingMedia:
            self.setStatusInfo("Loading...")
            pass
        elif status == QMediaPlayer.StalledMedia:
            self.setStatusInfo("Media Stalled")
            pass
        elif status == QMediaPlayer.EndOfMedia:
            QApplication.alert(self)
            pass
        elif status == QMediaPlayer.InvalidMedia:
            # self.displayErrorMessage()
            pass
        else:
            self.setStatusInfo("-")
            pass

    def setStatusInfo(self, msg):
        self.status_label.setText(msg)

    def _handle_BtnStart(self):

        """再生/停止を行うボタンのコールバック"""
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def set_url(self, url):

        """外部から再生ファイルをセット.
        ファイルがセットされると状態遷移しStateChangedがコールされる"""

        assert os.path.exists(url)
        url = QUrl.fromLocalFile(url)
        self.url = url
        contents = QMediaContent(url)
        self.mediaPlayer.setMedia(contents)

    def currentTimeMS(self):
        return self.mediaPlayer.position()

    def currentTiemPersent(self):
        return self.mediaPlayer.position() / self.mediaPlayer.duration()

    @Slot()
    def tock(self):
        """一定時間ごとに呼び出される"""
        self.time = self.mediaPlayer.position()
        # print(self.time)
        time = self.time
        time = time / 1000.
        h = int(time / 3600.)
        m = int((time - 3600 * h) / 60.)
        s = int(time - 3600 * h - m * 60)
        self.time_label.setText('%02d:%02d:%02d' % (h, m, s))

    @Slot()
    def restart(self):
        self.seek_slider.setValue(0)
        self.mediaPlayer.setPosition(0)


def main():
    VIDEO_PATH = "./data/test.avi"
    app = QApplication(sys.argv)
    window = pVideoPlayer(url=VIDEO_PATH)
    window.show()
    # It's exec_ because exec is a reserved word in Python
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
