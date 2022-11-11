import getpass
import math
import os
import time

from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAbstractItemView
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette, QImage, QPixmap, QBrush, QColor
from PySide2.QtCore import Qt, QSize, QSettings

from Setting import Setting
from Gallery import Core, stop_thread

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

from threading import Thread


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load("resources/MainWindow.ui")
        self.window_init()
        self.setting_window = Setting()
        self.signal_process()
        self.song_duration = 0
        self.music_thread = Thread()
        self.username = getpass.getuser()
        self.song_playing = None
        self.state = None
        self.progress_thread = None

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
        self.ui.tableWidget.itemDoubleClicked.connect(self.play_song_thread)
        self.ui.play_music.clicked.connect(self.play_button_clicked)

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

    def song_clicked(self):
        """
        播放选中的歌曲并且设置相应的标签，信号处理函数
        :return: None
        """

        if self.state == "playing":
            self.pause_play()
        song_path, title, artist, album = self.get_current_song_info()

        self.set_icon(self.ui.play_music, r'resources-inverted/pause_gray.png', size=32)
        self.set_cover(song_path, title, album)
        self.ui.song_name.setText(title)
        self.ui.song_info.setText(f"{artist} - {album}")

        song = AudioSegment.from_mp3(song_path)
        self.song_playing = _play_with_simpleaudio(song)
        self.song_duration = song.duration_seconds
        self.state = "playing"

        self.progress_thread = Thread(target=self.song_progress)
        self.progress_thread.start()

    def play_song_thread(self):
        """
        简简单单开一个多线程耍一耍
        :return: None
        """

        self.music_thread = Thread(target=self.song_clicked)
        self.music_thread.start()

    def song_progress(self):
        """
        进度条显示
        :return: None
        """

        for i in range(int(self.song_duration)):
            progress = (i + 1) / self.song_duration
            self.ui.progressBar.repaint()
            self.ui.progressBar.setValue(math.floor(progress * 100))
            time.sleep(1)

    def play_button_clicked(self):
        """
        信号处理函数，分为在播放和不在播放两种情况讨论
        :return: None
        """

        if self.state == "playing":
            self.pause_play()
        else:
            self.set_icon(self.ui.play_music, r'resources-inverted/pause_gray.png', size=32)

    def pause_play(self):
        """
        停止播放歌曲，并且改变图标
        :return: None
        """

        self.song_playing.stop()
        self.state = "stopped"
        self.set_icon(self.ui.play_music, r'resources-inverted/play_icon_gray.png', size=32)
        stop_thread(self.progress_thread)

    def set_cover(self, song_path, title, album):
        """
        获取当前歌曲的封面，并且保存在f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover"文件夹下，并设置封面
        :param song_path: 歌曲的绝对路径
        :param title: 歌曲的标题
        :param album: 歌曲所在专辑
        :return: None
        """

        try:
            *args, files = os.walk(f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover")
        except ValueError:
            if not os.path.exists(f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover"):
                os.makedirs(f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover")
            files = []
        song_info_str = f"{title} - {album}.jpg"
        if r'/' in song_info_str:
            song_info = song_info_str.replace(r'/', '&')
            if song_info not in files:
                Core.save_cover(song_path, f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{song_info}")
                self.set_icon(self.ui.song_cover,
                              f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{song_info}", size=47)
        else:
            if f"{title}-{album}.jpg" not in files:
                Core.save_cover(song_path,
                                f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{title}-{album}.jpg")
            self.set_icon(self.ui.song_cover,
                          f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{title}-{album}.jpg", size=47)

    def get_current_song_info(self):
        """
        获取当前选中歌曲的路径以及相关信息
        :return:
        """

        all_path_list = QSettings('config/all_path_config.ini', QSettings.IniFormat)
        path_list = all_path_list.value('all_path')
        song_index = self.ui.tableWidget.currentRow()
        song_path = path_list[song_index]
        title, artist, album = Core().get_mp3_info(song_path)
        return song_path, title, artist, album


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("plastique")
    mw = MainWindow()
    mw.ui.show()
    app.exec_()
