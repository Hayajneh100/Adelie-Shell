.. Adelie documentation master file, created by
   sphinx-quickstart on Wed May 12 16:15:43 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Adélie's documentation!
***********************************
Adelie GNU/Linux Terminal Assistant
===================================

Adelie is a tool created to provide support for novice Linux terminal
users. It assists users by enabling them to execute different Linux
commands through an easy to use and simple GUI. Adelie is **not** a
replacement for the esteemed shell, it is only a tool designed for
introducing novice users to the Linux command line. Adelie introduces
common Linux commands to the user, these commands include networking
commands, common adminstration commands, and Cron.

+----------------------+-----------------------------------------+
| Package              | Example                                 |
+======================+=========================================+
| GNU Core Utilities   | ``cat``, ``chmod``, and ``ls``          |
+----------------------+-----------------------------------------+
| Network Tools        | Ping, ifconfig, iwconfig, and netstat   |
+----------------------+-----------------------------------------+
| Schedulers           | Cron                                    |
+----------------------+-----------------------------------------+

Installation
------------

To install Adelie on your system execute the following commands

.. code:: bash

    git clone https://github.com/Hayajneh100/Adelie-Shell.git
    cd ./Adelie-shell
    pyinstaller main.spec

Then you can run Adelie using

.. code:: bash

    ./dist/Adelie/Adelie

Incase of any errors try installing and running Adelie from the source
code directly. Follow these steps:

.. code:: bash

    1. pip3 install -r requirements.txt 
    2. python3 Adelie/src/Adelie.py


.. toctree::
   :maxdepth: 2
   :caption: Contents
   

   modules
   


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
