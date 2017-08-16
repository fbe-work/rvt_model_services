using System;
using System.IO;
using System.Reflection;
using System.Linq;
using System.Text;
using Autodesk.Revit;
using IronPython.Runtime.Exceptions;
using IronPython.Compiler;
using Microsoft.Scripting;
using Microsoft.Scripting.Hosting;
using Autodesk.Revit.UI;
using Autodesk.Revit.DB;
using System.Collections.Generic;

namespace RMSCmdExecutor
{
    // Executes a script
    public class ScriptExecutor
    {
        private readonly UIApplication _revit;

        public ScriptExecutor(ExternalCommandData commandData)
        {
            _revit = commandData.Application;
        }


        public int ExecuteScript(RMSCmdExecutorCommand rmsCmd)
        {
            // Get engine and setup
            var engine = CreateEngine();
            var scope = CreateScope(engine, ref rmsCmd);

            // Add script directory address to sys search paths
            var path = engine.GetSearchPaths();
            path.Add(System.IO.Path.GetDirectoryName(rmsCmd.ScriptSourceFile));

            if (! rmsCmd.GuiMode) {
                foreach (var search_path in rmsCmd.ModuleSearchPaths) {
                    path.Add(search_path);
                }
            }
            else {
                path.Add(GetCommandServicesModulePath());
            }


            engine.SetSearchPaths(path);

            // Add output streams
            engine.Runtime.IO.SetOutput(rmsCmd.OutputStream, Encoding.UTF8);
            engine.Runtime.IO.SetErrorOutput(rmsCmd.OutputStream, Encoding.UTF8);

            // setting module to be the main module so __name__ == __main__ is True
            var compiler_options = (PythonCompilerOptions) engine.GetCompilerOptions(scope);
            compiler_options.ModuleName = "__main__";
            compiler_options.Module |= IronPython.Runtime.ModuleOptions.Initialize;

            // Create the script from source file
            var script = engine.CreateScriptSourceFromFile(rmsCmd.ScriptSourceFile, Encoding.UTF8, SourceCodeKind.Statements);

            // Setting up error reporter and compile the script
            var errors = new ErrorReporter();
            var command = script.Compile(compiler_options, errors);
            // Process compile errors if any
            if (command == null)
            {
                // compilation failed, print errors and return
                rmsCmd.OutputStream.WriteError(string.Join("\r\n", "IronPython Traceback:",
                                                           string.Join("\r\n", errors.Errors.ToArray())));
                return (int)Result.Cancelled;
            }


            try
            {
                script.Execute(scope);
                return (int)(scope.GetVariable("__result__") ?? Result.Succeeded);
            }
            catch (SystemExitException)
            {
                // ok, so the system exited. That was bound to happen...
                return (int)Result.Succeeded;
            }
            catch (Exception exception)
            {
                // show (power) user everything!
                string _dotnet_err_message = exception.ToString();
                string _ipy_err_messages = engine.GetService<ExceptionOperations>().FormatException(exception);

                // Print all errors to stdout and return cancelled to Revit.
                // This is to avoid getting window prompts from Revit.
                // Those pop ups are small and errors are hard to read.
                _ipy_err_messages = string.Join("\r\n", "IronPython Traceback:", _ipy_err_messages);
                _dotnet_err_message = string.Join("\r\n", "Script Executor Traceback:", _dotnet_err_message);

                rmsCmd.OutputStream.WriteError(_ipy_err_messages + "\r\n\r\n" + _dotnet_err_message);
                return (int)Result.Cancelled;
            }
            finally
            {
                if (rmsCmd.LogFile != null)
                    AppendToLog(rmsCmd.LogFile, rmsCmd.OutputWindow.GetContents());
            }
        }

        private void AppendToLog(string logFilePath, string outputContents)
        {
            if (!File.Exists(logFilePath))
            {
                using (StreamWriter logWriter = File.CreateText(logFilePath))
                {
                    logWriter.Write(outputContents);
                }
            }
            else
            {
                using (StreamWriter logWriter = File.AppendText(logFilePath))
                {
                    logWriter.Write(outputContents);
                }
            }
        }

        public string GetAssemblyDirectory()
        {
            return Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
        }

        public string GetCommandServicesModulePath()
        {
            // find RMS/cmdservices from current assembly path (assuming root is 4 levels up)
            var rmsRoot = Directory.GetParent(
                            Directory.GetParent(
                              Directory.GetParent(
                                  Directory.GetParent(GetAssemblyDirectory()).FullName
                                                                                ).FullName
                                                                                    ).FullName
                                                                                        ).FullName;
            var cmdservicesPath = Path.Combine(rmsRoot, "cmdservices");

            return cmdservicesPath;
        }


