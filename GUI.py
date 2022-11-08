import os

from PySide2.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem, QAbstractItemView, QTableWidget
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette, QImage, QPixmap, QBrush, QColor
from PySide2.QtCore import Qt, QSize, QSettings, QItemSelectionModel

from Setting import Setting
from Gallery import Core


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
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
        self.display_all_songs()
        self.column_adjust()
        self.ui.listWidget.itemSelectionChanged.connect(self.shift_stack)
        self.ui.listWidget.itemSelectionChanged.connect(self.shift_stack)

    @staticmethod
    def set_icon(button, icon):
        img = QImage(icon)
        pixmap = QPixmap(img)
        fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio,
                                   Qt.SmoothTransformation)  # 注意 scaled() 返回一个 QtGui.QPixmap
        button.setIcon(fit_pixmap)
        button.setIconSize(QSize(23, 23))

    def set_list_icon(self, exception: int):
        icon_list = ['resources/all_music.png', 'resources/recent.png', 'resources/favourite_music.png', 'resources/recommended.png',
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
                fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                self.ui.listWidget.item(i).setIcon(fit_pixmap)
            self.ui.listWidget.setIconSize(QSize(23, 23))

    def change_icon(self):
        icon_list = ['resources-inverted/all_music.png', 'resources-inverted/recent.png',
                     'resources-inverted/favourite_music.png', 'resources-inverted/recommended.png',
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

    def column_adjust(self):
        self.ui.tableWidget.setColumnWidth(0, 600)
        self.ui.tableWidget.setColumnWidth(1, 250)
        self.ui.tableWidget.setColumnWidth(2, 250)
        self.ui.tableWidget.horizontalHeader().setHidden(True)
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(35)
        self.ui.tableWidget.verticalHeader().setHidden(True)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        row_number = self.ui.tableWidget.rowCount()
        for i in range(row_number):
            self.ui.tableWidget.item(i, 1).setForeground(QBrush(QColor('#707070')))
            self.ui.tableWidget.item(i, 2).setForeground(QBrush(QColor('#707070')))

    def display_all_songs(self):
        source_settings = QSettings('config/source_config.ini', QSettings.IniFormat)
        path_list = source_settings.value('source_files')
        all_path_list = Core().source_scan(path_list)
        all_path_settings = QSettings('config/all_path_config.ini', QSettings.IniFormat)
        all_path_settings.setValue('all_path', all_path_list)
        self.ui.tableWidget.setRowCount(len(all_path_list))
        for index in range(len(all_path_list)):
            path = all_path_list[index]
            assert isinstance(path, str), 'path is not str!'
            if path.endswith('mp3'):
                title, artist, album = Core().get_mp3_info(path)
                self.ui.tableWidget.setItem(index, 0, QTableWidgetItem(title))
                self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(artist))
                self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(album))

    def shift_stack(self):
        idx = self.ui.listWidget.currentRow()
        self.ui.stackedWidget.setCurrentIndex(idx + 1)


app = QApplication([])
mw = MainWindow()
mw.ui.show()
app.exec_()
