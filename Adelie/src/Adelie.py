from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5 import QtGui
import re
import sys
import subprocess
from main_window_logic import main_window_logic
"""Main function of and the starting point of this project.
"""
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = main_window_logic(None)

    ui.show()

    sys.exit(app.exec_())
