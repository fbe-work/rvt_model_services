"""
Little helper to purge files in a directory,
that are older than certain threshold.
"""
from pathlib import Path
import time
import colorful as col


def purge_old(directory: Path, extension: str, threshold_age_days=60):
    """
    deletes all files with specified extension older than the threshold_age_days
    :param directory: path to search
    :param extension: file extension to filter by
    :param threshold_age_days: max file age date modified
    :return:
    """
    found = 0
    now = time.time()
    for node in directory.iterdir():
        if node.suffix == f".{extension}":
            file_modified = node.stat().st_mtime
            if (now - file_modified) // (24 * 3600) >= threshold_age_days:
                node.unlink()
                found += 1

    if found > 0:
        print(col.bold_green(f" cleaned-up {found} {extension} files older than: {threshold_age_days} in {directory}"))
