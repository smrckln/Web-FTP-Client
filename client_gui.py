from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCloseEvent
import os
import ftp_class

class FileTree(QTreeView):
    '''
    QTreeView subclass to handle file view
    '''
    def __init__(self, rootPath, parent=None):
        super(FileTree, self).__init__(parent)
        self.model = QFileSystemModel()
        self.model.setRootPath(rootPath)
        self.setModel(self.model)
        self.index = self.model.index('.')

    def mouseDoubleClickEvent(self, event):
        self.index = self.selectedIndexes()[0]
        self.setRootIndex(self.model.index(self.model.filePath(self.index)))

    def chdir_back(self):
        if self.index.parent().isValid():
            self.setRootIndex(self.model.index(self.model.filePath(self.index.parent())))
            self.index = self.index.parent()

    def chdir(self, path):
        self.setRootIndex(self.model.index(path))
        self.index = self.model.index(path)

    def get_path(self):
        return self.model.filePath(self.index)

class Login(QDialog):
    '''
    QDialog subclass to handle login credentials for connection to remote server
    '''
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)

        #layout = QGridLayout
        hostLabel = QLabel("Host:")
        portLabel = QLabel("Port:")
        userLabel = QLabel("Username:")
        passLabel = QLabel("Password:")
        self.hostLine = QLineEdit()
        self.portLine = QLineEdit()
        self.userLine = QLineEdit()
        self.passLine = QLineEdit()

        self.passLine.setEchoMode(QLineEdit.Password)

        layout = QGridLayout(self)
        layout.addWidget(hostLabel,0,0)
        layout.addWidget(self.hostLine,0,1)
        layout.addWidget(portLabel,1,0)
        layout.addWidget(self.portLine,1,1)
        layout.addWidget(userLabel,2,0)
        layout.addWidget(self.userLine,2,1)
        layout.addWidget(passLabel,3,0)
        layout.addWidget(self.passLine,3,1)


        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons,4,1)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def getValues(self):
        host = self.hostLine.text()
        if self.portLine.text() != '':
            port = int(self.portLine.text())
        else:
            port = 0
        user = self.userLine.text()
        passwd = self.passLine.text()
        return (host, port, user, passwd)

    @staticmethod
    def getLogin(parent=None):
        login = Login(parent)
        result = login.exec_()
        host, port, user, passwd = login.getValues()
        return (host, port, user, passwd, result == QDialog.Accepted)




class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.sftp = ftp_class.SFTP()

        host, port, user, passwd, ok = Login.getLogin()
        self.connected = False

        if ok:
            self.connected = self.sftp.connect(user, passwd, host, port)

        if self.sftp.isActive():
            pathLabel = QLabel("Goto Path:")
            self.pathLine = QLineEdit()
            self.go_btn = QPushButton("Go")

            self.go_btn.clicked.connect(self.goto_path)


            self.view = FileTree(self.sftp.get_cwd())

            self.back_btn = QPushButton("Back")
            self.back_btn.clicked.connect(self.back)

            self.down_btn = QPushButton("Download")
            self.up_btn = QPushButton("Upload")

            self.down_btn.clicked.connect(self.download)
            self.up_btn.clicked.connect(self.upload)

            mainLayout = QVBoxLayout()
            btnLayout = QGridLayout()
            upDownLayout = QGridLayout()

            btnLayout.addWidget(self.back_btn,0,0)
            btnLayout.addWidget(pathLabel,0,1)
            btnLayout.addWidget(self.pathLine,0,2)
            btnLayout.addWidget(self.go_btn,0,3)

            upDownLayout.addWidget(self.down_btn,0,0)
            upDownLayout.addWidget(self.up_btn,0,1)

            mainLayout.addItem(btnLayout)
            mainLayout.addWidget(self.view)
            mainLayout.addItem(upDownLayout)


            self.setLayout(mainLayout)
            self.setWindowTitle("FTP Client")
            self.setFixedSize(800,500)
            self.show()

        else:
            if self.sftp.isActive():
                self.sftp.close()
            sys.exit(0)

    def back(self):
        self.view.chdir_back()

    def goto_path(self):
        path = self.pathLine.text()
        self.view.chdir(path)

    def download(self):
        remotepath = self.view.get_path()
        localpath = QFileDialog.getSaveFileName(self, "Save file",
                                                os.path.join(os.getcwd(),'untitled'))

    def upload(self):
        pass

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = Form()
    #screen.show()

    sys.exit(app.exec_())
