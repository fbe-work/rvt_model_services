# rvt_model_services python install guide
since rvt_model_services relies on a bunch of awesome packages here is an installation guide which might be useful:<br>

## CPython:
* install cpython 3.6: download Python 3.6.x installer from [python.org](https://www.python.org/) make sure you install it for all users if you need installation and rvt_model_services with different user privileges and make sure "add to path" ist selected. (recommended!)
* the only tricky package could be numpy. in order to install it without too much hassle: download the precompiled version from this website: [lfd.uci.edu gohlke pythonlibs](http://www.lfd.uci.edu/~gohlke/pythonlibs/) then navigate with your command prompt to the download directoy and install it via "python -m pip install numpy‑1.13.0rc1+mkl‑cp36‑cp36m‑win_amd64.whl"
* the other packages should not be problematic, they can be installed from this directory:<br>
  * either with the included requirements.txt:<br>
    python -m pip install -r requirements.txt<br>
  * or for each package individually:<br>
    python -m pip install beautifulsoup4==4.6.0<br>
    python -m pip install bokeh==0.12.4<br>
    python -m pip install colorama==0.3.9<br>
    python -m pip install colorful==0.4.0<br>
    python -m pip install docopt==0.6.2<br>
    python -m pip install numpy==1.12.1<br>
    python -m pip install pandas==0.19.2<br>
    python -m pip install psutil==5.2.2<br>
* check afterwards with a "pip list" if your installation process was successful<br>
* optionally you could set this up in an virtual environment, but that is beyond the scope of this guide.

## RevitPythonShell
* download the newest installer from the releases section from [github revitpythonshell](https://github.com/architecture-building-systems/revitpythonshell) <br>
    if you are stuck:
     * [installation details on file locations from Daren Thomas' gitbook](https://daren-thomas.gitbooks.io/scripting-autodesk-revit-with-revitpythonshell/content/installing_revitpythonshell_for_autodesk_revit/files_and_locations.html)
     * with the IT setup at our company I had to do the following on a win7 machine: <br>
        install RPS as Administrator, then copy the following files and folders with content over:<br>
        - C:\Users\<InstallAdmin>\AppData\Roaming\RevitPythonShell201X -> C:\Users\<YourUserAccount>\AppData\Roaming\RevitPythonShell201X
        - C:\Users\<InstallAdmin>\AppData\Roaming\Autodesk\Revit\Addins\201X\RevitPythonShell201X.addin -> C:\Users\<YourUserAccount>\AppData\Roaming\Autodesk\Revit\Addins\201X\RevitPythonShell201X.addin

## Autodesk Revit®
* regular install to the standard paths like these: 
    - C:\Program Files\Autodesk\Revit Architecture 2016
    - C:\Program Files\Autodesk\Revit 2017

## not required but recommended:
* install a console emulator that is fun to use and combine Python and windows prompt: 
    - cmder console emulator download from: [cmder webpage](http://cmder.net/)
    - xonsh (via pip install xonsh)
