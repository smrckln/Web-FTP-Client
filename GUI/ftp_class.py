'''
    Class written by Samuel Ricklin

    Makes use of paramiko ssh/ftp library for ease of connections

    Class written to facilitate connections with GUI as simply importing
    paramiko would get hairy

'''
import os
from stat import S_ISDIR
from stat import S_ISREG
import paramiko

class SFTP():
    def __init__(self):
        self.user = ''
        self.passwd = ''
        self.host = 'localhost'
        self.port = 22
        self.trans = paramiko.Transport((self.host, self.port))
        self.cwd = '.'

    def connect(self, user='anonymous', passwd='anonymous@', host='localhost', port=22):
        ''' connects to host/port with user/pass
            returns true if connected
        '''
        try:
            self.trans = paramiko.Transport((host, port))
            self.trans.connect(username=user, password=passwd)
            self.sftp = paramiko.SFTPClient.from_transport(self.trans)
            self.sftp.chdir(self.cwd)

            return self.trans.is_authenticated()
        except:
            return False

    def get_cwd(self):
        ''' Returns current working directory'''
        return self.sftp.getcwd()

    def chdir(self, path='.'):
        ''' Changes directory to given path
            Default path -> .
        '''
        self.sftp.chdir(path)

    def list_files(self):
        ''' Returns list of files in current directory '''
        files = []
        dirlist = self.sftp.listdir_attr(self.sftp.getcwd())
        for file in dirlist:
            if S_ISDIR(file.st_mode):
                files.append("(folder) " + file.filename)
            elif S_ISREG(file.st_mode):
                files.append("(file) " + file.filename)
        return files

    def is_active(self):
        return self.trans.is_authenticated()

    def close(self):
        if self.trans.is_authenticated():
            self.trans.close()
