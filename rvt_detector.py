import winreg
import re
import olefile


def get_rvt_file_version(rvt_file):
    """
    Seraches for the BasiFileInfo stream in the rvt file ole structure.
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


def installed_rvt_detection(search_version):
    """
    Finds install path of rvt versions in win registry
    :param search_version: major version number
    :return:str: install path
    """
    search_version = str(search_version)
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    soft_uninstall = "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
    install_keys = winreg.OpenKey(reg, soft_uninstall)

    install_location = "InstallLocation"
    rvt_reg_keys = {}
    rvt_install_paths = {}

    index = 0
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
        rvt_reg = winreg.OpenKey(reg, soft_uninstall + "\\" + rk)
        # print([rk, rvt_reg, install_location])
        exe_location = winreg.QueryValueEx(rvt_reg, install_location)[0] + "Revit.exe"
        rvt_install_paths[rvt_install_version] = exe_location

    return rvt_install_paths[search_version]