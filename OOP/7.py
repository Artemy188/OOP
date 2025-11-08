import sys
from PyQt6 import QtWidgets, uic


class MyDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('my_form.ui', self)
        self.pushButton.clicked.connect(self.save_data)
    def save_data(self):
        text1 = self.lineEdit.text()
        text2 = self.lineEdit_2.text()
        self.label.setText(f"{text1}, {text2}")
        print(f"Данные сохранены: {text1}, {text2}")
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = MyDialog()
    dialog.show()
    sys.exit(app.exec())