# Adelie GNU/Linux Terminal Assistant

Adelie is a tool created to provide support for novice Linux terminal users.
It assists users by enabling them to execute different Linux commands through
an easy to use and simple GUI. Adelie is  **not** a replacement for
the esteemed shell, it is only a tool designed for introducing novice users
to the Linux command line.
Adelie introduces common Linux commands to the user, these commands include
networking commands, common adminstration commands, and Cron.  

| Package            | Example                                  |
| ------------------ | ---------------------------------------- |
| GNU Core Utilities | `cat`, `chmod`, and `ls`  (90+ commands) |
| Network Tools      | Ping, ifconfig, iwconfig, and netstat    |
| Schedulers         | Cron                                     |

## Installation

To install Adelie on your system execute the following commands

```bash
git clone https://github.com/Hayajneh100/Adelie-Shell.git
cd ./Adelie-shell
pyinstaller main.spec
```

Then you can run Adelie using

```bash
./dist/Adelie/Adelie
```

Incase of any errors try installing and running Adelie from the source code
directly. Follow these steps:

```bash
1. pip3 install -r requirements.txt 
2. python3 Adelie/src/Adelie.py
```

## Using the Tool

The following sections will go through simple use cases for the implemented
commands.

----

### GNU Core Utilities

The GNU Core Utilities commands UI will display all the available commands, then
the user can simply select the command to be executed.

![GitHub Logo](/docs/readme_pics/GNU_GUI.png)

| Component | Title            | Purpose                                                  |
| --------- | ---------------- | -------------------------------------------------------- |
| 1         | Command List     | Displays and selects commands                            |
| 2         | Command guide    | Informs users when commands have arguments or options    |
| 3         | Options' List    | Displays and selects commands' options                   |
| 4         | Arguments' Panel | Displays the arguments required for the commands         |
| 5         | Output Terminal  | The output of the executed commands is displayed here    |
| 6         | Command History  | Displays the history of executed commands                |
| 7         | Command Tracker  | Tracks the selected commands and their options/arguments |

Once the user hovers
over any command, option, or arguments the tool will display a
ToolTip extracted from the commands manpages. The ToolTip will describe
the command's purpose or the meaning of the options or arguments. For example,
for the commands displayed in the figure above the tool will show the
following ToolTips

| Option | ToolTip                                       |
| ------ | --------------------------------------------- |
| d      | Decode data                                   |
| i      | When decoding, ignore non-alphabet characters |
| w      | Wrap encoded lines after (cols) characters.   |

----

### Network Tools

Adelie implements four different network tools: ping, ifconfig, iwconfig,
and netstat. Adelie reads the output of these network tools and formats it
in an easy to read table. Users can click on the table cells to configure
the interfaces shown in the figure below. Because Adelie is an educational tool,
the reset button will reset the networking configurations to their default
settings. Unlike the GNU Core Utilities UI, the networks tools implement
specific common options and not all the options supported by the tools.
The figure below is for **ifconfig** commands. Make sure to explore the
rest of the commands!

![ifconfig_ui](/docs/readme_pics/ifconfig_UI.png)

| Component | Title           | Purpose                                                 |
| --------- | --------------- | ------------------------------------------------------- |
| 1         | Output Table    | Used for executing commands and displaying their output |
| 2         | Options Panel   | Check to select command's options                       |
| 3         | Buttons Panel   | Execute commands and clear the terminal                 |
| 4         | Command History | Displays the history of executed commands               |
| 5         | Output Terminal | The output of the executed commands is displayed here   |
| 6         | Cron Panel      | Schedule the command using Cron                         |

----

### Cron

Adelie enables users to schedule the network commands using an easy to use
GUI for the famous **Cron** daemon. Simply put, it writes Crontabs. The user
can simply select the required date from the calendar, choose time, or the
*every* mask, and Adelie will display the Cron time format.
Scheduling the network commands implemented in Adelie
has no real use but to introduce users to Cron, Crontabs, and the Cron time
format.

![ifconfig_ui](/docs/readme_pics/crontime_selection.png)

Follow these steps to schedule a command

1. Check all the options and fill the related data field.
2. Check the **Enable CronTab** checkbox.
3. Click on **CronTab Options** button.
4. Select time and date.
5. Save.
6. Execute the command.

Because Cron does not notify users if the command executed will cause an error,
step 6 is **required** to write the equivalent crontab.

## Docs Installation

Adelie's source code is documented and a sphinx generated documentation is
available. To generate the HTML documentation, execute the following command.

```bash
cd ./docs
make html
cd /build
```

Then open **index.html** file.
