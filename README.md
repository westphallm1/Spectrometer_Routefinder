# Pushbroom Planner
-------------------------

## About
Pushbroom Planner is a Python3 gui application that generates flight paths
 for aircraft carrying pushbroom scanners. 
## Installation
The installation of this package requires both Python3 and pip3. It's 
currently targeted at Python 3.7.  Python3 comes with Ubuntu by default, 
but pip3 must be installed from the package manager via `sudo apt install 
python3-pip`. On Windows, Python3 and pip3 can be downloaded and installed 
from [the Python website](https://www.python.org/).

If using this application in production as a stand alone program, it's best
to put it in a Python virtual environement, ie: `python3.7 -m venv 
ScanlineFlightPlanner` and then `. ScanFlightPlanner/bin/activate`.
After installing Python3 and downloading this package, just navigate to the
directory of this README and run the command `pip3 install .` A script called
`scan_route_plotter` will be added in your `$PATH`, running this script will
invoke the gui.
