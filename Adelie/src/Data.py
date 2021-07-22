""" 
    This module is the Data module for the :mod:`GNU_Logic`. 
    It contains the supported arguments ToolTips and mandatory options.
    
    Attributes:
        Arg_Hints (dict): Dictionary that contains the description and tooltips
            for arguments or mandatory options.
        types (dict): Dictionary that contains all the supported GNU Core Utilities
            arguments.
        MIV (list): List that contains the mandatory options supported in the 
            current version of Adelie.    
        FMT_Lines (list): List that contains the ToolTips for the lines
            ``format`` mandatory options.
        FMT_Date (dict):  Dictionary   that contains the ToolTips for the Date
            ``format`` mandatory options. 
        FMT_Files (dict): ist that contains the ToolTips for the files
            ``format`` mandatory options.
"""

import sys


Arg_Hints = {
            "OWNER": "User who owns file",
            "SUFFIX": "File Extension",
            "GROUP": "A group is a collection of users",
            "STRING": "Sequence of characters (text)",
            "USERNAME": "Username... check whomai",
            "PREFIX": "A fix to be added at the begging of a file",
            "PATTERN": "A pattern can be an interger that specifies"
                        + "  line number or a regular expression",
            "Duration": "Floating pint number use (s) for seconds m for minuts"
                        + "(h) for hours and (d) for days",
            "WIDTH": "Number of columns",
            "NUMBER": "Digit",
            "FILE": "Specify a file/s",
            "RFILE": "Specify a file/s",
            "FILE1": "Specify a file/s",
            "FILE2": "Specify a file/s",
            "DIRECTORY": "Specify Folder/Directory",
            "F": "Specify a file",
            "INPUT": "Input from a file",
            "NAME": "File name",
            "SOURCE": "File or Directory as a source",
            "DEST": "File or a Directory as a destination",
            "SIZE": "An integer and optional unit (10K). Units are "
                    + "K,M,G,T,P,E,Z,Y",
            "LIST": "One range, or many ranges separated by commas",
            "STR": "Sequence of characters (text)",
            "FORMAT": "Specify how the output is presented",
            "NUM": "Digit",
            "MODE": "Permission",
            "printf": "Use printf style floating-point format",
            "format_date": "Date format",
            "VARIABLE": "Environment Variable",
            "N": "List or a digit",
            "USER": "Username",
            "LAST": "Sequence of digits "
}
types = {
            "Path": ["FILE", "NAME", "FILE1", "FILE2", "SOURCE", "DEST",
                     "DIRECTORY", "INPUT", "F"],
            "Text": ["OWNER", "SUFFIX", "GROUP", "STRING", "USERNAME",
                     "PREFIX", "PATTERN", "VARIABLE", "USER", "NAME"],
            "Digit": ["DURATION", "WIDTH", "NUMBER", "LAST"],
            "Mode": ['rwx', 'rw-', 'r-x', 'r--', '-wx',
                     '-w-', '--x', '---'],
            }
# MAN_IMPLEMENTED_IN_THIS_VERSION

MIV = ["FILE", "LIST", "SIZE", "RFILE",
       "FORMAT", "MODE", "STR", "STRING", "NUM", "NUMBER", "N"]


# nl
FMT_Lines = {"ln": "left justified, no leading zeros",
                "rn": "right justified, no leading zeros",
                "rz": "right justified, leading zeros"}

FMT_Date = {
  "%%a": "literal %",
  "%a":   "locale's abbreviated weekday name (e.g., Sun)",
  "%A":   "locale's full weekday name (e.g., Sunday)",
  "%b":   "locale's abbreviated month name (e.g., Jan)",
  "%B":   "locale's full month name (e.g., January)",
  "%c":   "locale's date and time (e.g., Thu Mar  3 23:05:25 2005)",
  "%C":   "century; like %Y, except omit last two digits (e.g., 20)",
  "%d":   "day of month (e.g., 01)",
  "%D":   "date; same as %m/%d/%y",
  "%e":   "day of month, space padded; same as %_d",
  "%F":   "full date; same as %Y-%m-%d",
  "%g:":   "last two digits of year of ISO week number (see %G)",
  "%G":   "year of ISO week number (see %V); normally useful only with %V",
  "%h":   "same as %b",
  "%H":   "hour (00..23)",
  "%I":   "hour (01..12)",
  "%j":   "day of year (001..366)",
  "%k":   "hour, space padded ( 0..23); same as %_H",
  "%l":   "hour, space padded ( 1..12); same as %_I",
  "%m":   "month (01..12)",
  "%M":   "minute (00..59)",
  "%n":   "a newline",
  "%N":   "nanoseconds (000000000..999999999)",
  "%p":   "locale's equivalent of either AM or PM; blank if not known",
  "%P":   "like %p, but lower case",
  "%q":   "quarter of year (1..4)",
  "%r":   "locale's 12-hour clock time (e.g., 11:11:04 PM)",
  "%R":   "24-hour hour and minute; same as %H:%M",
  "%s":   "seconds since 1970-01-01 00:00:00 UTC",
  "%S":   "second (00..60)",
  "%t":   "a tab",
  "%T":   "time; same as %H:%M:%S",
  "%u":   "day of week (1..7); 1 is Monday",
  "%U":   "week number of year, with Sunday as first day of week (00..53)",
  "%V":   "ISO week number, with Monday as first day of week (01..53)",
  "%w":   "day of week (0..6); 0 is Sunday",
  "%W":   "week number of year, with Monday as first day of week (00..53)",
  "%x":   "locale's date representation (e.g., 12/31/99)",
  "%X":   "locale's time representation (e.g., 23:13:48)",
  "%y":   "last two digits of year (00..99)",
  "%Y":   "year",
  "%z":   "+hhmm numeric time zone (e.g., -0400)",
  "%:z":  "+hh:mm numeric time zone (e.g., -04:00)",
  "%::z":  "+hh:mm:ss numeric time zone (e.g., -04:00:00)",
  "%:::z":  "numeric time zone with : to necessary precision (e.g., -04, +05:30)",
  "%Z":   "alphabetic time zone abbreviation (e.g., EDT)"
}
FMT_Files = {
  "%a":   "access rights in octal (note '#' and '0' printf flags)",
  "%A":   "access rights in human readable form",
  "%b":   "number of blocks allocated (see %B)",
  "%B":   "the size in bytes of each block reported by %b",
  "%C":   "SELinux security context string",
  "%d":   "device number in decimal",
  "%D":   "device number in hex",
  "%f":   "raw mode in hex",
  "%F":   "file type",
  "%g":   "group ID of owner",
  "%G":   "group name of owner",
  "%h":   "number of hard links",
  "%i":   "inode number",
  "%m":   "mount point",
  "%n":   "file name",
  "%N":   "quoted file name with dereference if symbolic link",
  "%o":   "optimal I/O transfer size hint",
  "%s":   "total size, in bytes",
  "%t":   "major device type in hex, for character/block device special files",
  "%T":   "minor device type in hex, for character/block device special files",
  "%u":   "user ID of owner",
  "%U":   "user name of owner",
  "%w":   "time of file birth, human-readable; - if unknown",
  "%W":   "time of file birth, seconds since Epoch; 0 if unknown",
  "%x":   "time of last access, human-readable",
  "%X":   "time of last access, seconds since Epoch",
  "%y":   "time of last data modification, human-readable",
  "%Y":   "time of last data modification, seconds since Epoch",
  "%z":   "time of last status change, human-readable",
  "%Z":   "time of last status change, seconds since Epoch",
}

