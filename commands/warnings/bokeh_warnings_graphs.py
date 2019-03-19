# -*- coding: utf-8 -*-
""" bokeh_warnings_graphs.py
Usage:
    bokeh_warnings_graphs.py        <project_code> [options]

Arguments:
    project_code                    unique project code consisting of 'projectnumber_projectModelPart' 
                                    like 456_11 , 416_T99 or 123_N

Options:
    -h, --help                      Show this help screen.
    --html_path=<html>              path to store html bokeh graphs, default in /commands/qc/*.html 
"""

from docopt import docopt
import os.path as op
from collections import defaultdict
from bs4 import BeautifulSoup
import re
import pandas as pd
import datetime
import colorful
from bokeh.plotting import figure, output_file, save, ColumnDataSource
from bokeh.layouts import column
from bokeh.models import Legend, Plot, Square, Range1d, Text, HoverTool
from bokeh.palettes import viridis
from bokeh.models import DatetimeTickFormatter

# TODO categorize warnings
# TODO adjust bokeh graph accordingly


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


def timestamp_now():
    return datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")


def read_warning_html(html_warnings_file):
    warning_ids = defaultdict(list)
    warning_count = defaultdict(int)

    with open(html_warnings_file, 'r', encoding="utf-16") as html_warnings:
        data = html_warnings.read()

        soup = BeautifulSoup(data, "html.parser")

        h1s = soup.findAll("h1")
        re_h1_date = re.compile(r"\((.*)\)")
        p_date = re_h1_date.findall(h1s[0].text)
        warn_time_stamp = datetime.datetime.strptime(p_date[0], "%d.%m.%Y %H:%M:%S")
        iso_time_stamp = warn_time_stamp.strftime("%Y-%m-%d %H:%M:%S")

        warning_table = soup.findAll("td")
        pattern = re.compile(r"\bid\s*?(\d+)")
        id_line = re.compile(r" : ")
        last_seen_err_type = ""

        for line in warning_table:
            err_ids = []
            if id_line.findall(line.text):
                for elem_id in pattern.findall(line.text):
                    err_ids.append(elem_id)
                warning_ids[last_seen_err_type] = err_ids
            else:
                err_type = line.text.strip()
                last_seen_err_type = err_type
                warning_count[err_type] += 1

        html_warnings_df = pd.DataFrame({iso_time_stamp: warning_count})
        warnings_id_df = pd.DataFrame({iso_time_stamp: warning_ids})
        print(warning_ids)
        return html_warnings_df, warnings_id_df


def read_warning_json(warnings_json):
    warnings_df = None
    if op.exists(warnings_json):
        with open(warnings_json, 'r', encoding="utf-8") as warn_json:
            warnings_df = pd.read_json(warn_json, orient="index")
    return warnings_df


def write_df_to_json(df, json_file):
    with open(json_file, 'w', encoding="utf-8") as jsn:
        df.to_json(jsn, orient="index", date_format="iso")


def write_bokeh_graph(data_frame, html_output, project_code):
    df_tp = data_frame.T
    df_tp.index = pd.to_datetime(df_tp.index)
    df_tp.sort_index(inplace=True)
    df_columns_count = df_tp.shape[0]
    df_rows_count = df_tp.shape[1]
    colors = viridis(len(df_tp.columns))

    # option_sets
    hover = HoverTool(tooltips=[("name", "@name"),
                                ("time", "@time"),
                                ("count", "@count"),
                                ]
                      )
    tools_opt = [hover, "save", "pan", "wheel_zoom", "reset"]
    graph_opt = dict(width=900, x_axis_type="datetime",
                     toolbar_location="left", tools=tools_opt, toolbar_sticky=False,
                     background_fill_alpha=0, border_fill_alpha=0,
                     )
    line_opt = dict(line_width=3, alpha=0.8)
    output_file(html_output, mode="inline")

    legend_items = []

    # figure and line glyphs
    warning_figure = figure(title=project_code + " rvt warnings",
                            **graph_opt,
                            )

    for i, warning_type in enumerate(df_tp.columns):
        # print(f"df_tp.index is: \n{df_tp.index}")
        line_name_dict = [warning_type for _ in range(df_columns_count)]
        cds = ColumnDataSource(data=dict(x=df_tp.index,
                                         y=df_tp[warning_type],
                                         name=line_name_dict,
                                         count=df_tp[warning_type],
                                         time=df_tp.index.strftime("%Y-%m-%d %H:%M:%S"),
                                         )
                               )
        warning_figure.line("x",
                            "y",
                            color=colors[i],
                            name="name",
                            source=cds,
                            **line_opt
                            )
        legend_items.append((warning_type, colors[i]))

    square_size, legend_sq_offset = 20, 20
    legend_plot_height = df_rows_count * (legend_sq_offset + square_size)
    # print(f"plot height is: {legend_plot_height}")

    legend = Plot(plot_width=900,
                  plot_height=legend_plot_height,
                  x_range=Range1d(0, 300),
                  y_range=Range1d(0, legend_plot_height),
                  toolbar_location="left",
                  background_fill_alpha=0,
                  border_fill_alpha=0,
                  outline_line_alpha=0,
                  )

    for i, item in enumerate(legend_items):
        warn_type = item[0]
        color = item[1]

        square_y_pos = legend_plot_height - legend_sq_offset - i * (legend_sq_offset + square_size)

        square = Square(x=square_size,
                        y=square_y_pos,
                        size=square_size,
                        fill_color=color,
                        line_alpha=0,
                        )
        legend.add_glyph(square)

        warning_count_text = str(df_tp[warn_type][-1]).rjust(5)
        warning_text = warn_type

        count_txt = Text(x=square_size + 15,
                         y=square_y_pos,
                         text_align="right",
                         text_baseline="middle",
                         text=[warning_count_text],
                         text_font_size="10pt",
                         )
        legend.add_glyph(count_txt)
        warn_txt = Text(x=square_size + 16,
                        y=square_y_pos,
                        text_align="left",
                        text_baseline="middle",
                        text=[warning_text[:120]],
                        text_font_size="10pt",
                        )
        legend.add_glyph(warn_txt)

    save(column(style_plot(warning_figure), legend))
    print(colorful.bold_green(f" {html_output}\n updated successfully."))
    return df_tp


