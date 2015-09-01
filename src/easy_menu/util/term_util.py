from __future__ import division, print_function, absolute_import, unicode_literals

import sys
import os
import time
import subprocess

if os.name == 'nt':
    # for Windows
    import msvcrt
else:
    # for Unix/Linux/Mac
    import termios
    import tty

LAST_GETCH_TIME = 0.0
LAST_GETCH_CHAR = ''


def _wrap_termios(_input, func):
    assert hasattr(_input, 'fileno'), 'Invalid input device.'

    fd = _input.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        ret = func()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ret


def getch(_input=sys.stdin):
    """Wait and get one character from input"""

    global LAST_GETCH_TIME
    global LAST_GETCH_CHAR

    if os.name == 'nt':
        ch = msvcrt.getch()
    else:
        ch = _wrap_termios(_input, lambda: _input.read(1))

    t = time.time()

    # check key repeat
    if LAST_GETCH_CHAR == ch:
        if t < LAST_GETCH_TIME + 0.3:
            LAST_GETCH_TIME = t
            return ''

    LAST_GETCH_TIME = t
    LAST_GETCH_CHAR = ch
    return ch


def clear_screen(_input=sys.stdin, _output=sys.stdout):
    """Clear terminal screen."""

    if not _input.isatty():
        return

    cmd = 'cls' if os.name == 'nt' else 'clear'
    subprocess.call(cmd, shell=True, stdin=_input, stdout=_output, stderr=_output)
