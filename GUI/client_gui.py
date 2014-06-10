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
        if self.selectedIndexes():
            index = self.selectedIndexes()[0]
            return self.model.filePath(index)
        else:
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

        self.login_attempted = False
        self.login_authed = False
        self.connected = False

        while not self.connected:
          self.sftp = ftp_class.SFTP()
          if not self.login_authed:
              host, port, user, passwd, ok = Login.getLogin()

              if ok:
                  self.connected = self.sftp.connect(user, passwd, host, port)
                  self.login_attempted = True

              if not self.connected:
                  self.closeEvent(QCloseEvent())

        self.login_authed = True
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

    def back(self):
        self.view.chdir_back()

    def goto_path(self):
        path = self.pathLine.text()
        self.view.chdir(path)

    def download(self):
        remotepath = self.view.get_path()
        localpath = QFileDialog.getSaveFileName(self, "Save file",
                                                os.path.join(os.getcwd(),'untitled'))
                                                
        success = self.sftp.get(remotepath, localpath[0])

        if success:
            QMessageBox.information(self, 'Success', 'File successfully downloaded')
        else:
            QMessageBox.information(self, 'Error', 'Error retrieving file')

        self.view.clearSelection()

    def upload(self):
        self.view.clearSelection()

        localpath = QFileDialog.getOpenFileName(self, 'Choose file',
                                                os.environ['HOME'])

        temp_index = localpath[0].rfind('/')
        temp_path = localpath[0][temp_index:]

        remotepath = self.view.get_path() + temp_path

        success = self.sftp.put(remotepath, localpath[0])

        if success:
            QMessageBox.information(self, 'Success', 'File successfully uploaded')
        else:
            QMessageBox.information(self, 'Error', 'Error uploading file')

    def closeEvent(self, event):
        if not self.login_attempted:
            event.accept()
            sys.exit(0)
        elif self.login_attempted and not self.login_authed:
            response = QMessageBox.question(self, "Login denied",
                                            "Login credentials not correct. Retry?",
                                            QMessageBox.Ok | QMessageBox.Cancel,
                                            QMessageBox.Ok)
            if response == QMessageBox.Ok:
                event.ignore()
            else:
                event.accept()
                sys.exit(0)
        elif self.login_attempted and self.login_authed:
            if self.isVisible():
                response = QMessageBox.question(self, "Exit?",
                                                "Are you sure you want to exit?",
                                                QMessageBox.Ok | QMessageBox.Cancel,
                                                QMessageBox.Ok)
                if response == QMessageBox.Ok:
                    self.sftp.close()
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = Form()
    screen.show()

    sys.exit(app.exec_())
