import PyQt5
from PyQt5.QtWidgets import *
from PyQt5 import uic

class MyGUI(QMainWindow):
    def __init__(self):
        super(MyGUI, self).__init__()
        uic.loadUi("my_ui.ui", self)
        self.show()

        self.pushButton.clicked.connect(self.submit)

    def submit(self):
        if self.lineEdit_3.text() == "text":
            self.lineEdit.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
        else:
            message = QMessageBox()
            message.setText("Invalid API Key")
            message.exec_()

def main():
    app = QApplication([])
    window = MyGUI()
    app.exec_()

if __name__ == "__main__":
    main()