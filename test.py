from PySide2 import QtWidgets, QtGui


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Create a QTableWidget and set its properties
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        self.table.setVerticalHeaderLabels(["Row 1", "Row 2", "Row 3"])

        # Set the itemClicked signal to call the switch_page method
        # when the user clicks on an item in the table
        self.table.itemClicked.connect(self.switch_page)

        # Add the table to a layout and set the layout on the window
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def switch_page(self, item):
        # Get the index of the item that was clicked on
        index = self.table.indexFromItem(item)

        # Check if a valid item was clicked on
        if index.isValid():
            # Create a new page to switch to
            new_page = QtWidgets.QWidget()
            new_page.setWindowTitle("New Page")
            new_page.show()

            # Hide the current page
            self.hide()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()
