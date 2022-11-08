import logging
from argparse import ArgumentParser

from myutils.cpp_class_creator import CreateCppClass
from myutils.cpp_definition_adder import CppFunctionAdder
from myutils.script_interface import ScriptInterface

scripts_list: list[ScriptInterface] = [CppFunctionAdder(), CreateCppClass()]


def main():
    """
    This is the main function of the script.
    """
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(message)s"
    )

    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    # Create a subparser for each script and store it in the scripts_dict
    for script in scripts_list:
        script_parser = subparsers.add_parser(
            script.get_name(), description=script.get_description()
        )
        script.add_subparser_args(script_parser)
        script_parser.set_defaults(func=script.__call__)

    args = parser.parse_args()
    args.func(args)  # pylint: disable=no-member


if "__main__" == __name__:
    main()
