import argparse
import os
from typing import Sequence

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


def create_cpp_class(
    cpp_parser: argparse.ArgumentParser, args_partial: Sequence[str]
):
    """
    This is the main function of the cpp_tools script.

    Args:
        cpp_parser (argparse.ArgumentParser): _description_
    """
    cpp_parser.add_argument("class_name", type=str)
    args = cpp_parser.parse_args(args_partial)

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


def main():
    """
    This is the main function of the script.
    """
    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    cpp_parser = subparsers.add_parser("create_cpp_class")
    cpp_parser.set_defaults(func=create_cpp_class)

    args, args_partial = parser.parse_known_args()

    if "func" not in args:
        parser.print_help()
        return
    args.func(cpp_parser, args_partial)  # pylint: disable=no-member


if "__main__" == __name__:
    main()
