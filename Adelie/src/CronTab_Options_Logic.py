from PyQt5 import QtCore, QtGui, QtWidgets, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, Qt, QTime
from PyQt5 import uic
from crontab import CronTab
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
GUI_DIR = os.path.join(CURRENT_DIR, "GUI")
ui_filename = os.path.join(GUI_DIR, "crontab_options.ui")
baseUIClass, baseUIWidget = uic.loadUiType(ui_filename)


class CronTab_Options_Logic(baseUIClass, baseUIWidget):
    """
        This class handles the logic for the ``crontab`` options menu.

        Using this class users will be able to schedule cron process
        and network options in Adelie. For example, :class:`Ping_UI_Logic` and
        :class:`netstat_Logic`.


        Attributes:
            cron (:class:`CronTab`):  Writes and modifies ``Crontabs``.

            minute (:obj:`str`): Current job minute (``cron`` format)
            hour (:obj:`str`): Current job hour (``cron`` format)
            day (:obj:`str`): Current job day in month (``cron`` format)
            month (:obj:`str`): Current job month (``cron`` format)
            dayOfWeek (:obj:`str`): Current day of week for the job 0-6 
                (``cron`` format)

        Important:
            The time attributes are updated when any time value is changed
            in the GUI.

    """

    cron = CronTab(user=True)
    minute = ""
    hour = ""
    day = ""
    month = ""
    dayOfWeek = ""

    def __init__(self, parent=None):

        super(CronTab_Options_Logic, self).__init__(parent)

        self.setupUi(self)
        self.time.setTime(QTime.currentTime())
        self.stackedWidget.setCurrentIndex(0)
        self.view_tab_button.clicked.connect(self.Show_Table)
        self.ok_button.clicked.connect(
                                        lambda: self.close()
                                       )
        self.save_button.clicked.connect(self.Set_Job_Time)
        self.sched_menu_button.clicked.connect(
        lambda:self.stackedWidget.setCurrentIndex(0)
        )
        self.remove_job_button.clicked.connect(self.Remove_Job)
        self.minute_enable.stateChanged.connect(self.Set_Job_Time)
        self.hour_enable.stateChanged.connect(self.Set_Job_Time)
        self.allmonth_enable.stateChanged.connect(self.Set_Job_Time)
        self.month_enable.stateChanged.connect(self.Set_Job_Time)
        self.day_enable.stateChanged.connect(self.Set_Job_Time)
        self.calendar.selectionChanged.connect(self.Set_Job_Time)
        self.time.timeChanged.connect(self.Set_Job_Time)
        self.clear_history_button.clicked.connect(
        lambda:self.command_history.clear()
        )
        self.Set_Job_Time()

        header = self.cron_table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

    def Show_Table(self):
        """
            Updates the GUI table and re-creates it by executing the method
            :meth:`Create_Tab`.
        """

        self.cron = CronTab(user=True)
        self.stackedWidget.setCurrentIndex(1)
        self.Create_Tab()

    def Create_Tab(self):
        """
            Build crontab table.

            Table is built from reading the ``cron`` scheduler :attr:`cron`
        """

        self.cron_table.setRowCount(0)
        for job in self.cron:
            row_postion = self.cron_table.rowCount()
            self.cron_table.insertRow(row_postion)
            if "#" in job:
                continue
            else:
                slice = str(job.slices)
                command = str(job.command)
                Item = QtWidgets.QTableWidgetItem(slice)
                Item_1 = QtWidgets.QTableWidgetItem(command)
                Item.setTextAlignment(Qt.AlignCenter)
                Item_1.setTextAlignment(Qt.AlignCenter)
                self.cron_table.setItem(row_postion, 0, Item)
                self.cron_table.setItem(row_postion, 1, Item_1)

        self.command_history.append("crontab -l")

    def Remove_Job(self):
        """
            Remove current selected job.
        """

        current_row = self.cron_table.currentRow()
        prd = self.cron_table.item(current_row, 0).text()
        cmd = self.cron_table.item(current_row, 1).text()
        for job in self.cron:
            if cmd == job.command and prd == job.slices:
                self.cron.remove(job)

        self.cron.write()
        self.Show_Table()

    def Set_Job_Time(self):
        """
            Sets the `cron` time format for the job.

            Important:
                If user changes date or any value related to the time format
                the cron time format will be automatically saved. This method
                only re-saves it.
        """

        if self.cron is None:
            return

        date = self.calendar.selectedDate()
        time = self.time.time()

        self.minute = str(time.minute())
        if self.minute_enable.isChecked():
            self.minute = "*"
        cron_time = self.minute

        self.hour = str(time.hour())
        if self.hour_enable.isChecked():
            self.hour = "*"
        cron_time = cron_time + self.hour

        self.day = str(date.day())
        if self.allmonth_enable.isChecked():
            self.day = "*"
        cron_time = cron_time + self.day

        self.month = str(date.month())
        if self.month_enable.isChecked():
            self.month = "*"

        cron_time = cron_time + self.month

        self.dayOfWeek = str(date.dayOfWeek())
        if self.day_enable.isChecked():
            self.dayOfWeek = "*"

        cron_time = cron_time + self.dayOfWeek

        self.cron_time.setText(
                                "Cron Time: " + self.minute + " "
                                + self.hour + " "
                                + self.day + " " + self.month
                                + " " + self.dayOfWeek
                                )

    def Start_Job(self, command):

        new_job = self.cron.new(command)
        new_job.setall(
                        self.minute, self.hour,
                        self.day, self.month, self.dayOfWeek
                        )
        time = [
                self.minute,
                self.hour,
                self.day,
                self.month,
                self.dayOfWeek
                ]
        self.cron.write()
        self.Add_Job_To_Table(command, time)

    def Add_Job_To_Table(self, command, time):
        """Adds scheduled job to command history.

        Args:
            command (:obj:`str`): Linux Command to be scheduled.
            time (:obj:`str`): Job ``cron`` time format.

        Note:
            The job is not added to ``crontab`` using this method,
            The job is added by executing :meth:`Show_Table` which in 
            returns exectues  :meth:`Create_Tab`.
        """        
      
        self.command_history.append("crontab -e")
        self.command_history.append(" ".join(time) + " " + command)
        self.Show_Table()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ui = CronTab_Options_Logic(None)
    ui.show()
    sys.exit(app.exec_())
