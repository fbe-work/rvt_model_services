import os
import sys
import csv
import datetime
import os.path as op
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, DetachFromCentralOption, FilePath
from Autodesk.Revit.DB import WorksetConfiguration, WorksetConfigurationOption

import Autodesk.Revit.UI
from Autodesk.Revit.DB import FilteredElementCollector as Fec
from Autodesk.Revit.DB import FilteredWorksetCollector as Fwc
from Autodesk.Revit.DB import BuiltInCategory, ModelPathUtils, WorksetKind
from System.Diagnostics import Stopwatch


app = __revit__.Application

if "RVT_QC_PRJ" not in os.environ:
    print("no model specified")

else:
    project = os.environ["RVT_QC_PRJ"]
    model_path = os.environ["RVT_QC_PATH"]
    rvt_path = FilePath(model_path)

    ws_conf = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
    open_opt = OpenOptions()
    open_opt.Audit = True
    open_opt.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
    open_opt.SetOpenWorksetsConfiguration(ws_conf)

    try:
        no_ui_doc = app.OpenDocumentFile(rvt_path, open_opt)
        # print("{} - {}".format(project, model_path))
    except:
        # added for models with a specific family corruption blocking the check
        print("loading model {} failed".format(rvt_path))
        sys.exit()


stopwatch = Stopwatch()
stopwatch.Start()

sqft_sqm = 10.764
doc = no_ui_doc


def count_views(view_type):
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.View).ToElements()
    counter = 0
    for view in collector:
        if not view.IsTemplate:
            if view.ViewType.ToString() == view_type:
                counter += 1
    return str(counter)


def count_plan_views():
    plan_view_types = ["AreaPlan", "CeilingPlan", "Detail",
                       "DraftingView", "Elevation", "FloorPlan", "Section"]
    counter = 0
    for view_type in plan_view_types:
        counter += int(count_views(view_type))
    return str(counter)


def count_templateless_plan_views():
    plan_view_types = ["AreaPlan", "CeilingPlan", "Detail",
                       "DraftingView", "Elevation", "FloorPlan", "Section"]
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.View).ToElements()
    counter = 0
    for view in collector:
        if not view.IsTemplate:
            if view.ViewType.ToString() in plan_view_types:
                if view.ViewTemplateId.IntegerValue == -1:
                    counter += 1
    return str(counter)


def all_line_styles():
    line_categs = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Lines)
    return str(line_categs.SubCategories.Size)


def count_fonts():
    fonts = set()
    collector = Fec(doc).OfCategory(BuiltInCategory.OST_TextNotes).WhereElementIsNotElementType().ToElements()
    for txt in collector:
        fonts.add(txt.Symbol.LookupParameter("Text Font").AsString())
    return str(len(fonts))


def count_import_instances(link_type):
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.ImportInstance).ToElements()
    counter = 0
    counter_linked = 0
    counter_imported = 0
    for item in collector:
        if item.IsLinked:
            counter_linked += 1
        if not item.IsLinked:
            counter_imported += 1
    if link_type == "linked":
        counter = counter_linked
    elif link_type == "imported":
        counter = counter_imported
    elif link_type == "all":
        counter = counter_linked + counter_imported
    return str(counter)


def count_non_project_dwg_links(filter_paths):
    counter = 0
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.ImportInstance).ToElements()
    for inst in collector:
        if inst.IsLinked:
            inst_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(doc.GetElement(inst.GetTypeId()).GetExternalFileReference().GetAbsolutePath())
            for img_path in filter_paths:
                if img_path in inst_path:
                    counter += 1
    return str(counter)


def get_pattern(pat_class, name_filter):
    collector = Fec(doc).OfClass(pat_class).ToElements()
    counter = 0
    if name_filter:
        for pat in collector:
            if name_filter in pat.Name:
                counter += 1
        return str(counter)
    else:
        return str(collector.Count)


def count_view_filters_usage(usage_filter):
    filter_count = Fec(doc).OfClass(Autodesk.Revit.DB.FilterElement).ToElements().Count
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.View).ToElements()
    used_filters = set()
    counter = 0
    for view in collector:
        if not view.IsTemplate:
            if not view.ViewType.ToString() == "Schedule":
                try:
                    view_filters = view.GetFilters()
                    for view_filter in view_filters:
                        used_filters.add(doc.GetElement(view_filter).Name)
                except:
                    pass

    if usage_filter == "used":
        counter = len(usage_filter)
    elif usage_filter == "unused":
        counter = filter_count - len(used_filters)
    return str(counter)


def get_unplaced_groups():
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.GroupType).ToElements()
    counter = 0
    for group in collector:
        instances = group.Groups
        if instances.IsEmpty == 1:
            counter += 1
    return str(counter)


def count_raster_images(filtered, filter_paths):
    collector = Fec(doc).OfClass(Autodesk.Revit.DB.ImageType).ToElements()
    if filtered == "all":
        return str(collector.Count)
    if filtered == "non-project":
        counter = 0
        for img in collector:
            for img_path in filter_paths:
                if img_path in img.Path:
                    counter += 1
        return str(counter)


