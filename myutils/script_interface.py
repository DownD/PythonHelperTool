from argparse import ArgumentParser, Namespace


class ScriptInterface:
    """
    This class is used to create a script interface.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    def get_name(self):
        """
        Returns the name of the script.
        """
        return self.name

    def get_description(self):
        """
        Returns the description of the script.
        """
        return self.description

    def add_subparser_args(self, parser: ArgumentParser):
        """
        This function returns a subparser for the script.

        Args:
            parser (ArgumentParser): The subparser of the script
        """
        raise NotImplementedError()

    def __call__(self, args: Namespace):
        """
        This function is called when the script is launched.

        Args:
            parser (ArgumentParser): The parser of the script
            args_partial (list, optional): The arguments to parse. Defaults to None.
        """
        raise NotImplementedError()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other

    def __hash__(self):
        return hash(self.name)
