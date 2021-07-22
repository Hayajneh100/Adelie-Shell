from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView
import subprocess
import sys
import os.path
from CronTab_Options_Logic import CronTab_Options_Logic
import re
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(CURRENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "netstat.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)


class netstat_Logic(baseUIWidget, baseUIClass):
    """A GUI for the ``netstat tool``.

        This GUI enables users to execute common ``netstat`` commands
        and check ports usage. 

        The GUI displays the output in a formated table.

    Attributes:
        netstat_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``netstat`` processes.
        tcp_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``netstat`` TCP process.
        udp_process (:obj:`QProcess`): QProcess object that is used 
            to execute the ``netstat`` UDP process.
        grep1 (:obj:`QProcess`): QProcess object that is used 
            to execute the ``netstat -n -t -u`` command.
            Its output is piped to :obj:`.grep2`
        grep2 (:obj:`QProcess`): Process object that is used 
            to execute the ``grep:portnumber`` command.
            The output of this processes shows the port usage of the
            ``portnumber`` defined.

        send_command (:obj:`pyqtSignal(str)`): Emits a signal that is 
            connected to the ``command_history``, the signal contains
            the command formed.
        send_output (:obj:`pyqtSignal(str)`): Emits a signal 
            when the ``netstat`` process has an available output to be read.

        crontab_options (:mod:`.CronTab_Options_Logic`): Used to schedule
                and show the ``Crontab``.

    Note:
        This is an educational tool and does not use the use
        ``netstat`` utility at its full potential.
            
    """    

    netstat_process = QProcess()
    send_command = pyqtSignal(str)
    send_output = pyqtSignal(str)
    tcp_process = QProcess()
    udp_process = QProcess()
    grep1 = QProcess()
    grep2 = QProcess()

    def __init__(self, parent=None):
        super(netstat_Logic, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags
        (QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
        # Set all tables resize contents width

        self.grep1.setStandardOutputProcess(self.grep2)
        self.crontab_options = None
        self.label_error.hide()
# ==============================================================================
#                       GUI SIGNALS
# ==============================================================================

        self.send_output.connect(self.Print_On_Terminal)
        self.send_command.connect(self.Print_Command)
        self.clear_history_button.clicked.connect(self.Clear_History)
        self.clear_terminal_button.clicked.connect(self.Clear_Terminal)
        self.netstat_button.clicked.connect(self.Netstat)
        self.clear_table_button.clicked.connect(self.Clear_Netstat_Table)
        self.port_checkbox.stateChanged.connect(self.Enable_Usage)
        self.grep2.readyReadStandardOutput.connect(self.Grep_Output)
        self.tcp_process.readyReadStandardOutput.connect(self.TCP_Output)
        self.udp_process.readyReadStandardOutput.connect(self.UDP_Output)
        self.netstat_process.readyReadStandardOutput.connect(
                                                            self.Netstat_Output)
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

    def Netstat(self):

        """
            This method executes netstat commands and
            prints the result on ``output_terminal``.

            Executes the command according to the argument checked.

            Note:

                if ``-r`` argument is present, netstat will ignore ``-t``, 
                ``-u``
        """
        self.Build_Table_Header("NETSTAT")
        args_list = []  # List of Arguments added
        # Clear Table, required if -r is add,
        # netstat ignores other arguments with it
        if self.port_checkbox.isChecked():
            # Check port usage

            self.Port_Usage()
            return
        if self.routing_checkbox.isChecked():
            # Routing table
            args_list.append("-r")
        if self.numeric_address_checkbox.isChecked():
            # Numeric Address
            args_list.append("-n")
        self.netstat_table.setRowCount(0)
        if self.tcp_checkbox.isChecked():
            # TCP Connections
            # If routing table option is added
            # do not check tcp connections
            # if -r is added, netstat ignores -t,-u
            args_list.append("-t")
            if self.routing_checkbox.isChecked() is False:
                self.Get_TCP_Connections()

        if self.udp_checkbox.isChecked():
            # UDP Connections
            # If routing table option is added
            # do not check tcp connections
            # if -r is added, netstat ignores -t,-u
            args_list.append("-u")
            if self.routing_checkbox.isChecked() is False:
                self.Get_UDP_Connections()
        # Start process
        self.netstat_process.start("netstat", args_list)
        # Send command
        self.send_command.emit(
                                "netstat " + " ".join(args_list))

        if self.crontab_enable.isChecked():
            if self.crontab_options is None:
                self.label_error.show()
                self.label_error.setText("Set CronTab Options First!")
                return
            self.crontab_options.Start_Job("netstat " + " ".join(args_list))

    def Netstat_Output(self):

        """
            Reads netstat result using :obj:`.netstat_process`
            and emits the output to the terminal.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``
        """
        # Read Routing table line by line and add it to Routing Table
        if self.routing_checkbox.isChecked():
            self.Build_Table_Header("ROUTING")
            for counter in range(2):
                header = self.netstat_process.readLine()
                self.send_output.emit(bytes(header).decode("utf8"))
            while self.netstat_process.canReadLine():
                line = self.netstat_process.readLine()
                data = bytes(line).decode("utf8")
                data = data.split()
                self.send_output.emit("\t".join(item for item in data))
                self.Add_Row_Routing_Table(data)

        output = self.netstat_process.readAllStandardOutput()
        data = bytes(output).decode("utf8")
        self.send_output.emit(data)

    def Print_On_Terminal(self, str):
        """ Prints on output terminal.

        Args:
            str (:obj:`str`): Output to be printed on the output terminal
                (``output_terminal``).
        """        

        self.output_terminal.appendPlainText(str)

    def Print_Command(self, str):
        """Prints the executed command on command history.

        Args:
            str (obj:`str`): Command to be printed on the command history
                (``command_history``).
        """        

        self.command_history.append(str)

    def Clear_Terminal(self):

        """
            Clears the Terminal.

            Emits the signal :obj:`.send_command` which is connected to 
            :meth:`.Print_Commant` Then the output is is displayed
            on the ``command_history``.

        """
        self.send_command.emit("clear")
        self.output_terminal.clear()

    def Clear_History(self):

        """
            Clears command history.
        """

        self.command_history.clear()

    def Clear_Netstat_Table(self):
        """
            Clears ``netstat_table`` (UDP/TCP) table.
        """
        self.netstat_table.setRowCount(0)

    def Get_UDP_Connections(self):

        """Finds UDP connections.
            
            Executes the command ``netstat -u``.
            if numerical option is required, it
            executes the command ``netsat -u -n``.

        See Also:
            :meth:`.Get_TCP_Connections` for TCP.    
        """

        if self.numeric_address_checkbox.isChecked():
            self.udp_process.start("netstat", ['-u', '-n'])
        else:
            # Start UDP process
            # UDP process prints its result on netstat_table
            self.udp_process.start("netstat", ['-u'])

    def Get_TCP_Connections(self):

        """Finds TCP connections.

            Executes the command ``netstat -t``.
            if numerical option is required, it 
            executes ``netsat -t -n``.

        See Also:
            :meth:`.Get_UDP_Connections` for UDP.        
        """
        if self.numeric_address_checkbox.isChecked():
            self.tcp_process.start("netstat", ['-t', '-n'])
        else:
            # Start TCP process
            # TCP process prints its result on netstat_table
            self.tcp_process.start("netstat", ['-t'])

    def UDP_Output(self):

        """After ``netstat -u`` is executed this method adds
            the UDP process result the ``netstat_table``.

            Splits the output result of the ``netstat -u`` into a ``list``
            this list containts the output line by line.
            Then it splits each line to words in order to get
            Recv-Q, Send-Q, Local Address, Foregin Addresses, State
            ``netstat -u`` returns this information in form of a table
            this method reads that table and adds the data to
            netstat_table

            See Also:
                :meth:`.TCP_OUTPUT`
        """

        output = self.udp_process.readAllStandardOutput()

        data = bytes(output).decode("utf8").strip()
        # Split the found data line by line
        data_by_line = data.split('\n')
        for line in data_by_line:
            # For each line in the result of netstat -u execution
            if(line == "Active Internet connections (w/o servers)"):
                # Unnecessary, remove
                continue
            if ("Send-Q" in line):
                # unnecessary, remove
                continue
            # Split each line by spaces (to get each word)
            line_list = line.split(" ")
            # Remove empty "" in the list
            # Add line_list to the nestat_table
            self.Add_Row_Netstat_Table(list(filter(None, line_list)))

    def TCP_Output(self):

        """After ``netstat -t`` is executed this method
            Adds the TCP process results to the ``netstat_table``.

            Splits the output result of the ``netstat -t`` into a ``list``
            this list containts the output line by line.
            Then it splits each line to words in order to get
            Recv-Q, Send-Q, Local Address, Foregin Addresses and State.

            ``netstat -t`` returns this information in form of a table
            this method reads that table and adds the data to
            ``netstat_table``.

            See Also:
                :meth:`.UDP_OUTPUT`
        """

        line_list = []
        output = self.tcp_process.readAllStandardOutput()
        data = bytes(output).decode("utf8").strip()
        # Split the found data line by line
        data_by_line = data.split('\n')
        # For each line in the result of netstat -t execution
        for line in data_by_line:
            # Unnecessary, remove
            if(line == "Active Internet connections (w/o servers)"):
                continue
            if ("Send-Q" in line):
                # unnecessary, remove
                continue
            line_list = line.split(" ")
            self.Add_Row_Netstat_Table(list(filter(None, line_list)))

    def Enable_Usage(self):

        if self.port_checkbox.isChecked():
            self.checkbox_frame.setEnabled(False)
            self.numeric_address_checkbox.setChecked(True)
            self.tcp_checkbox.setChecked(True)
            self.udp_checkbox.setChecked(True)
            self.port_number_spinbox.setEnabled(True)
        else:
            self.checkbox_frame.setEnabled(True)
            self.port_number_spinbox.setEnabled(False)

    def Port_Usage(self):

        """
            Checks connections to UDP/TCP ports.

            Executes ``netstat -n -t -u | grep :[PORT NUMBER]``.
        """
        self.netstat_table.setRowCount(0)
        port_number = self.port_number_spinbox.value()
        self.grep1.start("netstat", ["-n", "-t", "-u"])
        self.grep2.start("grep", [":"+str(port_number)])
        self.send_command.emit("netstat -n -t -u | grep :"
                               + str(port_number))

        # CronTabs Start if command structure os OK!
        # It does not matter if there is an exception or not
        # CronTab will be Written
        if self.crontab_enable.isChecked():
            if self.crontab_options is None:
                self.label_error.show()
                self.label_error.setText("Set CronTab Options First!")
                return
            self.crontab_options.Start_Job("netstat -n -t -u | grep :"
                                           + str(port_number))

    def Grep_Output(self):
        """
            Outputs the grep process to ``netstat_table``.

            Emits the signal :obj:`.send_output` which is connected to 
            :meth:`.Print_On_Terminal` Then the output is is displayed
            on the ``output_terminal``

        """
        output = self.grep2.readAllStandardOutput()
        data = bytes(output).decode("utf8").strip()
        self.send_output.emit(data)
        # Split the found data line by line
        data_by_line = data.split('\n')
        # For each line in the result of netstat -t execution
        for line in data_by_line:
            line_list = line.split(" ")
            self.Add_Row_Netstat_Table(list(filter(None, line_list)))

    def Add_Row_Netstat_Table(self, connection_list):
        """Adds a row of TCP/UDP data to the ``netstat_table``.

            Data is sent as list from :meth:`.TCP_Output`, :meth:`.UDP_Output`.

        Args:
            connection_list (:obj:`list` of ``str``): List that contains 
                TCP or UDP connections to be added to the table
                (``netstat_table``).
        """        

        # Create a new row for each new connection
        rowPosition = self.netstat_table.rowCount()
        self.netstat_table.insertRow(rowPosition)

        # Protcol, Recv-Q, Send-Q, Local Address, Foregin Address, State
        # Make the previous properties selectable only
        # Fill each row data from the dictionary
        col_counter = 0   # Add each column to the table
        for item in connection_list:  # item == column data
            item_not_editable = QtWidgets.QTableWidgetItem(item)
            item_not_editable.setTextAlignment(Qt.AlignCenter)
            self.netstat_table.setItem(
                rowPosition, col_counter, item_not_editable)
            col_counter = col_counter + 1

    def Add_Row_Routing_Table(self, row):
        """Adds a row of routing table data to the ``netstat_table``.


        Args:
            row (:obj:`list` of ``str``): Routing table data to be added.
                The data is a row from the routing table found from executing
                the ``netstat`` command.
        """        
        rowPosition = self.netstat_table.rowCount()
        self.netstat_table.insertRow(rowPosition)
        for counter in range(len(row)):
            item = QTableWidgetItem(row[counter])
            item.setTextAlignment(Qt.AlignCenter)
            tt = ""
            if counter == 3:
                if "G" in row[3]:

                    tt = tt + " Route uses a gateway."
                    item.setToolTip(tt)
                if "U" in row[3]:
                    tt = tt + " Interface to be used is up."
                    item.setToolTip(tt)
                if "H" in row[3]:
                    tt = tt + (" Only a single host can be reached through"
                               + " the route.")

                    item.setToolTip(tt)
                if "D" in row[3]:
                    tt = tt + " Means this route is dynamically created."
                    item.setToolTip(tt)

                if "I" in row[3]:
                    tt = tt + (" Means the route is a reject route"
                               + "and data will be dropped.")
                    item.setToolTip(tt)

            self.netstat_table.setItem(rowPosition, counter, item)

    def Build_Table_Header(self, table):
        """Builds ``netstat_table`` header.

        Args:
            table (:obj:`str`): String that represents a table.
                the table provided can be of two values ``NETSTAT|ROUTING``.
                Builds the header of the table specified.
        """        
        tb = self.netstat_table
        tb.setRowCount(-1)
        font = QFont()
        font.setBold(True)
        header = QHeaderView(Qt.Horizontal)
        header.setStretchLastSection(True)
        header.setSectionResizeMode(header.ResizeToContents)
        tb.setHorizontalHeader(header)

        tb.horizontalHeader().setVisible(True)
        color1 = QColor(50, 73, 96)
        color2 = QColor(11, 117, 237, 255)
        if table == "ROUTING":
            header_items = [
                        QTableWidgetItem("Destination"),
                        QTableWidgetItem("Gateway"),
                        QTableWidgetItem("Genmask"),
                        QTableWidgetItem("Flags"),
                        QTableWidgetItem("MSS"),
                        QTableWidgetItem("Window"),
                        QTableWidgetItem("IRTT"),
                        QTableWidgetItem("IFace")]
            tt = [
                    "Destination IP",
                    "Gateway to which the routing entry points",
                    "Netmask for the destination network",
                    "Flags that describe the route",
                    "Maximum Segment Size",
                    "Maximum amount of data the system will accept"
                    + " in a single burst from a remote host",
                    "Initial Round Trip Time",
                    "Interface Name"
            ]
            tb.setColumnCount(8)
        if table == "NETSTAT":
            header_items = [
                        QTableWidgetItem("Protcol"),
                        QTableWidgetItem("Recv-Q"),
                        QTableWidgetItem("Send-Q"),
                        QTableWidgetItem("Local Address"),
                        QTableWidgetItem("Foregin Address"),
                        QTableWidgetItem("State")]
            tt = [
                    "Network Protocol used",
                    "Bytes of data in the queue to be sent to the user program"
                    + " that established the connection",
                    "Bytes in the queue to be sent to the remote program",
                    "Destination host and port number",
                    "Source of the connection and the port number "
                    + "of the program",
                    "Connection status"
            ]
            tb.setColumnCount(6)

        for item in header_items:
            index = header_items.index(item)
            item.setToolTip(tt[index])
            if index % 2 == 0:
                item.setBackground(color1)
            else:
                item.setBackground(color2)
            item.setFont(font)
            tb.setHorizontalHeaderItem(index, item)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = netstat_Logic(None)

    ui.show()

    sys.exit(app.exec_())