def all_detail_items():
    collector = Fec(doc).OfCategory(BuiltInCategory.OST_DetailComponents).WhereElementIsNotElementType().ToElements()
    counter = 0
    for item in collector:
        if item.Name != "Detail Filled Region":
            counter += 1
    return str(counter)


def count_rooms(filtered):
    collector = Fec(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()
    counter = 0
    if filtered == "all":
        return str(collector.Count)
    elif filtered == "0sqm":
        for room in collector:
            if room.Area < 0.1:
                counter += 1
        return str(counter)


def count_groups(group_type, count_type):
    if group_type == "model":
        if count_type == "types":
            collector = Fec(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsElementType().ToElements()
            return str(collector.Count)
        elif count_type == "instances":
            collector = Fec(doc).OfCategory(BuiltInCategory.OST_IOSModelGroups).WhereElementIsNotElementType().ToElements()
            return str(collector.Count)
    if group_type == "detail":
        if count_type == "types":
            collector = Fec(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsElementType().ToElements()
            return str(collector.Count)
        elif count_type == "instances":
            collector = Fec(doc).OfCategory(BuiltInCategory.OST_IOSDetailGroups).WhereElementIsNotElementType().ToElements()
            return str(collector.Count)


def count_line_styles():
    categories = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Lines)
    return str(categories.SubCategories.Size)


def user_worksets():
    return Fwc(doc).OfKind(WorksetKind.UserWorkset).ToWorksets().Count


def count_line_styles_usage(usage_filter):
    counter = 0
    collector = Fec(doc).OfCategory(BuiltInCategory.OST_Lines).WhereElementIsNotElementType().ToElements()
    doc_styles = int(count_line_styles())
    used_line_styles = set()
    for line in collector:
        used_line_styles.add(line.LineStyle.Name)
    if usage_filter == "used":
        counter = len(used_line_styles)
    elif usage_filter == "unused":
        counter = doc_styles - len(used_line_styles)
    return str(counter)


def count_category_elements(category):
    collector = Fec(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    return str(collector.Count)


def count_class_elements(cls):
    collector = Fec(doc).OfClass(cls).WhereElementIsNotElementType().ToElements()
    return str(collector.Count)


def count_class_type_elements(cls):
    collector = Fec(doc).OfClass(cls).WhereElementIsElementType().ToElements()
    return str(collector.Count)


def sum_sqm(category):
    total_area = 0.0
    collector = Fec(doc).OfCategory(category).WhereElementIsNotElementType().ToElements()
    for area_elem in collector:
        total_area += area_elem.Area
    return str(total_area / sqft_sqm)


def pull_stats(log_data, path="", model_path=""):
    # reading rvt model stats:

    if "RVT_QC_PRJ" in os.environ:
        file_size = str(int(os.path.getsize(model_path))/1000000)

        log_data[0].append(path)  # path
        log_data[0].append(model_path)  # fileName
        log_data[0].append(__file__)  # scriptFileName
        log_data[0].append(check_modules_overview)  # checkModules
        log_data[0].append(file_size)  # q_FileSize
    # v_
    log_data[0].append(count_plan_views())  # v_AllPlanViews
    log_data[0].append(count_views("DrawingSheet"))  # v_AllSheets
    log_data[0].append(count_views("Schedule"))  # v_AllSchedules
    log_data[0].append(count_views("Legend"))  # v_AllLegends
    log_data[0].append(count_class_elements(Autodesk.Revit.DB.FilterElement))  # v_AllViewFilters #view filter narrow down?
    # d_
    log_data[0].append(count_category_elements(BuiltInCategory.OST_TextNotes))  # d_AllText
    log_data[0].append(count_fonts())  # d_AllFonts
    log_data[0].append(count_class_elements(Autodesk.Revit.DB.FilledRegion))  # d_AllFilledRegions
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Dimensions))  # d_AllDimensions
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Lines))  # d_AllLines
    log_data[0].append(all_line_styles())  # d_AllLinesStyles
    log_data[0].append(count_import_instances("imported"))  # q_ImportedDWG
    log_data[0].append(get_pattern(Autodesk.Revit.DB.LinePatternElement, "IMPORT"))  # q_ImportedLinePattern
    log_data[0].append(get_pattern(Autodesk.Revit.DB.FillPatternElement, "IMPORT"))  # q_ImportedFillPattern
    log_data[0].append(count_view_filters_usage("unused"))  # v_UnusedViewFilters
    # q_
    log_data[0].append(count_line_styles_usage("unused"))  # q_UnusedStyles
    # g_
    log_data[0].append(get_unplaced_groups())  # g_UnplacedGroups
    # d_
    log_data[0].append(all_detail_items())  # d_AllDetailItems
    # e_
    log_data[0].append(count_rooms("all"))  # e_AllRooms
    log_data[0].append(count_rooms("0sqm"))  # e_0qmRooms
    # v_
    log_data[0].append(count_templateless_plan_views())  # v_noVTPlanViews
    # g_
    log_data[0].append(count_groups("model", "types"))  # g_AllModelGroups
    log_data[0].append(count_groups("model", "instances"))  # g_AllModelGroupInstances
    log_data[0].append(count_groups("detail", "types"))  # g_AllDetailGroups
    log_data[0].append(count_groups("detail", "instances"))  # g_AllDetailGroupInstances
    # q_
    log_data[0].append(count_non_project_dwg_links(non_project_paths))  # q_nonProjectPathDWGLinks
    log_data[0].append(count_raster_images("non-project", non_project_paths))  # q_nonProjectPathRasterImages

    # addon_
    log_data[0].append(get_pattern(Autodesk.Revit.DB.LinePatternElement, ""))  # AllLinePatterns
    log_data[0].append(get_pattern(Autodesk.Revit.DB.FillPatternElement, ""))  # AllFillPatterns
    log_data[0].append(count_raster_images("all", None))  # AllRasterImages
    log_data[0].append(count_line_styles())  # AllLineStyles
    log_data[0].append(count_import_instances("all"))  # AllLinksImports

    # q_
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Constraints))  # AllConstraints
    log_data[0].append(count_line_styles_usage("used"))  # UsedLineStyles
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Grids))  # AllGrids
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Walls))  # AllWalls
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Windows))  # AllWindows
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Doors))  # AllDoors
    log_data[0].append(count_category_elements(BuiltInCategory.OST_RevisionClouds))  # AllRevisionClouds
    log_data[0].append(count_category_elements(BuiltInCategory.OST_VolumeOfInterest))  # AllScopeBoxes
    log_data[0].append(sum_sqm(BuiltInCategory.OST_Rooms))  # AllRoomsSQM
    log_data[0].append(sum_sqm(BuiltInCategory.OST_Areas))  # AllAreasSQM
    log_data[0].append(count_class_type_elements(Autodesk.Revit.DB.FilledRegionType))  # FilledRegionTypes
    log_data[0].append(count_category_elements(BuiltInCategory.OST_Revisions))  # RevisionSets

    return log_data


