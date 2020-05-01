import os
import shutil


def CallFuncInDir(Directory, Function, *args, **kwArgs):
    CurrentDir = os.getcwd()
    os.chdir(Directory)
    Function(*args, **kwArgs)
    os.chdir(CurrentDir)


def CreateDir(Directory):
    """ return True if operation succesful and False if failed """
    if not os.path.isfile(Directory):
        if not os.path.isdir(Directory):
            os.mkdir(Directory)
        return True
    else:
        return False


def CopyFile(Source, Destination):
    """ raises exception if fails.
    Implement exception handling else program will abort.
    """
    try:
        # hard link if on same partition
        os.link(Source, Destination)
    except FileExistsError:
        # FIXME: create a function to compare if two files
        # are same and use it here
        pass
    except OSError:
        # copy if on different partition
        shutil.copy2(Source, Destination)
    except Exception as unknownError:
        raise unknownError
