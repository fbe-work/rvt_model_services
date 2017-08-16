using System;
using System.Collections.Generic;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using System.Windows.Forms;


namespace RMSCmdExecutor
{
    [Regeneration(RegenerationOption.Manual)]
    [Transaction(TransactionMode.Manual)]
    public class RMSCmdExecutorCommand : IExternalCommand
    {
        private string _scriptSource;
        private string _syspaths;
        private string _modelName;
        private string _commandOutputDir;
        private string _commandOutputPrefix;
        private string _logFile;
        private bool _debugMode = false;
        private bool _uimode = false;

        private ScriptOutput _scriptOutput;
        private ScriptOutputStream _outputStream;
        private UIApplication _application;
        private ExternalCommandData _commandData;
        private ElementSet _elements;


        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            _application = commandData.Application;
            _commandData = commandData;
            _elements = elements;


            // 1: ---------------------------------------------------------------------------------------------------------------------------------------------
            // Processing Journal Data and getting the script path to be executed in IronPython engine
            IDictionary<String, String> dataMap = commandData.JournalData;
            try
            {
                _scriptSource = dataMap["ScriptSource"];
                _syspaths = dataMap["SearchPaths"];
                _modelName = dataMap["ModelName"];
                _commandOutputDir = dataMap["OutputPath"];
                _commandOutputPrefix = dataMap["OutputPrefix"];
                _logFile = dataMap["LogFile"];
            }
            catch (Exception)
            {
                _syspaths = "";
                var fdlg = new OpenFileDialog();
                fdlg.Filter = "|*.py";
                fdlg.RestoreDirectory = true;
                fdlg.Multiselect = false;

                if (fdlg.ShowDialog() == DialogResult.OK)
                {
                    _scriptSource = fdlg.FileName;
                }
                else
                {
                    return Result.Cancelled;
                }

                _uimode = true;
            }

            // 2: ---------------------------------------------------------------------------------------------------------------------------------------------
            // Stating a new output window
            _scriptOutput = new ScriptOutput();
            _outputStream = new ScriptOutputStream(_scriptOutput);
            // Forces creation of handle before showing the window
            var hndl = _scriptOutput.Handle;

            // 3: ---------------------------------------------------------------------------------------------------------------------------------------------
            // Executing the script

            // Get script executor
            var executor = new ScriptExecutor(commandData);
            // Execute script
            var resultCode = executor.ExecuteScript(this);

            // Return results
            if (resultCode == 0)
                return Result.Succeeded;
            else
                return Result.Cancelled;
        }


        public string ScriptSourceFile
        {
            get
            {
                return _scriptSource;
            }
        }

        public string[] ModuleSearchPaths
        {
            get
            {
                return _syspaths.Split(';');
            }
        }

        public string ModelName
        {
            get
            {
                return _modelName;
            }
        }

        public string OutputPath
        {
            get
            {
                return _commandOutputDir;
            }
        }

        public string OutputPrefix
        {
            get
            {
                return _commandOutputPrefix;
            }
        }

        public string LogFile
        {
            get
            {
                return _logFile;
            }
        }

        public bool DebugMode
        {
            get
            {
                return _debugMode;
            }
        }

        public bool GuiMode
        {
            get
            {
                return _uimode;
            }
        }


        public ScriptOutput OutputWindow
        {
            get
            {
                return _scriptOutput;
            }
        }

        public ScriptOutputStream OutputStream
        {
            get
            {
                return _outputStream;
            }
        }

        public ExternalCommandData CommandData
        {
            get
            {
                return _commandData;
            }
        }

        public ElementSet SelectedElements
        {
            get
            {
                return _elements;
            }
        }
    }

    public class RMSCmdExecutorCommandAvail : IExternalCommandAvailability
    {
        public RMSCmdExecutorCommandAvail()
        {
        }

        public bool IsCommandAvailable(UIApplication uiApp, CategorySet selectedCategories)
        {
            return true;
        }
    }
}
