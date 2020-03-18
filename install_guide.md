# rvt_model_services python install guide
since rvt_model_services relies on a bunch of awesome packages,<br> 
here is an installation guide which might be useful:<br>

## CPython:
* install cpython 3.7 or higher: download Python the installer (64bit recommended)<br> 
  from [python.org](https://www.python.org/) . make sure you install it for all users, 
  if you need installation and rvt_model_services with different user privileges.<br>
  ideally have "add to path" ist selected. (recommended!)
* the python packages can be installed from this directory:<br>
  * either with the included requirements.txt:<br>
    `python -m pip install --user -r requirements.txt`
  * or for each package individually:<br>
    `python -m pip install --user beautifulsoup4`    
    `python -m pip install --user bokeh`             
    `python -m pip install --user colorama`          
    `python -m pip install --user colorful`          
    `python -m pip install --user docopt`            
    `python -m pip install --user numpy`             
    `python -m pip install --user pandas`            
    `python -m pip install --user psutil`            
    `python -m pip install --user olefile`           
    `python -m pip install --user slackclient==1.0.6`
    `python -m pip install --user rvt_detector`      
    `python -m pip install --user rjm`               
    `python -m pip install --user tinydb`            
    `python -m pip install --user prompt-toolkit`    
    `python -m pip install --user requests`
* check afterwards with a "pip list" if your installation process was successful<br>
* optionally/ideally you could set this up in an virtual environment, but that is beyond the scope of this guide.

## Autodesk Revit®
* regular install to the standard paths like these: 
    - `C:\Program Files\Autodesk\Revit Architecture 2019`
    - `C:\Program Files\Autodesk\Revit 2020`

## not required but recommended:
* RevitPythonShell: download the newest installer from the releases section from [github revitpythonshell](https://github.com/architecture-building-systems/revitpythonshell) <br>
    if you are stuck:
     * [installation details on file locations from Daren Thomas' gitbook](https://daren-thomas.gitbooks.io/scripting-autodesk-revit-with-revitpythonshell/content/installing_revitpythonshell_for_autodesk_revit/files_and_locations.html)
     * with the IT setup at our company I had to do the following on a win7 machine: <br>
        install RPS as Administrator, then copy the following files and folders with content over:<br>
        * `C:\Users\<InstallAdmin>\AppData\Roaming\RevitPythonShell201X`
           <br>-> `C:\Users\<YourUserAccount>\AppData\Roaming\RevitPythonShell201X`
        * `C:\Users\<InstallAdmin>\AppData\Roaming\Autodesk\Revit\Addins\201X\RevitPythonShell201X.addin`
            <br>-> `C:\Users\<YourUserAccount>\AppData\Roaming\Autodesk\Revit\Addins\201X\RevitPythonShell201X.addin`

* install a console emulator that is both powerful and fun to use.<br>
    - cmder console emulator:<br>
        download from: [cmder webpage](http://cmder.net/) <br>
        or install via [chocolatey.org](https://chocolatey.org/) : `choco install cmder`
* maybe even combine Python and windows prompt: 
    - xonsh: install via: `python3 -m pip install --user xonsh`
