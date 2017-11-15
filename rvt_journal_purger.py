"""
Little helper to purge journal logs from /journals,
that are older than certain threshold.
"""
import os
import time
import colorful


def purge(journal_dir, threshold_age_days=60):
    """
    deletes all files starting with 'journal' older than the threshold_age_days
    :param journal_dir:
    :param threshold_age_days:
    :return:
    """
    found = 0
    now = time.time()
    for jrn in os.scandir(journal_dir):
        file_modified = os.stat(jrn).st_mtime
        if jrn.name.endswith(".txt") or jrn.name.endswith(".log"):
            if (now - file_modified) // (24 * 3600) >= threshold_age_days:
                os.remove(jrn)
                found += 1

    if found > 0:
        print(colorful.bold_orange(f" deleted {found} journals older than: {threshold_age_days} in {journal_dir}"))
