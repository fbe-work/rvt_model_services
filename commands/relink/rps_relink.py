import os
import sys
import json
from collections import defaultdict
import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, DetachFromCentralOption, LinkedFileStatus
from Autodesk.Revit.DB import SaveAsOptions, WorksharingSaveAsOptions, TransmissionData
from Autodesk.Revit.DB import PathType, FilePath, ModelPathUtils, ExternalFileReferenceType
from System.Diagnostics import Stopwatch


def relink_for_ref_type(external_ref_id, ref_types, relink_map):
    global relink_counter
    ext_ref_last_saved = tm_data.GetLastSavedReferenceData(external_ref_id)
    if not ref_types.get(ext_ref_last_saved.ExternalFileReferenceType):
        return
    ref_type_name = ref_types[ext_ref_last_saved.ExternalFileReferenceType]
    ref_link_path = ext_ref_last_saved.GetPath()
    loaded_status = ext_ref_last_saved.GetLinkedFileStatus()
    user_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(ref_link_path)
    ref_name  = os.path.basename(user_path)
    print(" {}: {}  - {}".format(ref_type_name, loaded_status, user_path))

    for search_key in relink_map[ref_type_name]:
        if search_key in ref_name:
            target_user_path = os.path.join(relink_map[ref_type_name][search_key], ref_name)
            target_ref_path  = ModelPathUtils.ConvertUserVisiblePathToModelPath(target_user_path)
            # print(" desired TO>: {}".format(target_user_path))
            tm_data.SetDesiredReferenceData(
                external_ref_id,
                target_ref_path,
                PathType.Relative,
                load_status_map[loaded_status],
            )
            ext_ref_desired   = tm_data.GetDesiredReferenceData(ext_ref_id)
            desired_ref_path  = ext_ref_desired.GetPath()
            desired_user_path = ModelPathUtils.ConvertModelPathToUserVisiblePath(desired_ref_path)
            print(" now TO>: {}".format(desired_user_path))
            print(" found current: {}; target: {}".format(
                os.path.exists(user_path),
                os.path.exists(desired_user_path))
            )
            relink_counter["{}_relink_counter".format(ref_type_name)] += 1
            return


stopwatch = Stopwatch()
stopwatch.Start()

app = __revit__.Application

print(os.path.basename(__file__))

if not os.environ.get("RVT_QC_PATH"):
    print("no model specified - exiting.")
    sys.exit()

model_path = os.environ["RVT_QC_PATH"]

relink_dir = os.path.dirname(os.environ["RVT_QC_PATH"])
dir_files = os.listdir(relink_dir)

relink_json_name = "relink_map.json"
relink_json_path = os.path.join(relink_dir, relink_json_name)
if relink_json_name not in dir_files:
    print("missing move mapping definition '{}' - exiting.".format(relink_json_name))
    sys.exit()

with open(relink_json_path) as json_map:
    relink_map = json.load(json_map)

relink_counter = defaultdict(int)
load_status_map = {
    LinkedFileStatus.Loaded:   True,
    LinkedFileStatus.Unloaded: False,
    LinkedFileStatus.NotFound: True,
}
ref_types = {
    ExternalFileReferenceType.CADLink:   "cad",
    ExternalFileReferenceType.RevitLink: "rvt",
}

rvt_models = set()

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
    elif model.endswith("0001.rvt"):
        skip_counter[model] = "model_is_a_backup_file"
        continue
    rvt_models.add(model)


for model in rvt_models:
    print("\n\n" + 18 * "-+-" + model)
    model_path = os.path.join(relink_dir, model)
    rvt_model_path = FilePath(model_path)
    tm_data = TransmissionData.ReadTransmissionData(rvt_model_path)

    if not tm_data:
        continue

    ext_refs = tm_data.GetAllExternalFileReferenceIds()
    for ext_ref_id in ext_refs:
        target_rvt_path = None
        desired_user_path = None
        print(55 * "-")
        print(ext_ref_id.IntegerValue)

        relink_for_ref_type(ext_ref_id, ref_types, relink_map)

        tm_data.IsTransmitted = True
        TransmissionData.WriteTransmissionData(rvt_model_path, tm_data)

print(55 * "=")
print("revit relink updated:")
for topic, count in relink_counter.items():
    print("{}: {}".format(count, topic))

stopwatch.Stop()
print("in: {}".format(stopwatch.Elapsed))
