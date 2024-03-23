from PyQt5 import QtCore, QtGui, QtWidgets
import socket, time
from PyQt5.QtWidgets import QMessageBox
import tetris

def find(raw: str):
    first = None
    for num, sign in enumerate(raw):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            result = list(raw[first + 1:second].split(","))
            return result
    return ""

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(684, 630)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(280, 10, 111, 41))
        self.label.setStyleSheet("background-color: rgb(38, 255, 0);")
        self.label.setObjectName("label")
        self.pushButton_2 = QtWidgets.QPushButton(parent=self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(240, 350, 191, 31))
        self.pushButton_2.setStyleSheet("")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.func)
        self.label_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(300, 110, 81, 41))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(300, 220, 71, 31))
        self.label_3.setObjectName("label_3")
        self.lineEdit = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(280, 50, 113, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(280, 150, 113, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(parent=self.centralwidget)
        self.lineEdit_3.setGeometry(QtCore.QRect(280, 250, 113, 31))
        self.lineEdit_3.setObjectName("lineEdit_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 684, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.score = 0
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "Войти"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600;\">IP-адрес</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:10pt; font-weight:600;\">Никнэйм</span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt; font-weight:600;\">Пароль</span></p></body></html>"))
    
    def func(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            row = self.lineEdit.text()
            row1 = row.split(':')
            self.port = row1[1]
            row1 = str(row1[0])
            row1 = row1.split(',')
            row1 = str(row1[0])
            self.ip = row1.split('.')
        except:
            print('invalid str')
            return
        if not (self.port.isnumeric() and 1024 <= int(self.port) <= 65535):
            print('invalid port')
            return
        for byte in self.ip:
            if not (byte.isnumeric() and 0 <= int(byte) <= 255):
                print('invalid ip')
                return
        if len(self.ip)!=4:
            print('invalid ip')
            return
        self.name = self.lineEdit_2.text()
        if len(self.name) < 1:
            print('invalid nickname')
            return
        self.pasw = self.lineEdit_3.text()
        if len(self.pasw) < 1:
            print('invalid password')
            return
        self.ip = '.'.join(self.ip)
        print(self.name,self.pasw)
        print(self.ip,self.port)
        try:
            sock.connect((self.ip, int(self.port)))
            info = f"<{self.name},{self.pasw}>".encode()
            sock.send(info)
        except:
            print("Не смог подключиться")
            return
        tick = 0
        while True:
          try:
              data = sock.recv(1024).decode()
              data = find(data)
              print(data)
              if int(data[0]) >= 0:
                  self.start_game()
                  return
              if data[0] == '0':
                  return
              if data[0] == '-1':
                  wrong = QMessageBox()
                  wrong.setWindowTitle("Внимание")
                  wrong.setText("Неправильный пароль. Попробуйте ещё раз.")
                  wrong.setIcon(QMessageBox.Icon.Warning)
                  wrong.exec()
                  return
          except:
              tick += 1
              time.sleep(0.5)
              if tick == 20:
                  return
    def start_game(self):
        self.tetris = tetris.Tetris(self,app)
        self.tetris.setStyleSheet("background-color: white")
        self.tetris.show()
        self.close()
    def showEvent(self, event):
        if self.score == 0:
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        try:
            print(1)
            sock.connect((self.ip, int(self.port)))
            print(2)
            info = f"<final,{self.name},{self.pasw},{self.score}>".encode()
            sock.send(info)
            print(3)
        except:
            print("Не смог подключиться")
            return

class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
if __name__ == "__main__":
    import sys
    stylesheet = """
QMainWindow {
 background-image: url("Giraffe.JPG");
 background-repeat: no-repeat;
 background-position: center;
} """
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    w = Window()
    w.show()
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    sys.exit(app.exec())
