from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QFileDialog
import getpass


class Setting:

    def __init__(self):
        self.window = QUiLoader().load(r"resources/Setting.ui")
        palette = self.window.palette()
        palette.setColor(QPalette.Background, '#f3f3f3')
        self.window.setPalette(palette)
        self.window.setAutoFillBackground(True)
        self.username = getpass.getuser()
        self.window.sources.addItem(f"C:/Users/{self.username}/Music")
        self.window.listWidget.itemSelectionChanged.connect(self.shift_stack)
        self.window.add_source.clicked.connect(self.add_source)
        self.window.delete_source.clicked.connect(self.delete_source)

    def shift_stack(self):
        idx = self.window.listWidget.currentRow()
        self.window.stackedWidget.setCurrentIndex(idx + 1)

    def add_source(self):
        new_source = QFileDialog.getExistingDirectory(self.window.add_source, "打开源文件")
        self.window.sources.addItem(new_source)

    def delete_source(self):
        if self.window.sources.currentRow() is not None:
            self.window.sources.takeItem(self.window.sources.currentRow())
