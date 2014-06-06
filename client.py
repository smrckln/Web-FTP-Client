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

    prompt = 'SFTP>>> '
    intro = 'Welcome to SFTP shell. Type help to list commands. \n'

    def do_setuser(self, arg):
        'Set username or use default. To set, pass command as >>> setuser user.\nTo use default, simply type >>> setuser'
        if len(arg) == 0:
            self.username = "anonymous"
        else:
            self.username = arg

    def do_setpass(self, arg):
        'Set password or use default. To set, pass command as >>> setpass \nTo use default, simply type >>> setpass default'
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
        'Set port by passing arg as >>> setport port\nTo use default port simply type >>> setport'
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
        self.sftp.chdir('.')
        self.root_dir = self.sftp.getcwd()
        print '\nConnected'

    def do_list(self, args):
        """List files in current directory"""
        dirlist = self.sftp.listdir_attr(self.sftp.getcwd())
        for file in dirlist:
            if S_ISDIR(file.st_mode):
                print file.filename, '(folder)\n'
            elif S_ISREG(file.st_mode):
                print file.filename, '(file)\n'

    def do_cd(self, args):
        'Change directory to path passed. cd .. goes up 1 directory. No arg goes to root'
        if len(args) == 0:
            self.sftp.chdir(self.root_dir)
        elif args == '..':
            self.sftp.chdir('..')
        else:
            self.sftp.chdir(args)

    def do_get(self, args):
        'Download file from server to local by passing filename'
        if len(args) == 0:
            print 'Must pass filename'
        else:
            localpath = raw_input('Enter path for downloaded file (default %s)' % os.getcwd())
            if localpath == '':
                localpath = os.getcwd() + '/' + args
            remotepath = self.sftp.getcwd() + '/' + args
            print 'Download Started'
            self.sftp.get(remotepath, localpath)
            print 'Download Completed'

    def do_put(self, args):
        'Upload file from local to server by passing full file path and remote path'
        if len(args) == 0:
            print 'Must pass filename'
        else:
            localpath = args
            remotepath = raw_input('Please enter path for upload to remote server (default %s)' % self.sftp.getcwd())
            if remotepath == '':
                remotepath = self.sftp.getcwd()
            print 'Upload Started'
            self.sftp.put(localpath, remotepath)
            print 'Upload Completed'

    def do_disconnect(self, args):
        'Closes open connection'
        print 'Closing open connection'
        if self.trans.is_active():
            self.trans.close()
            print 'Connection closed'
        else:
            print 'No open connections'

    def do_quit(self, args):
        """Quits shell and closes FTP connection"""
        print "Closing Connection"
        try:
            self.trans.close()
            raise SystemExit
        except:
            raise SystemExit

if __name__ == '__main__':
    shell = FTPShell()
    os.system('clear')
    shell.cmdloop()
