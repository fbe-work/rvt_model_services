# -*- coding: utf-8 -*-
""" bokeh_qc_graphs.py
Usage:
    bokeh_qc_graphs.py  [options]
                        <project_code> 

Arguments:
    project_code        unique project code consisting of 'projectnumber_projectModelPart' 
                        like 456_11 , 416_T99 or 377_S

Options:
    -h, --help          Show this help screen.
    --html_path=<html>  path to store html bokeh graphs, default in /commands/qc/*.html 
"""

from docopt import docopt
import os.path as op
import os
import colorful
import pandas as pd
from bokeh.palettes import viridis
from bokeh.models import ColumnDataSource
from bokeh.models import DatetimeTickFormatter, HoverTool
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column

# TODO submissions optional -> submissions disabled


def graph(_csv, _project_code, graph_topics):
    figures = []
    graph_x_range = None
    for topic in graph_topics.keys():
        # data source
        csv_topic = _csv.copy().filter(regex=topic)
        csv_topic["timeStamp"] = _csv.timeStamp.copy()
        csv_topic.set_index('timeStamp', inplace=True)
        csv_topic.index = pd.to_datetime(csv_topic.index)
        csv_topic.sort_index(inplace=True)
        df_columns_count = csv_topic.shape[1]
        df_rows_count = csv_topic.shape[0]

        colors = viridis(df_columns_count)

        topic_title = f"{_project_code} - RVT - {graph_topics[topic]}"

        # print(topic_title)
        # print(csv_topic.head())

        line_opt = dict(line_width=3, alpha=0.8)
        hover = HoverTool(tooltips=[("name", "@name"),
                                    ("time", "@time"),
                                    ("count", "@count"),
                                    ]
                          )
        tools_opt = ["resize", hover, "save", "pan", "wheel_zoom", "reset"]
        graph_opt = dict(width=900, x_axis_type="datetime",
                         toolbar_location="left", tools=tools_opt, toolbar_sticky=False,
                         background_fill_alpha=0, border_fill_alpha=0)

        if graph_x_range:
            topic_figure = figure(title=topic_title, x_range=graph_x_range, **graph_opt)
        else:
            topic_figure = figure(title=topic_title, **graph_opt)
            graph_x_range = topic_figure.x_range

        # glyphs
        # print(len(cds.column_names))
        for i, col_name in enumerate(csv_topic.columns):
            if topic in col_name:
                # print(col_name)
                csv_topic["color"] = colors[i]
                name_list = [col_name[2:] for i in range(df_rows_count)]

                cds = ColumnDataSource(data=dict(x=csv_topic.index.values,
                                                 y=csv_topic[col_name].values,
                                                 name=name_list,
                                                 count=csv_topic[col_name].values,
                                                 time=csv_topic.index.strftime("%Y-%m-%d %H:%M:%S"),
                                                 )
                                       )

                topic_figure.line("x", "y",
                                  color=colors[i], name="name", source=cds, legend=col_name[2:],
                                  **line_opt
                                  )

        figures.append(style_plot(topic_figure))

    return figures


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
    plot.legend.location = "top_left"
    plot.legend.border_line_alpha = 0
    plot.legend.background_fill_alpha = 0
    plot.title.text_font_size = "14pt"
    return plot


def submission_bars():
    """
    bar_opt = dict(fill_alpha=0.3, fill_color='orange', line_alpha=0)
    
    subm = {"A": [2016, 2, 17],
        "B": [2016, 3, 24],
        "C": [2016, 5, 17],
        "D": [2016, 6, 27],
        "E": [2016, 8, 5],
        "F": [2016, 9, 23],
        "H": [2016, 10, 30],
        "G": [2016, 11, 16],
        "I": [2017, 2, 17],
        }

    for k in subm.values():
        js_left = int(time.mktime(datetime.date(k[0], k[1], k[2]).timetuple())) * 1000
        js_right = int(time.mktime(datetime.date(k[0], k[1], k[2] + 1).timetuple())) * 1000

        for fig in [g, q, v, e, d, l, s, m]:
            fig.add_layout(BoxAnnotation(left=js_left, right=js_right, **bar_opt))
            # fig.add_glyph(Text(x=js_right, y=0, angle=90, angle_units="deg",
            #                   text=["abgabe"], text_color="#cccccc", text_font_size="5pt"))

    :return: 
    """
    pass


def update_graphs(project_code, html_path):
    pd.set_option('display.width', 1800)
    html_path = op.join(html_path, "{0}.html".format(project_code))

    qc_path = op.dirname(op.abspath(__file__))
    commands_dir = op.dirname(qc_path)
    root_dir = op.dirname(commands_dir)
    log_dir = op.join(root_dir, "logs")

    csv_path = op.join(log_dir, project_code + ".csv")

    csv = pd.read_csv(csv_path, delimiter=";")
    csv.timeStamp = pd.to_datetime(csv.timeStamp)

    output_file(html_path, mode="inline")

    topics = {"q_": "QC",
              "l_": "LINKS",
              "g_": "GROUPS",
              "v_": "VIEWS",
              "d_": "2D",
              "s_": "STYLES",
              "e_": "ELEMENTS",
              "m_": "PROJECT_SQM",
              }

    graphs = graph(csv, project_code, topics)

    save(column(graphs), validate=False)
    print(colorful.bold_green(f" {html_path} updated successfully."))


if __name__ == "__main__":

    args = docopt(__doc__)
    project_code = args["<project_code>"]
    html_path = args["--html_path"]
    qc_path = op.dirname(op.abspath(__file__))
    """

    html_path = op.dirname(op.abspath(__file__))
    project_code = "123_N"
    """

    print(f"command args: {args}")
    if not html_path:
        html_path = qc_path

    update_graphs(project_code, html_path)
