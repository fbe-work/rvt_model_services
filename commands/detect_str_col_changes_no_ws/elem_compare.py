from collections import defaultdict
from datetime import datetime
from pathlib import Path


def dict_compare(current, previous, mode="added"):
    set_current  = set( current.keys())
    set_previous = set(previous.keys())
    intersect   = set_current.intersection(set_previous)
    if mode == "added":
        return {o:f"{current[o]}" for o in set_current - intersect}
    elif mode == "removed":
        return {o:"<REMOVED>" for o in set_previous - intersect}
    elif mode == "changed":
        return {o:f"{previous[o]}->{current[o]}" for o in intersect if previous[o] != current[o]}
    elif mode == "unchanged":
        return {o:f"{current[o]}" for o in intersect if previous[o] == current[o]}
    else:
        return {}


def print_dict_changes(current, previous, results, results_raw, reduced_header):
    compare_modes = {"added", "removed","changed"}
    change_collector = []
    change_result = {}
    guid = current['GUID']
    rvt_id = current['rvt_id']
    for mode in compare_modes:
        compare_result = dict_compare(current, previous, mode=mode)
        if compare_result:
            print(f"{mode.rjust(7)} door {rvt_id.rjust(10)}: {compare_result}")
            change_collector.append(compare_result)

    if change_collector:
        for change in change_collector:
            # print(change)
            change_result.update(change)
            # print("change_result: ", change_result)

    if "location" in change_result:
        results["moved"].append([guid, rvt_id, "moved", str(change_result)])
        results_raw["moved"].append([guid, rvt_id, "moved", change_result])
        reduced_header.update(change_result)
    else:
        results["changed"].append([guid, rvt_id, "changed", str(change_result)])
        results_raw["changed"].append([guid, rvt_id, "changed", change_result])
        reduced_header.update(change_result)


def compare_elems(current_csv: Path, previous_csv: Path):
    today = datetime.now().strftime("%Y%m%d")

    if not current_csv.exists() or not previous_csv.exists():
        print("please provide with functional paths")
        exit()

    current_root          = current_csv.parent
    result_csv            = current_root / f"{today}_comparison_result.csv"
    result_table_view_csv = current_root / f"{today}_comparison_result_table_view.csv"

    previous_elems = {}
    current_elems  = {}
    results        = defaultdict(list)
    results_raw    = defaultdict(list)
    reduced_header = set()

    with open(current_csv) as txt_file:
        for line in txt_file.readlines():
            if line.startswith("rvt_id"):
                keys = line.strip().replace('"', '').split(";")
                current_header = keys
            else:
                vals = line.strip().replace('"', '').split(";")
                guid = vals[1]
                elem_dict = {k: v for k, v in zip(keys, vals) if v}
                current_elems[guid] = elem_dict

    with open(previous_csv) as txt_file:
        for line in txt_file.readlines():
            if line.startswith("rvt_id"):
                keys = line.strip().replace('"', '').split(";")
            else:
                vals = line.strip().replace('"', '').split(";")
                guid = vals[1]
                elem_dict = {k:v for k,v in zip(keys, vals) if v}
                previous_elems[guid] = elem_dict

    new_elem_ids = []
    for guid in current_elems:
        if guid not in previous_elems:
            rvt_id = current_elems[guid]["rvt_id"]
            new_elem_ids.append(rvt_id)
            results["new"].append([guid, rvt_id, "new"])
            results_raw["new"].append([guid, rvt_id, "new"])

    deleted_elem_ids = []
    for guid in previous_elems:
        if guid not in current_elems:
            rvt_id = previous_elems[guid]["rvt_id"]
            deleted_elem_ids.append(rvt_id)
            results["deleted"].append([guid, rvt_id, "deleted"])
            results_raw["deleted"].append([guid, rvt_id, "new"])

    print(f"{today} - comparing revit element data dumps:\ncurrent:  {current_csv}\nprevious: {previous_csv}")

    print(f"elements in current:  {len(current_elems):>4}")
    print(f"elements in previous: {len(previous_elems):>4}")

    print(23*"=")
    print("    new elements:")
    for elem_id in new_elem_ids:
        print(f"    new elem {elem_id.rjust(10)}")

    print(23*"=")
    print("deleted elements:")
    for elem_id in deleted_elem_ids:
        print(f"deleted elem {elem_id.rjust(10)}")

    print(23*"=")
    print("changed elements:")
    changed_elem_ids = []
    for guid in current_elems:
        curr_elem = current_elems[guid]
        prev_elem = previous_elems.get(guid)
        if not previous_elems.get(guid):
            continue
        if curr_elem != prev_elem:
            changed_elem_ids.append(current_elems[guid]["rvt_id"])
            print_dict_changes(curr_elem, prev_elem, results, results_raw, reduced_header)

    print(23*"=")
    for mode, elems in results.items():
        print(mode.rjust(7), len(elems))

    print(f"writing: {result_csv}")
    with open(result_csv, "w") as res_csv:
        header = f"guid;rvt_id;change_type;changed_parameters"
        res_csv.write(header + "\n")
        for mode in results:
            for elem_data in results[mode]:
                data = ";".join(elem_data)
                res_csv.write(data + "\n")

    print(f"writing: {result_table_view_csv}")
    with open(result_table_view_csv, "w") as res_csv:
        header_prefix = f"guid;rvt_id;change_type;"
        res_csv.write(header_prefix + ";".join(sorted(reduced_header)) + "\n")
        for mode in results_raw:
            for elem_data in results_raw[mode]:
                has_dict_data = isinstance(elem_data[-1], dict)
                if has_dict_data:
                    line_data = elem_data[:-1]
                    line_vals = [elem_data[-1].get(key) or ""  for key in sorted(reduced_header)]
                else:
                    line_data = elem_data
                    line_vals = ["" for key in sorted(reduced_header)]
                line_data.extend(line_vals)
                print(line_data)
                line_data = ";".join(line_data)
                res_csv.write(line_data + "\n")

    if results.get("new") or results.get("moved") or results.get("deleted"):
        changes = {
            "new_ids"    : ";".join(new_elem_ids)     or "",
            "deleted_ids": ";".join(deleted_elem_ids) or "",
            "changed_ids": ";".join(changed_elem_ids) or "",
            "result_table_view_csv": str(result_table_view_csv),
        }
        return changes

