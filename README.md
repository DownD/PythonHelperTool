# HelperScripts

Simple project to have my scripts that I use on a daily basis into a single module.


## Installation
```pip install .```

## Usage
```myutils -h```

## Current Scripts
- ```create_cpp_class```: Create a new C++ class header and source file given a class name.
- ```add_cpp_definitions```: Add definitions of an C++ header to the cpp file if not present.

## Add new scripts
To add new scripts just create a new file and extend the class ```ScriptInterface``` in ```script_interface.py``` by implementing the required methods.
Then add the instantion of the object in Line 8 on the main.py file. 

It's possible to add any arguments by using the callback ```add_subparser_args``` in the ```ScriptInterface``` class, to specify a name and a description, that will be used as the command and the help message, just pass it to the constructor of ```ScriptInterface```. 
And the main module will take care of calling the function ```__call__``` of the object and passing the necessary arguments if the script is selected. 
