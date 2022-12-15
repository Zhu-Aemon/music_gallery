# -*- coding: utf-8 -*-
from PySide2 import QtCore, QtGui, QtWidgets
import sys


class WindowDemo(QtWidgets.QMainWindow):
    def __init__(self):
        super(WindowDemo, self).__init__()
        self.setup_ui()
        self.add_shadow()

    def setup_ui(self):
        self.setWindowOpacity(0.93)  # 设置窗口透明度
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)  # 隐藏边框

        self.setFixedSize(300, 400)

        self.base_widget = QtWidgets.QWidget()  # 创建透明窗口
        self.base_widget.setStyleSheet('''QWidget{  border-radius:7px;background-color:rgb(255, 255, 255);}''')
        self.base_widget.setObjectName('base_widget')
        self.base_layout = QtWidgets.QGridLayout()
        self.base_widget.setLayout(self.base_layout)
        self.base_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setStyleSheet('''QWidget{border-radius:7px;background-color:rgb(255,255,255);}''')

        self.base_layout.addWidget(self.main_widget)

        self.setCentralWidget(self.base_widget)  # 设置窗口主部件

    def add_shadow(self):
        # 添加阴影
        self.effect_shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.effect_shadow.setOffset(0, 0)  # 偏移
        self.effect_shadow.setBlurRadius(10)  # 阴影半径
        self.effect_shadow.setColor(QtCore.Qt.gray)  # 阴影颜色
        self.main_widget.setGraphicsEffect(self.effect_shadow)  # 将设置套用到widget窗口中


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = WindowDemo()
    MainWindow.show()
    sys.exit(app.exec_())