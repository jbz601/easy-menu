import os
import socket
import getpass


def get_hostname():
    hostname = socket.gethostname()
    nickname = os.environ.get('NICKNAME')
    return hostname + (' (%s)' % nickname if nickname else '')


def get_username():
    return getpass.getuser()