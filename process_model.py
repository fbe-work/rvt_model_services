""" process_model.py
Usage:
    process_model.py    [options] 
                        <command> <project_code> 
                        <revit_model_path> <revit_model_file_name> 
                        <revit_version_path> <revit_version> <timeout>

Arguments:
    command             action to be run on model, like: qc or dwf
                        currently available: qc, dwf
    project_code        unique project code consisting of 'projectnumber_projectModelPart' 
                        like 456_11 , 416_T99 or 377_S
    model_path          revit model path without file name
    model_file_name     revit model file name
    rvt_version_path    revit .exe path of appropriate version like: 
                        "C:/Program Files/Autodesk/Revit Architecture 2015/Revit.exe"
    rvt_version         the revit main version number like: 2015
    timeout             timeout in seconds before revit process gets terminated

Options:
    -h, --help          Show this help screen.
    --html_path=<html>  path to store html bokeh graphs, default in /commands/qc/*.html
"""

from docopt import docopt
import os.path as op
import os
import subprocess
import psutil
import time
import logging
import colorful
import rps_xml
import rvt_journal_writer
from commands.qc.bokeh_qc_graphs import update_graphs
from commands.warn.bokeh_warnings_graphs import update_json_and_bokeh

# TODO write model not found to log -> to main log from logging
# TODO write log header if log not exists with logging module?
# TODO implement audit option
# TODO make rvt_pulse available from process model?


def rvt_journal_run(program, journal_file):
    return psutil.Popen([program, journal_file], cwd=root_dir,
                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


print(colorful.bold_blue("+process model job control started"))
args = docopt(__doc__)

command = args["<command>"]
project_code = args["<project_code>"]
model_path = args["<revit_model_path>"]
model_file_name = args["<revit_model_file_name>"]
rvt_version_path = args["<revit_version_path>"]
rvt_version = args["<revit_version>"]
timeout = int(args["<timeout>"])
html_path = args["--html_path"]

semicolon_concat_args = ";".join([f"{k}={v}" for k, v in args.items()])
comma_concat_args = ",".join([f"{k}={v}" for k, v in args.items()])

root_dir = op.dirname(op.abspath(__file__))
log_dir = op.join(root_dir, "logs")
warnings_dir = op.join(root_dir, "warnings" + op.sep)
journals_dir = op.join(root_dir, "journals")
commands_dir = op.join(root_dir, "commands")
qc_dir = op.join(commands_dir, "qc")
warn_dir = op.join(commands_dir, "warn")

print(colorful.bold_orange('-detected following path structure:'))
print(f' ROOT_DIR:     {root_dir}')
print(f' LOG_DIR:      {log_dir}')
print(f' WARNINGS_DIR: {warnings_dir}')
print(f' JOURNALS_DIR: {journals_dir}')
print(f' COMMANDS_DIR: {commands_dir}')
print(f' QC_DIR:       {qc_dir}')

rvt_model_path = model_path + model_file_name
journal_file_path = op.join(journals_dir, project_code + ".txt")
model_exists = op.exists(rvt_model_path)

if not html_path:
    if command == "qc":
        html_path = qc_dir
    elif command == "warnings":
        html_path = warn_dir
elif not os.path.exists(html_path):
    if command == "qc":
        html_path = qc_dir
        print(f"your specified html path was not found - html graph will be exported to {qc_dir} instead")
    elif command == "warnings":
        html_path = warn_dir
        print(f"your specified html path was not found - html graph will be exported to {warn_dir} instead")

job_logging = op.join(log_dir, "job_logging.csv")
header_logging = "time_stamp;level;project;process_hash;error_code;args\n"
if not op.exists(job_logging):
    with open(job_logging, "w") as logging_file:
        logging_file.write(header_logging)
    print(colorful.bold_blue(f"logging goes to: {job_logging}"))

logging.basicConfig(format='%(asctime)s;%(levelname)s;%(message)s',
                    datefmt="%Y%m%dT%H%M%SZ",
                    filename=job_logging,
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("bokeh").setLevel(logging.CRITICAL)

print(colorful.bold_orange('-detected following process structure:'))
current_proc_hash = hash(psutil.Process())
print(f" current process hash: {colorful.cyan(current_proc_hash)}")
logging.info(f"{project_code};{current_proc_hash};;{comma_concat_args};{'task_started'}")

os.environ["RVT_QC_PRJ"] = project_code
os.environ["RVT_QC_PATH"] = rvt_model_path
os.environ["RVT_LOG_PATH"] = log_dir

if model_exists:

    cmd_dict = {"qc": rps_xml.get_rps_button(rps_xml.find_xml_command(rvt_version, ""), "qc_model"),
                "dwf": rps_xml.get_rps_button(rps_xml.find_xml_command(rvt_version, ""), "dwf_export"),
                "audit": rvt_journal_writer.audit,
                "warnings": rvt_journal_writer.warnings_export_command(rvt_journal_writer.export_warnings_template,
                                                                       warnings_dir,
                                                                       project_code,
                                                                       ),
                }

    if command == "audit":
        journal_template = rvt_journal_writer.audit_detach_template
    else:
        journal_template = rvt_journal_writer.detach_rps_template

    journal = rvt_journal_writer.write_journal(journal_file_path,
                                               journal_template,
                                               model_path,
                                               model_file_name,
                                               cmd_dict[command],
                                               )

    addin_file_path = op.join(journals_dir, "RevitPythonShell.addin")
    rps_addin = rvt_journal_writer.write_addin(addin_file_path,
                                               rvt_journal_writer.rps_addin_template,
                                               rvt_version,
                                               )

    run_proc = rvt_journal_run(rvt_version_path, journal_file_path)
    run_proc_id = run_proc.pid
    run_proc_name = run_proc.name()

    print(f" initiating process id: {run_proc_id} - {run_proc_name}")

    # let's wait a second for rvt process to fire up
    time.sleep(1)

    child_proc = run_proc.children()[0]
    child_pid = run_proc.children()[0].pid
    if child_proc.name() == "Revit.exe":
        proc_name_colored = colorful.bold_green(child_proc.name())
    else:
        proc_name_colored = colorful.bold_red(child_proc.name())

    print(f" number of child processes: {len(run_proc.children())}")
    print(f" first child process: {child_pid} - {proc_name_colored}")
    print(colorful.bold_orange("-countdown:"))
    print(f" timeout until termination of process: {child_pid} - {proc_name_colored}:")

    for sec in range(timeout):
        time.sleep(1)
        print(f" {str(timeout-sec).zfill(4)} seconds", end="\r")
        poll = run_proc.poll()

        if poll == 0:
            print(colorful.bold_green(f" {poll} - revit finished!"))
            logging.info(f"{project_code};{current_proc_hash};0")

            if command == "qc":
                update_graphs(project_code, html_path)
            break

        elif timeout-sec-1 == 0:
            print("\n")
            print(colorful.bold_red(" timeout!!"))
            if not poll:
                print(colorful.bold_red(f" kill child process now: {child_pid}"))
                child_proc.kill()
                if command != "warnings":
                    logging.warning(f"{project_code};{current_proc_hash};1")

    if command == "warnings":
        update_json_and_bokeh(project_code, html_path)
        logging.info(f"{project_code};{current_proc_hash};0")

else:
    print("model not found")

print(colorful.bold_blue("+process model job control script ended"))
