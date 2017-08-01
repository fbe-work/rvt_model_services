from psutil._pswindows import cext as psutil_cext


def proc_open_files(psutil_process):
    """Returns all the local and network files open by a process.

    If the revit_model_services are located on a network drive, the
    path to journals folder will be a network path and the standard
    Process.open_files() does not return those open files.

    This function uses a nasty method of reaching inside psutils and
    accessing the internals of its windows modules to do the job.

    Example:
        If a process has this file open,
        '\\Device\\Mup\\subdoman.domain.com\\files\\user\\journal.txt'
        the Process.open_files() will return None incorrectly.

    Args:
        psutil_process (psutil.Process): Child psutils process

    Returns:
        str: full path for all resources open by a process
    """

    return psutil_cext.proc_open_files(psutil_process.pid)
