
from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import  QFileDialog

from GNU_Logic import GNU_Logic
from Ping_UI_Logic import Ping_UI_Logic
from ifconfig_Logic import ifconfig_Logic
from iwconfig_Logic import iwconfig_Logic
from netstat_Logic import netstat_Logic
import sys
import os.path


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(CURRENT_DIR, "GUI")

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

        self.actionPing_4.triggered.connect(self.Show_Ping_Widgets)
        self.actionIfconfig.triggered.connect(self.Show_Ifconfig_Logic)
        self.actionIwconfig.triggered.connect(self.Show_Iwconfig_Logic)
        self.actionNetstat.triggered.connect(self.Show_Netstat_Logic)
        self.actionGNU_Core_Utilities.triggered.connect(self.Show_GNU_Widgets)

        self.GNU_Logic = GNU_Logic()
        layout = self.centralWidget()
        layout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget.addWidget(self.GNU_Logic)
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentWidget(self.GNU_Logic)

        self.ping_widget = Ping_UI_Logic()
        self.stackedWidget.addWidget(self.ping_widget)
        
        self.ifconfig_widget = ifconfig_Logic()
        self.stackedWidget.addWidget(self.ifconfig_widget)

        self.iwconfig_widget = iwconfig_Logic()
        self.stackedWidget.addWidget(self.iwconfig_widget)

        self.netstat_widget = netstat_Logic()
        self.stackedWidget.addWidget(self.netstat_widget)

    def Show_GNU_Widgets(self):
        """Displays the GNU Core Utilities GUI.
        """ 
        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget.setCurrentWidget(self.GNU_Logic)

    def Show_Ifconfig_Logic(self):
        """Displays ifconfig GUI
        """
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget.setCurrentWidget(self.ifconfig_widget)

    def Show_Iwconfig_Logic(self):
        """Displays iwconfig GUI
        """
        self.stackedWidget.setCurrentIndex(2)
        self.stackedWidget.setCurrentWidget(self.iwconfig_widget)

    def Show_Netstat_Logic(self):
        """Displays netstat GUI
        """
        self.stackedWidget.setCurrentIndex(3)
        self.stackedWidget.setCurrentWidget(self.netstat_widget)

    def Show_Ping_Widgets(self):
        """Displays Ping GUI
        """
        self.stackedWidget.setCurrentIndex(4)
        self.stackedWidget.setCurrentWidget(self.ping_widget)

    



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = main_window_logic(None)

    ui.show()

    sys.exit(app.exec_())
