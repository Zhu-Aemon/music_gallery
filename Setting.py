from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette, QImage, QPixmap, Qt
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QSettings, QSize

from Gallery import Core

import getpass


class Setting:

    def __init__(self):
        self.window = QUiLoader().load(r"resources/Setting.ui")
        self.username = getpass.getuser()
        self.window_init()
        self.signal_process()

    def window_init(self):
        """
        初始化设置窗口，包括背景颜色与相关侧边选项卡资源
        :return: None
        """

        # 设置背景颜色
        palette = self.window.palette()
        palette.setColor(QPalette.Background, '#f3f3f3')
        self.window.setPalette(palette)
        self.window.setAutoFillBackground(True)
        self.set_style_sheet()

        # 初始化来源管理
        self.init_sources_settings()
        self.init_avatar_setting()

    def signal_process(self):
        """
        信号处理
        :return: None
        """

        self.window.add_source.clicked.connect(self.add_source)
        self.window.delete_source.clicked.connect(self.delete_source)
        self.window.save_button.clicked.connect(self.save_source_changes)
        self.window.sources.addItem(f"C:/Users/{self.username}/Music")
        self.window.listWidget.itemSelectionChanged.connect(self.shift_stack)
        self.window.avatar.clicked.connect(self.select_avatar)
        self.window.save.clicked.connect(self.save_username)

    def shift_stack(self):
        """
        侧边选项卡点击切换右侧界面信号处理函数
        :return: None
        """

        idx = self.window.listWidget.currentRow()
        self.window.stackedWidget.setCurrentIndex(idx + 1)

    def add_source(self):
        """
        添加来源的处理函数
        :return: None
        """

        new_source = QFileDialog.getExistingDirectory(self.window.add_source, "打开源文件")
        self.window.sources.addItem(new_source)

    def delete_source(self):
        """
        删除来源的信号处理函数
        :return: None
        """

        if self.window.sources.currentRow() is not None:
            self.window.sources.takeItem(self.window.sources.currentRow())

    def save_source_changes(self):
        """
        保存已经发生的变化的信号处理函数
        :return: None
        """

        current_sources = []
        for i in range(self.window.sources.count()):
            current_sources.append(self.window.sources.item(i).text())

        source_settings = QSettings('config/source_config.ini', QSettings.IniFormat)
        source_settings.setValue('source_files', current_sources)

    def init_sources_settings(self):
        """
        初始化来源
        :return: None
        """

        source_settings = QSettings('config/source_config.ini', QSettings.IniFormat)
        saved_sources = source_settings.value('source_files')

        if saved_sources is not None:
            for source in saved_sources:
                self.window.sources.addItem(source)

        if saved_sources is None or f"C:/Users/{self.username}/Music" not in saved_sources:
            self.window.sources.addItem(f"C:/Users/{self.username}/Music")

    def select_avatar(self):
        avatar = QFileDialog.getOpenFileName(self.window.avatar, "选择个人资料图片")
        avatar_setting = QSettings('config/source_config.ini', QSettings.IniFormat)
        avatar_setting.setValue('avatar', avatar[0])

        self.set_icon(self.window.avatar, avatar[0], size=50)

    def init_avatar_setting(self):
        avatar_setting = QSettings('config/source_config.ini', QSettings.IniFormat)
        avatar_source = avatar_setting.value('avatar')
        username = avatar_setting.value('username')
        if avatar_source:
            Core.circle_corner(avatar_source, 0.2, r'tmp/avatar.png')
            self.set_icon(self.window.avatar, r'tmp/avatar.png', size=50)
        if username:
            self.window.username.setText(username)
        else:
            self.window.username.setText('enter username')

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

    def set_style_sheet(self):
        self.window.username.setStyleSheet("""
        QLineEdit {
            border: none;
            outline: none;
            background: #fff;
            font: 14px 'Microsoft Yahei';
            border-radius: 5px;
        }""")

    def save_username(self):
        username = self.window.username.text()
        avatar_setting = QSettings('config/source_config.ini', QSettings.IniFormat)
        avatar_setting.setValue('username', username)
