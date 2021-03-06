#! coding:utf-8
"""
BasedMainWindowの使い方

スロットの使い方
"""

import sys

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

Signal = pyqtSignal
Slot = pyqtSlot

from BaseMainWindow import BasedMainWindow


class YourMainWindow(BasedMainWindow):
    """ BaseMainWindwの使いかた """

    def __init__(self):
        super().__init__()
        self.fileLoaded.connect(self.loadedfilename)

    @Slot(str)
    def loadedfilename(self, filename):
        print(filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)

    win = YourMainWindow()
    win.show()
    sys.exit(app.exec_())
s
