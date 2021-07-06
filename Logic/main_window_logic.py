
from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import  QFileDialog

from GNU_Handler import GNU_Handler
from GNU_Logic import GNU_Logic
import sys
import os.path

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(PARENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "main_window.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)


class main_window_logic(baseUIWidget, baseUIClass):
    """
        Main container of the applications

        Attributes:
            GNU_Logic (:class:`GNU_Logic`): The GNU Core Utilities interface.
    """    

    def __init__(self, parent=None):

        super(main_window_logic, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
                            QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowMinimizeButtonHint
                            )
        self.GNU_Logic = GNU_Logic()
        self.Show_GNU_Widgets()

    def Show_GNU_Widgets(self):
        """Displays the ``GNU`` Core Utilities GUI.
        """        
        
        self.setCentralWidget(self.GNU_Logic)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = main_window_logic(None)

    ui.show()

    sys.exit(app.exec_())
