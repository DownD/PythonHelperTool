# HelperScripts

Simple project to have my scripts that I use on a daily basis into a single module.


## Installation
```pip install .```

## Usage
```myutils -h```

## Current Scripts
- ```create_cpp_class```: Create a new C++ class header and source file given a class name.
- ```add_cpp_definitions```: Add definitions of an C++ header to the cpp file if not present.
- ```video_img_split```: Saves multiple frames from a video and stored them as .jpg.
- ```cv_inference```: Run inference on a video/window using a given model.

## Limitations
The script ```cv_inference``` uses ONNX Runtime an thus only is only supported up to Python 3.9.
Also, in order to do inference on GPU it will be necessary to install CUDA and cuDNN. [See here](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html) for more details.
If there is an error regarding onnxruntime-gpu, try removing this dependency from ```requirements.txt``` and using ```--cpu``` flag when running the script.

## TODO
- [ ] Add ```cv_inference``` to be able to run on GUI windows.
- [ ] Allow ```cv_inference``` to inference on batch of frames.
- [ ] Test ```cv_inference``` on multiple platforms and without GPU.

## Add new scripts
To add new scripts just create a new file and extend the class ```ScriptInterface``` in ```script_interface.py``` by implementing the required methods.
Then add the instantion of the object in Line 8 on the main.py file. 

It's possible to add any arguments by using the callback ```add_subparser_args``` in the ```ScriptInterface``` class, to specify a name and a description, that will be used as the command and the help message, just pass it to the constructor of ```ScriptInterface```. 
And the main module will take care of calling the function ```__call__``` of the object and passing the necessary arguments if the script is selected. 
