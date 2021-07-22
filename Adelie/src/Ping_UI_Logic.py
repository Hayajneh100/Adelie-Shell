
from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5 import QtGui
from CronTab_Options_Logic import CronTab_Options_Logic
import sys
import os.path

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(CURRENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "Ping.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)


class Ping_UI_Logic(baseUIWidget, baseUIClass):
    """Provides a UI for the Ping utility.
    Using this class users can utilize the ping utility on Linux Systems
        

        This class handles the logic for ``Ping.ui``
        Users that use the GUI will be able to ping and choose some common options.
        This class will perform the ping process and show users the equivalent
        shell command.

    Attributes:
        ping_finished (:obj:`pyqtSignal(str)`): Emits a signal when the ping 
            process is finished.
        ping_output_ready (:obj:`pyqtSignal(str)`): Emits a signal when
            the ping process
            has an available output to be read.
        send_command (:obj:`pyqtSignal(str)`): Emits a signal that is connected 
            to the ``command_history``, the signal contains the command formed.
        process (:obj:`QProcess`): QProcess object that is used to execute the 
            ``ping`` processes.
        ping_count (:obj:`int`): counts the current ping request count.
            Enabled through the GUI.        
        crontab_options (:mod:`.CronTab_Options_Logic`): Used to schedule
            and show the ``Crontab``.

    Note:
        This is an educational tool and does not use the use ping utility at
        its full potential.

    """    
  
    #  Sends signal when ping process is finished
    ping_finished = pyqtSignal(str)
    #  Sends signal when ping executes and there is an output
    ping_output_ready = pyqtSignal(str)
    send_command = pyqtSignal(str)
    # Ping process
    process = QProcess()
    ping_count = 0

    def __init__(self, parent=None):
        super(Ping_UI_Logic, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
                            QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowMinimizeButtonHint
                            )
        self.crontab_options = None
        self.label_error.hide()
        self.ping_stop_button.hide()
# ==============================================================================
#                       GUI SIGNALS
# ==============================================================================
#  pingButton CLICKED --> Network_Tools_Ping_Execute()
#  ping_stop_button CLICKED --> Stop_Ping()
#  ping_clear_terminal_button CLICKED --> ()
#  ping_clear_history_button CLICKED --> Clear_Ping_Terminal()

# bytes_check.TOGGLED --> Check_Bytes_Count()
# ttl_check TOGGLED --> Check_Status()
# inf_count_radioButton TOGGLED --> Check_Count()

# Signals below are defined by the code writer
# ping_output_ready --> Print_Ping_Terminal()
# ping_finished --> Print_Terminated()

# Signals below are part of Qprocess and are not defined by the code writer
# readyReadStandardOutput --> Set_Ping_Output()
# readyReadStandardError --> Ping_Erorr()
# ==============================================================================
        self.pingButton.clicked.connect(self.Network_Tools_Ping_Execute)
        self.ping_stop_button.clicked.connect(self.Stop_Ping)
        self.ping_clear_terminal_button.clicked.connect(
        self.Clear_Ping_Terminal)
        self.ping_clear_history_button.clicked.connect(
        self.Clear_Ping_Command_History)

        self.send_command.connect(self.Print_Command)
        self.ping_output_ready.connect(self.Print_Ping_Terminal)
        self.ping_finished.connect(self.Print_Terminated)

        self.bytes_check.stateChanged.connect(self.Check_Bytes_Count)
        self.ttl_check.stateChanged.connect(self.Check_Status)
        self.inf_count.stateChanged.connect(self.Check_Count)

        self.process.readyReadStandardOutput.connect(self.Set_Ping_Output)
        self.process.readyReadStandardError.connect(self.Ping_Error)
        self.process.finished.connect(lambda: self.ping_stop_button.hide())
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

    def Print_Terminated(self, str):
        """When Ping process is killed, this methods prints (Terminated)
        on the GUI Terminal.

        Args:
            str (:obj:`str`): String to be appended to the output terminal.
                In this method, the string is ``Terminated``.
        """        

        self.ping_terminal_text.appendPlainText(str)

    def Ping_Finished(self):
        """When Ping process is over, this methods prints (Ping Finished)
            on the GUI Terminal.
        """        

        self.ping_terminal_text.appendPlainText("Ping Finished")

    def Check_Count(self):

        """
            This method checks if Number of requests is
            enabled in the ping process.

                It is enabled by when the user uncheckes
                ``the inf_count_radioButton``.
                If it is unchecked, ``count_spinBox`` is enabled
                and the user can input the number of requests sent.
                
        """

        if self.inf_count.isChecked():
            # If checked disable count
            self.count_spinBox.setEnabled(False)
        else:
            # If unchecked enable count
            self.count_spinBox.setEnabled(True)

    def Check_Status(self):

        """
            This method checks if Time to Live (TTL)
            is enabled in the ping process.
                It is enabled when the user checks the ``ttl_check``.
                Then ``ttl_spinBox`` is enabled and the user
                can specify the packets Time to Live. 

            Note:
                Max TTL is 255.


        """

        if self.ttl_check.isChecked():
            # If checked enable TTL
            self.ttl_spinBox.setEnabled(True)
        else:
            # If checked disable TTL
            self.ttl_spinBox.setEnabled(False)

    def Check_Bytes_Count(self):

        """This method checks if Byte Count is enabled in the ping process.
                It is enabled when the user checks ``the bytes_check``.
                If  it is checked
                then ``bytes_count_spinBox`` is enabled and the user
                can specify the number of bytes
                to send in the ping process.
        """

        if (self.bytes_check.isChecked()):
            # If checked enable Byte Count
            self.bytes_count_spinBox.setEnabled(True)
        else:
            # If checked enable Byte Count
            self.bytes_count_spinBox.setEnabled(False)

    def Clear_Ping_Command_History(self):
        """
            Clears the command history when Clear History button is clicked.

            Clears ``ping_command_history``.
        """

        self.ping_command_history.clear()

    def Clear_Ping_Terminal(self):

        """
            Clears the Ping Terminal when Clear Terminal button is clicked.
            Clears ``ping_terminal_text``.
        """

        self.ping_terminal_text.clear()
        self.send_command.emit("clear")

    def Set_Ping_Output(self):

        """
            This methods reads the standard output from the process
            then sends the result to ``ping_terminal_text`` by emiting the singal
            :obj:`.ping_output_ready`. that is connected to
            :meth:`.Print_Ping_Terminal()` method.
        """
        # Read process standard output
        data = self.process.readAllStandardOutput()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        # Emits a signal to Print_Ping_Terminal()
        self.ping_output_ready.emit(output)

    def Stop_Ping(self):

        """
            This method is activated when the user clicks on Stop Button.
            It kills the ping process that started and emitting the signals 
            :obj:`.ping_finished` and 
            :obj:`.send_command` emits ``Keyboard: CTRL+C``

            :obj:`.ping_finished` signal is connected to :meth:`.Print_Terminated()`
            and :obj:`.send_command` signal is connected
            to :meth:`.Print_Command()`

        """

        # CTRL+C kills the process on keyboard (shell)
        self.send_command.emit("Keyboard: CTRL+C")
        self.ping_finished.emit("Terminated")
        # Kill Ping Process
        self.process.kill()

    def Ping_Error(self):
        """
            This methods reads the standard Error from the process
            then sends the result to ``ping_terminal_text`` by emiting the
            singal :obj:`.ping_output_ready`.

            :obj:`.ping_output_ready` is connected to
            :meth:`.Print_Ping_Terminal()` method.
        """
        # Read Error
        error = self.process.readAllStandardError()
        # Remove Empty Bytes
        if error.isEmpty():
            return
        # Decodes data to a readable String
        error = bytes(error).decode("utf8").strip()

        self.ping_output_ready.emit(error)

    def Print_Ping_Terminal(self, string):
        """Prints on output terminal.

        Args:
            string (:obj:`str`): String to be printed on the 
                ``ping_terminal_text``
        """        
        #  Emits a signal to Print_Ping_Terminal()
        self.ping_terminal_text.appendPlainText(string)

    def Print_Command(self, str):

        """
            Prints command
        """

        self.ping_command_history.append(str)

    def Network_Tools_Ping_Execute(self):

        """
            This method is responsible for checking user command INPUT
            converts the chosen options to the SHELL command Format
            then this method outputs the command to ``ping_command_history``

            Parameters:

                arg_list (:obj:`list`): List of Arguments chosen.
                address (:obj:`str`): Ping Destination Address.
                adaptive_ping (:obj:`bool`): ``True`` if the adaptive ping option
                    is chosen.

            Note:
                CronTab Jobs are not process in this method.
                Instead, see :meth:`.CronTab_Command_Execute`.
        """

        self.label_error.hide()
        if self.crontab_enable.isChecked():
            self.CronTab_Command_Execute()
            return
        arg_list = []
        # Get the value from the GUI component
        address = self.ping_address.text()
        # Check if a number of replies is specified
        inf_count = self.inf_count.isChecked()
        # Check if the Adaptive Option is enabled
        adaptive_ping = self.adaptive_ping.isChecked()
        # Number of replies
        self.ping_count = self.count_spinBox.value()
        # Append address to the argument list
        arg_list.append(str(address))

        if self.adaptive_ping.isChecked():
            # If adaptive ping is checked then
            # arg_list = [address,-A]
            arg_list.append("-A")
        if self.bytes_check.isChecked():
            # If Byte Count is checked
            # arg_list = [address,-s,bytes_count_spinBox]
            # if adaptive_ping and bytes_check is checked then
            # arg_list = [address,-A,-s,bytes_count_spinBox]
            arg_list.append("-s")
            arg_list.append(str(self.bytes_count_spinBox.value()))
        if self.ttl_check.isChecked():
            # If TTL is Checked then
            # arg_list = [address,-t,ttl_spinBox]
            # If adaptive_ping, bytes_check,
            # ttl_check is checked then
            # arg_list = [address,-A,-s,bytes_count_spinBox,-t,ttl_spinBox]
            arg_list.append("-t")
            arg_list.append(str(self.ttl_spinBox.value()))

        if(inf_count):
            # If number of replies is not specified (inf_count)
            # is checked
            # Convert arg_list to readable format
            self.ping_command_history.append("ping " + " ".join(arg_list))
            # Start ping process (ping,[arguments])
            self.process.start("ping", arg_list)
            self.ping_stop_button.show()
        else:
            # If number of replies is specified (inf_count)
            # is unchecked
            arg_list.append("-c")
            arg_list.append(str(self.ping_count))
            self.send_command.emit("ping " + " ".join(arg_list))
            # Convert arg_list to readable format
            self.process.start("ping", arg_list)
            self.ping_stop_button.show()

    def CronTab_Command_Execute(self):

        """CronTab Jobs are processed in this method.

            Note:
                For regular command execution see :meth:`.Network_Tools_Ping_Execute()`
            
        """

        if self.crontab_options is None:
            self.label_error.show()
            self.label_error.setText("Set CronTab Options First!")
            return
        arg_list = []
        # Get the value from the GUI component
        address = self.ping_address.text()
        # Check if a number of replies is specified
        inf_count = self.inf_count.isChecked()
        # Check if the Adaptive Option is enabled
        adaptive_ping = self.adaptive_ping.isChecked()
        # Number of replies
        self.ping_count = self.count_spinBox.value()
        # Append address to the argument list
        arg_list.append(str(address))

        if self.adaptive_ping.isChecked():
            # If adaptive ping is checked then
            # arg_list = [address,-A]
            arg_list.append("-A")
        if self.bytes_check.isChecked():
            # If Byte Count is checked
            # arg_list = [address,-s,bytes_count_spinBox]
            # if adaptive_ping and bytes_check
            # is checked then
            # arg_list = [address,-A,-s,bytes_count_spinBox]
            arg_list.append("-s")
            arg_list.append(str(self.bytes_count_spinBox.value()))
        if self.ttl_check.isChecked():
            # If TTL is Checked then
            # arg_list = [address,-t,ttl_spinBox]
            # If adaptive_ping, bytes_check,
            # ttl_check is checked then
            # arg_list = [address,-A,-s,bytes_count_spinBox,-t,ttl_spinBox]
            arg_list.append("-t")
            arg_list.append(str(self.ttl_spinBox.value()))

        if(inf_count):
            # If number of replies is not specified (inf_count)
            # is checked
            # Convert arg_list to readable format
            self.ping_command_history.append("ping " + " ".join(arg_list))
            # Start ping process (ping,[arguments])
            self.process.start("ping", arg_list)
            self.ping_stop_button.show()
            # Start CronTab Job
            self.crontab_options.Start_Job("ping " + " ".join(arg_list))
        else:
            # If number of replies is specified (inf_count)
            # is unchecked
            # Add -c and number of relies after the address
            # [Address,-c,ping_count]
            arg_list.insert(0, "-c")
            arg_list.insert(1, str(self.ping_count))
            self.send_command.emit("ping " + " ".join(arg_list))
            # Convert arg_list to readable format
            self.process.start("ping", arg_list)
            self.ping_stop_button.show()
            # Start CronTab Job
            self.crontab_options.Start_Job("ping " + " ".join(arg_list))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = Ping_UI_Logic()
    ui.show()
    sys.exit(app.exec_())
