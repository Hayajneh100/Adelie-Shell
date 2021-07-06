
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QProcess, Qt
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog, QAbstractItemView, QListWidgetItem
from GNU_Handler import GNU_Handler
import Data
import re
import sys
import os.path
import rsrs_rc


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(PARENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "GNU_Core_Interface.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)


class GNU_Logic(baseUIWidget, baseUIClass):
    """Handles Logic for GNU Core Utilities (GNU_Core_Interface.ui)

    Attributes:
        files (:obj:`list` of ``str``): File Arguments added from browse button.
        pipe_files (:obj:`list` of ``str``): File Arguments (``PIPED`` ) 
        man_files (:obj:`list` of ``str``): ``Mandatory options`` Files 
        man_pipe_files (:obj:`list` of ``str``): ``Mandatory options PIPED`` Files 
        cmd (:obj:`list` of ``list``): List that contains all currently selected
            or typed arguments. User for the command tracker.
        cmd1 (:obj:`list` of ``list``): Used for ``PIPED`` commad.  See :attr:`.cmd`

        output_ready (:obj:`pyqtSignal(str)`): Prints the output on Output Terminal
        task (:obj:`pyqtSignal(str)`): Emits a signal that indictate command's 
            required input. For example, if the command selected has options and
            no arguments, it emits: "command has no arguments choose options"

        command_change (:obj:`pyqtSignal()`): Emitted when command arguments, 
            options selection have changed. 
        process (:obj:`QProcess`): Process to execute non ``piped`` commands.
        process1 (:obj:`QProcess`): Process to execute first command in the 
            pipe chain, its output is redirected to :attr:`.process2`
        process2 (:obj:`QProcess`): Process to execute the second command in 
            the pipe chain.   
        selected_options (:obj:`list` of ``str``): Contains the list of options
            currently selected by the user. It is updated each time the user
            makes a new selection. See :meth:`See_Option_Change`. This list
            will also contain Mandatory Options, :attr:`.man_option_chosen`.

        selected_pipe_options(:obj:`list` of ``str``): Used for piped command 
            see :attr:`selected_options` and :meth:`Show_Man_Option_Change`
        current_args(:obj:`list` of ``str``): Contains the current arguments
            typed by the user. Updated each time an argument is changed. 
            See :meth:`Show_Arg_Change`
        current_mode (:obj:`list` of ``str``): Contains the current selected
            mode.            
        current_pipe_args(:obj:`list` of ``str``): Contains the current
            selected ``PIPED`` arguments see :attr:`.current_args`.
        man_args(:obj:`list` of ``str``): Contains a list of the current selected
            mandatory options see :meth:`Show_Man_Option_Change`
        man_args_piped(:obj:`list` of ``str``): Contains a list of ``PIPED``
            mandatory arguments see :attr:`.man_args`

        GNU(:obj:`GNU_Handler`): Uses GNU Handler API to read the GNU Core 
            Utilities Options and Arguments   . 
    """    

    files = []
    pipe_files = []
    man_files = []
    man_pipe_files = []
    cmd = []
    cmd1 = []
    output_ready = pyqtSignal(str)
    task = pyqtSignal(str)
    command_change = pyqtSignal()
    process = QProcess()
    process1 = QProcess()
    process2 = QProcess()
    selected_options = []
    selected_pipe_options = []
    current_args = [""]
    current_mode = [""]
    current_pipe_args = [""]
    man_args = [""]
    man_args_pipe = [""]
    GNU = GNU_Handler()
    types = GNU.Get_Supported_Types()

    def __init__(self, parent=None):
        super(GNU_Logic, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(
                            QtCore.Qt.WindowCloseButtonHint
                            | QtCore.Qt.WindowMinimizeButtonHint
                            )
        self.process1.setStandardOutputProcess(self.process2)
        self.stacked_args.setCurrentIndex(0)
        self.Hide_Arguments_Widgets()
        self.opt_frame.hide()
        self.cmd1_label.hide()
        self.cmd2_label.hide()
        self.man_1.hide()
        self.man_2.hide()
# ==============================================================================
        self.fwd_button.hide()
        self.bck_button.hide()
        self.fwd_button.clicked.connect(lambda:
                                        self.stacked_args.setCurrentIndex(1))
        self.bck_button.clicked.connect(lambda:
                                        self.stacked_args.setCurrentIndex(0))

# ==============================================================================

        self.stop_process.clicked.connect(self.Kill_Process)
        self.clear_history.clicked.connect(
                                        lambda: self.command_history.clear())
        self.clear_terminal.clicked.connect(self.Clear_Terminal)
        self.file_open_button.clicked.connect(self.openFileNamesDialog)
        self.execute_command_button.clicked.connect(self.Execute_Command)
        self.shrt_opt_list.itemClicked.connect(self.Check_Man_Options)
        self.piped_list.itemClicked.connect(self.Check_Man_Options)
        self.pipe.stateChanged.connect(self.Enable_PIPE)
        self.gnu_tools = self.GNU.Get_GNU_Tools()
        self.Show_GNU_Tools(self.gnu_tools)
        self.output_ready.connect(self.Print_Output)
        self.process.readyReadStandardOutput.connect(self.Process_Output)
        self.process.readyReadStandardError.connect(self.Process_Output_Error)
        self.process1.readyReadStandardError.connect(self.Process_Output_Error)
        self.process2.readyReadStandardOutput.connect(self.Process_Output)
        self.process2.readyReadStandardError.connect(self.Process_Output_Error)
        self.shrt_list.itemSelectionChanged.connect(self.Enforce_Selection_Size
                                                    )
        self.pipe_file.clicked.connect(self.Open_PIPE_File)
        self.task.connect(self.Set_Current_Task)
        self.task.emit("Choose Your Command")
# ==============================================================================
        self.man_file.clicked.connect(self.openFileNamesDialog)
        self.man_pipe_file.clicked.connect(self.openFileNamesDialog)
# ==============================================================================
        self.command_change.connect(self.Formed_Command)
        self.shrt_list.itemSelectionChanged.connect(self.Formed_Command)
        self.shrt_opt_list.itemSelectionChanged.connect(self.Show_Option_Change
                                                        )
        self.text_option.textChanged.connect(self.Show_Arg_Change)
        self.piped_list.itemSelectionChanged.connect(self.Show_Option_Change)
        self.text_pipe.textChanged.connect(self.Show_Arg_Change)
        self.mode_list.itemSelectionChanged.connect(self.Show_Arg_Change)
        self.man_text.textChanged.connect(self.Show_Man_Option_Change)
        self.format_list.itemSelectionChanged.connect(
                                                    self.Show_Man_Option_Change
                                                    )
        self.man_text_pipe.textChanged.connect(self.Show_Man_Option_Change)
        self.format_list_pipe.itemSelectionChanged.connect(
                                                          self.
                                                          Show_Man_Option_Change
                                                         )
        self.user_radio.clicked.connect(self.Show_Arg_Change)
        self.group_radio.clicked.connect(self.Show_Arg_Change)
        self.other_radio.clicked.connect(self.Show_Arg_Change)
# ==============================================================================

    def Clear_Terminal(self):
        """Clears the output terminal
        """        
        self.terminal_text.clear()
        self.command_history.append("clear")

    def Formed_Command(self):
        """
            Displays the formed command on formed_command widget.

            Invoked from command_changed signal.
            :meth:`.Show_Option_Change()`
            :meth:`.Show_Arg_Change()`
            :meth:`.Show_File_Change`
            These methods ensure that the command is displayed
            in the same order that the users chooses.

        """
        
        if self.shrt_list.selectedItems() == []:
            self.formed_command.clear()
            return
        text = self.shrt_list.selectedItems()[0].text() + " "
        for item in self.cmd:
            if item is self.selected_options:
                for x in item:
                    if isinstance(x, list):
                        text = " " + text + " ".join(x) + " "
                    else:
                        text = " " + text + x + " "
            else:
                text = " " + text + " ".join(item) + " "
            # When there is a list inside the list

        if self.pipe.isChecked() and len(self.shrt_list.selectedItems()) == 2:
            text = (text + " | " + self.shrt_list.selectedItems()[1].text()
                    + " ")
            for item in self.cmd1:
                if item is self.selected_pipe_options:
                    for x in item:
                        if isinstance(x, list):
                            text = text + " ".join(x) + " "
                        else:
                            text = text + x + " "
                else:
                    text = text + " ".join(item) + " "
                
       
        self.formed_command.setText(text)

    def Set_Current_Task(self, task):
        """Sets the task label.

        Args:
            task (:obj:`str`): Sets the heading label in the GNU Logic window
                according to the availability of options or arguments. 
                :attr:`.task` signal is connected to this method.
        """        
        
        self.current_task.setText(task)



    def Enforce_Selection_Size(self):
        """
            Ensures that only two commands are selected.

            Then invokes :meth:`.Show_Options()` to display command options.

            Note:
                This method will not disable the ``QListWidget.selectionChanged()``
                signal. Clicking on a different item will emit 
                any ``QListWidget`` signals.
        """

        selected_items = self.shrt_list.selectedItems()
        if len(selected_items) < 2:
            self.shrt_list.blockSignals(False)
        if len(selected_items) > 2:
            selected_items[2].setSelected(False)
        self.Show_Options()

    def Enable_PIPE(self):
        """
            Enables commands piping, sets process output accordingly.
        """
        # If piping is enabled, Allow multiple selection on the command list
        if self.pipe.isChecked():
            self.shrt_list.setSelectionMode(QAbstractItemView.MultiSelection)

        else:
            self.shrt_list.setSelectionMode(QAbstractItemView.SingleSelection)

    def Print_Output(self, str):
        """Appends command output to the terminal widget.

        Note:
            Use ``QPlainTextEdit`` as a terminal. Its :obj:`append` method 
            is faster than ``QTextBrowser``. 

        The signal :attr:`.output_ready` is connected to this method.

        Args:
            str (:obj:`str`): output to be printed.

        """        

        self.terminal_text.appendPlainText(str)

    def Process_Output_Error(self):
        """
            Reads the process error output and sends it to the terminal.

            Note:
                This method is shared between :attr:`process1` and
                :attr:`process2`
                If Piping is enabled :attr:`process2` will invoke this method
                then only :attr:`process2` output should be read.
        """

        if self.sender() is self.process:
            data = self.process.readAllStandardError()
        if self.sender() is self.process1:
            data = self.process1.readAllStandardError()
        if self.sender() is self.process2:
            data = self.process2.readAllStandardError()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8").strip()
        if "/usr/bin/" in output:
            output = output.replace("/usr/bin/", "")
        self.output_ready.emit(output)

    def Process_Output(self):
        """
            Reads the process standard output and sends it to the terminal.

            Note:
                This method is shared between :attr:`process1` and
                :attr:`process2`
                If Piping is enabled :attr:`process2` will invoke this method
                then only :attr:`process2` output should be read.
        """
        if self.sender() is self.process:
            data = self.process.readAllStandardOutput()
        if self.sender() is self.process2:
            data = self.process2.readAllStandardOutput()
        # Sends Empty Bytes
        if data.isEmpty():
            return
        # Decodes data to a readable String
        output = bytes(data).decode("utf8", errors="ignore").strip()
        self.output_ready.emit(output)

    def Check_Man_Options(self):
        """
            Checks if the option selected has a Man.Option.
        """
        # This method is invoked twice from both lists
        # Because piped and normal Man.Options are on the same frame
        # Hiding one and keeping the other is going to be difficult
        # use self.man_wdigets to show both widgets togother

        if self.sender() is self.piped_list:
            self.Check_Man_Options_PIPED()
            return
        self.man_1.hide()

        self.Hide_Man_Widgets(True, "NORMAL")
        tool_name = self.shrt_list.selectedItems()[0].text()
        if self.sender() is self.shrt_opt_list:
            # On Deselection
            if (self.shrt_opt_list.currentItem() not in
                    self.shrt_opt_list.selectedItems()):
                return

            option = self.shrt_opt_list.currentItem().text()
            man_option1 = self.GNU.Get_Man_Option(tool_name, option)

            if man_option1 is not None:
                self.Hide_Man_Widgets(False, "NORMAL")
                self.Set_Man_Options(tool_name, man_option1, 1)

            if tool_name == "stat" and option == "c":
                self.Hide_Man_Widgets(False, "NORMAL")
                self.Set_Man_Options(tool_name, "FORMAT", 1)

            if tool_name =="head" and option == "n":
                self.Hide_Man_Widgets(False, "NORMAL")
                self.Set_Man_Options(tool_name, "NUM", 1)


    def Check_Man_Options_PIPED(self):
        """
            Checks if the option selected has a Man.Option for the PIPED tool.
        """
        self.man_2.hide()
        self.Hide_Man_Widgets(True, "PIPE")
        # On Deselection
        if (self.piped_list.currentItem() not in
                self.piped_list.selectedItems()):
            return
        tool1_name = self.shrt_list.selectedItems()[1].text()
        option1 = self.piped_list.currentItem().text()
        man_option2 = self.GNU.Get_Man_Option(tool1_name, option1)
        if man_option2 is not None:
            self.Hide_Man_Widgets(False, "PIPE")
            self.Set_Man_Options(tool1_name, man_option2, 2)

        if tool1_name == "stat" and option1 == "c":
            self.Hide_Man_Widgets(False, "NORMAL")
            self.Set_Man_Options("stat", "FORMAT",2)

        if tool1_name =="head" and option1 == "n":
                self.Hide_Man_Widgets(False, "NORMAL")
                self.Set_Man_Options(tool1_name, "NUM", 2)

    def Set_Man_Options(self, tool_name, man_option, index):
        """Displays the Man. Options of the tools.

        Args:
            tool_name (:obj:`str`): Tool's (Command) name
            man_option (:obj:`str`): Mandatory Option to be displayed
            index (:obj:`int`): int that determines the index 
                of the selected tool. If ``index = 1``, normal command no pipe,
                ``index = 2`` piped command.
        """        
        
        if man_option in Data.MIV:
            if man_option == "FILE" or man_option == "RFILE" :
                tip = Data.Arg_Hints[man_option]
                if index == 1:
                    self.man_file.show()
                    self.man_file.setToolTip(tip)
                else:
                    self.man_pipe_file.show()
                    self.man_pipe_file.setToolTip(tip)
                    self.man_pipe_file.setText(tool_name + " file")

            elif man_option == "FORMAT":
                if tool_name == "pr":
                    if index == 1:
                        self.man_1.show()
                        self.man_1.setText(tool_name + " Mandatory Options")
                        self.Gen_Format_List(self.format_list, Data.FMT_Date)
                        self.format_list.show()
                    else:
                        self.man_2.show()
                        self.man_2.setText(tool_name + " Mandatory Options")
                        self.Gen_Format_List(self.format_list_pipe,
                                             Data.FMT_Date)
                        self.format_list_pipe.show()

                elif tool_name == "nl":
                    if index == 1:
                        self.man_1.show()
                        self.man_1.setText(tool_name + " Mandatory Options")
                        self.Gen_Format_List(self.format_list, Data.FMT_Lines)
                        self.format_list.show()
                    else:
                        self.man_2.show()
                        self.man_2.setText(tool_name)
                        self.Gen_Format_List(self.format_list_pipe,
                                             Data.FMT_Lines)
                        self.format_list_pipe.show()

                elif tool_name == "stat":
                    if index == 1:
                        self.man_1.show()
                        self.man_1.setText(tool_name + " Mandatory Options")
                        self.Gen_Format_List(self.format_list, Data.FMT_Files)
                        self.format_list.show()
                    else:
                        self.man_2.show()
                        self.man_2.setText(tool_name + " Mandatory Options")
                        self.Gen_Format_List(self.format_list_pipe,
                                             Data.FMT_Files)
                        self.format_list_pipe.show()
                else:
                    # csplit
                    if index == 1:
                        self.man_1.show()
                        self.man_1.setText(tool_name + " Mandatory Options")
                        self.man_text.show()
                        self.man_text.setToolTip(Data.Arg_Hints["printf"])
                        self.man_text.setPlaceholderText("Input "
                                                     + man_option + " for "
                                                     + tool_name)
                    else:
                        self.man_2.show()
                        self.man_2.setText(tool_name + " Mandatory Options")
                        self.man_text_pipe.show()
                        self.man_text_pipe.setToolTip(Data.Arg_Hints["printf"])
                        self.man_text.setPlaceholderText("Input "
                                                     + man_option + " for "
                                                     + tool_name)
            else:
                if index == 1:
                    self.man_1.show()
                    self.man_1.setText(tool_name + " Mandatory Options")
                    self.man_text.setPlaceholderText("Input "
                                                     + man_option + " for "
                                                     + tool_name)
                    tip = Data.Arg_Hints[man_option]
                    self.man_text.show()
                    self.man_text.setToolTip(tip)
                else:
                    self.man_2.show()
                    self.man_2.setText(tool_name + " Mandatory Options")
                    tip = Data.Arg_Hints[man_option]
                    self.man_text_pipe.setPlaceholderText("Input "
                                                          + man_option
                                                          + " for "
                                                          + tool_name)
                    self.man_text_pipe.show()
                    self.man_text_pipe.setToolTip(tip)
            self.stacked_args.setCurrentIndex(1)
        else:
            if index == 1:
                self.notsupp.setText(tool_name + " " + " not supported")
                self.notsupp.show()
            else:
                self.notsupp_pipe.setText(tool_name + " " + " not supported")
                self.notsupp_pipe.show()

    def Show_GNU_Tools(self, gnu_tools):
        """Display GNU Coreutils installed on the System on the user interface.

        Args:
            gnu_tools (:obj:`list` of ``str``): List which contains all the
                GNU Core Utilities tools (commands) installed on the host system
        """        

        for item in self.gnu_tools:
            item_desc = self.GNU.Get_Tool_Description(item)
            item_adedd = QtWidgets.QListWidgetItem(item)
            item_adedd.setTextAlignment(Qt.AlignCenter)
            item_adedd.setToolTip(item_desc)
            self.shrt_list.addItem(item_adedd)

    def Show_Options_PIPED(self):
        """
            Displays ``Command1`` and ``Command2`` options when piping
            is enabled.
        """
        if self.shrt_list.currentItem() not in self.shrt_list.selectedItems():
            return
        # Clear previous entries and hide unnecessary widgets
        self.Hide_Arguments_Widgets()
        self.cmd.clear()
        self.cmd1.clear()
        self.files.clear()
        self.opt_frame.hide()
        self.shrt_opt_list.hide()
        self.cmd1_label.hide()
        self.cmd2_label.hide()
        self.shrt_opt_list.clear()
        self.piped_list.clear()
        tool_name = self.shrt_list.selectedItems()[0].text()
        tool1_name = self.shrt_list.selectedItems()[1].text()
        if tool_name in ["flock", "test", "expr", "pinky", "expr"]:
            self.task.emit(tool_name + " Not Implemented")
            return
        if tool1_name in ["flock", "test", "expr", "pinky", "expr"]:
            self.task.emit(tool1_name + " Not Implemented")
            return
        string = ""
        if self.GNU.Has_Options(tool_name):
            string = " " + string + tool_name + ":" + " have options "
        else:
            string = " " + string + tool_name + ":" + " No options "
        if self.GNU.Has_Arguments(tool_name):
            string = string + " have arguments "
        else:
            string = string + " No arguments"

        if self.GNU.Has_Options(tool1_name):
            string = " " + string + " | " + tool1_name + ":" + " have options "
        else:
            string = " " + string + " | " + tool1_name + ":" + " No options "

        if self.GNU.Has_Arguments(tool1_name):
            string = string + " have arguments"
        else:
            string = string + " No Arguments"
        self.task.emit(string)

        if self.GNU.Has_Options(tool_name):
            self.opt_frame.show()
            self.shrt_opt_list.show()
            self.cmd1_label.show()
            # Dispaly tool name above its list
            self.cmd1_label.setText(tool_name)
            for option in self.GNU.Get_Tool_Options(tool_name):
                tip = self.GNU.Get_Option_Description(tool_name, option)
                item_added = QtWidgets.QListWidgetItem(option)
                item_added.setTextAlignment(Qt.AlignCenter)
                if tip is not None:
                    item_added.setToolTip(tip)
                self.shrt_opt_list.addItem(item_added)
        if self.GNU.Has_Arguments(tool_name):
            self.Argument_Checker_PIPED(tool_name, 1)
        if self.GNU.Has_Options(tool1_name):
            self.opt_frame.show()
            self.piped_list.show()
            self.cmd2_label.show()
            self.cmd2_label.setText(tool1_name)
            for option in self.GNU.Get_Tool_Options(tool1_name):
                tip = self.GNU.Get_Option_Description(tool1_name, option)
                item_added = QtWidgets.QListWidgetItem(option)
                item_added.setTextAlignment(Qt.AlignCenter)
                # In case of regex failure
                if tip is not None:
                    item_added.setToolTip(tip)
                self.piped_list.addItem(item_added)
        if self.GNU.Has_Arguments(tool1_name):
            self.Argument_Checker_PIPED(tool1_name, 2)

    def Show_Options(self):
        """
            Displays the tool options.

            This Method will continue execution if ``PIPE`` is enabled
            and only one item is selected.
        """
        # If a third tool is clicked do not complete this method's execution
        # Enforcing selection size doesn't disable clicking or
        # Selection changed signal.
        if len(self.shrt_list.selectedItems()) == 2:
            if (self.shrt_list.currentItem() not in
                    self.shrt_list.selectedItems()):
                return

        self.Hide_Man_Widgets(True, "NORMAL")
        self.Hide_Man_Widgets(True, "PIPE")
        self.Hide_Arguments_Widgets()
        self.cmd.clear()
        self.cmd1.clear()
        self.files.clear()
        self.opt_frame.hide()
        self.piped_list.hide()
        self.shrt_opt_list.clear()
        self.cmd1_label.hide()
        self.cmd2_label.hide()
        #  Deselection
        if self.shrt_list.selectedItems() == []:
            return
        # Invoke PIPE methods when Two items are selected
        # If one Item is selected invoke this method
        if self.pipe.isChecked() and len(self.shrt_list.selectedItems()) == 2:
            self.Show_Options_PIPED()
            return

        tool_name = self.shrt_list.selectedItems()[0].text()
        # Tools that have different options format than regex
        if tool_name in ["flock", "test", "expr", "pinky", "expr"]:
            self.task.emit("Not Implemented")
            return
        if self.GNU.No_Options_Arguments(tool_name):
            self.task.emit("No Arguments and Options")
            return

        if self.GNU.Has_Options(tool_name):
            self.opt_frame.show()
            for option in self.GNU.Get_Tool_Options(tool_name):
                tip = self.GNU.Get_Option_Description(tool_name, option)
                item_added = QtWidgets.QListWidgetItem(option)
                item_added.setTextAlignment(Qt.AlignCenter)
                if tip is not None:
                    item_added.setToolTip(tip)
                self.shrt_opt_list.addItem(item_added)

        if (self.GNU.Has_Options(tool_name)
                and not self.GNU.Has_Arguments(tool_name)):
            self.task.emit("Choose Options, No Arguments to Choose")
        elif (not self.GNU.Has_Options(tool_name)
                and self.GNU.Has_Arguments(tool_name)):
            self.task.emit("Choose Arguments, No Options to Choose")
        else:
            self.task.emit("Now Choose Option/s or Arguments")
        if self.GNU.Has_Arguments(tool_name):
            self.Argument_Checker(tool_name)

    def openFileNamesDialog(self):
        """
            static function in ``QFileDialog`` which creates a
            file dialog or a file picker.
            
        """

        options = QFileDialog.Options()
        options = QFileDialog.DontUseNativeDialog
        files = QFileDialog.getOpenFileNames(self,
                                             "Choose Files",
                                             "",
                                             "All Files (*)",
                                             options=options)
        if self.sender() is self.file_open_button:
            if len(files[0]) > 0:
                # Returns a Tuple ([LIST OF FILES],"All Files (*)")
                # Extend self.files to keep the object from pointing to a random
                # list. This is important for Show_File_Change
                self.files.extend(files[0])
            else:
                self.files.clear()

        if self.sender() is self.man_file:

            if len(files[0]) > 0:
                # Returns a Tuple ([LIST OF FILES],"All Files (*)")
                # Extend self.files to keep the object from pointing to a random
                # list. This is important for Show_File_Change
                self.man_files.extend(files[0])
            else:
                self.man_files.clear()
        if self.sender() is self.man_pipe_file:
            if len(files[0]) > 0:
                # Returns a Tuple ([LIST OF FILES],"All Files (*)")
                # Extend self.files to keep the object from pointing to a random
                # list. This is important for Show_File_Change
                self.man_pipe_files.extend(files[0])
            else:
                self.man_pipe_files.clear()
        self.Show_File_Change()

    def Open_PIPE_File(self):
        """
            Static Function in QFileDialog Which Creates a File Dialog.
            
        """
        options = QFileDialog.Options()
        options = QFileDialog.DontUseNativeDialog
        files = QFileDialog.getOpenFileNames(self,
                                             "Choose Files",
                                             "",
                                             "All Files (*)",
                                             options=options)
        if len(files[0]) > 0:
            # Returns a Tuple ([LIST OF FILES],"All Files (*)")
            # Extend self.pipe_files to keep
            # the object from pointing to a random
            # list. This is important for Show_File_Change
            self.pipe_files.extend(files[0])
        else:
            self.pipe_files.clear()
        self.Show_File_Change()

    def Argument_Checker_PIPED(self, tool_name, index):
        """Check Arguments when PIPE mode is enabled.

        Args:
            tool_name (:obj:`str`): Tool's (command) name.
            index (:obj:`int`): int that determines the index 
                of the selected tool. If ``index = 2``, normal command no pipe,
                ``index = 2`` piped command.
        """        

        self.args.show()
        srch = self.GNU.Get_Tool_Argument(tool_name)
        # Show only if CHMOD is selected
        self.mode_list.hide()
        # Show only if CHMOD is selected
        self.label_mode.hide()
        # Initally hide
        # Initally hide
        if tool_name == "chmod":
            # If the current tool is chmod
            # Mode is used as an argument
            # display the mode list for user
            self.args_frame.show()
            self.label_mode.show()
            # Not to duplicate modes
            self.mode_list.clear()
            self.mode_list.show()
            self.mode_frame.show()
            for item in self.types["Mode"]:
                tip = self.Gen_Mode_Tooltip(item)
                item_added = QtWidgets.QListWidgetItem(item)
                item_added.setTextAlignment(Qt.AlignCenter)
                item_added.setToolTip(tip)
                self.mode_list.addItem(item_added)
        # line in list or before (,)
        for usage in srch:
            for item in self.types["Path"]:
                # Compare list of path (FILE,NAME,FILE1....)
                # with each word in usage

                if item in usage:
                    if index == 1:
                        self.label_text_type.setText(
                                                    "Click on Button to"
                                                    + " choose File/s"
                                                    )
                        self.label_text_type.show()
                        self.file_open_button.show()
                        self.file_open_button.setToolTip(Data.Arg_Hints[item])
                    else:
                        self.label_text_type.setText(
                                                    "Click on Button to"
                                                    + " choose File/s"
                                                    )
                        self.pipe_file.setText(tool_name + " File")
                        self.pipe_file.show()
                        self.pipe_file.setToolTip(Data.Arg_Hints[item])

            for item in self.types["Text"]:
                if item in usage:
                    if index == 1:
                        self.text_option.setPlaceholderText("input a "
                                                            + item
                                                            + " here")
                        self.text_option.show()
                        self.text_option.setToolTip(Data.Arg_Hints[item])
                    else:
                        self.text_pipe.setPlaceholderText(tool_name
                                                          + " command "
                                                          + "input a "
                                                          + item
                                                          + " here")
                        self.text_pipe.show()
                        self.text_pipe.setToolTip(Data.Arg_Hints[item])

            for item in self.types["Digit"]:
                if item in usage:
                    if index == 1:
                        self.text_option.setPlaceholderText("input a "
                                                            + item
                                                            + " here")
                        self.text_option.show()
                        self.text_option.setToolTip(Data.Arg_Hints[item])
                    else:
                        self.text_pipe.setPlaceholderText(tool_name
                                                          + " command "
                                                          + "input a "
                                                          + item
                                                          + " here")
                        self.text_pipe.show()
                        self.text_pipe.setToolTip(Data.Arg_Hints[item])

    def Argument_Checker(self, tool_name):
        """
            Checks if the tool uses Files, Text, Digits, and Show Components
            depending on the result.
            This methods is activated when user clicks on tools list
         """
        self.args.show()
        self.selected_options.clear()
        # Show only if CHMOD is selected
        self.mode_list.hide()
        # Show only if CHMOD is selected
        self.label_mode.hide()
        # Initally hide
        self.file_open_button.hide()
        # Initally hide
        self.text_option.hide()
        if tool_name == "touch":
            
            self.args_frame.show()
            self.text_option.setPlaceholderText("input "
                                                + "  Path"
                                                + " here")
            self.text_option.show()
            self.text_option.setToolTip("Full File Path")

        if tool_name == "chmod":
            # If the current tool is chmod
            # Mode is used as an argument
            # display the mode list for user
            self.args_frame.show()
            self.label_mode.show()
            # Not to duplicate modes
            self.mode_list.clear()
            self.mode_list.show()
            self.mode_frame.show()
            for item in self.types["Mode"]:
                tip = self.Gen_Mode_Tooltip(item)
                item_added = QtWidgets.QListWidgetItem(item)
                item_added.setTextAlignment(Qt.AlignCenter)
                item_added.setToolTip(tip)
                self.mode_list.addItem(item_added)

        if tool_name == "touch":
            self.args_frame.show()
            self.text_option.setPlaceholderText("input "
                                                + "File Path"
                                                + " here")
            self.text_option.show()
            self.text_option.setToolTip("File Path")

        if tool_name == "split":
            self.args_frame.show()
            self.label_text_type.show()
            self.label_text_type.setText("Click on Browse to"
                                         + " choose File/s"
                                         )
            self.file_open_button.show()
            self.file_open_button.setToolTip("Specify a file/s")

        # Returns a list with all usages
        args = self.GNU.Get_Tool_Argument(tool_name)
        # line in list or before (,)
        for arg in args:
            #print(arg)
            for item in self.types["Path"]:
                # Compare list of path (FILE,NAME,FILE1....)
                # with each word in usage
                if item in args:
                    self.args_frame.show()
                    self.label_text_type.show()
                    self.label_text_type.setText(
                                                "Click on Browse to"
                                                + " choose File/s"
                                                )
                    self.file_open_button.show()
                    self.file_open_button.setToolTip(Data.Arg_Hints[item])

            for item in self.types["Text"]:
                if item in args:
                    self.args_frame.show()
                    self.text_option.setPlaceholderText("input "
                                                        + item
                                                        + " here")
                    self.text_option.show()
                    self.text_option.setToolTip(Data.Arg_Hints[item])
            for item in self.types["Digit"]:
                if item in args:
                    self.args_frame.show()
                    self.text_option.setPlaceholderText("input "
                                                        + item
                                                        + " here")
                    self.text_option.show()
                    self.text_option.setToolTip(Data.Arg_Hints[item])

    def Execute_Command(self):
        """
            Executes Command and All the Options,
            Activated using Execute button.

        """

        if self.pipe.isChecked() and len(self.shrt_list.selectedItems()) == 2:

            self.Execute_PIPE_Command()
            return
        tool_name = self.shrt_list.selectedItems()[0].text()
        command1 = []
        for item in self.cmd:
            if item is self.selected_options:
                for option in item:
                    if option is self.man_args:
                        command1.extend(option)
                    else:
                        # " -Option" is for visuals on the command tracker
                        # Remove the space or it will file not found error
                        option = option.replace(" -", "-")
                        command1.append(option)

            if item is self.current_args:
                item[0] = item[0].strip()
                command1.extend(item)

            if item is self.files:
                command1.extend(item)

        print(command1)
        self.process.start(tool_name, command1)
        self.command_history.append(tool_name + " " + " ".join(command1))

    def Execute_PIPE_Command(self):
        """
            Executes PIPE commands.
            PIPE commands are command that are piped togother.
        """

        tool1_name = self.shrt_list.selectedItems()[0].text()
        if len(self.shrt_list.selectedItems()) == 1:
            tool2_name = ""
        else:
            tool2_name = self.shrt_list.selectedItems()[1].text()

        if self.process1.state() == 2 or self.process2.state() == 2:
            self.terminal_text.appendPlainText(
                "Process Already Running Please Stop it")
            return
        command1 = []
        command2 = []
        # command format  [ [OPTIONs, MAN OPTIONS], [MAN ARGS], [FILES] ]
        for item in self.cmd:
            if item is self.selected_options:
                # selected_options contan another list (man args)
                for option in item:
                    # Extend Man.Args
                    if option is self.man_args:
                        command1.extend(option)
                    else:
                        # " -Option" is for visuals on the command tracker
                        # Remove the space or it will file not found error
                        option = option.replace(" -", "-")
                        command1.append(option)

            if item is self.current_args:
                item[0] = item[0].strip()
                command1.extend(item)

            if item is self.files:
                command1.extend(item)

        self.process1.start(tool1_name, command1)
        print(self.cmd1)
        for item in self.cmd1:
            print("ITEM " + str(item))
            if item == [" "]:
                self.cmd1.remove(item)
            print(self.cmd1)    
            if item is self.selected_pipe_options:
                for option in item:
                    if option is self.man_args_pipe:
                        command2.extend(option)
                    else:
                        # " -Option" is for visuals on the command tracker
                        # Remove the space or it will file not found error
                        option = option.replace(" -", "-")
                        command2.append(option)

            if item is self.current_pipe_args:
                item[0] = item[0].strip()
                command2.extend(item)

            if item is self.pipe_files:
                command2.extend(item)

        self.process2.start(tool2_name, command2)
        print(command2)
        self.command_history.append(
                                    tool1_name + " " + " ".join(command1)
                                    + " | "
                                    + tool2_name + " " + " ".join(command2)
                                    )

    def Kill_Process(self):
        """
            Kills any running process.
        """
        if self.process.state() == 2:
            self.process.kill()
        if self.process1.state() == 2:
            self.process1.kill()
        if self.process2.state() == 2:
            self.process2.kill()
        self.command_history.append("Keyboard: Ctrl+C")

    def Show_Option_Change(self):
        """
            Changes selected_options according to the user selected options.

            Adds the selected options to the cmd list and removes it
            if options are deselected,
            a specific element of :attr:`.cmd` should point to the options
            This specific element index is determined by how the user chooses
            options or arguments
            :attr:`.command_change` will emit a signal at the end 
            of this method indicating that options are changed
                
        """
        if len(self.shrt_list.selectedItems()) > 2:
            return
        # If no options are selected and selected_options in cmd
        # then the options are deselected, remove selected options from cmd
        if self.sender() is self.shrt_opt_list:
            if (self.shrt_opt_list.selectedItems() == []
                    and self.selected_options in self.cmd):
                self.cmd.remove(self.selected_options)
                self.command_change.emit()
            else:
                # If options were already chosen do not re append it
                if self.selected_options not in self.cmd:
                    self.cmd.append(self.selected_options)
                for option in self.shrt_opt_list.selectedItems():
                    opt = " -" + option.text()
                    if opt not in self.selected_options:
                        self.selected_options.append(opt)
                # Remove Deselected Options
                for opt in self.selected_options:
                    if opt is self.man_args:
                        continue
                    option = opt.replace(" -", "")
                    lst_opt = [
                            item.text()
                            for item in self.shrt_opt_list.selectedItems()
                            ]
                    # Options that are not present are deselected
                    # Remove deselected options from the list
                    if option not in lst_opt and option not in self.man_args:
                        self.selected_options.remove(opt)

        if self.sender() is self.piped_list:

            if (self.piped_list.selectedItems() == []
                    and self.selected_pipe_options in self.cmd1):
                self.cmd1.remove(self.selected_pipe_options)
                self.command_change.emit()
            else:
                # If options were already chosen do not re append it
                if self.selected_pipe_options not in self.cmd1:
                    self.cmd1.append(self.selected_pipe_options)
                for option in self.piped_list.selectedItems():
                    opt = " -" + option.text()
                    if opt not in self.selected_pipe_options:
                        self.selected_pipe_options.append(opt)
                # Remove Deselected Options
                for opt in self.selected_pipe_options:
                    if opt is self.man_args_pipe:
                        continue
                    option = opt.replace(" -", "")
                    lst_opt = [
                            item.text()
                            for item in self.piped_list.selectedItems()
                            ]
                    # Options that are not present are deselected
                    # Remove deselected options from the list
                    if (option not in lst_opt
                            and option not in self.man_args_pipe):
                        self.selected_pipe_options.remove(opt)

        self.command_change.emit()

    def Show_Man_Option_Change(self):
        """
            Reflects the Man.Option change on the command tracker.

            :attr:`.command_change` will emit a signal at the end of this
            method to indicate the Mandatory options chosen have changed
        """
        # When a third item is clicked
        if len(self.shrt_list.selectedItems()) > 2:
            return

        tool_name = self.shrt_list.selectedItems()[0].text()
        # if list is empty remove it from the options list
        if self.man_args == [""] and self.man_args in self.selected_options:
            self.selected_options.remove(self.man_args)
        if (self.man_args_pipe == [""]
                and self.man_args_pipe in self.selected_pipe_options):
            self.selected_pipe_options.remove(self.man_args_pipe)

        # Get Option index and insert the Man.Option in the next index
        for option in self.selected_options:
            index = self.selected_options.index(option)
            # The manidotry option is appended to the selected_options list
            # as a list
            # Check if the option inside the list is a the mandatory arguments
            if option is self.man_args:
                continue
            # Check if this option has a Man.Option
            # Then the widget displayed is for that option

            if self.GNU.Has_Supported_ManOptions(
                                                tool_name,
                                                option.replace(" -", "")):
                # Depending on the sender of the signal
                # The widget can be a list or text

                if (self.sender() is self.man_text):
                    self.man_args[0] = self.man_text.text()
                if self.sender() is self.format_list:
                    # Format Lists support multiple selection
                    fmt = [
                        item.text()
                        for item in self.format_list.selectedItems()
                        ]
                    self.man_args[0] = "".join(fmt)
                if self.sender() is self.man_file:
                    self.man_args[0] = " ".join(self.man_files)
                if self.man_args not in self.selected_options:
                    self.selected_options.insert(index + 1, self.man_args)
        # PIPED Man.Options
        if (self.sender() is self.man_text_pipe
                or self.sender() is self.format_list_pipe
                or self.sender() is self.man_pipe_file):
            tool1_name = self.shrt_list.selectedItems()[1].text()
            for option in self.selected_pipe_options:
                index = self.selected_pipe_options.index(option)
                if option is self.man_args_pipe:
                    continue

                if self.GNU.Has_Supported_ManOptions(
                                                tool1_name,
                                                option.replace(" -", "")):
                    if self.sender() is self.man_text_pipe:
                        self.man_args_pipe[0] = self.man_text_pipe.text()

                    if self.sender() is self.format_list_pipe:
                        fmt = [
                                item.text()
                                for item in
                                self.format_list_pipe.selectedItems()
                                 ]
                        self.man_args_pipe[0] = "".join(fmt)
                    if self.sender() is self.man_pipe_file:
                        self.man_args_pipe[0] = "".join(self.man_pipe_files)
                    if self.man_args_pipe not in self.selected_pipe_options:
                        self.selected_pipe_options.insert(index + 1,
                                                          self.man_args_pipe)

        self.command_change.emit()

    def Show_Arg_Change(self):
        """
            Changes :attr:`.current_args` according to the user selected arguments.

            Adds the selected args to the :attr:`.cmd` list and removes it.
            if arguments are removed,
            a specific element of :attr:`.cmd` should point to the arguments
            This specific element index is determined by how the user chooses
            options or arguments
            :attr:`.command_change` will emit a signal a the end
            of this method
            to indicate the that arguments typed have changed.
        """

        if len(self.shrt_list.selectedItems()) > 2:
            return

        # If no arguments are selected and current_args in cmd
        # then the args are removed, remove current_args from cmd
        if self.text_option.text() == "" and self.current_args in self.cmd:
            self.cmd.remove(self.current_args)
            self.command_change.emit()
        else:
            self.current_args[0] = self.text_option.text() + " "
            if self.current_args not in self.cmd:
                self.cmd.append(self.current_args)
        # CHNOD
        if (self.sender() is self.mode_list
                or self.sender() is self.user_radio
                or self.sender() is self.group_radio
                or self.sender() is self.other_radio):

            if self.user_radio.isChecked():
                # If users selected the radio button only
                if self.mode_list.selectedItems() == []:
                    self.current_mode[0] = ("u=")
                else:
                    self.current_mode[0] = (
                                            "u="
                                            + self.mode_list.
                                            currentItem().text())

            if self.group_radio.isChecked():
                if self.mode_list.selectedItems() == []:
                    self.current_mode[0] = ("g=")
                else:
                    self.current_mode[0] = (
                                            "g="
                                            + self.mode_list.
                                            currentItem().text())
            if self.other_radio.isChecked():

                if self.mode_list.selectedItems() == []:
                    self.current_mode[0] = ("o=")
                else:
                    self.current_mode[0] = (
                                            "o="
                                            + self.mode_list.
                                            currentItem().text())

            if self.current_mode not in self.cmd:
                self.cmd.append(self.current_mode)

        if self.pipe.isChecked():

            if (self.text_pipe.text() == ""
                    and self.current_pipe_args in self.cmd1):
                self.cmd1.remove(self.current_pipe_args)
                self.command_change.emit()
            else:
                self.current_pipe_args[0] = " " + self.text_pipe.text()
                if self.current_pipe_args not in self.cmd1:
                    self.cmd1.append(self.current_pipe_args)

        self.command_change.emit()

    def Show_File_Change(self):
        """
            Adds the selected files to cmd.

                :attr:`.command_change` will emit a signal at 
                the end of this method
                indicating that the chosen files have changed.
        """

        if len(self.shrt_list.selectedItems()) > 2:
            return

        if self.files == [] and self.files in self.cmd:
            self.cmd.remove(self.files)
            self.command_change.emit()

        if self.files not in self.cmd:
            self.cmd.append(self.files)

        if self.man_files == [] and self.man_files in self.cmd:
            self.cmd.remove(self.man_files)
            self.command_change.emit()

        if self.man_files not in self.cmd:
            self.cmd.append(self.man_files)

        if self.pipe.isChecked():

            if self.pipe_files == [] and self.pipe_files in self.cmd1:
                self.cmd1.remove(self.pipe_files)
                self.command_change.emit()

            if self.pipe_files not in self.cmd1:
                self.cmd1.append(self.pipe_files)

            if self.man_pipe_files == [] and self.man_pipe_files in self.cmd1:
                self.cmd1.remove(self.man_pipe_files)
                self.command_change.emit()

            if self.man_pipe_files not in self.cmd1:
                self.cmd1.append(self.man_pipe_files)

        self.command_change.emit()

    def Gen_Mode_Tooltip(self, mode):
        """Generates ToolTip for mode List.

        Args:
            mode (:obj:`str`): Mode to genrate its ToolTIp.

        Returns:
            :obj:`str` : Generated ToolTip
        """        
      

        tip = ""
        if mode[0] == "r":
            tip = tip + " read allowed"
        else:
            tip = tip + " no read "

        if mode[1] == "w":
            tip = tip + " write allowed "
        else:
            tip = tip + " no write"

        if mode[2] == "x":
            tip = tip + " execution allowed "
        else:
            tip = tip + " no execution "

        return tip

    def Gen_Format_List(self, LIST, items):
        """Generates Given List according to items.

        Args:
            LIST (:obj:`QListWidget`): UI List to add ``items`` and generate
                their ToolTips.
            items (:obj:`dict`): Dictionary that containts the items and 
                their ToolTips.  The dict must be formated {(``str``: item name) : (``str``:ToolTip)}
        """        
  
        LIST.clear()
        for key in items:
            item = QListWidgetItem(key)
            item.setTextAlignment(Qt.AlignCenter)
            LIST.addItem(item)
            item.setToolTip(items[key])

    def Hide_Man_Widgets(self, state, widgets):
        """Hides Mandatory Options widgets.

        Args:
            state (:obj:`bool`): ``True``  hides widgets, 
                ``False`` displays widgets
            widgets (:obj:`str`): widgets  have the string values ``NORMAL`` | ``PIPE``

                ``NORMAL`` hides normal (not piped) widgets,
                ``PIPE`` hides piped widgets.
        """        
    
        args_sheet_def = """
                                QStackedWidget{
                                background-color: rgba(191, 64, 64, 0);
                                                }
                                """
        args_sheet_nodef = """
                                QStackedWidget{
                                background-color: rgba(191, 64, 64, 0);
                                border-style: solid;
                                border-width: 1px;
                                border-color:red;
                                                }
                                """
        if widgets == "NORMAL":
            if state is True:
                self.man_1.hide()
                self.stacked_args.setCurrentIndex(0)
                self.fwd_button.hide()
                self.bck_button.hide()
                #self.stacked_args.widget(1).hide()
                self.notsupp.hide()
                #self.notsupp_pipe.hide()
                self.man_file.hide()
                #self.man_pipe_file.hide()
                self.man_text.hide()
                self.man_text_pipe.hide()
                self.format_list.hide()
                #self.format_list_pipe.hide()
                self.stacked_args.setStyleSheet(args_sheet_def)
                # State that there are no arguments
                self.args.show()
            else:
                #self.stacked_args.widget(1).show()
                self.fwd_button.show()
                self.bck_button.show()
                self.stacked_args.setStyleSheet(args_sheet_nodef)
        if widgets == "PIPE":
            if state is True:
                self.man_2.hide()
                self.stacked_args.setCurrentIndex(0)
                self.fwd_button.hide()
                self.bck_button.hide()
                self.notsupp_pipe.hide()
                self.man_pipe_file.hide()
                self.man_text_pipe.hide()
                self.format_list_pipe.hide()
            else:
                self.fwd_button.show()
                self.bck_button.show()
                self.stacked_args.setStyleSheet(args_sheet_nodef)

    def Hide_Arguments_Widgets(self):
        """
            Hides Arguments Widgets.
        """
        self.args.hide()
        self.fwd_button.hide()
        self.file_open_button.hide()
        self.pipe_file.hide()
        self.label_text_type.hide()
        self.text_option.hide()
        self.text_pipe.hide()
        self.piped_list.hide()
        self.mode_frame.hide()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = GNU_Logic(None)
    ui.show()
    sys.exit(app.exec_())