check_modules = ["QC_ScriptRuntime", "timeStamp", "path", "fileName", "scriptFileName", "checkModules", "q_FileSize",
                 "v_AllPlanViews", "v_AllSheets", "v_AllSchedules", "v_AllLegends", "v_AllViewFilters",
                 "d_AllText", "d_AllFonts", "d_AllFilledRegions", "d_AllDimensions", "d_AllLines", "d_AllLinesStyles",
                 "q_ImportedDWG", "q_ImportedLinePattern", "q_ImportedFillPattern", "v_UnusedViewFilters",
                 "q_UnusedStyles", "g_UnplacedGroups", "d_AllDetailItems", "e_AllRooms", "e_0qmRooms",
                 "v_noVTPlanViews", "g_AllModelGroups", "g_AllModelGroupInstances", "g_AllDetailGroups",
                 "g_AllDetailGroupInstances", "q_nonProjectPathDWGLinks", "q_nonProjectPathRasterImages",
                 "s_AllLinePatterns", "s_AllFillPatterns", "l_AllRasterImages", "s_AllLineStyles", "l_AllLinksImports",
                 "e_AllConstraints", "s_UsedLineStyles", "e_AllGrids", "e_AllWalls", "e_AllWindows", "e_AllDoors",
                 "e_AllRevisionClouds", "e_AllScopeBoxes", "m_AllRoomsSQM", "m_AllAreasSQM", "s_FilledRegionTypes",
                 "e_RevisionSets"
                 ]

check_modules_overview = ";".join(["{}".format(m) for m in check_modules])

non_project_paths = ["U:", "D:", "C:"]
path = os.getcwd()
time_stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")

qc_path = op.dirname(op.abspath(__file__))
commands_dir = op.dirname(qc_path)
root_dir = op.dirname(commands_dir)

log_header = check_modules_overview + "\n"
log_data = [[time_stamp]]  # timeStamp

if "RVT_QC_PRJ" in os.environ:
    project = os.environ["RVT_QC_PRJ"]
    model_path = os.environ["RVT_QC_PATH"]
    log_dir = os.environ["RVT_LOG_PATH"]

    print('QC_DIR: {}'.format(qc_path))
    print('ROOT_DIR: {}'.format(root_dir))
    print('LOG_DIR: {}'.format(log_dir))
    print('COMMANDS_DIR: {}'.format(commands_dir))

    log_file = op.join(log_dir, project + ".csv")
    log_data = pull_stats(log_data, path, model_path)

    stopwatch.Stop()
    timespan = stopwatch.Elapsed

    # prepend the script run time
    run_time = [[str(timespan)]]
    run_time[0].extend(log_data[0])

    if not op.exists(log_file):
        with open(log_file, "w") as _log:
            _log.write(log_header)

    with open(log_file, "a") as csv_file:
        writer = csv.writer(csv_file, delimiter=';', lineterminator='\n')
        writer.writerows(run_time)

else:
    for stats in pull_stats(log_data, path="", model_path=""):
        for mod, stat in zip(check_modules[6:], stats):
            print("{} - {}".format(mod, stat))
    print(50 * "-")
    print("ERROR - environment variable not found - not writing to log!! \nfind model stats above.")

# __window__.Close()
