""" process_model.py
Usage:
    process_model.py    <command> <project_code> <full_model_path> [options]

Arguments:
    command                 action to be run on model, like: qc, audit or dwf
                            currently available: qc, audit, dwf
    project_code            unique project code consisting of 'projectnumber_projectModelPart'
                            like 456_11 , 416_T99 or 377_S
    full_model_path         revit model path including file name
                            use cfg shortcut if your full model path is already set in config.ini

Options:
    -h, --help              Show this help screen.
    --viewer                run revit in viewer mode (-> no transactions)
    --html_path=<html>      path to store html bokeh graphs, default in /commands/qc/*.html
    --write_warn_ids        write warning ids from warning command
    --rvt_path=<rvt>        full path to force specific rvt version other than detected
    --rvt_ver=<rvtver>      specify revit version and skip checking revit file version
                            (helpful if opening revit server files)
    --audit                 activate open model with audit
    --noworkshared          open non-workshared model
    --nodetach              do not open workshared model detached
    --notify                choose to be notified with configured notify module(s)
    --nofilecheck           skips verifying model path actually exists
                            (helpful if opening revit server files)
    --timeout=<seconds>     timeout in seconds before revit process gets terminated
"""

from docopt import docopt
import os
import os.path as op
import pathlib
import subprocess
import psutil
import configparser
import time
import logging
import colorful
import rvt_journal_parser
import rvt_journal_purger
import rvt_detector
import win_utils
from collections import defaultdict
from importlib import machinery
from notify.email import send_mail
from notify.slack import send_slack


def get_paths_dict():
    """
    Maps path structure into a dict.
    :return:dict: path lookup dictionary
    """
    path_dict = defaultdict()

    current_dir = op.dirname(op.abspath(__file__))
    root_dir = current_dir
    journals_dir = op.join(root_dir, "journals")
    logs_dir = op.join(root_dir, "logs")
    warnings_dir = op.join(root_dir, "warnings" + op.sep)
    commands_dir = op.join(root_dir, "commands")
    com_warnings_dir = op.join(commands_dir, "warnings")
    com_qc_dir = op.join(commands_dir, "qc")

    path_dict["root_dir"] = root_dir
    path_dict["logs_dir"] = logs_dir
    path_dict["warnings_dir"] = warnings_dir
    path_dict["journals_dir"] = journals_dir
    path_dict["commands_dir"] = commands_dir
    path_dict["com_warnings_dir"] = com_warnings_dir
    path_dict["com_qc_dir"] = com_qc_dir

    return path_dict


def check_cfg_path(prj_number, cfg_str_or_path, cfg_path):
    config = configparser.ConfigParser()
    ini_file = op.join(cfg_path, "config.ini")
    if cfg_str_or_path == "cfg":
        if not op.exists(cfg_str_or_path):
            if op.exists(ini_file):
                config.read(ini_file)
                if prj_number in config:
                    config_path = config[prj_number]["path"]
                    return config_path

    return cfg_str_or_path


def exit_with_log(message):
    """
    Ends the whole script with a warning.
    :param message:
    :return:
    """
    logging.warning(f"{project_code};{current_proc_hash};1;;{message}")
    exit()


def get_jrn_and_post_process(search_command, commands_dir):
    """
    Searches command paths for register dict in __init__.py in command roots to
    prepare appropriate command strings to be inserted into the journal file
    :param search_command: command name to look up
    :param commands_dir: commands directory
    :return: command module, post process dict
    """
    found_dir = False
    module_rjm = None
    post_proc_dict = defaultdict()

    for directory in os.scandir(commands_dir):
        command_name = directory.name
        # print(command_name)
        if search_command == command_name:
            found_dir = True
            print(f" found appropriate command directory {op.join(commands_dir, command_name)}")
            if op.exists(f"{commands_dir}/{command_name}/__init__.py"):
                mod = machinery.SourceFileLoader(command_name, op.join(commands_dir,
                                                                       command_name,
                                                                       "__init__.py")).load_module()
            else:
                exit_with_log('__init__.py in command directory not found')

            if "register" in dir(mod):
                if mod.register["name"] == command_name:
                    # print("command_name found!")
                    if "rjm" in mod.register:
                        module_rjm = mod.register["rjm"]
                    if "post_process" in mod.register:
                        external_args = []
                        for arg in mod.register["post_process"]["args"]:
                            external_args.append(globals().get(arg))
                        post_proc_dict["func"] = mod.register["post_process"]["func"]
                        post_proc_dict["args"] = external_args

    if not found_dir:
        print(colorful.bold_red(f" appropriate command directory for '{search_command}' not found - aborting."))
        exit_with_log('command directory not found')

    return module_rjm, post_proc_dict


def get_rvt_proc_journal(process, jrn_file_path):
    open_files = process.open_files()
    for proc_file in open_files:
        file_name = op.basename(proc_file.path)
        if file_name.startswith("journal"):
            return proc_file.path

    # if nothing found using the process.open_files
    # dig deeper and get nasty
    for proc_res in win_utils.proc_open_files(process):
        res_name = op.basename(proc_res)
        if res_name.startswith("journal") and res_name.endswith("txt"):
            return op.join(jrn_file_path, res_name)


paths = get_paths_dict()

args = docopt(__doc__)
command = args["<command>"]
project_code = args["<project_code>"]
full_model_path = args["<full_model_path>"]
full_model_path = check_cfg_path(project_code, full_model_path, paths["root_dir"])
model_path = op.dirname(full_model_path)
model_file_name = op.basename(full_model_path)
timeout = args["--timeout"]
html_path = args["--html_path"]
write_warn_ids = args["--write_warn_ids"]
rvt_override_path = args["--rvt_path"]
rvt_override_version = args["--rvt_ver"]
notify = args["--notify"]
disable_filecheck = args["--nofilecheck"]
disable_detach = args["--nodetach"]
disable_ws = args["--noworkshared"]
audit = args["--audit"]
viewer = args["--viewer"]
if viewer:
    viewer = "/viewer"

