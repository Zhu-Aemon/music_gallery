from PySide2.QtWidgets import QApplication, QMessageBox, QFileDialog, QWidget, QPushButton, QListWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette, QColor, QPainter, QBrush, QImage, QPixmap, QIcon
from PySide2.QtCore import Qt, QRect, QSize
from Setting import Setting


class MainWindow:

    def __init__(self):
        self.ui = QUiLoader().load("resources/MainWindow.ui")
        self.ui.setWindowTitle("Music Gallery")
        palette = self.ui.palette()
        palette.setColor(QPalette.Background, '#ffffff')
        self.ui.setPalette(palette)
        self.ui.setAutoFillBackground(True)
        self.set_icon(self.ui.settings, r'resources/setting_button.png')
        self.set_icon(self.ui.add, r'resources/add.png')
        self.set_list_icon(exception=None)
        self.ui.listWidget.itemSelectionChanged.connect(self.change_icon)
        self.setting_window = Setting()
        self.ui.settings.clicked.connect(self.show_setting)

    def set_icon(self, button, icon):
        img = QImage(icon)
        pixmap = QPixmap(img)
        fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio,
                                  Qt.SmoothTransformation)  # 注意 scaled() 返回一个 QtGui.QPixmap
        button.setIcon(fit_pixmap)
        button.setIconSize(QSize(23, 23))

    def set_list_icon(self, exception: int):
        icon_list = ['resources/all_music.png', 'resources/favourite_music.png', 'resources/recommended.png',
                     'resources/MV.png', 'resources/bilibili.png']
        if exception is not None:
            for i in range(self.ui.listWidget.count()):
                if i != exception:
                    img = QImage(icon_list[i])
                    pixmap = QPixmap(img)
                    fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio,
                                               Qt.SmoothTransformation)  # 注意 scaled() 返回一个 QtGui.QPixmap
                    self.ui.listWidget.item(i).setIcon(fit_pixmap)
                else:
                    continue
            self.ui.listWidget.setIconSize(QSize(23, 23))
        else:
            for i in range(self.ui.listWidget.count()):
                img = QImage(icon_list[i])
                pixmap = QPixmap(img)
                fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio,
                                            Qt.SmoothTransformation)  # 注意 scaled() 返回一个 QtGui.QPixmap
                self.ui.listWidget.item(i).setIcon(fit_pixmap)
            self.ui.listWidget.setIconSize(QSize(23, 23))

    def change_icon(self):
        icon_list = ['resources-inverted/all_music.png', 'resources-inverted/favourite_music.png',
                     'resources-inverted/recommended.png',
                     'resources-inverted/MV.png', 'resources-inverted/bilibili.png']
        index = self.ui.listWidget.currentRow()
        img = QImage(icon_list[index])
        pixmap = QPixmap(img)
        fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio,
                                   Qt.SmoothTransformation)
        self.ui.listWidget.item(index).setIcon(fit_pixmap)
        self.ui.listWidget.setIconSize(QSize(23, 23))
        self.set_list_icon(exception=index)

    def show_setting(self):
        self.setting_window.window.show()


app = QApplication([])
mw = MainWindow()
mw.ui.show()
app.exec_()
