import os
import re
from pathlib import Path
from . import elem_compare
from notify.email import send_mail
from utils import dir_purger


def data_pickup_and_compare(project_code):
    model_path  = os.environ["RVT_QC_PATH"]
    model_title = os.path.basename(model_path).split(".rvt")[0]

    re_string = r"\d{8}_\d{4}_" + model_title + r".+_StructuralColumns\.csv"
    re_dump = re.compile(re_string)

    found_data_dumps = {}
    for node in DATA_DUMPS_DIR.iterdir():
        if re.match(re_dump, node.name):
            found_data_dumps[node.name] = node

    if len(found_data_dumps) < 2:
        print("not enough matching data dumps found")
        return

    last_two_data_dumps = sorted(found_data_dumps)[-2:]
    found_changes = elem_compare.compare_elems(
        Path(found_data_dumps[last_two_data_dumps[-1]]),  # current data_dump
        Path(found_data_dumps[last_two_data_dumps[-2]]),  # one data_dump before
    )
    if found_changes:
        print("would notify on: ", found_changes)
        send_mail.notify(
            project_code,
            model_path,
            found_changes,
            subject="structural columns change!",
            attachment=found_changes["result_table_view_csv"]
        )
    dir_purger.purge_old(directory=DATA_DUMPS_DIR, extension="csv")


DATA_DUMPS_DIR = Path(__file__).parent.parent.parent / "data_dumps"
