import argparse

from cpp_class_creator import create_cpp_class
from cpp_definition_adder import add_class_definitions_to_cpp


def main():
    """
    This is the main function of the script.
    """
    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    cpp_parser = subparsers.add_parser("create_cpp_class")
    cpp_parser.set_defaults(func=create_cpp_class)

    cpp_parser = subparsers.add_parser("add_cpp_definitions")
    cpp_parser.set_defaults(func=add_class_definitions_to_cpp)

    args, args_partial = parser.parse_known_args()

    if "func" not in args:
        parser.print_help()
        return
    args.func(cpp_parser, args_partial)  # pylint: disable=no-member


if "__main__" == __name__:
    main()
