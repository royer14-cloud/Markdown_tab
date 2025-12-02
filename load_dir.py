# paths.py
import os
import sys


def load_init():
    global BASE_DIR
    if hasattr(sys, '_MEIPASS'):
        BASE_DIR = sys._MEIPASS
    elif getattr(sys, 'frozen',False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    os.chdir(BASE_DIR)


def abs_path(*paths):
    return os.path.join(BASE_DIR, *paths)
