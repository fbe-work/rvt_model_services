# -*- coding: utf-8 -*-
""" bokeh_audit_pulse.py
Usage:
    bokeh_audit_pulse.py
    bokeh_audit_pulse.py      <optional_html_output_path>

Options:
    -h, --help                Show this help screen.
"""

from docopt import docopt
from collections import defaultdict
import os.path as op
from math import pi
import pandas as pd
import numpy as np
from bokeh.charts import Bar, output_file, save
from bokeh.layouts import column

# TODO tick label get first date in month from separate column


def command_get_paths(verbose=False):
    path_dict = defaultdict()

    current_dir = op.dirname(op.abspath(__file__))
    commands_dir = op.dirname(current_dir)
    root_dir = op.dirname(commands_dir)
    journals_dir = op.join(root_dir, "journals")
    logs_dir = op.join(root_dir, "logs")
    warnings_dir = op.join(root_dir, "warnings")

    path_dict["current_file"] = __file__
    path_dict["current_dir"] = current_dir
    path_dict["commands_dir"] = commands_dir
    path_dict["root_dir"] = root_dir
    path_dict["journals_dir"] = journals_dir
    path_dict["logs_dir"] = logs_dir
    path_dict["warnings_dir"] = warnings_dir

    if verbose:
        for pathname in path_dict.keys():
            print("{} - {}".format(pathname, path_dict[pathname]))

    return path_dict


args = docopt(__doc__)
print(args)
paths = command_get_paths(verbose=True)

if args["<optional_html_output_path>"]:
    html_output_path = args["<optional_html_output_path>"]
else:
    html_output_path = ""

html_output = op.join(html_output_path + "rvt_audit_pulse.html")
print(html_output_path)

csv_path = op.join(paths["logs_dir"], "job_logging.csv")

log_lvl_color = {"INFO": "green", "WARNING": "orange", "CRITICAL": "red"}
drop_columns = ["time_stamp", "level", "offset_timestamp", "args", "error_code"]

pd.set_option('display.width', 1800)
df = pd.read_csv(csv_path, sep=";", index_col=False)
df["time_stamp"] = pd.to_datetime(df["time_stamp"], format="%Y-%m-%d")

df_paired = pd.concat([group for _, group in df.copy().groupby("process_hash") if len(group) > 1])

df_paired["offset_timestamp"] = df_paired.time_stamp.shift(1)
df_paired["args"] = df_paired.args.shift(1)

df_ends = df_paired[(df_paired["error_code"] >= 0.0) &
                    (df_paired["args"].str.startswith("<command>=audit"))
                    ].copy()

df_ends["duration"] = (df_ends["time_stamp"] - df_ends["offset_timestamp"]) / np.timedelta64(1, "s")
df_ends["minutes"] = df_ends["time_stamp"].dt.strftime("%Y-%m-%d_%H-%M")

df_ends["color"] = df_ends["level"].copy()
df_ends["color"].replace(log_lvl_color, inplace=True)

df_ends.drop(drop_columns, axis=1)

# loop over all found projects
all_projects = df["project"].unique()
all_plots = []
print(all_projects)

for project in sorted(all_projects):
    print("creating plot for project: {0}".format(project))

    df_project = df_ends[(df_ends["project"] == project)].copy()

    if df_project.empty:
        print("no data yet for project: {0}".format(project))
    else:
        print(df_project.head())

        # Bar.help.builders[0].glyph.line_alpha = 0.0 # no effect?
        plot = Bar(df_project.tail(60), "minutes", values="duration", color="color", title=project,
                   background_fill_alpha=0, border_fill_alpha=0, outline_line_alpha=0,
                   xgrid=False, legend=None, toolbar_location=None,
                   width=900, height=400
                   )

        # plot styling
        plot.axis.axis_label = None
        plot.xaxis.axis_label = None
        plot.axis.major_tick_line_color = None
        plot.axis.minor_tick_line_color = None
        # plot.xaxis[0].ticker.desired_num_ticks = 5
        # plot.xaxis.major_label_text_alpha = 0
        plot.xaxis.major_label_orientation = pi / 2

        for g in plot.renderers:
            if "GlyphRenderer" in str(g.__repr__):
                g.glyph.line_alpha = 0

        all_plots.append(plot)

output_file(html_output, title="rvt_audit_pulse", mode="inline")
save(column(all_plots))
