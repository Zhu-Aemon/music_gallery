import getpass
import math
import os
import time
import random
import faulthandler

from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QAbstractItemView, QMenu, QAction, QWidget, \
    QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette, QImage, QPixmap, QBrush, QColor, QFont, QIcon, QCursor, QPen
from PySide2.QtCore import Qt, QSize, QSettings, QLine

from Setting import Setting
from Gallery import Core, stop_thread

from pydub import AudioSegment
from pydub.playback import _play_with_simpleaudio

from threading import Thread
from collections import Counter
from functools import partial


class MainWindow(QMainWindow):

    def __init__(self):
        self.song_duration = 0
        self.music_thread = Thread()
        self.username = getpass.getuser()
        self.song_playing = None
        self.state = None
        self.progress_thread = None
        self.break_time = None
        self.current_progress = 0
        self.song = None
        self.loop_state = "loop"
        self.all_list = None
        self.index = None

        self.config_init()
        super().__init__()
        self.ui = QUiLoader().load("resources/MainWindow.ui")
        self.window_init()
        self.setting_window = Setting()
        self.signal_process()
        self.set_style_sheet()
        self.set_graphics_effect()

    def window_init(self):
        """
        初始化窗口的标题、背景颜色、图标等相关元素，并且预加载各个侧边栏的相关资源内容
        :return: None
        """

        # 设置窗口标题
        self.ui.setWindowTitle("Music Gallery")

        # 设置背景颜色
        palette = self.ui.palette()
        palette.setColor(QPalette.Background, '#f9f9f9')
        self.ui.setPalette(palette)
        self.ui.setAutoFillBackground(True)

        # 设置界面上的所有图标
        self.set_icon(self.ui.settings, r'resources/setting_button.png', size=23)
        self.set_icon(self.ui.add, r'resources/add.png', size=23)
        self.set_icon(self.ui.play_music, r'resources-inverted/play_icon_gray.png', size=32)
        self.set_icon(self.ui.last_song, r'resources-inverted/last_song_gray.png', size=32)
        self.set_icon(self.ui.next_song, r'resources-inverted/next_song_gray.png', size=32)
        self.set_icon(self.ui.show_album, r'resources/show.png', size=23)

        self.set_icon(self.ui.add_to_album, r'resources-inverted/add_to_album.png', size=32)
        self.set_icon(self.ui.change_mode, r'resources-inverted/loop.png', size=32)
        self.set_icon(self.ui.history_info, r'resources-inverted/history.png', size=32)

        self.set_list_icon(exception=None)

        self.set_icon(self.ui.all_music, r'resources-inverted/all_music.png', size=23)

        # 设置初始化歌曲名与信息值， 以及进度条进度
        self.ui.song_name.setText("")
        self.ui.song_info.setText("")
        self.ui.progressBar.setValue(0)
        self.ui.album_divider.setText('Albums')

        # 加载所有音乐中的有关内容，并且调整表格列宽
        self.display_all_songs()
        self.table_setting()

        # 设置初始行
        self.ui.listWidget.setCurrentRow(0)
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

        # 设置avatar
        avatar_setting = QSettings('config/source_config.ini', QSettings.IniFormat)
        avatar_source = avatar_setting.value('avatar')
        username = avatar_setting.value('username')
        if avatar_source:
            Core.circle_corner(avatar_source, 0.2, r'tmp/avatar.png')
            self.set_icon(self.ui.avatar, avatar_source, size=40)
        if username:
            self.ui.username.setText(username)
        else:
            self.ui.username.setText('set username')

    def signal_process(self):
        """
        处理接收到的各种信号
        :return: None
        """

        self.ui.listWidget.itemSelectionChanged.connect(self.change_icon)
        self.ui.settings.clicked.connect(self.show_setting)
        self.ui.listWidget.itemSelectionChanged.connect(self.shift_stack)
        self.ui.tableWidget.itemDoubleClicked.connect(self.play_song_thread)
        self.ui.play_music.clicked.connect(self.play_button_clicked)
        self.ui.next_song.clicked.connect(self.play_next_song)
        self.ui.last_song.clicked.connect(self.play_last_song)
        self.ui.like.clicked.connect(self.like_clicked)

        self.ui.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tableWidget.customContextMenuRequested.connect(self.show_table_menu)
        self.ui.change_mode.clicked.connect(self.change_mode_clicked)
        self.ui.search_button.clicked.connect(self.search)
        self.ui.restore.clicked.connect(self.restore_clicked)

    @staticmethod
    def config_init():
        song_history = QSettings('config/song.ini', QSettings.IniFormat)
        play_history = song_history.value('song_history')
        liked_songs = song_history.value('liked')
        if len(play_history) == 0:
            play_history = ["I don't like bugs", "I don't like bugs either"]
            song_history.setValue('song_history', play_history)
        else:
            if "I don't like bugs" in play_history:
                play_history.remove("I don't like bugs")
            if "I don't like bugs either" in play_history:
                play_history.remove("I don't like bugs either")
            song_history.setValue('song_history', play_history)
        if len(liked_songs) == 0:
            liked_songs = ["I don't like bugs", "I don't like bugs either"]
            song_history.setValue('liked', liked_songs)
        else:
            if "I don't like bugs" in liked_songs:
                liked_songs.remove("I don't like bugs")
            if "I don't like bugs either" in liked_songs:
                liked_songs.remove("I don't like bugs either")
            song_history.setValue('liked', liked_songs)

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

        if exception is None:
            self.set_icon(self.ui.all_music, r'resources/all_music.png', size=23)
            self.set_icon(self.ui.favourite_music, r'resources/favourite_music.png', size=23)
            self.set_icon(self.ui.statistics, r'resources/statistic.png', size=23)
        else:
            if exception == 0:
                # self.set_icon(self.ui.all_music, r'resources-inverted/all_music.png', size=23)
                self.set_icon(self.ui.favourite_music, r'resources/favourite_music.png', size=23)
                self.set_icon(self.ui.statistics, r'resources/statistic.png', size=23)
            elif exception == 1:
                self.set_icon(self.ui.all_music, r'resources/all_music.png', size=23)
                # self.set_icon(self.ui.favourite_music, r'resources-inverted/favourite_music.png', size=23)
                self.set_icon(self.ui.statistics, r'resources/statistic.png', size=23)
            else:
                self.set_icon(self.ui.all_music, r'resources/all_music.png', size=23)
                self.set_icon(self.ui.favourite_music, r'resources/favourite_music.png', size=23)
                # self.set_icon(self.ui.statistics, r'resources-inverted/statistic-inverted.png', size=23)

    def change_icon(self):
        """
        在左侧选项卡的某一选项被选中时，将会被高亮，高亮的颜色与默认状态下的图标颜色一致，为了使得图标仍然被凸显出来，需要重新设置图标
        :return: None
        """

        index = self.ui.listWidget.currentRow()
        if index == 0:
            self.set_icon(self.ui.all_music, r'resources-inverted/all_music.png', size=23)
        elif index == 1:
            self.set_icon(self.ui.favourite_music, r'resources-inverted/favourite_music.png', size=23)
        else:
            self.set_icon(self.ui.statistics, r'resources-inverted/statistic-inverted.png', size=23)
        self.set_list_icon(exception=index)

    def show_setting(self):
        self.setting_window.window.show()

    def table_setting(self):
        """
        调整所有音乐中table的各列列宽
        :return: None
        """

        self.ui.tableWidget.setColumnWidth(0, 550)
        self.ui.tableWidget.setColumnWidth(1, 250)
        self.ui.tableWidget.setColumnWidth(2, 300)
        self.ui.tableWidget.horizontalHeader().setHidden(True)
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(35)
        self.ui.tableWidget.verticalHeader().setHidden(True)
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.ui.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.ui.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        row_number = self.ui.tableWidget.rowCount()
        for i in range(row_number):
            self.ui.tableWidget.item(i, 1).setForeground(QBrush(QColor('#707070')))
            self.ui.tableWidget.item(i, 2).setForeground(QBrush(QColor('#707070')))

    def set_style_sheet(self):
        self.ui.listWidget.setStyleSheet("""
        QListWidget
        {
            background-color: #ffffff;
            border: none;
            font: 10.5pt "Microsoft Yahei";
            outline: 0px;
            padding-top: 110px;
            padding-right: 10px;
            padding-left: 40px;
            border-bottom: 1px solid #eaeaea;
        }
        QListWidget::item
        {
            background-color: transparent;
            color: rgb(153, 153, 153);
            border: 0px;
            padding-left: 5px;
            height: 50px;
        }
        QListWidget::item:selected
        {
            color: #000000;
            background: transparent;
        }""")

        self.ui.settings.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #f0f3f6;
        }
        """)

        self.ui.add.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #ffffff;
        }
        """)

        self.ui.avatar.setStyleSheet("""
        QPushButton
        {
            border-radius: 8px;
        }""")

        # self.ui.label.setStyleSheet("color: rgb(255, 255, 255)")
        # self.ui.label_2.setStyleSheet("color: rgb(255, 255, 255)")

        self.ui.tableWidget.setStyleSheet("""
        QTableWidget {
            background-color: #ffffff;
            border: none;
            border-radius: 15px;
            outline: none;
        }
        QHeaderView::section{
            text-align:center;
            padding:3px;
            margin:0px;
            border-left-width:0;
        }
        QTableWidget::item {
            border-bottom:1px solid #eaeaea;
            padding-left: 10px;
        }
        QTableWidget::item:selected{
            outline: none;
            background-color: #dbe7f4;
        }
        QTableWidget QScrollBar {
            
        }""")

        self.ui.widget.setStyleSheet("""
        QWidget {
            background-color: #ffffff;
            border-radius: 15px;
        }""")

        self.ui.widget_2.setStyleSheet("""
        QWidget {
            background-color: #ffffff;
            border-radius: 15px;
        }""")

        # self.ui.line.setStyleSheet("""
        # Line {
        #     color: rgb(153, 153, 153);
        # }""")

        self.ui.username.setStyleSheet("""
        QLabel {
            font: 15px 'Micorosoft Yahei';
            color: rgb(109, 109, 109);
        }""")

        self.ui.progressBar.setStyleSheet("""
        QProgressBar {
            border: none;
            border-radius: 2px;
            background-color: #f9f9f9;
            qproperty-textVisible: false;
        }

        QProgressBar::chunk {
            background-color: #808080;
            border-radius: 2px;
        }
        """)

        self.ui.album_divider.setStyleSheet("""
        QLabel {
            font: 15px 'Microsoft Yahei UI Semibold';
            color: #000000;
        }""")

        self.ui.show_album.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #ffffff;
        }
        """)

        self.ui.all_music.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #ffffff;
        }
        """)

        self.ui.all_music.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #ffffff;
        }
        """)

        self.ui.favourite_music.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #ffffff;
        }
        """)

        self.ui.statistics.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: #ffffff;
        }
        """)

        self.ui.listWidget_2.setStyleSheet("""
        QListWidget
        {
            background-color: #ffffff;
            border: none;
            font: 10.5pt "Microsoft Yahei";
            outline: 0px;
            padding-right: 10px;
            padding-left: 12px;
        }
        QListWidget::item
        {
            background-color: transparent;
            color: rgb(153, 153, 153);
            border: 0px;
            padding-left: 5px;
            height: 45px;
        }
        QListWidget::item:selected
        {
            color: #000000;
            background: transparent;
        }""")

        self.ui.search_box.setStyleSheet("""
        QLineEdit {
            border: 2px solid #eaeaea;
            outline: none;
            background: #fff;
            font: 14px 'Microsoft Yahei';
            border-radius: 8px;
        }""")

        self.ui.search_button.setStyleSheet("""
        QPushButton {
            font: 13px 'Microsoft Yahei';
            border-radius: 8px;
            border: none;
            background-color: rgb(79, 70, 186);
            color: #ffffff;
        }""")

        self.ui.restore.setStyleSheet("""
        QPushButton {
            font: 13px 'Microsoft Yahei';
            border-radius: 8px;
            border: 1px solid #eaeaea;
            background-color: #ffffff;
            color: #000000;
        }""")

    def set_graphics_effect(self):
        effect_tableWidget = QGraphicsDropShadowEffect(self.ui.tableWidget)
        effect_tableWidget.setBlurRadius(15)
        effect_tableWidget.setColor('#eaeaea')
        effect_tableWidget.setOffset(0, 5)

        self.ui.tableWidget.setGraphicsEffect(effect_tableWidget)

        effect_widget = QGraphicsDropShadowEffect(self.ui.widget)
        effect_widget.setBlurRadius(15)
        effect_widget.setColor('#eaeaea')
        effect_widget.setOffset(0, 5)

        self.ui.widget.setGraphicsEffect(effect_widget)

        effect_widget_2 = QGraphicsDropShadowEffect(self.ui.widget_2)
        effect_widget_2.setBlurRadius(15)
        effect_widget_2.setColor('#eaeaea')
        effect_widget_2.setOffset(0, 5)

        self.ui.widget_2.setGraphicsEffect(effect_widget_2)

        effect_widget_3 = QGraphicsDropShadowEffect(self.ui.widget_3)
        effect_widget_3.setBlurRadius(15)
        effect_widget_3.setColor('#eaeaea')
        effect_widget_3.setOffset(0, 5)

        self.ui.widget_3.setGraphicsEffect(effect_widget_3)

        effect_widget_4 = QGraphicsDropShadowEffect(self.ui.widget_4)
        effect_widget_4.setBlurRadius(15)
        effect_widget_4.setColor('#eaeaea')
        effect_widget_4.setOffset(0, 5)

        self.ui.widget_4.setGraphicsEffect(effect_widget_4)

    def change_mode_clicked(self):
        if self.loop_state == 'loop':
            self.loop_state = 'shuffle'
            self.set_icon(self.ui.change_mode, r'resources-inverted/shuffle.png', size=32)
        else:
            self.loop_state = 'loop'
            self.set_icon(self.ui.change_mode, r'resources-inverted/loop.png', size=32)

    def display_all_songs(self):
        """
        从缓存的音乐数据中读取全部音乐，并且在列表中显示出来
        :return: None
        """

        self.ui.tableWidget.clearContents()
        source_settings = QSettings('config/source_config.ini', QSettings.IniFormat)
        path_list = source_settings.value('source_files')
        all_path_list = Core().source_scan(path_list)
        self.all_list = all_path_list
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
        if idx == 0:
            self.ui.stackedWidget.setCurrentIndex(1)
            self.display_all_songs()
        elif idx == 1:
            self.ui.stackedWidget.setCurrentIndex(1)
            self.display_liked_songs()
        elif idx == 2:
            self.ui.stackedWidget.setCurrentIndex(2)

    def song_clicked(self):
        """
        播放选中的歌曲并且设置相应的标签，信号处理函数
        :return: None
        """

        if self.state == "playing":
            self.pause_play()
            self.current_progress = 0
        self.play_song()

    def play_song_thread(self):
        """
        简简单单开一个多线程耍一耍
        :return: None
        """

        self.music_thread = Thread(target=self.song_clicked)
        self.music_thread.start()

    def song_progress(self, is_to_continue=False):
        """
        进度条显示
        :return: None
        """

        if not is_to_continue:
            for i in range(int(self.song_duration)):
                progress = (i + 1) / self.song_duration
                self.ui.progressBar.repaint()
                self.ui.progressBar.setValue(math.floor(progress * 100))
                self.current_progress = i + 1
                time.sleep(1)
            self.ui.progressBar.setValue(100)
            self.set_icon(self.ui.play_music, r'resources-inverted/play_icon_gray.png', size=32)
        else:
            for i in range(int(self.song_duration)):
                progress = ((i + 1) + self.break_time) / (self.song_duration + self.break_time)
                self.ui.progressBar.repaint()
                self.ui.progressBar.setValue(math.floor(progress * 100))
                self.current_progress = i + 1
                time.sleep(1)
            self.ui.progressBar.setValue(100)
            self.set_icon(self.ui.play_music, r'resources-inverted/play_icon_gray.png', size=32)
        self.state = 'stopped'
        self.play_next_song()
        # print('playing next song')

    def play_button_clicked(self):
        """
        信号处理函数，分为在播放和不在播放两种情况讨论
        :return: None
        """

        if self.state == "playing":
            self.pause_play()
        else:
            self.set_icon(self.ui.play_music, r'resources-inverted/pause_gray.png', size=32)
            self.continue_play()
            self.state = "playing"

    def pause_play(self):
        """
        停止播放歌曲，并且改变图标
        :return: None
        """

        self.song_playing.stop()
        self.state = "stopped"
        self.set_icon(self.ui.play_music, r'resources-inverted/play_icon_gray.png', size=32)
        if self.progress_thread.is_alive():
            stop_thread(self.progress_thread)
        self.break_time = self.current_progress

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
        song_info_str = f"{title}-{album}.jpg"
        if r'/' in song_info_str:
            song_info = song_info_str.replace(r'/', '&')
            song_info = song_info.replace(' ', '_')
            if song_info not in files:
                Core.save_cover(song_path, f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{song_info}")
                Core.circle_corner(f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{song_info}", 0.25, r'tmp/cover.png')
                self.set_icon(self.ui.song_cover, r"tmp/cover.png", size=47)
        else:
            if f"{title}-{album}.jpg" not in files:
                song_info = f"{title}-{album}.jpg"
                song_info = song_info.replace(' ', '_')
                Core.save_cover(song_path,
                                f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{song_info}")
                Core.circle_corner(f"C:/Users/{self.username}/AppData/Roaming/Gallery/cover/{song_info}", 0.25, r'tmp/cover.png')
            self.set_icon(self.ui.song_cover, r'tmp/cover.png', size=47)

    def get_current_song_info(self):
        """
        获取当前选中歌曲的路径以及相关信息
        :return: 一个元组(song_path, title, artist, album)
        """

        song_index = self.ui.tableWidget.currentRow()
        song_path = self.all_list[song_index]
        title, artist, album = Core().get_mp3_info(song_path)
        return song_path, title, artist, album

    def crop_song(self):
        """
        切割歌曲，从而使得能够继续播放歌曲
        :return: None
        """

        cropped_song = self.song[(self.break_time * 1000): math.floor(self.song_duration * 1000)]
        cropped_song.export(out_f=r"tmp/tmp.mp3", format='mp3')

    def continue_play(self):
        """
        继续播放刚刚暂停的歌曲
        :return: None
        """

        self.crop_song()
        self.song = AudioSegment.from_mp3(r"tmp/tmp.mp3")
        self.song_playing = _play_with_simpleaudio(self.song)
        self.song_duration = self.song.duration_seconds

        self.progress_thread = Thread(target=self.song_progress, args=(True,))
        self.progress_thread.start()

    def play_next_song(self):
        if self.state != 'stopped':
            self.pause_play()
        if self.index != self.ui.tableWidget.rowCount() - 1 and self.loop_state == 'loop':
            self.ui.tableWidget.selectRow(self.index + 1)
            self.play_song()
        elif self.loop_state == 'shuffle':
            idx = random.randint(0, self.ui.tableWidget.rowCount() - 1)
            self.ui.tableWidget.selectRow(idx)
            self.play_song()
        else:
            self.index = -1
            self.play_next_song()

    def play_song(self):
        song_path, title, artist, album = self.get_current_song_info()

        self.index = self.ui.tableWidget.currentRow()

        self.set_icon(self.ui.play_music, r'resources-inverted/pause_gray.png', size=32)
        self.set_cover(song_path, title, album)
        self.ui.song_name.setText(title)
        self.ui.song_info.setText(f"{artist} - {album}")

        self.song = AudioSegment.from_mp3(song_path)
        self.song_playing = _play_with_simpleaudio(self.song)
        self.song_duration = self.song.duration_seconds
        self.state = "playing"

        self.progress_thread = Thread(target=self.song_progress)
        self.progress_thread.start()

        song_history = QSettings('config/song.ini', QSettings.IniFormat)
        play_history = song_history.value('song_history')
        liked_songs = song_history.value('liked')
        play_history.append(song_path)
        song_history.setValue('song_history', play_history)

        if song_path not in liked_songs:
            self.set_icon(self.ui.like, r'resources/to-be-like.png', size=23)
        else:
            self.set_icon(self.ui.like, r'resources/liked.png', size=23)

    def play_last_song(self):
        if self.state != 'stopped':
            self.pause_play()
        song_history = QSettings('config/song.ini', QSettings.IniFormat)
        play_history = song_history.value('song_history')

        last_path = play_history[-2]
        idx = self.all_list.index(last_path)
        self.ui.tableWidget.selectRow(idx)
        self.play_song()

    def like_clicked(self):
        song_index = self.ui.tableWidget.currentRow()
        song_path = self.all_list[song_index]

        song_history = QSettings('config/song.ini', QSettings.IniFormat)
        liked_songs = song_history.value('liked')

        if song_path not in liked_songs:
            liked_songs.append(song_path)
            self.set_icon(self.ui.like, r'resources/liked.png', size=23)
        else:
            liked_songs.remove(song_path)
            self.set_icon(self.ui.like, r'resources/to-be-like.png', size=23)

        song_history.setValue('liked', liked_songs)

    def show_table_menu(self, position):

        menu_artist = QMenu()
        menu_album = QMenu()

        item = self.ui.tableWidget.itemAt(position)
        if not item:
            return
        column = item.column()

        if column == 1:
            artist_all = item.text()
            if r'/' in artist_all:
                artist_list = artist_all.split(r'/')
            else:
                artist_list = [artist_all]

            actions = {}
            for artist in artist_list:
                actions[artist] = QAction(artist, self.ui.tableWidget)
                menu_artist.addAction(actions[artist])

                # Bind the parameter to the signal handler
                signal_process = partial(self.show_artist, artist=artist)

                # Connect the action to the signal handler
                actions[artist].triggered.connect(signal_process)

            menu_artist.exec_(self.ui.tableWidget.mapToGlobal(position))

        if column == 2:
            album = item.text()
            action = QAction(album, self.ui.tableWidget)
            menu_album.addAction(action)

            # Bind the parameter to the signal handler
            signal_process = partial(self.show_album, album=album)

            # Connect the action to the signal handler
            action.triggered.connect(signal_process)

            menu_album.exec_(self.ui.tableWidget.mapToGlobal(position))

    def show_artist(self, artist):
        # image_url, text_info = Core.get_artist_info(Core.get_artist_page_url(artist))
        # Core.image_down(image_url)
        tab = QWidget()
        self.ui.stackedWidget.addWidget(tab)
        tab.resize(1200, 910)

        # background = QPixmap('tmp/background.jpeg')
        # background = background.scaledToWidth(1200)

        text_label = QLabel(tab)
        text_label.move(30, 70)
        text_label.setText(artist)
        text_label.setStyleSheet("color: black;")
        text_label.setAlignment(Qt.AlignLeft)
        font = QFont('Microsoft Yahei UI Semibold', 30)
        text_label.setFont(font)

        back_button = QPushButton(tab)
        back_button.resize(23, 23)
        back_button.move(30, 38)
        self.set_icon(back_button, r'resources/back.png', size=18)
        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.setStyleSheet("""
        QPushButton
        {
            margin: 0px;
            border: 0px;
            background-color: none;
        }""")

        # image_label = QLabel(tab)
        # image_label.setPixmap(background)
        # image_label.move(10, 0)

        # text_label.raise_()

        # print('start shifting...')
        stack_shift_thread = Thread(target=self.ui.stackedWidget.setCurrentWidget, args=(tab,))
        stack_shift_thread.start()
        # print('done')

    def show_album(self, album):
        print(album)

    def show_artist_thread(self, artist):
        show_artist_thread = Thread(target=self.show_artist, args=(artist,))
        show_artist_thread.start()

    def search(self):
        search_info = self.ui.search_box.text()
        match_items = self.ui.tableWidget.findItems(search_info, Qt.MatchContains)
        row_count = self.ui.tableWidget.rowCount()

        if not search_info:
            return

        if not match_items:
            for i in range(row_count):
                self.ui.tableWidget.setRowHidden(i, True)
        else:
            idx_list = [item.row() for item in match_items]
            for i in range(row_count):
                if i not in idx_list:
                    self.ui.tableWidget.setRowHidden(i, True)

    def restore_clicked(self):
        row_count = self.ui.tableWidget.rowCount()

        for i in range(row_count):
            self.ui.tableWidget.setRowHidden(i, False)

        self.ui.search_box.setText("")

    def display_liked_songs(self):
        self.ui.tableWidget.clearContents()
        songs = QSettings('config/song.ini', QSettings.IniFormat)
        all_like_list = songs.value('liked')
        self.all_list = all_like_list

        self.ui.tableWidget.setRowCount(len(all_like_list))
        for index in range(len(all_like_list)):
            path = all_like_list[index]
            assert isinstance(path, str), 'path is not str!'
            if path.endswith('mp3'):
                title, artist, album = Core().get_mp3_info(path)
                self.ui.tableWidget.setItem(index, 0, QTableWidgetItem(title))
                self.ui.tableWidget.setItem(index, 1, QTableWidgetItem(artist))
                self.ui.tableWidget.setItem(index, 2, QTableWidgetItem(album))


if __name__ == "__main__":
    faulthandler.enable()

    app = QApplication([])
    # app.setStyle("plastique")
    mw = MainWindow()
    mw.setWindowFlag(Qt.FramelessWindowHint)
    mw.ui.show()
    app.exec_()
