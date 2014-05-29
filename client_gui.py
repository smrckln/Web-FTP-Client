from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import ftp_class

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.sftp = ftp_class.SFTP()

        hostLabel = QLabel("Host:")
        portLabel = QLabel("Port:")
        userLabel = QLabel("Username:")
        passLabel = QLabel("Password:")
        self.hostLine = QLineEdit()
        self.portLine = QLineEdit()
        self.userLine = QLineEdit()
        self.passLine = QLineEdit()
        self.connectBtn = QPushButton('&Connect')

        self.passLine.setEchoMode(QLineEdit.Password)

        buttonLayout1 = QGridLayout()
        buttonLayout1.addWidget(hostLabel,0,0)
        buttonLayout1.addWidget(self.hostLine,0,1)
        buttonLayout1.addWidget(portLabel,1,0)
        buttonLayout1.addWidget(self.portLine,1,1)
        buttonLayout1.addWidget(userLabel,2,0)
        buttonLayout1.addWidget(self.userLine,2,1)
        buttonLayout1.addWidget(passLabel,3,0)
        buttonLayout1.addWidget(self.passLine,3,1)
        buttonLayout1.addWidget(self.connectBtn,4,1)

        self.connectBtn.clicked.connect(self.connectFTP)

        mainLayout = QGridLayout()
        mainLayout.addLayout(buttonLayout1,0,0)

        self.setLayout(mainLayout)
        self.setWindowTitle("FTP Client")

        #print self.sftp.is_active()

    def connectFTP(self):
        host = self.hostLine.text()
        port = int(self.portLine.text())
        user = self.userLine.text()
        passwd = self.passLine.text()

        ok = self.sftp.connect(user, passwd, host, port)

        if not ok:
            QMessageBox.information(self, "problem",
                                    "problem")
            return
        else:
            QMessageBox.information(self, "Success!",
                                    "Success!")
        self.sftp.close()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = Form()
    screen.show()

    sys.exit(app.exec_())
