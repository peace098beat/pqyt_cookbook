import os
import sys

from datetime import datetime

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

Signal = pyqtSignal
Slot = pyqtSlot


class PlaylistModel(QAbstractItemModel):

    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)

        self.m_playlist = None

    def rowCount(self, parent=QModelIndex()):
        return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0

    def columnCount(self, parent=QModelIndex()):
        return self.ColumnCount if not parent.isValid() else 0

    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column) if self.m_playlist is not None and not parent.isValid() and row >= 0 and row < self.m_playlist.mediaCount() and column >= 0 and column < self.ColumnCount else QModelIndex()

    def parent(self, child):
        return QModelIndex()

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.m_playlist.media(index.row()).canonicalUrl()
                return QFileInfo(location.path()).fileName()

            return self.m_data[index]

        return None

    def playlist(self):
        return self.m_playlist

    def setPlaylist(self, playlist):
        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.disconnect(
                    self.beginInsertItems)
            self.m_playlist.mediaInserted.disconnect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.disconnect(
                    self.beginRemoveItems)
            self.m_playlist.mediaRemoved.disconnect(self.endRemoveItems)
            self.m_playlist.mediaChanged.disconnect(self.changeItems)

        self.beginResetModel()
        self.m_playlist = playlist

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.connect(
                    self.beginInsertItems)
            self.m_playlist.mediaInserted.connect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.connect(
                    self.beginRemoveItems)
            self.m_playlist.mediaRemoved.connect(self.endRemoveItems)
            self.m_playlist.mediaChanged.connect(self.changeItems)

        self.endResetModel()

    def beginInsertItems(self, start, end):
        self.beginInsertRows(QModelIndex(), start, end)

    def endInsertItems(self):
        self.endInsertRows()

    def beginRemoveItems(self, start, end):
        self.beginRemoveRows(QModelIndex(), start, end)

    def endRemoveItems(self):
        self.endRemoveRows()

    def changeItems(self, start, end):
        self.dataChanged.emit(self.index(start, 0),
                self.index(end, self.ColumnCount))


class PhononVideoPlayer(QWidget):
    def __init__(self, url=None, parent=None):
        QWidget.__init__(self)
        self.setWindowTitle('Video Player')

        # UI 生成
        # ***************
        self.setupUI()

        # Timer
        # *****
        self.timer = QTimer()
        self.timer.setInterval(1000/10)
        self.timer.timeout.connect(self.mainLoop)
        self.timer.start()


    def mainLoop(self):
        """一定時間ごとに呼び出される"""
        self.time = self.player.position()
        # print(self.time)
        time = self.time
        time = time / 1000.
        h = int(time / 3600.)
        m = int((time - 3600 * h) / 60.)
        s = int(time - 3600 * h - m * 60)
        self.labelDuration.setText('%02d:%02d:%02d' % (h, m, s))

        """ 時計の表示 """
        dt = QDateTime.currentDateTime()
        self.clock.setText(str(dt.toString()))

        """ 指定時間に再生 """
        d = datetime.now()

        target_hour = self.time_edit.time().hour()

        if d.hour == target_hour:
            if self.player.state() != QMediaPlayer.PlayingState:
                self.player.play()


    def setupUI(self):

        """UI生成シーケンス.
        可視性を高めるため別に記述
        """
        # Phonon Objects
        # ***************
        self.player = QMediaPlayer()
        self.playlist = QMediaPlaylist()
        self.player.setPlaylist(self.playlist)

        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)

        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(self.playlist.currentIndex(), 0))

        self.playlistView.activated.connect(self.jump)

        # SeekSlider
        self.seek_slider = QSlider(Qt.Horizontal,self)
        self.seek_slider.setRange(0, 100)
        self.player.positionChanged.connect(self.seek_slider.setValue)
        self.player.durationChanged.connect(self.seek_slider.setMaximum)
        self.seek_slider.valueChanged.connect(self.player.setPosition)
        # Volume
        self.volume_slider = QSlider(Qt.Horizontal,self)
        self.volume_slider.setRange(0,100)
        self.volume_slider.valueChanged.connect(self.player.setVolume)
        self.volume_slider.setValue(50)

        # Ctrl UI
        self.btn_start = QPushButton('PLAY', self)
        self.btn_start.clicked.connect(self._handle_BtnStart)

        # OpenBtn
        self.open_btn = QPushButton("Open")
        self.open_btn.released.connect(self.open)

        # 時間
        self.time_edit = QTimeEdit()

        # 今の時間
        self.clock = QLabel("::")

        # Status Label
        self.labelDuration = QLabel()

        # Layout
        layout = QGridLayout(self)
        # 一段目
        # 二段目
        layout.addWidget(self.btn_start, 0, 0)
        layout.addWidget(self.volume_slider, 0, 1)
        layout.addWidget(self.seek_slider, 1, 0 )
        layout.addWidget(self.labelDuration, 1, 1 )
        layout.addWidget(self.open_btn, 2, 0)
        layout.addWidget(self.time_edit, 2, 1)
        layout.addWidget(self.playlistView, 3, 0, 1, 2 )
        layout.addWidget(self.clock, 4, 0, 1, 2 )
        layout.setRowStretch(1, 1)
        # 三段目

        # Signal
        self.player.stateChanged.connect(self._handle_StateChanged)



    def _handle_StateChanged(self, newstate):

        """MediaPlayerの状態遷移時のコールバック
        ボタンの文字を変更している．
        """

        if newstate == QMediaPlayer.PlayingState:
            self.btn_start.setText('PAUSE')
        elif (newstate != QMediaPlayer.PausedState or newstate != QMediaPlayer.StoppedState):
            self.btn_start.setText('PLAY')


    def _handle_BtnStart(self):

        """再生/停止を行うボタンのコールバック"""

        if self.player.state() == QMediaPlayer.PlayingState:
            # self.media.stop()
            self.player.pause()
        else:
            self.player.play()


    def open(self):
        fileNames, _ = QFileDialog.getOpenFileNames(self, "Open Files")
        self.addToPlaylist(fileNames)

    def addToPlaylist(self, fileNames):
        for name in fileNames:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                if fileInfo.suffix().lower() == 'm3u':
                    self.playlist.load(url)
                else:
                    self.playlist.addMedia(QMediaContent(url))
            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))

    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.player.play()

    def playlistPositionChanged(self, position):
        self.playlistView.setCurrentIndex(
                self.playlistModel.index(position, 0))

def main():
    app = QApplication(sys.argv)
    window = PhononVideoPlayer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()