import argparse
import logging
import os
import re
from typing import Sequence

LOGGER = logging.getLogger(__name__)


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
                tuple(self.arguments_types),
                self.class_name,
            )
        )

    def __str__(self) -> str:
        return f"{self.return_type} {self.class_name}::{self.function_name}({self.arguments_str})"


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

        logging.debug(
            "Doing regex on class %s with content (%s)",
            class_name,
            class_content,
        )
        regex_results: list[tuple[str, str, str]] = re.findall(
            function_regex, class_content
        )

        for return_type, function_name, arguments in regex_results:
            cpp_functions.add(
                CppFunction(return_type, function_name, arguments, class_name)
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


def add_function_definitions(cpp_file: str, functions: set[CppFunction]):
    """
    This function adds the function definitions to the cpp file.

    Args:
        cpp_file (str): The path of the cpp file.
        functions (Sequence[CppFunction]): The functions to add to the cpp file.
    """
    with open(cpp_file, "r+", encoding="utf-8") as file:
        content = file.read().rstrip("\n")
        content += "\n"

        file.seek(0)
        for function in functions:
            content += "\n"
            function_definition = f"{function.return_type} {function.class_name}::{function.function_name}({function.arguments_str}) {{\n}}\n"
            content += function_definition

        file.write(content)
        file.truncate()
        LOGGER.info(
            "%d changes have been written to {cpp_file}", {len(functions)}
        )


def add_class_definitions_to_cpp(
    cpp_parser: argparse.ArgumentParser, args_partial: Sequence[str]
):
    """
    This is the main function of the cpp_tools script.

    Args:
        cpp_parser (argparse.ArgumentParser): _description_
        args_partial (Sequence[str]): _description_
    """

    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(message)s"
    )

    cpp_parser.add_argument(
        "-f", "--file", type=str, help="The header file name"
    )
    cpp_parser.add_argument(
        "-p",
        "--path",
        type=str,
        default=".",
        const=".",
        nargs="?",
        help="The path",
    )
    args = cpp_parser.parse_args(args_partial)

    lst_headers: list[tuple[str, str]] = []

    if "header_name" in args and args.header_name:
        header_strip = args.header_name.replace(".h", "")
        header_file = header_strip + ".h"
        cpp_file = header_strip + ".cpp"
        if not os.path.isfile(header_file):
            LOGGER.info("Header file %s not found. Aborting...", header_file)
            return

        if not os.path.isfile(cpp_file):
            LOGGER.info("Cpp file %s not found. Aborting...", cpp_file)
            return

        lst_headers.append((header_file, cpp_file))
    elif "path" in args and args.path:

        files = set(os.listdir(args.path))

        # Search for headers in the path
        for file in files:
            if file.endswith(".h"):
                cpp_file = file.replace(".h", ".cpp")

                if cpp_file not in files:
                    LOGGER.info(
                        "No cpp file found corresponding to %s. Ignoring.",
                        file,
                    )
                    continue

                lst_headers.append((file, cpp_file))

    else:
        LOGGER.info("No header file or path provided")
        exit(1)

    LOGGER.info("Found %d header files to scan", len(lst_headers))
    changes_needed: list[tuple[str, str, set[CppFunction]]] = []

    for header_file, cpp_file in lst_headers:
        # Get functions from files and compare them
        LOGGER.info("Scanning header file %s", header_file)
        header_functions = get_functions_from_header(header_file)
        cpp_functions = get_functions_definitions_from_cpp(cpp_file)
        missing_functions = compare_functions(header_functions, cpp_functions)

        # Save the files that need changes and display a message
        if len(missing_functions) > 0:
            LOGGER.info("The following functions are missing in %s", cpp_file)
            LOGGER.info("-------------------------------------------------")
            for func in missing_functions:
                LOGGER.info(func)
            LOGGER.info("-------------------------------------------------")

            changes_needed.append((header_file, cpp_file, missing_functions))

    # LOGGER.infos a summary of changes needed
    LOGGER.info("SUMMARY:")
    LOGGER.info("%d files with changes needed", len(changes_needed))
    for header_file, cpp_file, missing_functions in changes_needed:
        LOGGER.info("Header file requires %d changes", len(missing_functions))

    # Prompt user for confirmation
    if len(changes_needed) > 0:
        var_input = input("Do you want to proceed? (y/n)")
        if var_input.lower() != "y":
            LOGGER.info("Aborting...")
            return

        # Make changes to the files
        for header_file, cpp_file, missing_functions in changes_needed:
            add_function_definitions(cpp_file, missing_functions)

    LOGGER.info("Done!")
