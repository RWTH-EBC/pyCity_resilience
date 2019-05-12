[![Build Status](https://travis-ci.com/RWTH-EBC/pyCity_resilience.svg?token=ssfy4ps1Qm5kvs5yAxfm&branch=master)](https://travis-ci.com/RWTH-EBC/pyCity_resilience.svg?token=ssfy4ps1Qm5kvs5yAxfm&branch=master)
[![License](http://img.shields.io/:license-mit-blue.svg)](http://doge.mit-license.org)

# pyCity_resilience
pyCity addon to identify resilient energy system configurations

## Contributing

1. Clone repository: `git clone git@github.com:RWTH-EBC/pyCity_resilience.git`
(for SSH usage)
   otherwise, use https path: `git clone https://github.com/RWTH-EBC/pyCity_resilience.git`
2. Create issue on  [https://github.com/RWTH-EBC/pyCity_resilience/issues](https://github.com/RWTH-EBC/pyCity_resilience/issues)
Create your feature branch: `git checkout -b issueXY_explanation`
3. Add and commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin issueXY_explanation`
5. Submit a pull request (for merging into development branch) to `@JSchiefelbein` [https://github.com/RWTH-EBC/pyCity_resilience/pulls](https://github.com/RWTH-EBC/pyCity_resilience/pulls)
6. Working version of development branch can later be merged into master


## Installation

pyCity_resilience requires the following EBC Python packages:
- richardsonpy
- uesgraphs
- pyCity
- pyCity_calc
- TEASER

richardsonpy is available via [https://github.com/RWTH-EBC/richardsonpy](https://github.com/RWTH-EBC/richardsonpy)

uesgraph is available via [https://github.com/RWTH-EBC/uesgraphs](https://github.com/RWTH-EBC/uesgraphs)

pyCity is available via [https://github.com/RWTH-EBC/pyCity](https://github.com/RWTH-EBC/pyCity)

pyCity_calc is available via [https://github.com/RWTH-EBC/pyCity_calc](https://github.com/RWTH-EBC/pyCity_calc)

TEASER is available  via[https://github.com/RWTH-EBC/TEASER](https://github.com/RWTH-EBC/TEASER)

Both can be installed into your system Python path via pip:

`pip install -e 'your_path_to_richardsonpy_setup_folder'`

`pip install -e 'your_path_to_uesgraph_setup_folder'`

and

`pip install -e 'your_path_to_pycity_setup_folder'`

In your current Python path does not point at your Python installation, you
can directly call your Python interpreter and install the packages via pip, e.g.:

    "<path_to_your_python_distribution>\Python.exe" -m pip install -e <your_path_to_uesgraph_setup>

You can check if installation / adding packages to python has been successful
by adding new .py file and trying to import richardsonpy, uesgraphs and pycity.

`import richardsonpy`

`import uesgraphs`

`import pycity_base`

Import should be possible without errors.

TEASER can be installed the same way (recommended, if you want to actively work on TEASER code) or
directly via pip `pip install teaser` (if you only want to use TEASER).

Further required packages are:

- shapely (for uesgraphs integration)
- pyproj (for uesgraphs integration)


### Shapely installation on Windows machine

On Windows systems, pip install of shapely (or pyproj etc.) will probably raise an error during installation.
However, there is a workaround with precompiled Python packages.

-  Go to  [http://www.lfd.uci.edu/~gohlke/pythonlibs/](http://www.lfd.uci.edu/~gohlke/pythonlibs/)
-  Search for Python package, you could not install via pip (such as shapely)
-  Choose download file depending on your Python version and machine (e.g. cp34 stands for Python 3.4; win32 for 32 bit; amd64 for 64 bit)
-  Download wheel file and remember its path
-  Open a command prompt within your Python environment
-  Type: ''pip install <path_to_your_whl_file>'
-  Python packages should be installed

Under Linux and Mac OS pip installation of shapely and pyproj should work without problems.

## License

pyCity_resilience is released under the [MIT License](https://opensource.org/licenses/MIT)

## Acknowledgements

Grateful acknowledgement is made for financial support by Federal Ministry for Economic Affairs and Energy (BMWi),
promotional references 03ET1138D and 03ET1381A.

<img src="http://www.innovation-beratung-foerderung.de/INNO/Redaktion/DE/Bilder/Titelbilder/titel_foerderlogo_bmwi.jpg;jsessionid=4BD60B6CD6337CDB6DE21DC1F3D6FEC5?__blob=poster&v=2)" width="200">
