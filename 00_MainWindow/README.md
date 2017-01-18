
# QMainWindowのQMainWindowを使う場合のテンプレートクラス。

継承して使おう。

```
from BaseMainWindow import BasedMainWindow
```

メニューバーとステータスバーを装備してます。

メニューバーはファイルの読み込みアクションを装備。

ステータスバーの端には、メインループのFPSを常時表示を装備。
あとは適時カスタムしてください。

# 使い方

```python
#! coding:utf-8
"""
BasedMainWindowの使い方

子QWidgetを配置する方法.

"""

import sys
import os
import time


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

Signal = pyqtSignal
Slot = pyqtSlot

from BaseMainWindow import BasedMainWindow


class YourMainWindow(BasedMainWindow):
    """ BaseMainWindwの使いかた その2
    ウィジェットのレイアウトの方法
    """

    MAINLOOP_FPS = 30

    def __init__(self):
        super().__init__()

        # おまじない
        self.main_widget = QWidget(self)
        self.main_layout = QGridLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # 子供UI
        label1 = QLabel("Top - Left")
        label2 = QLabel("Top - Right")
        label3 = QLabel("Bottom - Left")
        label4 = QLabel("Bottom - right")

        # レイアウトをセット
        self.main_layout.addWidget(label1, 0, 0)
        self.main_layout.addWidget(label2, 0, 1)
        self.main_layout.addWidget(label3, 1, 0)
        self.main_layout.addWidget(label4, 1, 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)

    win = YourMainWindow()
    win.show()
    sys.exit(app.exec_())


```