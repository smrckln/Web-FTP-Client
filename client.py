import getpass
import sys
import os
from stat import S_ISDIR
from stat import S_ISREG
import traceback
import getopt
import paramiko
from cmd import Cmd


class FTPShell(Cmd):

    intro = 'Welcome to SFTP shell. Type help to list commands. \n'
    prompt = 'SFTP>>> '

    def do_setuser(self, arg):
        'Set username or use default.'\
        ' To set, pass command as >>> setuser user.'\
        '\nTo use default, simply type >>> setuser'
        if len(arg) == 0:
            self.username = "anonymous"
        else:
            self.username = arg

    def do_setpass(self, arg):
        'Set password or use default. To set, pass command as >>> setpass' \
        ' \nTo use default, simply type >>> setpass default'
        if len(arg) == 0:
            self.password = getpass.getpass()
        elif arg == 'default':
            self.password = 'anonymous@'
        else:
            print 'Please enter a valid command'

    def do_sethost(self, arg):
        'Set hostname by passing arg as >>> sethost hostname'
        if len(arg) == 0:
            print "Must pass host"
        else:
            self.host = arg

    def do_setport(self, arg):
        'Set port by passing arg as >>> setport port\n' + \
        'To use default port simply type >>> setport'
        if len(arg) == 0:
            self.port = 22
        else:
            port = int(arg)

    def do_connect(self, arg):
        """Start FTP connection with userpass, URL and port already passed"""
        print "Connecting..."
        self.trans = paramiko.Transport((self.host, self.port))
        self.trans.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.trans)
        print '\nConnected'

    def do_list(self, args):
        """List files in current directory"""
        dirlist = self.sftp.listdir_attr('.')
        for file in dirlist:
            if S_ISDIR(file.st_mode):
                print file, ' folder ', '\n'
            elif S_ISREG(file.st_mode):
                print file, ' file', '\n'

    def do_cd(self, args):
        'Change directory to path passed. cd .. goes up 1 directory.'\
        ' No arg goes to root'
        if len(args) == 0:
            self.sftp.chdir('.')
        elif args == '..' and self.sftp.getcwd():
            'Super convoluted and needs to be changed'
            cwd = self.sftp.getcwd()
            cwd_reverse = cwd[::-1]
            index = cwd_reverse.find('/')
            cwd_reverse = cwd_reverse[index+1:]
            new_dir = cwd_reverse[::-1]
            self.sftp.chdir(new_dir)
        else:
            self.sftp.chdir(args)

    def do_quit(self, args):
        """Quits shell and closes FTP connection"""
        print "Closing Connection"
        self.trans.close()
        raise SystemExit

if __name__ == '__main__':
    shell = FTPShell()
    shell.cmdloop('Starting SFTP Shell...')
