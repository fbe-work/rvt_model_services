"""
Simple helper to:
 - detect the version of a .rvt file.
 - detect installed Autodesk Revit versions. (windows only)
"""

import winreg
import sys
import re
import olefile

__version__ = "0.1.0"


def get_rvt_file_version(rvt_file):
    """
    Searches for the BasicFileInfo stream in the rvt file ole structure.
    :param rvt_file: model file path
    :return:str: rvt_file_version
    """
    if olefile.isOleFile(rvt_file):
        rvt_ole = olefile.OleFileIO(rvt_file)
        file_info = rvt_ole.openstream("BasicFileInfo").read().decode("utf-16le", "ignore")
        pattern = re.compile(r" \d{4} ")
        rvt_file_version = re.search(pattern, file_info)[0].strip()
        return rvt_file_version
    else:
        print(f"file does not appear to be an ole file: {rvt_file}")


def installed_rvt_detection():
    """
    Finds install path of rvt versions in win registry
    :return:dict: found install paths
    """
    install_location = "InstallLocation"
    rvt_reg_keys = {}
    rvt_install_paths = {}
    index = 0
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    soft_uninstall = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    python32bit = "32 bit" in sys.version
    python64bit = "64 bit" in sys.version

    if python64bit:
        install_keys = winreg.OpenKey(reg, soft_uninstall)
    elif python32bit:
        install_keys = winreg.OpenKey(reg, soft_uninstall, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)

    while True:
        try:
            adsk_pattern = r"Autodesk Revit ?(\S* )?\d{4}$"
            current_key = winreg.EnumKey(install_keys, index)
            if re.match(adsk_pattern, current_key):
                rvt_reg_keys[current_key] = index
                # print([current_key, index])
        except OSError:
            break
        index += 1

    for rk in rvt_reg_keys.keys():
        version_pattern = r"\d{4}"
        rvt_install_version = re.search(version_pattern, rk)[0]
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        if python64bit:
            rvt_reg = winreg.OpenKey(reg, soft_uninstall + "\\" + rk)
        elif python32bit:
            rvt_reg = winreg.OpenKey(reg, soft_uninstall + "\\" + rk, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        # print([rk, rvt_reg, install_location])
        exe_location = winreg.QueryValueEx(rvt_reg, install_location)[0] + "Revit.exe"
        rvt_install_paths[rvt_install_version] = exe_location

    return rvt_install_paths
