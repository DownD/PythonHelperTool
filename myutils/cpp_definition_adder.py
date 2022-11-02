import argparse
import os
import re
from typing import Sequence


class CppFunction:
    def __init__(
        self,
        return_type: str,
        function_name: str,
        arguments: str,
        class_name: str,
    ):
        self.return_type = return_type.strip()
        self.function_name = function_name.strip()
        self.arguments_str = arguments.strip()
        self.class_name = class_name.strip()

        self.arguments_types = []

        # Parse arguments
        for token in self.arguments_str.split(","):
            if token.strip() == "":
                continue

            variables = token.split(" ")
            if len(variables) != 2:
                raise ValueError(
                    f"Invalid argument: {token} in function {self.class_name}::{function_name}"
                )

            self.arguments_types.append(variables[0])

    def compare(self, other: "CppFunction") -> bool:
        return (
            self.return_type == other.return_type
            and self.function_name == other.function_name
            and self.arguments_types == other.arguments_types
            and self.class_name == other.class_name
        )

    def __eq__(self, __o: object) -> bool:

        if not isinstance(__o, CppFunction):
            return False

        return self.compare(__o)

    def __hash__(self) -> int:
        return hash(
            (
                self.return_type,
                self.function_name,
                self.arguments_types,
                self.class_name,
            )
        )


def compare_functions(
    func1: set[CppFunction],
    func2: set[CppFunction],
) -> set[CppFunction]:
    """
    Compares two class functions and returns the functions func1 not found in func2

    Args:
        func1 (set[CppFunction]): The first list of functions to compare.
        func2 (set[CppFunction]): The second list function to compare.

    Returns:
        set[CppFunction]: Returns the functions not found in func2.
    """

    return func1 - func2


def get_functions_from_header(
    file_path: str,
) -> set[CppFunction]:
    """
    This function extracts the function names from a header file.

    Args:
        file_path (str): The path for the header file.

    Returns:
        set[CppFunction]: A set conatining the functions found in the header file.
    """
    file_data: str = ""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Read file and skip comments
            if line.startswith("//"):
                continue
            file_data += line

    # Remove newlines
    file_data = file_data.replace("\r", "").replace("\n", "")

    # Get classes and functions using regex
    class_regex = r"class\s+(\w+)\s*{([^}]+)}"
    function_regex = r"(\w+)\s+(\w+)\s*\(([^)]*)\)"

    # Set with all class functions
    cpp_functions: set[CppFunction] = set()

    lst_classes = re.findall(class_regex, file_data)

    for class_name, class_content in lst_classes:
        return_type, func_name, arguments = re.findall(
            function_regex, class_content
        )
        cpp_functions.add(
            CppFunction(return_type, func_name, arguments, class_name)
        )

    return cpp_functions


def get_functions_definitions_from_cpp(
    file_path: str,
) -> set[CppFunction]:
    """
    This function extracts the class definitions from the cpp file using regex.

    Args:
        file_path (str): The path of the cpp file

    Returns:
        set[CppFunction]: A set containing the functions found in the cpp file.
    """

    file_data: str = ""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Skip comments
            if line.startswith("//"):
                continue

            file_data += line.strip()

    # Remove newlines
    file_data = file_data.replace("\r", "").replace("\n", "")

    # Get classes and functions using regex
    regex_function = r"(\w+)\s+(\w+)::(\w+)\s*\(([^)]*)\)"
    lst_functions = re.findall(regex_function, file_data)

    functions_set = {
        CppFunction(return_type, func_name, arguments, class_name)
        for return_type, class_name, func_name, arguments in lst_functions
    }

    return functions_set


def add_class_definitions_to_cpp(
    cpp_parser: argparse.ArgumentParser, args_partial: Sequence[str]
):
    """
    This is the main function of the cpp_tools script.

    Args:
        cpp_parser (argparse.ArgumentParser): _description_
        args_partial (Sequence[str]): _description_
    """
    cpp_parser.add_argument("-h", "--header_name", type=str, optional=True)
    cpp_parser.add_argument("-p", "--path", type=str, default="", const="")
    args = cpp_parser.parse_args(args_partial)

    lst_headers: list[tuple[str, str]] = []

    if "header_name" in args:
        header_file = args.header_name + ".h"
        cpp_file = args.header_name + ".cpp"
        if not os.path.isfile(header_file):
            print("Header file", header_file, "not found. Aborting...")
            return

        if not os.path.isfile(cpp_file):
            print("Cpp file", cpp_file, "not found. Aborting...")
            return

        lst_headers.append((header_file, cpp_file))
    else:

        files = set(os.listdir(args.path))

        # Search for headers in the path
        for file in files:
            if file.endswith(".h"):
                cpp_file = file.replace(".h", ".cpp")

                if cpp_file not in files:
                    print(
                        "No cpp file found corresponding to",
                        file,
                        ". Ignoring.",
                    )
                    continue

                lst_headers.append((file, cpp_file))

    print("Found", len(lst_headers), "header files to scan")
