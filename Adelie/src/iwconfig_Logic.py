from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5.QtWidgets import  QFileDialog, QTableWidgetItem
from CronTab_Options_Logic import CronTab_Options_Logic
import subprocess
import sys
import re
import os.path
import time


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(CURRENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "iwconfig.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)

class iwconfig_Logic(baseUIWidget, baseUIClass):
    """Provides a UI for the ``iwconfig`` utility.

        Using this class users can utilize the ``iwconfig`` utility
        on Linux Systems
    

        This class handles the logic for ``iwconfig.ui``
        Users that use the GUI will be able to configure
        a wireless interface
        ESSID, Frequency, Mode, Access Point.
        Users can also turn the interface on or off.

        

    Attributes:
        iwconfig_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``iwconfig`` processes.
        essid_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``iwconfig`` processes that change an interface 
            essid.
        freq_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``iwconfig`` processes that change an interface 
            frequency.
        mode_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``iwconfig`` processes that changes an interface 
            mode.
        ap_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``iwconfig`` processes that changes an interface
            Access Point.
        flush_process (:obj:`QProcess`): QProcess object that is used 
            to flush the interface IP addresses to default settings.
        restart_process (:obj:`QProcess`): Process object that is used 
            to reset the interface to default settings.

        send_command (:obj:`pyqtSignal(str)`): Emits a signal that is connected 
            to the ``command_history``, the signal contains the command formed.
        send_output (:obj:`pyqtSignal(str)`): Emits a signal 
                when the ``iwconfig`` process has an available output to be read.

        wireless_interfaces (:obj:`dict`): Dictionary that contains a list of 
            all active wireless inferfaces.   

    Warning:
            Requires Administrator Privilege.    

    Note:
        This is an educational tool and does not use the use
        ``iwconfig`` utility at its full potential
        Since this is an educational tool, a reset button is implemented to
        restore the system default settings.
            

    """    

   
    iwconfig_process = QProcess()
    essid_process = QProcess()
    freq_process = QProcess()
    mode_process = QProcess()
    ap_process = QProcess()
    flush_process = QProcess()
    restart_process = QProcess()

    send_output = pyqtSignal(str)
    send_command = pyqtSignal(str)

    wireless_interfaces = {}

    def __init__(self, parent=None):
        super(iwconfig_Logic, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
                            QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowMinimizeButtonHint)
        self.crontab_options = None
        self.label_error.hide()
# ==============================================================================
#                       GUI SIGNALS
# ==============================================================================
        self.reset_button.clicked.connect(self.Reset_Interface)
        self.iwconfig_button.clicked.connect(self.Show_Wireless_Interfaces)
        self.clear_terminal_button.clicked.connect(self.Clear_Terminal)
        self.clear_history_button.clicked.connect(self.Clear_History)
        self.interface_table.itemChanged.connect(self.Configure_Changes)

        self.iwconfig_process.readyReadStandardOutput.connect(
                                                            self.Connect_Output)

        self.send_command.connect(self.Print_Command)
        self.send_output.connect(self.Print_Output)

        self.iwconfig_process.readyReadStandardError.connect(
                                                        self.IWCONFIG_Error)
        self.essid_process.readyReadStandardError.connect(self.ESSID_Error)
        self.freq_process.readyReadStandardError.connect(self.Freq_Error)
        self.mode_process.readyReadStandardError.connect(self.Mode_Error)
        self.ap_process.readyReadStandardError.connect(self.AP_Error)

        self.essid_process.finished.connect(self.Finished_ESSID)
        self.freq_process.finished.connect(self.Finished_Frequency)
        self.mode_process.finished.connect(self.Finished_Mode)
        self.ap_process.finished.connect(self.Finished_AP)
        self.crontab_options_button.clicked.connect(
                                                    self.Show_CronTab_Options)
#===============================================================================

    def Show_CronTab_Options(self):

        """
            Show CronTab Options Menu.
        """
        #  Check if options menu was created
        #  If it was created, show the menu

        if self.crontab_options is None:
            self.crontab_options = CronTab_Options_Logic()
        self.crontab_options.show()

    def Get_Interface_name(self):

        """
            This method finds the name of the interfaces that are active
            and adds the interface name to the table (``the interface_table``).

            REGEX are used to find the data mentioned
            ESSID, Frequency, Mode and Access Point Address.
           
        """

        self.label_error.hide()
        interface_dict = {}
        essid = ""
        mode = ""
        frequency = ""
        ap = ""
        output = subprocess.check_output(['iwconfig'], universal_newlines=True)
        # Find interface name
        result = re.findall(r"^\w+", output)
        for interface in result:
            # IF interface is not connected
            # there is no ESSID, Frequency, Mode, AP
            if re.search(r"\"(\w+)\"", output) is not None:
                essid = re.search(r"\"(\w+)\"", output)[1]
            if re.search(r"Mode:(\w+)", output) is not None:
                mode = re.search(r"Mode:(\w+)", output)[1]
            if re.search(r"Frequency:(.+GHz)", output) is not None:
                frequency = re.search(r"Frequency:(.+GHz)", output)[1]
            ap = re.findall(r"Access Point:\s(?:[0-9a-fA-F]:?){12}", output)
            ap = "".join(ap).replace("Access Point: ", "")

            # Add data in a dictionary
            # {Interface Name: [ESSID, Frequency, Mode, AP]}
            interface_dict.setdefault(interface, [essid, frequency, mode, ap])
        self.wireless_interfaces = interface_dict
        #  Return if there are no wireless interfaces
        if self.wireless_interfaces == {}:
            return
        for item in interface_dict:
            rowPosition = self.interface_table.rowCount()
            self.interface_table.insertRow(rowPosition)
            # Interface name is not editable using IWCONFIG
            item_not_editable = QtWidgets.QTableWidgetItem(item)
            item_not_editable.setFlags(QtCore.Qt.ItemIsSelectable
                                       | QtCore.Qt.ItemIsEnabled)
            self.interface_table.setItem(rowPosition, 0, item_not_editable)
            self.interface_table.setItem(rowPosition, 1,
                                         QTableWidgetItem(
                                                        interface_dict[item][0]
                                                        ))
            self.interface_table.setItem(rowPosition, 2,
                                         QTableWidgetItem(
                                                        interface_dict[item][1]
                                                        ))
            self.interface_table.setItem(rowPosition, 3,
                                         QTableWidgetItem(
                                                        interface_dict[item][2]
                                              ))
            self.interface_table.setItem(rowPosition, 4,
                                         QTableWidgetItem(
                                                        interface_dict[item][3]
                                                        ))

        # Set all tables resize contents width
        header = self.interface_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

    def Connect_Output(self):

        """
            Reads the :obj:`.iwconfig_process` standard output and decodes it.
            Then it is displayed on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        output = self.iwconfig_process.readAllStandardOutput()
        data = bytes(output).decode("utf8").strip()
        if output.isEmpty():
            return
        self.send_output.emit(data)

    def Show_Wireless_Interfaces(self):

        """
            Executes the command ``iwconfig`` that displays
            wireless interfaces.
        """

        self.iwconfig_process.start("iwconfig", [])
        self.send_command.emit("iwconfig")

        if self.crontab_enable.isChecked():
            if self.crontab_options is None:
                self.label_error.show()
                self.label_error.setText("Set CronTab Options First!")
                return
            self.crontab_options.Start_Job("iwconfig")
        self.Reload_Changes()

    def Print_Output(self, str):
        """This methods prints the process output on the output terminal.

        Args:
            str (:obj:`str`): Output to be printed on the output terminal 
                (``output_terminal``).
        """        

        self.output_terminal.appendPlainText(str)

    def Print_Command(self, str):
        """This method prints the command on the command history.

        Args:
            str (:obj:`str`): Command to be printed on the command history
                (``command_history``).
        """        

        self.command_history.append(str)

    def Configure_Changes(self):
        """
            Configure the changes made by the user.

            excutes ``iwconfig`` commands related to the changes
            made by the user.
        """
        # Get current row
        current_row = self.interface_table.currentRow()
        # Get current column
        current_col = self.interface_table.currentColumn()
        # Get interface name
        interface_name = self.interface_table.item(current_row, 0).text()
        # Changed Item
        new_item = self.interface_table.currentItem().text().replace(" ", "")

        if current_col == 1:
            # If user changes ESSID
            self.send_output.emit("This Message Is Not Visible " +
                                  "on Linux's Shell: " +
                                  "Changing Interface ESSID......")
            self.essid_process.start("iwconfig",
                                     [interface_name, "essid", new_item])
            self.send_command.emit("iwconfig " + " ".join(["essid", new_item]))
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    self.Reload_Changes()
                    return
                self.crontab_options.Start_Job("iwconfig "
                                               + " ".join(
                                                          ["essid", new_item]))

        if current_col == 2:
            # If user changes frequency
            self.send_output.emit("This Message Is Not Visible on Linux's "
                                  + " Shell: "
                                  + "Changing Interface Frequency......")

            self.freq_process.start("iwconfig",
                                    [interface_name, "freq", new_item])
            self.send_command.emit("iwconfig "
                                   + " ".join(
                                             [interface_name, "freq",
                                              new_item]))
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    self.Reload_Changes()
                    return
                self.crontab_options.Start_Job("iwconfig "
                                               + " ".join([interface_name,
                                                          "freq", new_item]))

        if current_col == 3:
            # If user changes mode
            self.send_output.emit("This Message Is Not Visible on Linux's "
                                  + "Shell: " + "Changing Interface Mode......"
                                  )

            self.mode_process.start("iwconfig", [interface_name,
                                                 "mode", new_item])
            self.send_command.emit("iwconfig "
                                   + " ".join([interface_name,
                                              "mode", new_item]))
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    self.Reload_Changes()
                    return
                self.crontab_options.Start_Job("iwconfig "
                                               + " ".join([interface_name,
                                                           "mode", new_item]))

        if current_col == 4:
            # If user changes AP
            self.send_output.emit("This Message Is Not Visible on Linux's "
                                  + " Shell: " + "Changing Interface AP......")

            self.ap_process.start("iwconfig", [interface_name, "ap", new_item])
            self.send_command.emit("iwconfig "
                                   + " ".join([interface_name, "ap", new_item])
                                   )
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    self.Reload_Changes()
                    return
                self.crontab_options.Start_Job("iwconfig "
                                               + " ".join([interface_name,
                                                          "ap", new_item]))

        # Reload interface_table with changes
        # If changes did not take effect this will show
        self.Reload_Changes()

    def IWCONFIG_Error(self):

        """
            If an error occurred while showing interfaces.

            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
            
        """

        output = self.iwconfig_process.readAllStandardError()
        data = bytes(output).decode("utf8").strip()
        if output.isEmpty():
            return
        self.send_output.emit(data)

    def ESSID_Error(self):

        """
            If an error occurred while changing ESSID
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        output = self.essid_process.readAllStandardError()
        data = bytes(output).decode("utf8").strip()
        if output.isEmpty():
            return
        self.send_output.emit(data)
        self.Reload_Changes()

    def Freq_Error(self):

        """
            If an error occurred while changing frequency
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        output = self.freq_process.readAllStandardError()
        data = bytes(output).decode("utf8").strip()
        if output.isEmpty():
            return
        self.send_output.emit(data)
        self.Reload_Changes()

    def Mode_Error(self):

        """
            If an error occurred while changing mode
            This method will display the error on the output terminal
        """

        output = self.mode_process.readAllStandardError()
        data = bytes(output).encode("utf8").strip()
        if output.isEmpty():
            return
        self.send_output.emit(data)
        self.Reload_Changes()

    def AP_Error(self):

        """
            If an error occurred while configuring AP
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        output = self.ap_process.readAllStandardError()
        data = bytes(output).decode("utf8").strip()
        if output.isEmpty():
            return
        self.send_output.emit(data)
        self.Reload_Changes()

    def Flush_Error(self):

        """
            If an error occurred while flushing previous network settings
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """
        data = self.flush_process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)
        self.Reload_Changes()

    def Restart_Error(self):

        """
            If an error occurred while restarting interface
            (switchting interface to down and up)
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        data = self.restart_process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)

    def Clear_History(self):

        """
            Clears command histroy.
        """

        self.command_history.clear()

    def Clear_Terminal(self):

        """
            Clears the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        self.output_terminal.clear()
        self.send_command.emit("clear")

    def Reset_Interface(self):

        """
            Resets network settings to avoid hazards.

            1. Flushes previous IPV4 address
            2. Restarts the interface
            3 .Restarts network manager (Restore IPV6 Address)
        """

        try:
            current_row = self.interface_table.currentRow()
            interface_name = self.interface_table.item(current_row, 0).text()
            # Flushing previous IPV4 addresses
            self.send_output.emit("This Message Is Not Visible on Linux's "
                                  + " Shell: " + "Flushing Started......")
            self.send_command.emit("ip "
                                   + " ".join(
                                      ['addr', 'flush', 'dev',
                                       interface_name]))
            self.flush_process.start("ip",
                                     ['addr', 'flush', 'dev', interface_name])
            self.flush_process.waitForFinished()

            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job("ip "
                                               + " ".join(
                                                         ['addr', 'flush',
                                                          'dev',
                                                          interface_name]))

            # Restarting the interface
            self.send_output.emit("This Message Is Not Visible on Linux's "
                                  + " Shell: " + "Restarting Interface......")
            self.restart_process.start("ifconfig", [interface_name, "down"])
            self.restart_process.waitForFinished()
            self.send_command.emit("ifconfig " + " ".join(
                                                           [interface_name,
                                                            "down"]))
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job("ifconfig "
                                               + " ".join(
                                                        [interface_name,
                                                         "down"]))

            self.restart_process.start("ifconfig", [interface_name, "up"])
            self.send_command.emit("ifconfig "+" ".join(
                                                        [interface_name,
                                                         "up"]))
            self.restart_process.waitForFinished()
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job("ifconfig "
                                               + " ".join([interface_name,
                                                          "up"]))

            # If no occurred during the restart process
            if self.restart_process.exitCode() == 0:
                self.send_output.emit("This Message Is Not Visible on Linux's "
                                      + "Shell: "
                                      + "Reseting network-manager......")

            # Restart Network Manager
            self.restart_process.start("service", ["network-manager",
                                                   "restart"])
            self.restart_process.waitForFinished()
            self.send_command.emit("service"
                                   + " ".join(["network-manager", "restart"]))
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job("service"
                                               + " ".join(["network-manager",
                                                          "restart"]))

            # Wait for the previous commands to finish
            time.sleep(5.5)
            self.send_output.emit("This Message Is Not Visible on Linux's "
                                  + " Shell: "
                                  + "Reseting Process Finished")

        except AttributeError:
            self.send_output.emit("Please Choose an Interface")

            # Reload the table
            # In order to do so,
            # first the interface_table itemChanged signal must be blocked
            # otherwise Configure_Changes() will be called
            # Then remove all the data under the table header
            # using interface_table.setRowCount(0)

        self.Reload_Changes()

    def Reload_Changes(self):

        # Reload the table
        # In order to do so,
        # first the interface_table itemChanged signal must be blocked
        # otherwise Configure_Changes() will be called
        # Then remove all the data under the table header
        # using interface_table.setRowCount(0)

        self.interface_table.blockSignals(True)
        self.interface_table.setRowCount(0)
        self.Get_Interface_name()
        self.interface_table.blockSignals(False)

    def Finished_ESSID(self):

        """
            Display a message when ESSID configuration is finished
        """

        if self.essid_process.exitCode() != 0:
            return
        self.send_output.emit("This Message Is Not Visible on Linux's "
                              + " Shell: "
                              + "ESSID Config Over\n")

    def Finished_Frequency(self):

        """
            Display a message when Frequency configuration is finished.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        if self.freq_process.exitCode() != 0:
            return
        self.send_output.emit("This Message Is Not Visible on Linux's "
                              + "  Shell: "
                              + "Frequency Config Over\n")

    def Finished_Mode(self):

        """
            Display a message when Mode configuration is finished.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """
        if self.mode_process.exitCode() != 0:
            return
        self.send_output.emit("This Message Is Not Visible on Linux's "
                              + "Shell: Mode Config Over\n")

    def Finished_AP(self):

        """
            Display a message when AP configuration is finished.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_Output` Then the output is is displayed
            on the ``output_terminal``.
        """

        if self.ap_process.exitCode() != 0:
            return
        self.send_output.emit("This Message Is Not Visible on Linux's "
                              + " Shell: AP Config Over\n")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = iwconfig_Logic(None)
    ui.show()
    sys.exit(app.exec_())
