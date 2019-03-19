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
    --skip_hash_unchanged   skips processing unchanged file
    --timeout=<seconds>     timeout in seconds before revit process gets terminated
"""

from docopt import docopt
import os
import pathlib
import hashlib
import subprocess
import psutil
import configparser
import time
import datetime
import logging
import colorful as col
import rvt_detector
from collections import defaultdict
from importlib import machinery
from tinydb import TinyDB, Query
from utils import rvt_journal_parser, rvt_journal_purger
from utils.win_utils import proc_open_files
from utils.rms_paths import get_paths
from notify.email import send_mail
from notify.slack import send_slack
from notify.req_post import send_post


def check_cfg_path(prj_number, cfg_str_or_path, cfg_path):
    config = configparser.ConfigParser()
    ini_file = cfg_path / "config.ini"
    if cfg_str_or_path == "cfg":
        if not cfg_str_or_path.exists():
            if ini_file.exists():
                config.read(ini_file)
                if prj_number in config:
                    config_path = config[prj_number]["path"]
                    return config_path

    return pathlib.Path(cfg_str_or_path)


def get_model_hash(rvt_model_path):
    """
    Creates a hash of provided rvt model file
    :param rvt_model_path:
    :return: hash string
    """
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()

    with open(rvt_model_path, "rb") as rvt:
        buf = rvt.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = rvt.read(BLOCKSIZE)

    return hasher.hexdigest()


def check_hash_unchanged(hash_db, rvt_model_path, model_hash, date):
    model_info = {"<full_model_path>": rvt_model_path,
                  ">last_hash": model_hash,
                  ">last_hash_date": date,
                  }
    unchanged = hash_db.search((Query()["<full_model_path>"] == rvt_model_path) &
                               (Query()[">last_hash"] == model_hash)
                               )
    if unchanged:
        return True
    else:
        hash_db.upsert(model_info, Query()["<full_model_path>"] == rvt_model_path
                       )


def exit_with_log(message, severity=logging.warning, exit_return_code=1):
    """
    Ends the whole script with a warning.
    :param message:
    :param exit_return_code:
    :return:
    """
    severity(f"{project_code};{current_proc_hash};{exit_return_code};;{message}")
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
            print(f" found appropriate command directory {commands_dir / command_name}")
            mod_init = commands_dir / command_name / "__init__.py"
            if mod_init.exists():
                mod = machinery.SourceFileLoader(command_name, str(mod_init)).load_module()

                if "register" in dir(mod):
                    if mod.register["name"] == command_name:
                        if "rjm" in mod.register:
                            module_rjm = mod.register["rjm"]
                        if "post_process" in mod.register:
                            external_args = []
                            for arg in mod.register["post_process"]["args"]:
                                external_args.append(globals().get(arg))
                            post_proc_dict["func"] = mod.register["post_process"]["func"]
                            post_proc_dict["args"] = external_args

            else:
                exit_with_log('__init__.py in command directory not found')

    if not found_dir:
        print(col.bold_red(f" appropriate command directory for '{search_command}' not found - aborting."))
        exit_with_log('command directory not found')

    return module_rjm, post_proc_dict


def get_rvt_proc_journal(process, jrn_file_path):
    open_files = process.open_files()
    for proc_file in open_files:
        file_name = pathlib.Path(proc_file.path).name
        if file_name.startswith("journal"):
            return proc_file.path

    # if nothing found using the process.open_files
    # dig deeper and get nasty
    for proc_res in proc_open_files(process):
        res_name = pathlib.Path(proc_res).name
        if res_name.startswith("journal") and res_name.endswith("txt"):
            return jrn_file_path / res_name


today_int = int(datetime.date.today().strftime("%Y%m%d"))
rms_paths = get_paths(__file__)

args = docopt(__doc__)
command = args["<command>"]
project_code = args["<project_code>"]
full_model_path = args["<full_model_path>"]
full_model_path = check_cfg_path(project_code, full_model_path, rms_paths.root)
model_path = full_model_path.parent
model_file_name = full_model_path.name
timeout = args["--timeout"]
html_path = args["--html_path"]
write_warn_ids = args["--write_warn_ids"]
rvt_override_path = args["--rvt_path"]
rvt_override_version = args["--rvt_ver"]
notify = args["--notify"]
disable_filecheck = args["--nofilecheck"]
disable_detach = args["--nodetach"]
disable_ws = args["--noworkshared"]
skip_hash_unchanged = args["--skip_hash_unchanged"]
audit = args["--audit"]
viewer = args["--viewer"]
if viewer:
    viewer = "/viewer"

comma_concat_args = ",".join([f"{k}={v}" for k, v in args.items()])

print(col.bold_blue(f"+process model job control started with command: {command}"))
print(col.bold_orange(f"-detected following root path:"))
print(f" {rms_paths.root}")

format_json = {"sort_keys": True, "indent": 4, "separators": (',', ': ')}
hashes_db = TinyDB(rms_paths.db / "model_hashes.json", **format_json)
journal_file_path = rms_paths.journals / f"{project_code}.txt"
model_exists = full_model_path.exists()

timeout = int(timeout) if timeout else 60

if not html_path:
    if command == "qc":
        html_path = rms_paths.com_qc
    elif command == "warnings":
        html_path = rms_paths.com_warnings
elif not pathlib.Path(html_path).exists():
    if command == "qc":
        html_path = rms_paths.com_qc
        print(f"your specified html path was not found - will export html graph to {rms_paths.com_qc} instead")
    elif command == "warnings":
        html_path = rms_paths.com_warnings
        print(f"your specified html path was not found - will export html graph to {rms_paths.com_warnings} instead")

if write_warn_ids:
    warn_ids_path = model_path / "RVT_fixme"
    pathlib.Path(warn_ids_path).mkdir(exist_ok=True)
    print(warn_ids_path)
else:
    warn_ids_path = ""

job_logging = rms_paths.logs / "job_logging.csv"
header_logging = "time_stamp;level;project;process_hash;error_code;args;comments\n"
if not job_logging.exists():
    with open(job_logging, "w") as logging_file:
        logging_file.write(header_logging)
    print(col.bold_blue(f"logging goes to: {job_logging}"))

logging.basicConfig(format='%(asctime)s;%(levelname)s;%(message)s',
                    datefmt="%Y%m%dT%H%M%SZ",
                    filename=job_logging,
                    level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("bokeh").setLevel(logging.CRITICAL)

print(col.bold_orange('-detected following process structure:'))
current_proc_hash = hash(psutil.Process())
print(f" current process hash: {col.cyan(current_proc_hash)}")

logging.info(f"{project_code};{current_proc_hash};;{comma_concat_args};{'task_started'}")

if skip_hash_unchanged:
    model_hash = get_model_hash(full_model_path)
    print(f" model hash:           {col.cyan(model_hash)}")
    hash_unchanged = check_hash_unchanged(hashes_db, full_model_path, model_hash, today_int)
    if hash_unchanged:
        print(col.bold_red(f" model hash has not changed since last run!"))
        print(col.bold_red(f" processing this model is skipped!!"))
        time.sleep(1)
        exit_with_log("unchanged_model", severity=logging.info, exit_return_code=0)

os.environ["RVT_QC_PRJ"]   = project_code
os.environ["RVT_QC_PATH"]  = str(full_model_path)
os.environ["RVT_LOG_PATH"] = str(rms_paths.logs)

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
    rvt_install_path = pathlib.Path(rvt_install_path)
else:
    rvt_install_path = pathlib.Path(rvt_override_path)

mod_rjm, post_proc = get_jrn_and_post_process(command, rms_paths.commands)

if disable_filecheck or model_exists:
    mod_rjm(project_code, full_model_path, journal_file_path, rms_paths.commands, rms_paths.logs)

    proc_args = [arg for arg in [str(rvt_install_path), str(journal_file_path), viewer] if arg]
    # print(proc_args)
    run_proc = psutil.Popen(proc_args, cwd=str(rms_paths.root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    run_proc_name = run_proc.name()

    # let's wait half a second for rvt process to fire up
    time.sleep(0.5)

    if run_proc.name() == "Revit.exe":
        proc_name_colored = col.bold_green(run_proc_name)
    else:
        proc_name_colored = col.bold_red(run_proc_name)

    print(f" process info: {run_proc.pid} - {proc_name_colored}")

    print(col.bold_orange("-detected revit:"))
    print(f" version:{rvt_model_version} at path: {rvt_install_path}")

    print(col.bold_orange("-process termination countdown:"))
    # print(f" timeout until termination of process: {run_proc_id} - {proc_name_colored}:")

    log_journal = get_rvt_proc_journal(run_proc, rms_paths.journals)
    return_code = 9
    return_logging = logging.info

    # the main timeout loop
    for sec in range(timeout):
        time.sleep(1)
        poll = run_proc.poll()
        print(f" {str(timeout-sec).zfill(4)} seconds, proc poll: {poll}", end="\r")

        if poll == 0:
            print(col.bold_green(f" {poll} - revit finished!"))
            return_code = "0"
            return_logging = logging.info
            break

        elif timeout-sec-1 == 0:
            print("\n")
            print(col.bold_red(" timeout!!"))
            if not poll:
                print(col.bold_red(f" kill process now: {run_proc.pid}"))
                run_proc.kill()
                return_code = "1"
                return_logging = logging.warning

    # post loop processing, naively parsing journal files
    print(col.bold_orange("-post process:"))
    print(f" process open journal for post process parsing:\n {log_journal}")
    log_journal_result = rvt_journal_parser.read_journal(log_journal)
    log_journal_result = ",".join([f"{k}: {v}" for k, v in log_journal_result.items()])
    if log_journal_result:
        print(f" detected: {log_journal_result}")
        if "corrupt" in log_journal_result:
            return_logging = logging.critical
            # run all notify modules
            if notify:
                notify_modules = [send_mail, send_slack, send_post]
                for notify_function in notify_modules:
                    notify_function.notify(project_code, full_model_path, log_journal_result)

    # getting post process funcs and args from command module for updating graphs and custom functionality
    if post_proc:
        post_proc["func"](*post_proc["args"])

    # write log according to return code
    logged_journal_excerpt = log_journal_result.strip('\n').strip('\r')
    return_logging(f"{project_code};{current_proc_hash};{return_code};;{logged_journal_excerpt}")

    # finally journal cleanup
    rvt_journal_purger.purge(rms_paths.journals)

else:
    print("model not found")
    logging.warning(f"{project_code};{current_proc_hash};1;;{'model not found'}")

print(col.bold_blue("+process model job control script ended"))
