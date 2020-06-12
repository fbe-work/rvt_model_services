import os
import sys
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, DetachFromCentralOption, FilePath, ModelPathUtils
from Autodesk.Revit.DB import WorksetConfiguration, WorksetConfigurationOption
from Autodesk.Revit.DB import SaveAsOptions, WorksharingSaveAsOptions, TransmissionData

app = __revit__.Application

print(os.path.basename(__file__))

if not os.environ.get("RVT_QC_PATH"):
    print("no model specified - exiting.")
    sys.exit()

model_path = os.environ["RVT_QC_PATH"]

upgrade_dir = os.path.dirname(os.environ["RVT_QC_PATH"])
dir_files = os.listdir(upgrade_dir)

rvt_models = set()
upgrade_suffix = "_upgraded_to_{}_.rvt".format(app.VersionNumber)

skip_counter = {}
skip_models = {
}

for model in dir_files:
    if not model.endswith(".rvt"):
        skip_counter[model] = "not_a_rvt_model"
        continue
    elif model in skip_models:
        skip_counter[model] = "model_in_skip_list"
        continue
    elif model.endswith(upgrade_suffix):
        skip_counter[model] = "model_is_upgraded_already"
        continue
    elif model.endswith("0001.rvt"):
        skip_counter[model] = "model_is_a_backup_file"
        continue
    elif model + upgrade_suffix in dir_files:
        skip_counter[model] = "model_is_upgraded_already"
        continue
    rvt_models.add(os.path.join(upgrade_dir, model))

for model_name, reason in skip_counter.items():
    print("{}:{}".format(reason.ljust(25), model_name))

print("following {} models found for upgrade:".format(len(rvt_models)))
for model_path in sorted(rvt_models):
    print(model_path)

for model_path in sorted(rvt_models):
    new_target_path = model_path + upgrade_suffix
    rvt_path = FilePath(model_path)
    rvt_model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(model_path)
    print("currently processing: {}".format(model_path))

    ws_conf = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
    open_opt = OpenOptions()
    open_opt.Audit = True
    open_opt.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
    open_opt.SetOpenWorksetsConfiguration(ws_conf)

    save_opt = SaveAsOptions()
    if os.path.exists(new_target_path):
        print("warning! overwriting: {}".format(new_target_path))
        save_opt.OverwriteExistingFile = True

    model_doc = app.OpenDocumentFile(rvt_path, open_opt)
    if model_doc.IsWorkshared:
        ws_opt = WorksharingSaveAsOptions()
        ws_opt.SaveAsCentral = True
        if TransmissionData.IsDocumentTransmitted(rvt_model_path):
            print("removing transmit   : {}".format(model_path))
            ws_opt.ClearTransmitted = True
        save_opt.SetWorksharingOptions(ws_opt)

    print("opened              : {}".format(model_path))
    model_doc.SaveAs(new_target_path, save_opt)
    print("saved as            : {}".format(new_target_path))
    model_doc.Close()
    print("closed")

sys.exit()
