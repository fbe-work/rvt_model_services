import os.path as op
import xml.etree.ElementTree as ETree
from collections import defaultdict


def find_xml_command(rvt_version, xml_path):
    """
    Finds name index src path and group of Commands in RevitPythonShell.xml configuration.
    :param rvt_version: rvt version to find the appropriate RevitPythonShell.xml.
    :param xml_path: path where RevitPythonShell.xml resides.
    :return: Commands dictionary: {com_name:[index, src_path, group]}
    """

    if not xml_path:
        xml_path = op.join(op.expanduser("~"),
                           "AppData\\Roaming\\RevitPythonShell{0}\\RevitPythonShell.xml").format(rvt_version)

    xml_tree = ETree.parse(xml_path)
    xml_root = xml_tree.getroot()
    commands = defaultdict(list)

    for child in xml_root:
        if child.tag == 'Commands':
            com_children = child.getchildren()
            for i, com_child in enumerate(com_children):
                com_name = com_child.attrib["name"]

                commands[com_name].append(i)
                commands[com_name].append(com_child.attrib["src"])
                commands[com_name].append(com_child.attrib["group"])

    return commands


def get_rps_button(com_dict, service_name):
    grouped_button = com_dict[service_name][-1]

    if grouped_button:
        command = '%CustomCtrl_%Add-Ins%RevitPythonShell%{0}%{1}:Command{2}"'.format(com_dict[service_name][-1],
                                                                                         service_name,
                                                                                         com_dict[service_name][0])
    else:
        command = '%Add-Ins%RevitPythonShell%{0}:Command{1}"'.format(service_name, com_dict[service_name][0])

    rps_button = f'  Jrn.RibbonEvent "Execute external command:CustomCtrl_%CustomCtrl_{command}'

    return rps_button


if __name__ == '__main__':
    commands_dict = find_xml_command("2016", "")
    print(f"___ commands_dictionary: \n{commands_dict}")
    print(f"___ found qc_model button: \n{ commands_dict['qc_model'] }")
