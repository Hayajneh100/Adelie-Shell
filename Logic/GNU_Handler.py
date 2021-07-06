import re
import subprocess
import Data
import sys
from psutil._common import bytes2human
import time


class GNU_Handler():
   

    """
        Uses the GNU coreutils Documentation to find options, arguments,
        description.

        Handles the GNU Manpages part of this application
        Uses Regular Expressions to find the options, descriptions,
        arguments of the toolusing the tools ``--help`` option
        finds all GNU coreutils installed on the host system
        finds the description of the tools by their names and vice versa
        finds the options of the tools by their names and vice versa
        invokes the help option of the tools
        finds the arguments used by the tools.

    Attributes:

        gnu_tool (:obj:`list` of ``str``): Contains the GNU Core Utils 
            installed on the system.

        ToolName_ToolDescription (:obj:`dict`): A dictionary that contains
            the tool name and its description

        tool_Options(:obj:`dict`): Contains Tool name and its options

        Name_OptionDescription_Option (:obj:`dict`): Contains the Tool name 
        options description and options. 
        
        types (:obj:`dict`) : Contains the supported arguments taken from 
            :mod:`.Data`
    """

    types = Data.types
    gnu_tools = []
    ToolName_ToolDescription = {}
    tool_Options = {}
    Name_OptionDescription_Option = {}

    def __init__(self):
        self.Create_GNU_Tools()
        self.Create_GNU_Descriptions()

    def Get_Tool_Help(self, tool_name):
        """Returns the result of ``--help`` of a tool given as a parameter

        Args:
            tool_name (:obj:`str`): Tool's name

        Returns:
            :obj:`str`: The output of the tool's ``--help``
        """        
    
        res = subprocess.check_output((tool_name, "--help"),
                                      universal_newlines=True)
        return res

    def Create_GNU_Tools(self):
        """ 
            Finds GNU Coreutils Installed on the System.
        """

        installed_utils = []
        res = subprocess.check_output(("dpkg", "-s", "coreutils"),
                                      universal_newlines=True)
        regex = r"Specifically, this package includes:\n ([\w \w+\n|*]+\n)"
        srch = re.search(regex, res)
        installed_utils = srch[1].split()
        # false returns exit code of 1
        installed_utils.remove('false')
        installed_utils.remove('sha*sum')
        self.gnu_tools = installed_utils

    def Get_GNU_Tools(self):
        """Returns a list of all GNU Coreutils installed on the system.

        Returns:
            :obj:`list` of ``str``: List of all GNU Core Utils installed.
                
        """        
  
        return self.gnu_tools

    def Create_GNU_Descriptions(self):
        """
            Finds and Creates Description of GNU Coreutils.
            using each tool ``--help``.
        """
        for tool in self.gnu_tools:
            res = self.Get_Tool_Help(tool)
            # Corner Case 1
            if tool == "expr":
                # --help --version writter under or (not Description)
                str1 = "Print the value of EXPRESSION to standard output"
                self.ToolName_ToolDescription["expr"] = str1
                # Added Item with its Description
                # Do not reach REGEX code (NoneType)
                continue
            # Corner Case 2
            if tool == "pinky":
                # Description written after arguments
                s = "A lightweight 'finger' program;  print user information"
                self.ToolName_ToolDescription["pinky"] = s
                # Added Item with its Description
                # Do not reach REGEX code (NoneType)
                self.Find_Options(tool)
                continue
            # Corner Case 3
            if tool == "flock":
                # No or after options
                string = "Manage file locks from shell scripts"
                self.ToolName_ToolDescription["flock"] = string
                # Do not reach REGEX code (NoneType)
                continue
            # Corner Case 4
            if tool == "test":
                # Arguments can be any string --help will not work
                test = ("Used as part of the conditional" +
                        " execution of shell commands")
                self.ToolName_ToolDescription["test"] = test
                # Do not reach REGEX code (NoneType)
                continue
            regex = "Usage:(.*\n\s+or.+)+\n+(.*)|Usage:.*\n*(([A-Z]).*)"
            srch = re.search(regex, res)
            if srch[2] is not None:
                self.ToolName_ToolDescription[tool] = srch[2]

            if srch[3] is not None:
                self.ToolName_ToolDescription[tool] = srch[3]
            self.Find_Options(tool)

    def Get_Tool_Description(self, tool_name):
        """Returns the description of the tool given as a parameter

        Args:
            tool_name (:obj:`str`): Tool's name

        Returns:
            :obj:`str`: Tool's description.
        """        
        
        return self.ToolName_ToolDescription[tool_name]

    def Get_Tool_Name_From_Description(self, desc):
        """Returns the name of the tool using its description given as a parameter.

        Args:
            desc (:obj:`str`): Tool's description

        Returns:
            :obj:`str` : Tool's name
        """        

        for tool in self.ToolName_ToolDescription:
            if self.ToolName_ToolDescription[tool] == desc:
                return tool

    def Find_Options(self, tool_name):
        """Finds the Options of a tool given as a parameter.

        Args:
            tool_name (:obj:`str`): Tool's Name.

        """

        res = self.Get_Tool_Help(tool_name)
        srch = re.findall(r"\n\s+-([A-Za-z])[,|\s]", res)
        self.tool_Options[tool_name] = srch
        tmp_optDesc_opt = {}
        for option in srch:
            REGEX = "-" + option + ",\s\S+\s+(.*)"
            rslt = re.search(REGEX, res)
            if rslt is not None:
                # Record result in a dictionary as
                #  {"Name":{"Option Description:Option"}}
                # {"Option Description:Option"}
                tmp_optDesc_opt[rslt[1]] = option
        # Assign a copy of temp dict
        self.Name_OptionDescription_Option[tool_name] = tmp_optDesc_opt.copy()
        tmp_optDesc_opt.clear()

    def Get_Tool_Options_Descriptions(self, tool_name):
        """Returns the Description of the options that belong to a tool given as a parameter.

        Args:
            tool_name (:obj:`str`): Tool's Name.

        Returns:
            :obj:`list` of ``str``: Descriptions of the tools options.
        """        
       
        option_description_list = []
        for opt_desc in self.Name_OptionDescription_Option[tool_name]:
            option_description_list.append(opt_desc)
        return option_description_list

    def Get_Tool_Option_From_Description(self, option_description, tool_name):
        """Returns the Option of a using the option description.

        Args:
            option_description (:obj:`str`): Option's description
            tool_name (:obj:`str`): Tool's Name.

        Returns:
            :obj:`str`: Option
        """        

        for optDesc in self.Name_OptionDescription_Option[tool_name]:
            if option_description == optDesc:
                return self.Name_OptionDescription_Option[tool_name][optDesc]

    def Get_Option_Description(self, tool_name, option):
        """Returns option description using tool's name and option.

        Args:
            tool_name (:obj:`str`): Tool's Name.
            option (:obj:`str`): Option to find its description.

        Returns:
            :obj:`str`: Option's description
        Note:
            uses REGEX =rf"  -{option},\s\S+\s+(.*)|  -{option}\s+(.*)" 
        """        
   
        tool_help = self.Get_Tool_Help(tool_name)
        REGEX = rf"  -{option},\s\S+\s+(.*)|  -{option}\s+(.*)"
        rslt = re.findall(REGEX, tool_help)
        if rslt[0][0] != "":
            return rslt[0][0]
        if rslt[0][1] != "":
            return rslt[0][1]
       
    def Get_Tool_Options(self, tool_name):
        """Returns the options of the tool name given as an argument.

        Args:
            tool_name (:obj:`str`): Tool's Name.

        Returns:
            :obj:`list` of ``str``: List of the Tool's Options.
        """        

        return self.tool_Options[tool_name]

    def Get_Tool_Argument(self, tool_name):
        """ Returns the Arguments used by a tool name given as a parameter

        Args:
            tool_name (:obj:`str`): Tool's Name.

        Returns:
            :obj:`list` of ``str``: Tool's Arguments.

        Note:
            Uses the following regex 
            regex = r"\s\[([A-Z]+)\]|([A-Z]+)\.{3}|\.{3}\s([A-Z]+)\d*\s"
        """        

        args_found = []
        # args - supported args
        args = []
        res = self.Get_Tool_Help(tool_name)
        # Returns a list with all usages
        regex = r"\s\[([A-Z]+)\]|([A-Z]+)\.{3}|\.{3}\s([A-Z]+)\d*\s"
        srch = re.findall(regex, res)
        
        # findall returns submatches
        # if capture groups are used it will return None if capture group
        # does not give a result
        for group in srch:
            args_found.extend(list(filter(None, group)))
        for arg in args_found:
            # Remove option from args
            if arg == "OPTION":
                continue
            if arg in self.types["Path"]:
                args.append(arg)

            if arg in self.types["Text"]:
                args.append(arg)

            if arg in self.types["Digit"]:
                args.append(arg)

        return args

    def Get_Man_Option(self, tool_name, option):
        """ Returns the Man. Options for an option, returns None if none.

        Args:
            tool_name (:obj:`str`): Tool's Name.
            option (:obj:`str`): Option to find its Mandatory option.

        Returns:
            :obj:`str`: Mandatory Option
        Note:
            uses regex regex = ("-" + option + ",.*=(\w+)")

        """        

        # stat -c issue
        tool_help = self.Get_Tool_Help(tool_name)
        if tool_name == "head" and option == "n":
            return "NUM"
        regex = ("-" + option + ",.*=(\w+)")
        res = re.search(regex, tool_help)
        print(res)
        if res is not None:
            return res[1]

    def Has_Options(self, tool_name):
        """Returns True if the tool have options

        Args:
            tool_name (:obj:`str`): Tool's Name.

        Returns:
            :obj:`bool`: Returns ``True`` if the tool has options,
            returns ``False`` otherwise.
        """        
       
        if (self.Get_Tool_Options(tool_name) == []
                or self.Get_Tool_Options(tool_name) is None):
            return False
        else:
            return True

    def Has_Arguments(self, tool_name):
        """Returns True if the tool have arguments.

        Args:
            tool_name (:obj:`str`): Tool's Name.

        Returns:
           :obj:`bool`: Returns ``True`` if the tool has Arguments, 
           returns ``False`` otherwise.
        """        
    
        # Returns a list with all usages
        # line in list or before (,)
        args = self.Get_Tool_Argument(tool_name)
        if args == []:
            return False
        else:
            return True

    def Has_Supported_ManOptions(self, tool_name, option):
        """Returns True if the option has a supported Mandatory Option

        Args:
            tool_name (:obj:`str`): Tool's Name.
            option (:obj:`str`): Option to find its Mandatory option.

        Returns:
            :obj:`bool`: Returns ``True`` if the options has Mandatory Options, 
            returns ``False`` otherwise.
        """        
        manopt = self.Get_Man_Option(tool_name, option)
        
        if tool_name == "stat" and option == "c":
            return True

        if manopt is None:
            return False
        else:
            return True

    def No_Options_Arguments(self, tool_name):
        """Returns True if tool has options and arguments.

        Args:
            tool_name (:obj:`str`): Tool's Name.

        Returns:
         
            :obj:`bool`: returns ``True`` if the tool has no options 
            and arguments, 
            returns ``False`` otherwise.
        """        
   

        if (self.Has_Arguments(tool_name) is False
                and self.Has_Options(tool_name) is False):
            return True
        else:
            return False

    def Get_Supported_Types(self):
        """Returns the types supported in the :mod:`.Data` module.

        Returns:
            :obj:`list` of ``str``: Supported Arguments.
        """        
        return self.types

    

# https://goshippo.com/blog/measure-real-size-any-python-object/

def get_size(obj, seen=None):
        """Recursively finds size of objects"""
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0
        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([get_size(v, seen) for v in obj.values()])
            size += sum([get_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__dict__'):
            size += get_size(obj.__dict__, seen)
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([get_size(i, seen) for i in obj])
        return size
if __name__== "__main__":

    gn = GNU_Handler()
    size = bytes2human(get_size( gn.Name_OptionDescription_Option))
    print(size)
