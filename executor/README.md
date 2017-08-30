# Revit Model Services Executor

***RMSExecutor is a dedicated Revit addon that executes a python script in Revit journal mode.***


### Addon File: RMSExecutor.addin

Addon file can be permanently placed under rms/journals folder to be loaded by Revit.


### Journal Entry that Runs the Command Executor

```vbscript
' Executing external command
Jrn.RibbonEvent "TabActivated:Add-Ins"
Jrn.RibbonEvent "Execute external command:CustomCtrl_%CustomCtrl_%Add-Ins%  Revit Model Services (RMS)  %RMSCmdExecutorCommand:RMSCmdExecutor.RMSCmdExecutorCommand"
' Providing command data to external command
Jrn.Data "APIStringStringMapJournalData"  _
    , 6 _
    , "ScriptSource" , "script.py"_
    , "SearchPaths" , "path1;path2;path3"_
    , "ModelName" , "model.rvt"_
    , "OutputPath" , "C:\output"_
    , "OutputPrefix" , "Session_prefix_"_
    , "LogFile" , "C:\output\results.txt"
```


### Data to be passed to the command

``` python
command_data = {'ScriptSource': 'source file of the python script to be executed in Revit document',
                'SearchPaths': ['list of paths to be added to sys.path'],
                'ModelName': 'model file name for the script to use when exporting data that belongs to that model',
                'OutputPath': 'output path for files to be exported by the script',
                'OutputPrefix': 'prefix to be added to the files when exported by the script',
                'LogFile': 'output file that the RMS Executor will use to write the script printed output into'}
```


### Executor Provides these builtin variables to the script

```python
# associated IronPython Engine
print('__ipyengine__: %s' % __ipyengine__)

# Output window and stream
print('__window__: %s' % __window__)
print('__output__: %s' % __output__)
print('__outputstream__: %s' % __outputstream__)

# Revit and documents
print('__revit__: %s' % __revit__)
print('__activeuidoc__: %s' % __activeuidoc__)
print('__activedoc__: %s' % __activedoc__)
print('__zerodoc__: %s' % __zerodoc__)

# RMS External Command
print('__externalcommand__: %s' % __externalcommand__)

# Command data and selected elements passed by Revit to the command
print('__commanddata__: %s' % __commanddata__)
print('__elements__: %s' % __commanddata__)

# associated IronPython Engine
print('__commandpath__: %s' % __commandpath__)

# Model name (passed to the Executor from Journal)
print('__modelname__: %s' % __modelname__)

# Output Path to be used by the script to output data
# (passed to the Executor from Journal)
print('__outputpath__: %s' % __outputpath__)

# Output file prefix
# (passed to the Executor from Journal)
print('__outputprefix__: %s' % __outputprefix__)
```
