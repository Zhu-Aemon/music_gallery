from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QSettings
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

        # 初始化来源管理
        self.init_sources_settings()

    def signal_process(self):
        """
        信号处理
        :return: None
        """
        self.window.add_source.clicked.connect(self.add_source)
        self.window.delete_source.clicked.connect(self.delete_source)
        self.window.save_button.clicked.connect(self.save_source_changes)
        # self.window.sources.addItem(f"C:/Users/{self.username}/Music")
        self.window.listWidget.itemSelectionChanged.connect(self.shift_stack)

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
