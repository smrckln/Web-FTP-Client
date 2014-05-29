'''
    Class written by Samuel Ricklin

    Makes use of paramiko ssh/ftp library for ease of connections

    Class written to facilitate connections with GUI as simply importing
    paramiko would get hairy

'''

import paramiko

class SFTP():
    def __init__(self):
        self.user = ''
        self.passwd = ''
        self.host = 'localhost'
        self.port = 22
        self.trans = paramiko.Transport((self.host, self.port))

    def connect(self, user='', passwd='', host='localhost', port=22):
        self.trans = paramiko.Transport((host, port))
        self.trans.connect(username=user, password=passwd)
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)

        return self.trans.is_active()

    def close(self):
        if self.trans.is_active():
            self.trans.close()
