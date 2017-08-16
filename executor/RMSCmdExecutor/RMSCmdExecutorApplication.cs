using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using System.Xml.Linq;
using Autodesk.Revit;
using Autodesk.Revit.UI;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Configuration;
using System.Collections.Specialized;

namespace RMSCmdExecutor
{
    [Regeneration(RegenerationOption.Manual)]
    [Transaction(TransactionMode.Manual)]
    class RMSCmdExecutorApp : IExternalApplication
    {
        // Hook into Revit to allow starting a command.
        Result IExternalApplication.OnStartup(UIControlledApplication application)
        {

            try
            {
                RegisterExternalCommand(application);
                return Result.Succeeded;
            }
            catch (Exception ex)
            {
                TaskDialog.Show("Error setting up RMSCmdExecutor", ex.ToString());
                return Result.Failed;
            }
        }

        private static void RegisterExternalCommand(UIControlledApplication application)
        {
            var assembly = typeof(RMSCmdExecutorApp).Assembly;

            RibbonPanel ribbonPanel = application.CreateRibbonPanel("  Revit Model Services (RMS)  ");

            // Run service button
            var smallImage = GetEmbeddedPng(assembly, "RMSCmdExecutor.Resources.RMS-16.png");
            var largeImage = GetEmbeddedPng(assembly, "RMSCmdExecutor.Resources.RMS-32.png");
            PushButtonData executeRMSCommand = new PushButtonData("RMSCmdExecutorCommand",
                                                                  "Run RMS\nService",
                                                                  assembly.Location,
                                                                  "RMSCmdExecutor.RMSCmdExecutorCommand");
            executeRMSCommand.Image = smallImage;
            executeRMSCommand.LargeImage = largeImage;
            executeRMSCommand.AvailabilityClassName = "RMSCmdExecutor.RMSCmdExecutorCommandAvail";



            // Git repo link button
            smallImage = GetEmbeddedPng(assembly, "RMSCmdExecutor.Resources.GitHubFilled-16.png");
            largeImage = GetEmbeddedPng(assembly, "RMSCmdExecutor.Resources.GitHubFilled-32.png");
            PushButtonData RMSRepoLinkCommand = new PushButtonData("RMSGitRepoLinkCommand",
                                                                   "Open RMS\nGit Repo",
                                                                   assembly.Location,
                                                                   "RMSCmdExecutor.RMSGitRepoLinkCommand");
            RMSRepoLinkCommand.Image = smallImage;
            RMSRepoLinkCommand.LargeImage = largeImage;
            RMSRepoLinkCommand.AvailabilityClassName = "RMSCmdExecutor.RMSGitRepoLinkCommandAvail";


            // Add both buttons to ribbon
            ribbonPanel.AddItem(executeRMSCommand);
            ribbonPanel.AddItem(RMSRepoLinkCommand);
        }


        private static ImageSource GetEmbeddedPng(System.Reflection.Assembly app, string imageName)
        {
            var file = app.GetManifestResourceStream(imageName);
            var source = PngBitmapDecoder.Create(file, BitmapCreateOptions.None, BitmapCacheOption.None);
            return source.Frames[0];
        }


        Result IExternalApplication.OnShutdown(UIControlledApplication application)
        {
            return Result.Succeeded;
        }
    }
}
