import clr
clr.AddReference("RevitAPI")
from Autodesk.Revit.DB import OpenOptions, SynchronizeWithCentralOptions, DetachFromCentralOption, RelinquishOptions
from Autodesk.Revit.DB import TransactWithCentralOptions
from Autodesk.Revit.DB import FilePath
from Autodesk.Revit.DB import WorksetConfiguration, WorksetConfigurationOption
import System
import os
from datetime import datetime
from collections import defaultdict


iterations = 10
timing_map = defaultdict(float)
time_now = str(datetime.now())
info = ""
app = __revit__.Application
benchmark_topic = os.environ.get("RVT_SYNC_BENCHMARK") or ""
machine_name = os.environ.get('COMPUTERNAME') or ""

if "RVT_QC_PRJ" not in os.environ:
    print("no model specified")

else:
    active_nic = ""
    test_ip = "9.9.9.9"
    udp_conn = System.Net.Sockets.UdpClient(test_ip, 1)
    local_addr = udp_conn.Client.LocalEndPoint.Address
    for nic in System.Net.NetworkInformation.NetworkInterface.GetAllNetworkInterfaces():
        ip_props = nic.GetIPProperties()
        for addr_info in ip_props.UnicastAddresses:
            if local_addr.ToString() == addr_info.Address.ToString():
                active_nic = nic.Description

    project = os.environ["RVT_QC_PRJ"]
    model_path = os.environ["RVT_QC_PATH"]
    pc_stats = os.environ["pc_stats"]
    rvt_path = FilePath(model_path)

    ws_conf = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
    open_opt = OpenOptions()
    open_opt.SetOpenWorksetsConfiguration(ws_conf)

    sync_opt = SynchronizeWithCentralOptions()
    relinquish_opt = RelinquishOptions(True)
    sync_opt.SetRelinquishOptions(relinquish_opt)
    sync_opt.SaveLocalAfter = True
    # sync_opt.Compact = True
    sync_opt.Comment = "syncing"

    trans_opt = TransactWithCentralOptions()
    print(time_now)
    print("machine stats:\n{}".format(pc_stats))
    print(active_nic)
    print("timing: {} {} times".format(model_path, iterations))

    for i in range(iterations):
        start = datetime.now()
        print("  start: {}".format(start))

        doc = app.OpenDocumentFile(rvt_path, open_opt)
        print("  openend: {}".format(str(datetime.now())))
        doc.SynchronizeWithCentral(trans_opt, sync_opt)
        print("  synced: {}".format(str(datetime.now())))
        doc.Close()

        end = datetime.now()
        print("  closed: {}".format(str(end)))

        timing_result = end - start
        timing_map[i] = timing_result.total_seconds()

        print("  single run duration: {}".format(str(timing_result.total_seconds())))


print(35*"=")
print("iter:seconds")
for iteration, timing in timing_map.items():
    print("{}:  {}".format(str(iteration).zfill(4), timing))
print(35*"=")
print("average timing:")
average = sum(timing_map.values()) / iterations
print("{} seconds".format(average))

log_info = "{};".format(time_now)
log_info += "{}:{};".format(app.VersionNumber, app.VersionBuild)

model_path = os.environ["RVT_QC_PATH"]
file_size = str(int(os.path.getsize(model_path))/1000000)

log_dir  = os.environ.get("RVT_LOG_PATH")
project  = os.environ.get("RVT_QC_PRJ")
pc_stats = os.environ.get("pc_stats")

log_info += "{};".format(file_size)
log_info += pc_stats
log_info += "average seconds:{};".format(average)
log_info += "iterations:{};".format(iterations)

if log_dir:
    log_file = os.path.join(log_dir, machine_name, project + "_benchmark_" + benchmark_topic + ".csv")
    with open(log_file, "a") as csv_file:
        csv_file.write(log_info + "\n")

if log_dir:
    log_file = os.path.join(log_dir, machine_name, project + "_benchmark_single_iteration_timing_" + benchmark_topic + ".csv")
    with open(log_file, "a") as csv_file:
        for iternum, timing in timing_map.items():
            csv_file.write("{};{};{}\n".format(time_now, iternum, timing))

