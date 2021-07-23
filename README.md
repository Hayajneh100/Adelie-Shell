# Adelie GNU/Linux Terminal Assistant

## Table of Content

- [Adelie GNU/Linux Terminal Assistant](#adelie-gnulinux-terminal-assistant)
  - [Table of Content](#table-of-content)
  - [Introduction](#introduction)
  - [Installation](#installation)
  - [Using the Tool](#using-the-tool)
    - [GNU Core Utilities](#gnu-core-utilities)
    - [Network Tools](#network-tools)
    - [Cron](#cron)
  - [Source Code Documentation](#source-code-documentation)

## Introduction

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

Adelie displays common Linux command directly on its GUI. Then you can choose
the commands you can choose the commands you would like to execute.
Each time you execute a command, Adelie
will display the command output and show you the __formed__ command. Adelie's
goal is to let you choose your required options from a GUI and then it will
show you the equivalent Linux command.

### GNU Core Utilities

![GNU_GUI](/docs/readme_pics/GNU_GUI.gif)

Do not worry if you do not understand what the commands or options do! Adelie
will help you by displaying ToolTips that explain the purpose of these
commands.

![GNU_GUI_ToolTip](/docs/readme_pics/GNU_ToolTip.gif)

### Network Tools

You can also do network configurations using common Linux commands like
`ifconfig` or `iwconfig` using a simple and an easy to use GUI. 
And Adelie will display the equivalent Linux command.

![Ifconfig_GUI](/docs/readme_pics/Ifconfig.gif)

### Cron

Cron is a must know tool and its commands can be confusing sometimes.
Using Adelie, you can schedule the network commands through an easy to use
GUI. After you finish your configurations, Adelie will display the Cron time
format and the equivalent commands used.

![cron](/docs/readme_pics/cron.gif)

----

## Source Code Documentation

Adelie's source code is documented and a sphinx generated documentation is
available. To generate the HTML documentation, execute the following commands.

```bash
cd ./docs
make html
cd /build
```

Then open **index.html** file.
