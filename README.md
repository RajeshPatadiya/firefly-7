<img src="https://github.com/febret/firefly/blob/master/screenshot.png?raw=true" width = 800/>

Firefly is a visualization app for simulations generated by the FIRE galaxy formation simulation (http://galaxies.northwestern.edu/fire-simulations/)

[![Build status](https://ci.appveyor.com/api/projects/status/0obju3q24wipfp35?svg=true)](https://ci.appveyor.com/project/febret/firefly)

The code is in python and runs using the Omegalib toolkit (https://github.com/uic-evl/omegalib)

## Installation ##
You can grab a binary installer from the Releases page (OSX only for now). After installing, firefly will be available as
a terminal command. To run firefly open a terminal window and type 
```
> firefly <datacconfig.py>
```
Where `dataconfig.py` is a **data configuration script* that describes what file(s) to load and how to display them. Read more information on this 
in the **Configuration** section

To uninstall firefly open a terminal and type `firefly-uninstall`

## Configuration ##
TODO

## Running a custom version of firefly ##
You use the installed firefly executable to run a custom version of firefly. This is useful if you want to fork a copy of this project and
want to test your own changes before creating a new binary distribution, or if you want to keep multiple version of firefly side-by-side.

We assume you are getting a version of firefly from this repository, and want to put it under your user account (ex. `/Users/myself`).
First, clone this repository (or just download and unzip if you don't care about version control):
```
/Users/myself> git clone http://www.github.com/febret/firefly
```

Then you need to modify `default_init.py` from your installed firefly binary distribution. If you installed in the default path on OSX, this
file is in `/Applications/firefly.app`

`default_init.py` looks like this:
```python
# Change this if you want to run a custom version of firefly
appScript = 'firefly/firefly.py'

# Initially set an empty data path variable. This will be filled by the dataset config
# file (if we choose one). If the app runs with this unset, we will show a splash screen.
datasetPath = None

# Execute the firefly script after the data config file had a chance to load
from threading import Timer
def main():
    queueCommand(':r ' + appScript)
bt = Timer(0.1, main)
bt.start()
```

You need to modify **line 2** to make it point to your copy of firefly, ex:
```python
appScript = '/Users/myself/firefly/firefly.py'
```

Now, when you run `firefly` from the terminal, your downloaded version of firefly will run instead of the vanilla one installed in the 
binary distribution.

## Building and Packaging Firefly##
> **REQUIRES:** git, cmake

First, install the Omegalib maintenance script:
```
> mkdir omegalib
> cd omegalib
omegalib> (on LINUX) wget https://uic-evl.github.io/omegalib/omega
omegalib> (on OSX)   curl https://uic-evl.github.io/omegalib/omega -o omega
omegalib> chmod +x omega
```

Then download and build firefly:
```
omegalib> ./omega get firefly:master nuitrcs/firefly
```
This will download and build firefly and all the required dependencies in a directory called firefly.

You will need to copy `firefly/modules/firefly/default_init.py`inside `firefly`, overwriting the existing default_init.py

You can then try running firefly using omegalib's `orun`:
```
omegalib> cd firefly/build/bin
omegalib/master/build/bin>./orun <path-to-data-config.py> -i
```

### Building on Windows ###
These are the full instructions for building and running on windows, assuming you downloaded omega.bat from here: https://uic-evl.github.io/omegalib/omega.bat and you are in a terminal in the directory where you downloaded it
```
> omega get firefly:master nuitrcs/firefly
> omega choose firefly
> copy firefly\modules\firefly\default_init.py firefly /Y
```

To run firefly, double click on choose_firefly.bat (find it in the same dir as omega.bat) and type orun in the opened console.

If you want to package this version of firefly type:
```
omegalib>./omega pack.app master firefly
```
This will create an installer binary in `omegalib/packs/firefly`.
