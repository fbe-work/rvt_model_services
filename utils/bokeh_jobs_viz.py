import pandas as pd
from bokeh.plotting import figure, save, output_file
from bokeh.palettes import viridis
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, HoverTool

# TODO optional separate charts per command groupby(?)


def style_plot(plot):
    plot.outline_line_color = None
    plot.axis.axis_label = None
    plot.axis.axis_line_color = None
    plot.axis.major_tick_line_color = None
    plot.axis.minor_tick_line_color = None
    plot.ygrid.grid_line_color = None
    plot.xgrid.grid_line_color = None
    plot.xaxis.formatter = DatetimeTickFormatter(hours=["%H:%M"],
                                                 days=["%H:%M"],
                                                 months=["%H:%M"],
                                                 years=["%H:%M"],
                                                 )

    plot.title.text_font_size = "14pt"
    return plot


def update_graph(jobs_db, graph_path):
    rows = []
    for job in jobs_db.all():
        rows.append([job.get("<project_code>"), job.get("<command>"), job.get(">start_time"), job.get("timeout")])

    df = pd.DataFrame(rows, columns=["project", "command", "start", "timeout"])
    df = df.sort_values(by="project", ascending=False)
    df["start"] = pd.to_datetime(df["start"], format="%H:%M:%S")
    df["start_txt"] = df.start.astype("str").str.extract(r"(\d+:\d+)", expand=True) + " h"
    df["timeout_txt"] = df['timeout'].copy().astype('str') + " seconds"
    df["timeout"] = df['timeout'].astype('timedelta64[s]')
    df["end"] = pd.to_datetime(df["start"], format="%H:%M:%S") + df["timeout"]

    colors = viridis(len(df["project"]))
    output_file(graph_path, title="rvt_model_services_jobs", mode="inline")

    cds = ColumnDataSource(data=dict(start=df["start"].values,
                                     end=df["end"].values,
                                     name=df["project"],
                                     timeout=df["timeout_txt"],
                                     start_txt=df["start_txt"],
                                     command=df["command"],
                                     color=colors,
                                     )
                           )

    hover = HoverTool(tooltips=[("project", "@name"),
                                ("command", "@command"),
                                ("start time:", "@start_txt"),
                                ("timeout:", "@timeout"),
                                ])

    tools_opt = [hover, "save", "pan", "wheel_zoom", "box_zoom", "reset"]
    graph_opt = dict(width=900, x_axis_type="datetime",
                     tools=tools_opt,
                     toolbar_location="right",
                     background_fill_alpha=0, border_fill_alpha=0)
    jobs_viz = figure(title="rvt_model_service_jobs",
                      y_range=list(df["project"].unique()),
                      **graph_opt)
    jobs_viz.hbar(source=cds,
                  y="name",
                  left="start",
                  right="end",
                  height=1,
                  color="color",
                  )

    style_plot(jobs_viz)
    save(jobs_viz)
