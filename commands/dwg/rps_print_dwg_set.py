import os
from System.Collections.Generic import List
from datetime import datetime
from Autodesk.Revit.DB import FilteredElementCollector as Fec
from Autodesk.Revit.DB import DWGExportOptions, ViewSheetSet, ViewSet, Transaction, ElementId

doc = __revit__.ActiveUIDocument.Document

path_param = "Auto_PDF_DWF_Path"
sheet_set_name = "Auto_PDF_DWG"
fileType = "_DWG\\"

if doc.ProjectInformation.BuildingName:
    building = doc.ProjectInformation.BuildingName
    base_path = doc.ProjectInformation.LookupParameter(path_param).AsString()
    today = datetime.now().strftime("%y%m%d")
    export_path = base_path + today + fileType

    if not os.path.exists(export_path):
        os.makedirs(export_path)

    view_sheet_sets = Fec(doc).OfClass(ViewSheetSet)

    # "Start" the transaction
    t = Transaction(doc, sheet_set_name)
    t.Start()

    for view_sheet_set in view_sheet_sets:
            if view_sheet_set.Name == sheet_set_name:
                views = []
                for view in view_sheet_set.Views:
                    views.append(view.Id)
                view_list = List[ElementId](views)    
                dwg_opt = DWGExportOptions()
                dwg_opt.ExportingAreas = True
                doc.Export(export_path, building, view_list, dwg_opt)

    # "End" the transaction
    t.Commit()
__window__.Close()
