import os
from argparse import ArgumentParser, Namespace

from myutils.script_interface import ScriptInterface

cpp_header_content = """

class <class_name> {
    public:
        <class_name>();
        ~<class_name>();
};
"""
cpp_source_file = """
#include "<class_name>.h"

<class_name>::<class_name>(){
}

<class_name>::~<class_name>() {
}

"""


class CreateCppClass(ScriptInterface):
    def __init__(self):
        super().__init__("create_cpp_class", "Create a cpp class")

    def add_subparser_args(self, parser: ArgumentParser):
        """
        This function serves to add arguments to the subparser.

        Args:
            parser (ArgumentParser): The subparser of the script
        """
        parser.add_argument("class_name", type=str)

    def __call__(self, args: Namespace):
        """
        This function is called when the script is launched.

        Args:
            parser (ArgumentParser): The parser of the script
            args_partial (list, optional): The arguments to parse. Defaults to None.
        """
        class_name: str = args.class_name

        # Enforce CamelCase
        class_name = class_name[0].capitalize() + class_name[1:]
        if "_" in class_name:
            class_name = class_name.replace("_", " ").title().replace(" ", "")

        # File names
        header_file = class_name + ".h"
        cpp_file = class_name + ".cpp"

        # Check if file already exists
        if os.path.isfile(cpp_file) or os.path.isfile(header_file):
            print("File already exists. Aborting...")
            return

        # Create Header file
        with open(header_file, "w", encoding="utf-8") as file:
            file.write(cpp_header_content.replace("<class_name>", class_name))

        print("Created header file: " + header_file)

        with open(cpp_file, "w", encoding="utf-8") as file:
            file.write(cpp_source_file.replace("<class_name>", class_name))

        print("Created cpp file: " + cpp_file)
        print("Files created successfully")
