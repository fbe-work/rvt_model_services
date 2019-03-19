import pathlib
from collections import namedtuple


def get_paths(prj_root):
    """
    Maps path structure into a namedtuple.
    :return:dict: namedtuple paths
    """
    root_dir = pathlib.Path(prj_root).absolute().parent
    RMSPaths = namedtuple("RMSPaths", "root logs warnings commands journals com_warnings com_qc db xml_exp xml_imp")
    path_map = RMSPaths(root=root_dir,
                        logs=root_dir / "logs",
                        warnings=root_dir / "warnings",
                        commands=root_dir / "commands",
                        journals=root_dir / "journals",
                        com_warnings=root_dir / "commands" / "warnings",
                        com_qc=root_dir / "commands" / "qc",
                        db=root_dir / "db",
                        xml_exp=root_dir / "db" / "xml_export",
                        xml_imp=root_dir / "db" / "xml_import",
                        )
    return path_map
