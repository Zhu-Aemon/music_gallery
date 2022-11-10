from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAbstractItemView
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette, QImage, QPixmap, QBrush, QColor
from PySide2.QtCore import Qt, QSize, QSettings

from Setting import Setting
from Gallery import Core


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("resources/MainWindow.ui")
        self.window_init()
        self.setting_window = Setting()
        self.signal_process()

    def window_init(self):
        """
        初始化窗口的标题、背景颜色、图标等相关元素，并且预加载各个侧边栏的相关资源内容
        :return: None
        """
        # 设置窗口标题
        self.ui.setWindowTitle("Music Gallery")

        # 设置背景颜色
        palette = self.ui.palette()
        palette.setColor(QPalette.Background, '#ffffff')
        self.ui.setPalette(palette)
        self.ui.setAutoFillBackground(True)

        # 设置界面上的所有图标
        self.set_icon(self.ui.settings, r'resources/setting_button.png', size=23)
        self.set_icon(self.ui.add, r'resources/add.png', size=23)
        self.set_icon(self.ui.play_music, r'resources-inverted/play_icon_gray.png', size=32)
        self.set_icon(self.ui.last_song, r'resources-inverted/last_song_gray.png', size=32)
        self.set_icon(self.ui.next_song, r'resources-inverted/next_song_gray.png', size=32)
        # self.set_icon(self.ui.song_cover, r'example.jpg', size=47)
        self.set_list_icon(exception=None)

        # 设置初始化歌曲名与信息值， 以及进度条进度
        self.ui.song_name.setText("")
        self.ui.song_info.setText("")
        self.ui.progressBar.setValue(0)

        # 加载所有音乐中的有关内容，并且调整表格列宽
        self.display_all_songs()
        self.column_adjust()

    def signal_process(self):
        """
        处理接收到的各种信号
        :return: None
        """
        self.ui.listWidget.itemSelectionChanged.connect(self.change_icon)
        self.ui.settings.clicked.connect(self.show_setting)
        self.ui.listWidget.itemSelectionChanged.connect(self.shift_stack)
        self.ui.listWidget.itemSelectionChanged.connect(self.shift_stack)

    @staticmethod
    def set_icon(button, icon, size):
        """
        :param button: 需要设置图标的按钮
        :param icon: 需要设置的图标源文件
        :param size: 图标的大小（正方形）
        :return: None
        设置任意button的图标
        """
        img = QImage(icon)
        pixmap = QPixmap(img)
        fit_pixmap = pixmap.scaled(size, size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        button.setIcon(fit_pixmap)
        button.setIconSize(QSize(size, size))

    def set_list_icon(self, exception: int):
        """
        :param exception: 不需要设置图标的列表元素下标
        :return: None
        设置左侧列表选项卡的图标，默认设置的列表图标大小为23px
        """
        icon_list = ['resources/all_music.png', 'resources/recent.png', 'resources/favourite_music.png',
                     'resources/recommended.png', 'resources/MV.png', 'resources/bilibili.png']
        if exception is not None:
            for i in range(self.ui.listWidget.count()):
                if i != exception:
                    img = QImage(icon_list[i])
                    pixmap = QPixmap(img)
                    fit_pixmap = pixmap.scaled(23, 23, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
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
        """
        在左侧选项卡的某一选项被选中时，将会被高亮，高亮的颜色与默认状态下的图标颜色一致，为了使得图标仍然被凸显出来，需要重新设置图标
        :return: None
        """
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
        """
        调整所有音乐中table的各列列宽
        :return: None
        """
        self.ui.tableWidget.setColumnWidth(0, 600)
        self.ui.tableWidget.setColumnWidth(1, 250)
        self.ui.tableWidget.setColumnWidth(2, 300)
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
        """
        从缓存的音乐数据中读取全部音乐，并且在列表中显示出来
        :return: None
        """
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
        """
        点击左侧列表选项卡切换右侧界面
        :return: None
        """
        idx = self.ui.listWidget.currentRow()
        self.ui.stackedWidget.setCurrentIndex(idx + 1)


app = QApplication([])
mw = MainWindow()
mw.ui.show()
app.exec_()
