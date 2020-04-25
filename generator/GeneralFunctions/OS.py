import os


def CallFuncInDir(Directory, Function, *args, **kwArgs):
    CurrentDir = os.getcwd()
    os.chdir(Directory)
    Function(*args, **kwArgs)
    os.chdir(CurrentDir)


# return True if operation succesful and False if failed
def CreateDir(Directory):
    if not os.path.isfile(Directory):
        if not os.path.isdir(Directory):
            os.mkdir(Directory)
        return True
    else:
        return False
