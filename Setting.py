from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QSettings
import getpass


class Setting:

    def __init__(self):
        self.window = QUiLoader().load(r"resources/Setting.ui")
        palette = self.window.palette()
        palette.setColor(QPalette.Background, '#f3f3f3')
        self.window.setPalette(palette)
        self.window.setAutoFillBackground(True)
        self.username = getpass.getuser()
        # self.window.sources.addItem(f"C:/Users/{self.username}/Music")
        self.init_sources_settings()
        self.window.listWidget.itemSelectionChanged.connect(self.shift_stack)
        self.window.add_source.clicked.connect(self.add_source)
        self.window.delete_source.clicked.connect(self.delete_source)
        self.window.save_button.clicked.connect(self.save_source_changes)

    def shift_stack(self):
        idx = self.window.listWidget.currentRow()
        self.window.stackedWidget.setCurrentIndex(idx + 1)

    def add_source(self):
        new_source = QFileDialog.getExistingDirectory(self.window.add_source, "打开源文件")
        self.window.sources.addItem(new_source)

    def delete_source(self):
        if self.window.sources.currentRow() is not None:
            self.window.sources.takeItem(self.window.sources.currentRow())

    def save_source_changes(self):
        current_sources = []
        for i in range(self.window.sources.count()):
            current_sources.append(self.window.sources.item(i).text())

        source_settings = QSettings('config/source_config.ini', QSettings.IniFormat)
        source_settings.setValue('source_files', current_sources)

    def init_sources_settings(self):
        source_settings = QSettings('config/source_config.ini', QSettings.IniFormat)
        saved_sources = source_settings.value('source_files')

        if saved_sources is not None:
            for source in saved_sources:
                self.window.sources.addItem(source)

        if saved_sources is None or f"C:/Users/{self.username}/Music" not in saved_sources:
            self.window.sources.addItem(f"C:/Users/{self.username}/Music")