comma_concat_args = ",".join([f"{k}={v}" for k, v in args.items()])

print(colorful.bold_blue(f"+process model job control started with command: {command}"))
print(colorful.bold_orange(f"-detected following root path path:"))
print(f" {paths['root_dir']}")

journal_file_path = op.join(paths["journals_dir"], project_code + ".txt")
model_exists = op.exists(full_model_path)

if timeout:
    timeout = int(timeout)
else:
    timeout = 60

if not html_path:
    if command == "qc":
        html_path = paths["com_qc_dir"]
    elif command == "warnings":
        html_path = paths["com_warnings_dir"]
elif not os.path.exists(html_path):
    if command == "qc":
        html_path = paths["com_qc_dir"]
        print(f"your specified html path was not found - will export html graph to {paths['com_qc_dir']} instead")
    elif command == "warnings":
        html_path = paths["com_warnings_dir"]
        print(f"your specified html path was not found - will export html graph to {paths['com_warnings_dir']} instead")
if write_warn_ids:
    warn_ids_path = op.normpath(op.join(model_path, "RVT_fixme"))
    pathlib.Path(warn_ids_path).mkdir(exist_ok=True)
    print(warn_ids_path)
else:
    warn_ids_path = ""

job_logging = op.join(paths["logs_dir"], "job_logging.csv")
header_logging = "time_stamp;level;project;process_hash;error_code;args;comments\n"
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
os.environ["RVT_QC_PATH"] = full_model_path
os.environ["RVT_LOG_PATH"] = paths["logs_dir"]

if not rvt_override_version:
    rvt_model_version = rvt_detector.get_rvt_file_version(full_model_path)
else:
    rvt_model_version = rvt_override_version

if not rvt_override_path:
    rvt_install_path = rvt_detector.installed_rvt_detection().get(rvt_model_version)
    if not rvt_install_path:
        print(f"no installed rvt versions for {rvt_model_version} detected - please use '--rvt_path' to specify path.")
        logging.warning(f"{project_code};{current_proc_hash};1;;{'no rvt versions for {rvt_model_version} detected'}")
        exit()
else:
    rvt_install_path = rvt_override_path

mod_rjm, post_proc = get_jrn_and_post_process(command, paths["commands_dir"])

if disable_filecheck or model_exists:
    mod_rjm(project_code, full_model_path, journal_file_path, paths["commands_dir"], paths["logs_dir"])

    proc_args = [arg for arg in [rvt_install_path, journal_file_path, viewer] if arg]
    # print(proc_args)
    run_proc = psutil.Popen(proc_args, cwd=paths["root_dir"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_proc_id = run_proc.pid
    run_proc_name = run_proc.name()

    # let's wait half a second for rvt process to fire up
    time.sleep(0.5)

    if run_proc.name() == "Revit.exe":
        proc_name_colored = colorful.bold_green(run_proc_name)
    else:
        proc_name_colored = colorful.bold_red(run_proc_name)

    print(f" process info: {run_proc_id} - {proc_name_colored}")

    print(colorful.bold_orange("-detected revit:"))
    print(f" version:{rvt_model_version} at path: {rvt_install_path}")

    print(colorful.bold_orange("-process termination countdown:"))
    # print(f" timeout until termination of process: {run_proc_id} - {proc_name_colored}:")

    log_journal = get_rvt_proc_journal(run_proc, paths["journals_dir"])
    return_code = None
    return_logging = logging.info

    # the main timeout loop
    for sec in range(timeout):
        time.sleep(1)
        print(f" {str(timeout-sec).zfill(4)} seconds", end="\r")
        poll = run_proc.poll()

        if poll == 0:
            print(colorful.bold_green(f" {poll} - revit finished!"))
            return_code = "0"
            return_logging = logging.info
            break

        elif timeout-sec-1 == 0:
            print("\n")
            print(colorful.bold_red(" timeout!!"))
            if not poll:
                print(colorful.bold_red(f" kill process now: {run_proc_id}"))
                run_proc.kill()
                return_code = "1"
                return_logging = logging.warning

    # post loop processing, naively parsing journal files
    print(colorful.bold_orange("-post process:"))
    print(f" process open journal for post process parsing:\n {log_journal}")
    log_journal_result = rvt_journal_parser.read_journal(log_journal)
    log_journal_result = ",".join([f"{k}: {v}" for k, v in log_journal_result.items()])
    if log_journal_result:
        print(f" detected: {log_journal_result}")
        if "corrupt" in log_journal_result:
            return_logging = logging.critical
            # run all notify modules
            if notify:
                notify_modules = [send_mail, send_slack]
                for notify_function in notify_modules:
                    notify_function.notify(project_code, full_model_path, log_journal_result)

    # getting post process funcs and args from command module for updating graphs and custom functionality
    if post_proc:
        post_proc["func"](*post_proc["args"])

    # write log according to return code
    logged_journal_excerpt = log_journal_result.strip('\n').strip('\r')
    return_logging(f"{project_code};{current_proc_hash};{return_code};;{logged_journal_excerpt}")

    # finally journal cleanup
    rvt_journal_purger.purge(paths["journals_dir"])

else:
    print("model not found")
    logging.warning(f"{project_code};{current_proc_hash};1;;{'model not found'}")

print(colorful.bold_blue("+process model job control script ended"))
