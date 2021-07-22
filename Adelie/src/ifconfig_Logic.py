
from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5.QtWidgets import  QFileDialog
from CronTab_Options_Logic import CronTab_Options_Logic
import subprocess
import sys
import re
import os.path
import time

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(CURRENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "ifconfig.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)


class ifconfig_Logic(baseUIWidget, baseUIClass):
    """
            Provides a UI for the ifconfig utility.
            Using this class users can utilize the ifconfig utility
            on Linux Systems.
            
            This class handles the logic for ``ifconfig.ui``
            Users that use the GUI will be able to configure an interface
            IPV4 Address, Network Mask, MAC Address and IPV6 Address
            Users can also turn the interface on or off.

           

        Attributes:
            process (:obj:`QProcess`): QProcess object that is used 
                to execute the ``ifconfig`` processes.
            IPV4_process (:obj:`QProcess`): QProcess object that is used 
                to execute the ``ifconfig`` processes which configure the
                    interface IP Address.
            restart_process (:obj:`QProcess`): QProcess object that is used 
                to reset the interface to default settings.
            interface_status_process (:obj:`QProcess`): QProcess object 
                that is used to switch the interface ``on`` or ``off``.   
            flush_process (:obj:`QProcess`): QProcess object that is used 
                to flush the interface IP addresses to default settings.  

            send_command (:obj:`pyqtSignal(str)`): Emits a signal that is 
                connected to the ``command_histroy``, the signal contains
                the command formed.
            send_output (:obj:`pyqtSignal(str)`): Emits a signal 
                when the ``ifconfig`` process has an available output to be read. 

            active_interfaces (:obj:`dict`): Dictionary that contains
                all the active interfaces data.
            prev_item (:obj:`str`): Contains the item before changes.

            crontab_options (:mod:`.CronTab_Options_Logic`): Used to schedule
                and show the ``Crontab``.

        Note:
            This is an educational tool and does not use the use
            ifconfig utility at its full potential.
            Since this is an educational tool, a reset button is implemented to
            restore the system default settings.

        Warning:
                Requires Administrator Privilege.    

    """

    ipv6_regex = (
    "inet6\s(?:^|(?<=\s))(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}"
    +"|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}"
    +"|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:)"
    +"{1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4})"
    +"{1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}"
    +":((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)"
    +"|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:)"
    +"{0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]"
    +"|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]"
    +"|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}"
    +"[0-9]))(?=\s|$)")

    process = QProcess()
    IPV4_process = QProcess()
    restart_process = QProcess()
    netmask_process = QProcess()
    interface_status_process = QProcess()

    send_output = pyqtSignal(str)
    send_command = pyqtSignal(str)
    flush_process = QProcess()

    active_interfaces = {}

    prev_item = ""

    def __init__(self, parent=None):
        super(ifconfig_Logic, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
                            QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowMinimizeButtonHint)
        self.crontab_options = None
        self.label_error.hide()

# ==============================================================================
#                       GUI SIGNALS
# ==============================================================================
        self.show_act_interface_button.clicked.connect(self.Show_Act_Interface)
        self.clear_history_button.clicked.connect(self.Clear_History)
        self.clear_terminal_button.clicked.connect(self.Clear_Terminal)
        self.reset_button.clicked.connect(self.Reset_Interface)

        self.send_output.connect(self.Print_On_Terminal)
        self.send_command.connect(self.Print_Command)

        self.process.readyReadStandardOutput.connect(self.Connect_Output)

        self.process.readyReadStandardError.connect(self.Connect_Error)
        self.IPV4_process.readyReadStandardError.connect(self.IPV4_Error)
        self.netmask_process.readyReadStandardError.connect(self.Netmask_Error)
        self.flush_process.readyReadStandardError.connect(self.Flush_Error)
        self.interface_status_process.readyReadStandardError.connect(
        self.Interface_Status_Error)
        self.restart_process.readyReadStandardError.connect(self.Restart_Error)

        self.interface_table.itemChanged.connect(self.Configure_Changes)
        self.interface_table.cellDoubleClicked.connect(self.Save_Prev_item)

        self.IPV4_process.finished.connect(self.Finished_IPV4_Config)
        self.flush_process.finished.connect(self.Finished_Flush)
        self.netmask_process.finished.connect(self.Finished_Netmask)
        self.interface_status_process.finished.connect(
        self.Finished_Interface_status)
        self.crontab_options_button.clicked.connect(
                                                    self.Show_CronTab_Options)
# ==============================================================================

    def Show_CronTab_Options(self):

        """
            Show CronTab Options Menu.
        """
        #  Check if options menu was created
        #  If it was created, show the menu

        if self.crontab_options is None:
            self.crontab_options = CronTab_Options_Logic()
        self.crontab_options.show()

    def Show_Act_Interface(self):

        """
            Uses the command ifconfig to show active interfaces.

            Depending on the user checked boxes this method will show
            all interfaces or a short list. If no check boxes are checked,
            this method will only display active interfaces.
        """
        self.send_output.emit(
                                "This Message Is Not Visible on Linux's Shell "
                                + "Resetting Process Finished\n")

        self.label_error.hide()
        arg_list = []
        # Show all interfaces checkbox
        if self.show_all_checkbox.isChecked():
            arg_list.append("-a")
        # Show short list checkbox
        if self.show_short_list_checkbox.isChecked():
            arg_list.append("-s")

        self.process.start("ifconfig", arg_list)  # Start the process
        # Send command to command history
        self.send_command.emit("ifconfig " + " ".join(arg_list))
        if self.crontab_enable.isChecked():
            if self.crontab_options is None:
                self.label_error.show()
                self.label_error.setText("Set CronTab Options First!")
                return
            self.crontab_options.Start_Job(
                                            "ifconfig "
                                            + " ".join(arg_list))
        self.Reload_Changes()

    def Interface_Status(self, str):
        """This method allows the user to change the interface status.

            ifconfig interfaces can be up or down. This provides the user
            with the option to change the interface from up or down.
            User can change the interface status by clicking on the interface
            then rewrite its status to up or down.
            
            New interface status is received from :meth:`.Configure_Changes`.

        Args:
            str (:obj:`str`): String that defines the interface status.
                Interface status can be ``up`` or ``down``.

        Warning:
            Requires Administrator Privilege.

        """        


        # Recives the new status from Configure_Changes()
        interface_status = str
        # Get currentRow
        current_row = self.interface_table.currentRow()
        # Get current interface name
        interface_name = self.interface_table.item(current_row, 0).text()
        # If interface is changed to "down"
        if interface_status == "down":
            interface_is_now = "down"
        # If interface is changed to "up"
        elif interface_status == "up":
            interface_is_now = "up"

        else:
            # If the interface is not chaned to up or down.
            # But some other string
            # Display an error
            current_row = self.interface_table.currentRow()
            current_col = self.interface_table.currentColumn()
            current_item = (self.interface_table.item(current_row, current_col)
                            .text())
            self.send_output.emit(
            "ERROR!!! Interface Can Only Be [up] or [down] \n")
            self.send_command.emit(
                                    "ifconfig "
                                    + " ".join([interface_name, current_item]))
            return

        try:
            # If the user did not click on an interface
            # infterface_name will be empty
            # This try and except block will handle the error accordingly
            # Set global interface status
            self.interface_status = interface_is_now
            # Send command to command history
            self.send_command.emit("ifconfig " + " ".join(
                                                        [interface_name,
                                                         interface_is_now]))
            # Start process
            self.interface_status_process.start(
                                                "ifconfig",
                                                 [interface_name,
                                                  interface_is_now])

            if self.crontab_enable.isChecked():
                self.crontab_options.Start_Job("ifconfig "
                                               + " ".join(
                                                [interface_name,
                                                 interface_is_now]))

        except AttributeError:
            # If no interface was chosen display a message
            self.send_output.emit("Please Choose an Interface")

    def Connect_Output(self):

        """
            Reads the process standard output and decodes it.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.

        """

        data = self.process.readAllStandardOutput()
        #Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output+"\n")

    def IPV4_Error(self):

        """
            If an error occurred while configuring ``IPV4``
            (changing IP address) This method will display the
            error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
            
        """

        data = self.IPV4_process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)
        self.Reload_Changes()

    def Netmask_Error(self):

        """
            If an error occurred while configuring ``network mask``
            (changing Netmask)
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
        """

        data = self.netmask_process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)
        self.Reload_Changes()

    def Interface_Status_Error(self):

        """
            If an error occurred while changing interface status(up or down)
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
        """

        data = self.interface_status_process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)
        self.Reload_Changes()

    def Flush_Error(self):

        """
            If an error occurred while flushing previous network settings
            This method will display the error on the output terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
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
            (switchting interface to down and up).

            This method will display the error on the output terminal
            (``output_terminal``).

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
        """

        data = self.restart_process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)
        self.Reload_Changes()

    def Connect_Error(self):

        """
            If an error occurred while using the command ifconfig,
            this method will display the error on the output terminal.

        """

        data = self.process.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        self.send_output.emit(output)

    def Print_Command(self, str):
        """
            This method prints the command on the command history
            ``command_history``

        Args:
            str (:obj:`str`): Command to be printed on ``command_history``.
        """        

        """
            
        """

        self.command_history.append(str)

    def Print_On_Terminal(self, str):
        """ This methods prints the process output on
            the output terminal ``output_terminal``

        Args:
            str (:obj:`str`): Output to be printed on the terminal.
        """        
        self.output_terminal.appendPlainText(str)

    def Clear_Terminal(self):

        """
            Clears the output terminal.
            Emits the signal :obj:`.send_command`.
        """

        self.output_terminal.clear()
        self.send_command.emit("clear")

    def Clear_History(self):

        """
            Clears command histroy.
        """

        self.command_history.clear()

    def Get_Interface_name(self):

        """
            This method finds the name of the interfaces that are active
            and adds the interface name  to the ``interface_table``.

            IPV4 Address, Network Mask, MAC Address, IPV6 Address
            REGEX are used to find the data mentioned.
        
        """
        # Set all tables resize contents width
        header = self.interface_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        interafces = {}
        
        interface_data={}
        ip_array = []
        netmask_array = []
        mac_array = []
        ip6_array = []

        # Get ifconfig output
        output = subprocess.check_output(['ifconfig'], universal_newlines=True)
        # Finds active interfaces name
        result = re.findall(r"(\w+):\s", output)
        interface_count = 0

        for interface in range(len(result)):
            interface_name = result[interface]
            interface_info = output.split("\n\n")[interface].replace("\n", "")

            # Use REGEX to find ipv4, netmask, mac address, ipv6
            # for each interface
            interafces.setdefault(interface_name, interface_info)
            ipv4 = re.findall(
                             r"inet\s\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
                             interface_info)
            netmask = re.findall(
            r"netmask\s\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b", interface_info)
            mac_add = re.findall(
            r"ether\s(?:[0-9a-fA-F]:?){12}", interface_info)
            ipv6 = re.findall(self.ipv6_regex, interface_info)

            # Remove the captured inet, netmaask, ether
            ipv4 = "".join(ipv4).replace("inet ", "")
            netmask = "".join(netmask).replace("netmask ", "")
            mac_add = "".join(mac_add).replace("ether ", "")

            # If there is no IPV6
            # replace with an empty string
            if len(ipv6) > 0:
                ipv6 = ipv6[0][0].replace("ipv6", "")

            # Record each interface and its data in a dictionary
            # interface_data =
            # {interface name:[
            # IPV4 address, Network Mask, MAC Addres, IPV6 address]}
            interface_data.setdefault(
                                      interface_name, [ipv4,
                                                       netmask, mac_add, ipv6])

        for item in interface_data:

            # Create a new row for each new interface
            rowPosition = self.interface_table.rowCount()
            self.interface_table.insertRow(rowPosition)

            # Interface name,
            # Interface MAC Address, IPV6 (in this version) cannot be changed
            # Make the previous properties selectable only
            # Fill each row data from the dictionary

            item_not_editable = QtWidgets.QTableWidgetItem(item)
            item_not_editable.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item_not_editable.setTextAlignment(Qt.AlignCenter)
            self.interface_table.setItem(rowPosition, 0, item_not_editable)
            self.interface_table.setItem(
            rowPosition, 1, QtWidgets.QTableWidgetItem("up"))
            (self.interface_table.item(rowPosition, 1)
             .setTextAlignment(Qt.AlignCenter))
            self.interface_table.setItem(
            rowPosition, 2, QtWidgets.QTableWidgetItem(interface_data[item][0]))
            (self.interface_table.item(rowPosition, 2).
             setTextAlignment(Qt.AlignCenter))
            self.interface_table.setItem(
            rowPosition, 3, QtWidgets.QTableWidgetItem(interface_data[item][1]))
            item_not_editable = QtWidgets.QTableWidgetItem(
            interface_data[item][2])
            item_not_editable.setFlags(
            QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.interface_table.setItem(
            rowPosition, 4, QtWidgets.QTableWidgetItem(item_not_editable))

            # If there is an IPV6 to the interface
            # Add it as not editable
            if len(interface_data[item][3]) > 0:
                item_not_editable = QtWidgets.QTableWidgetItem(
                                                    interface_data[item][3])
                item_not_editable.setFlags(
                                            QtCore.Qt.ItemIsSelectable
                                            | QtCore.Qt.ItemIsEnabled)
                self.interface_table.setItem(
                                             rowPosition, 5,
                                             QtWidgets.
                                             QTableWidgetItem(item_not_editable
                                             ))
            self.active_interfaces = interface_data
            (self.interface_table.item(rowPosition, 3).
                setTextAlignment(Qt.AlignCenter))
            (self.interface_table.item(rowPosition, 4).
                setTextAlignment(Qt.AlignCenter))
            (self.interface_table.item(rowPosition, 5).
                setTextAlignment(Qt.AlignCenter))


    def Save_Prev_item(self):
        """Saves the item before user changes.
        """        

        self.prev_item = self.interface_table.currentItem().text()

    def Finished_IPV4_Config(self):

        """
            Prints on the output terminal that IPV4 configuration is over.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
        """

        if self.IPV4_process.exitCode() != 0:
            return
        self.send_output.emit(
                             "This Message Is Not Visible on Linux's Shell: " +
                             "Finished IPV4 Configuration\n")

    def Finished_Flush(self):

        """
            Prints on the output terminal that flushing process is over.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
        """

        if self.flush_process.exitCode() != 0:
            return
        self.send_output.emit(
                             "This Message Is Not Visible on Linux's Shell:"
                             + " Flush Process Finished")

    def Finished_Reseting(self):

        """
            Prints on the output terminal that resetting process is over.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.

        """

        if self.restart_process.exitCode() != 0:
            return
        self.send_output.emit(
                             "This Message Is Not Visible on Linux's Shell " +
                             "Resetting Process Finished\n")

    def Finished_Netmask(self):

        """
            Prints on the output terminal that configuring Network Mask is over.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.

           
        """

        if self.netmask_process.exitCode() != 0:
            return
        self.send_output.emit(
                            "This Message Is Not Visible on Linux's Shell: " +
                            "Net Mask Configuration Finished\n")

    def Finished_Interface_status(self):

        """
            Prints on the output terminal that changing the interface status
            from up (``on``) to down (``off``) or vice versa is over.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``.
        """
        if self.interface_status_process.exitCode() != 0:
            return
        self.send_output.emit(
                            "This Message Is Not Visible on Linux's Shell: " +
                            "Interface Is " + self.interface_status+"\n")

    def Configure_Changes(self):

        """
            Configure the changes made by the user.

            It excutes ifconfig commands related to the changes
            made by the user.

            Warning:
                Requires Administrator Privilege.
        """

        self.label_error.hide()

        if self.crontab_enable.isChecked():
            if self.crontab_options is None:
                self.label_error.show()
                self.label_error.setText("Set CronTab Options First!")
                self.Reload_Changes()
                return

        current_row = self.interface_table.currentRow()
        current_column = self.interface_table.currentColumn()
        # Replaced text
        new_item = self.interface_table.currentItem().text().replace(" ", "")
        interface_name = self.interface_table.item(current_row, 0).text()

        if current_column == 1:

            # If user choose to change interface status from up
            # to down
            self.Interface_Status(new_item)

        if current_column == 2:

            # If user chooses to change the IPV4 Address
            self.send_output.emit(
                                "This Message Is Not Visible on Linux's "
                                + "Shell: "
                                + "Changing Interface IPV4......")
            self.IPV4_process.start("ifconfig", [interface_name, new_item])
            self.send_command.emit(
                                    "ifconfig "
                                    + " ".join([interface_name, new_item]))
            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    self.Reload_Changes()
                    return
                self.crontab_options.Start_Job(
                                                "ifconfig "
                                                + " ".join([interface_name,
                                                            new_item]))

        if current_column == 3:

            # If user chooses to change Mac Address
            self.send_output.emit(
                                    "Changing Interface NETMASK......\n"
                                    + "This Message Is Not Visible on"
                                    + " Linux's Shell")
            self.netmask_process.start(
                                     "ifconfig",
                                     [interface_name, 'netmask', new_item])
            self.netmask_process.waitForFinished()
            self.send_command.emit(
                                    "ifconfig "
                                    + " ".join(
                                                [interface_name, 'netmask',
                                                 new_item]))

            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    self.Reload_Changes()
                    return
                self.crontab_options.Start_Job(
                                                "ifconfig "
                                                + " ".join(
                                                            [interface_name,
                                                             'netmask',
                                                             new_item]))

        self.Reload_Changes()

    def Reset_Interface(self):

        """
            Resets network settings to avoid hazards.

            1. Flushes previous IPV4 address.
            2. Restarts the interface.
            3. Restarts network manager (Restore IPV6 Address).
        """
        try:
            current_row = self.interface_table.currentRow()
            interface_name = self.interface_table.item(current_row, 0).text()
            # Flushing previous IPV4 addresses
            self.send_output.emit(
                                 "This Message Is Not Visible on"
                                 + " Linux's Shell: "
                                 + "Flushing Started......")
            self.send_command.emit(
                                 "ip "
                                 + " ".join(
                                            ['addr',
                                             'flush',
                                             'dev', interface_name]))
            self.flush_process.start(
                                    "ip",
                                    ['addr', 'flush', 'dev', interface_name])
            self.flush_process.waitForFinished()

            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job(
                                              "ip "
                                              + " ".join(
                                                        ['addr',
                                                         'flush',
                                                         'dev',
                                                         interface_name]))

            # Restarting the interface
            self.send_output.emit("This Message Is Not Visible "
                                  + "on Linux's Shell: "
                                  + "Restarting Interface......")

            self.restart_process.start("ifconfig", [interface_name, "down"])
            self.restart_process.waitForFinished()
            self.send_command.emit("ifconfig "
                                   + " ".join([interface_name, "down"]))
            self.restart_process.start("ifconfig", [interface_name, "up"])
            self.send_command.emit("ifconfig "
                                   + " ".join([interface_name, "up"]))
            self.restart_process.waitForFinished()

            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job(
                                             "ifconfig "
                                             + " ".join(
                                                        [interface_name,
                                                         "down"]))

            # If no occurd during the restart process
            if self.restart_process.exitCode() == 0:
                self.send_output.emit("This Message Is Not Visible "
                                      + " on Linux's Shell: "
                                      + "Resetting network-manager......")
            # Restart Network Manager
            self.restart_process.start("service", [
                                                    "network-manager",
                                                    "restart"])
            self.restart_process.waitForFinished()
            self.send_command.emit("service"
                                   + " ".join(
                                         ["network-manager", "restart"]))

            if self.crontab_enable.isChecked():
                if self.crontab_options is None:
                    self.label_error.show()
                    self.label_error.setText("Set CronTab Options First!")
                    return
                self.crontab_options.Start_Job("service"
                                               + " ".join(
                                                     ["network-manager",
                                                      "restart"]))

            # Wait for the previous commands to finish
            time.sleep(5.5)
            self.send_output.emit("This Message Is Not Visible "
                                  + " on Linux's Shell:"
                                  + "Resetting Process Finished")

        except AttributeError:
            self.send_output.emit("Please Choose an Interface")

        # Reload the table
        # In order to do so,
        # first the interface_table itemChanged signal must be blocked
        # otherwise Configure_Changes() will be called
        # Then remove all the data under
        # the table header using interface_table.setRowCount(0)
        self.Reload_Changes()

    def Reload_Changes(self):

        """
            Reloads the configured changes, setting the table.

            Note:
                This method is used to ensure that the settings are configured 
                correctly. It re-executes the ``ifconfig`` command.
        """

        #  Signals are blocked to avoid onChanged
        self.interface_table.blockSignals(True)
        self.interface_table.setRowCount(0)
        self.Get_Interface_name()
        self.interface_table.blockSignals(False)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = ifconfig_Logic(None)
    ui.show()
    sys.exit(app.exec_())
