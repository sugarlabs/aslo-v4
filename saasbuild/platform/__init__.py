import os
import platform

PATH = os.getenv('PATH').split(os.pathsep)  # gets the PATH environment variable
SYSTEM = platform.system()


def get_executable_path(executable, raise_error=True):
    """
    Returns the absolute path of the executable
    if it is found on the PATH,
    if it is not found raises a FileNotFoundError
    :param executable:
    :return:
    """
    if SYSTEM == 'Windows':
        executable = "{}.exe".format(executable)
    for i in PATH:
        if os.path.exists(os.path.join(i, executable)):
            return os.path.join(i, executable)
    else:
        if raise_error:
            raise FileNotFoundError(
                "Could not find {p} on PATH. "
                "Make sure {p} is added to path and try again".format(p=executable)
            )
        else:
            return False