def style_plot(plot):
    # axis styling, legend styling
    plot.outline_line_color = None
    plot.axis.axis_label = None
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.axis.minor_tick_line_color = None
    plot.xgrid.grid_line_color = None
    plot.xaxis.formatter = DatetimeTickFormatter(hours=["%d %b %Y"],
                                                 days=["%d %b %Y"],
                                                 months=["%d %b %Y"],
                                                 years=["%d %b %Y"]
                                                 )
    #plot.legend.location = "top_left"
    #plot.legend.border_line_alpha = 0
    #plot.legend.background_fill_alpha = 0
    plot.title.text_font_size = "14pt"
    return plot


def update_json_and_bokeh(project_code, bokeh_html_path="", ids_path=""):
    paths = command_get_paths()

    if not bokeh_html_path:
        bokeh_html_path = paths["current_dir"]

    warning_html = project_code + ".html"
    html_exists = op.exists(op.join(paths["warnings_dir"], warning_html))

    warning_json = op.join(paths["warnings_dir"], warning_html.split(".")[0] + ".json")

    if html_exists:
        warn_df, warn_ids_df = read_warning_html(op.join(paths["warnings_dir"], warning_html))
        warning_html_date = str(warn_df.columns[0])

        print(colorful.bold_orange("\n-read warnings in html: \n"))
        print(warn_df.head())
        if ids_path:
            print(warn_ids_df.head())
            warn_ids_json = op.join(ids_path, warning_html.split(".")[0] + "_warning_ids.json")
            write_df_to_json(warn_ids_df, warn_ids_json)
        warnings_merged = warn_df

        json_update = True
        json_exists = op.exists(warning_json)

        if json_exists:
            existing_warnings = read_warning_json(warning_json)
            warnings_merged = existing_warnings
            print(existing_warnings.columns)

            existing_readout_timestamps = existing_warnings.columns

            print(colorful.bold_orange("\n-existing warnings in json: \n"))
            print(existing_warnings.head())

            if warning_html_date not in existing_readout_timestamps:
                print(colorful.bold_orange("\n-new warnings found - adding it to json."))
                warnings_merged = pd.concat([warn_df, existing_warnings], axis=1, join="inner")
                print(colorful.bold_orange("-merged warnings to json: \n"))
                print(warnings_merged.head())
                write_df_to_json(warnings_merged,
                                 op.join(paths["warnings_dir"], warning_html.split(".")[0] + ".json"))
            else:
                print(colorful.bold_orange("\n-html warnings already in json."))
                # warnings_merged = existing_warnings
                json_update = False

        if json_update:
            write_df_to_json(warnings_merged, warning_json)

        bokeh_html = op.join(bokeh_html_path, warning_html + "warnings_graph.html")
        bokeh_df = write_bokeh_graph(warnings_merged, bokeh_html, project_code)
        return bokeh_df


pd.set_option('display.width', 1800)

if __name__ == "__main__":

    args = docopt(__doc__)
    project_code = args["<project_code>"]
    html_path = args["--html_path"]

    paths = command_get_paths()

    if not html_path:
        html_path = paths["current_dir"]

    # debug mock:
    # project_code = "123_N"
    # paths = command_get_paths()
    # html_path = paths["current_dir"]

    if op.exists("warning_weighting_custom.csv"):
        warn_weighting = "warning_weighting_custom.csv"
    else:
        warn_weighting = "warning_weighting_template.csv"

    print(f"command args: {args}")

    update_df = update_json_and_bokeh(project_code, html_path)
