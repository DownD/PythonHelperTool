import sys
from argparse import ArgumentParser
from typing import Callable, Optional

from myutils.cpp_class_creator import create_cpp_class
from myutils.cpp_definition_adder import add_class_definitions_to_cpp

scripts_dict: dict[str, tuple[Callable, Optional[ArgumentParser]]] = {
    "create_cpp_class": (create_cpp_class, None),
    "add_cpp_definitions": (add_class_definitions_to_cpp, None),
}


def main():
    """
    This is the main function of the script.
    """
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # Create a subparser for each script and store it in the scripts_dict
    for script_name, tuple_function in scripts_dict.items():
        script_parser = subparsers.add_parser(script_name)
        script_parser.set_defaults(func=tuple_function[0])
        scripts_dict[script_name] = (tuple_function[0], script_parser)

    # Set temporary variables
    argv_set = set(sys.argv)
    tmp_argv = sys.argv.copy()
    script_in_use = set(scripts_dict.keys()).intersection(argv_set)

    # Remove the --help flag from the argv list if one of the subcommands is in use
    if {"--help", "-h"}.intersection(sys.argv) and len(script_in_use) > 0:
        if "--help" in sys.argv:
            tmp_argv.remove("--help")
        else:
            tmp_argv.remove("-h")

    # Parse the arguments without the help flag if provided
    args, args_partial = parser.parse_known_args(tmp_argv[1:])

    # Adds the help flag back to the argv list if it was removed
    if tmp_argv != sys.argv:
        args_partial.append("--help")

    # Launch the script with the correct commands
    script_sub_parser = scripts_dict[script_in_use.pop()][1]
    args.func(script_parser, args_partial)  # pylint: disable=no-member


if "__main__" == __name__:
    main()
