# rvt_model_services
python micro framework to process actions on revit models from cli/command line

## how it works:
  * you initialize it with a command to process_model.py specifying the task, project path and revit version and a timeout.
  * process_model.py will spin off a subprocess to write a journal file and addin according to your specified task and project.
  * it will then run Revit according to journal file, opening a detached version of your model and run the specified action like a [revitpythonshell](https://github.com/architecture-building-systems/revitpythonshell) script.
  * if the journal file cannot be run to completion the subprocess is killed and an error is logged.

## it requires/is currently run on:
  * cpython >= 3.6 (with additional modules: beautifulsoup4, bokeh, colorama, colorful, docopt, numpy, pandas, psutil, olefile)
  * [revitpythonshell](https://github.com/architecture-building-systems/revitpythonshell) >= 2017.03.07
  * Autodesk Revit® (currently tested on versions 2015.7, 2016.2, 2017.2)
  * see install_guide for help/further information.

## how to get started:
  * when the above mentioned requirements are met and this repo is cloned to your preferred path lets get started with a common task (read qc stats (qc meaning "quality check" in this context)) in three steps:
  * step 1: create a revitpythonshell button<br> 
    setup in RPS:   
    in your targeted Revit version add a RPS button "model_qc":
    "Add-Ins > RevitPythonShell > Configure", Add:
    Name: qc_model, Group: rvt_model_services
    Path: X:\your_path_to_the_cloned_repo\rvt_model_services\commands\qc\rps_qc_model.py
    restart Revit to check if the Button appears.
    click on it to see if the message window appears and gives you a few stats on the current model.
    
  * step 2: run a qc read out from cli<br> 
    run process_model.py from command line:
    now we can run the qc_model without even touching Revit and get interactive html graphs produced.
    Compose a command consisting of the following:

    your CPython interpreter<br>
    your path to process_model.py<br>
    command type<br>
    project name<br>
    path to the project Revit model<br>
    revit model file name<br>
    path to Revit executable to run it with<br>
    Revit version number to open the file with<br>
    a timeout for the process

    so it could look like this:

    "C:\Program Files\Python36\python.exe"<br>
    D:/testrun/934_rvt_model_services/process_model.py<br>
    qc<br>
    123_N<br>
    D:/testmodel/<br>
    123_N.rvt<br>
    "C:/Program Files/Autodesk/Revit Architecture 2016/Revit.exe"<br>
    2016<br>
    600<br>
    
    Just concatenate it (put it into one line).<br>
    Open a command line ("Win > type 'cmd'") paste it in("right-click > paste") and run it.<br>
    If you want to write the html to another directory you can use the optional switch "--html_path" followed by a path.
    Here is how this looks on my screen:
    
    ![cmder_screenshot][cmder_01]   

  * step 3: let task scheduler repeat your task<br>
    for recurring tasks hook it up to Windows® task scheduler:
    Open Task scheduler and create a new basic task<br>
        - give it a name<br>
        - set your interval rate e.g. daily<br>
        - set your start time<br>
        - action: start program:<br>
            Program/Script:<br>
                "C:\Program Files\Python36\python.exe"<br>
            Add Arguments:<br>
                D:/testrun/934_rvt_model_services/process_model.py qc 123_N D:/testmodel/ 123_N.rvt "C:/Program Files/Autodesk/Revit Architecture 2016/Revit.exe" 2016 600 <br>
        - Finish and test if it works: "Right-Click > Run"

## typical use cases(recurring tasks run via schedule Task Scheduler):
  * extraction of qc data to be gathered in csv table and visualized on interactive html graphs using bokeh 
  * check on model corruption with audit canary
  * export of DWF, DWG, PDF or IFC (so far only DWF export implemented)
  * export model warnings (API-less journal file warnings export)

## currently implemented tasks:
  * qc: rvt model qc statistics on workshared models<br>
  
    ![qc_elements_graph][qc_01] 
  
  * dwf: dwf sheet exports of sheet set "Auto_PDF_DWF" on workshared models<br>
  * warnings: model warnings export on workshared models<br>
  
    ![warnings_graph][warnings_01] 
  
  * pulse: bokeh graph showing the job log graphically(which project was process in what time, did it timeout -> red bar).<br>
    run separately from process_model with: "python bokeh_pulse.py" from commands/pulse/ directory.
    
    ![pulse_graph][pulse_01] 
    
  * audit: bokeh graph showing the rusult of models being opened with "audit".<br>
    success: green, unclassified error:orange, corrupt model: red.<br>
    run separately from process_model with: "python bokeh_pulse.py" from commands/pulse/ directory.
    
    ![pulse_graph][audit_pulse_01] 

## limitations (typical limitations a journal file run process typically has):
  * no white spaces in model path
  * no non-ascii characters in model path
  * task will not run to completion if confronted with any unexpected messages

## credits
 * Frederic Beaupere (original version, maintainer)
 * Daren Thomas (creator of [revitpythonshell](https://github.com/architecture-building-systems/revitpythonshell))
 * Ehsan Iran-Nejad (creator of [pyRevit](https://github.com/eirannejad/pyRevit))
 * Gui Talarico (creator of [revitpythonwrapper](https://github.com/gtalarico/revitpythonwrapper) and [revitapidocs](https://github.com/gtalarico/revitapidocs))

note: If you are not on this list, but believe you should be, please contact me!

## license
[MIT](https://opensource.org/licenses/MIT)

[cmder_01]: https://github.com/hdm-dt-fb/rvt_model_services/raw/master/docs/img/cmder_01.png "cmder_screenshot"
[qc_01]: https://github.com/hdm-dt-fb/rvt_model_services/raw/master/docs/img/qc_01.png "qc_elements"
[warnings_01]: https://github.com/hdm-dt-fb/rvt_model_services/raw/master/docs/img/warnings_01.png "warnings_graph"
[pulse_01]: https://github.com/hdm-dt-fb/rvt_model_services/raw/master/docs/img/pulse_01.png "pulse_graph"
[audit_pulse_01]: https://github.com/hdm-dt-fb/rvt_model_services/raw/master/docs/img/audit_pulse_01.png "audit_pulse_graph"