        private ScriptEngine CreateEngine()
        {
            var engine = IronPython.Hosting.Python.CreateEngine(new Dictionary<string, object>() {
                { "Frames", true },
                { "FullFrames", true },
                { "LightweightScopes", true}
            });

            // Add python stdlib
            AddEmbeddedLib(engine);

            // reference RevitAPI and RevitAPIUI
            engine.Runtime.LoadAssembly(typeof(Autodesk.Revit.DB.Document).Assembly);
            engine.Runtime.LoadAssembly(typeof(Autodesk.Revit.UI.TaskDialog).Assembly);

            // also, allow access to the RMS Executor internals
            engine.Runtime.LoadAssembly(typeof(RMSCmdExecutor.ScriptExecutor).Assembly);

            return engine;
        }


        private void AddEmbeddedLib(ScriptEngine engine)
        {
            // use embedded python lib
            var asm = this.GetType().Assembly;
            var resQuery = from name in asm.GetManifestResourceNames()
                           where name.ToLowerInvariant().EndsWith("python_27_lib.zip")
                           select name;
            var resName = resQuery.Single();
            var importer = new IronPython.Modules.ResourceMetaPathImporter(asm, resName);
            dynamic sys = IronPython.Hosting.Python.GetSysModule(engine);
            sys.meta_path.append(importer);
        }


        public ScriptScope CreateScope(ScriptEngine engine, ref RMSCmdExecutorCommand rmsCmd)
        {
            var scope = IronPython.Hosting.Python.CreateModule(engine, "__main__");

            SetupScope(engine, scope, ref rmsCmd);

            return scope;
        }

        public void SetupScope(ScriptEngine engine, ScriptScope scope, ref RMSCmdExecutorCommand rmsCmd)
        {
            // BUILTINS -----------------------------------------------------------------------------------------------
            // Get builtin to add custom variables
            var builtin = IronPython.Hosting.Python.GetBuiltinModule(engine);

            // Add current IronPython engine to builtins
            builtin.SetVariable("__ipyengine__", engine);

            // Adding output window handle (__window__ is for backwards compatibility)
            builtin.SetVariable("__window__", rmsCmd.OutputWindow);
            builtin.SetVariable("__output__", rmsCmd.OutputWindow);

            // Adding output window stream
            builtin.SetVariable("__outputstream__", rmsCmd.OutputStream);

            // Add host application handle to the builtin to be globally visible everywhere
            builtin.SetVariable("__revit__", _revit);

            // Add handles to current document and ui document
            if (_revit.ActiveUIDocument != null)
            {
                builtin.SetVariable("__activeuidoc__", _revit.ActiveUIDocument);
                builtin.SetVariable("__activedoc__", _revit.ActiveUIDocument.Document);
                builtin.SetVariable("__zerodoc__", false);
            }
            else
            {
                builtin.SetVariable("__activeuidoc__", (Object)null);
                builtin.SetVariable("__activedoc__", (Object)null);
                builtin.SetVariable("__zerodoc__", true);
            }

            // Add this script executor to the the builtin to be globally visible everywhere
            // This support pyrevit functionality to ask information about the current executing command
            builtin.SetVariable("__externalcommand__", rmsCmd);

            // Adding data provided by IExternalCommand.Execute
            builtin.SetVariable("__commanddata__", rmsCmd.CommandData);
            builtin.SetVariable("__elements__", rmsCmd.SelectedElements);

            builtin.SetVariable("__commandpath__", Path.GetDirectoryName(rmsCmd.ScriptSourceFile));
            builtin.SetVariable("__debugmode__", rmsCmd.DebugMode);

            // SCOPE --------------------------------------------------------------------------------------------------
            // Add command info to builtins
            scope.SetVariable("__file__", rmsCmd.ScriptSourceFile);
            scope.SetVariable("__result__", (int)Result.Succeeded);
            scope.SetVariable("__modelname__", rmsCmd.ModelName);
            scope.SetVariable("__outputpath__", rmsCmd.OutputPath);
            scope.SetVariable("__outputprefix__", rmsCmd.OutputPrefix);


        }
    }


    public class ErrorReporter : ErrorListener
    {
        public List<String> Errors = new List<string>();

        public override void ErrorReported(ScriptSource source, string message, SourceSpan span, int errorCode, Severity severity)
        {
            Errors.Add(string.Format("{0} (line {1})", message, span.Start.Line));
        }

        public int Count
        {
            get { return Errors.Count; }
        }
    }
}