from os.path import isfile as DoesFileExist

from .DataStructureManupulations import ConvertToStandardPathFormat

def ReadTextFile(FilePath):
    FilePath = ConvertToStandardPathFormat(FilePath)
    if DoesFileExist(FilePath) is True:
        File = open(FilePath)
        ReadFile = File.read()
        File.close()
        return ReadFile
    else:
        return ''
  
def ReadlinesTextFile(FilePath):
    String = ReadTextFile(FilePath)
    return String.split('\n')

def WriteTextFiles(FilePath, Text):
    if type(Text) != str:
        Text = '\n'.join(Text)
    File = open(FilePath, 'w')
    File.write(Text)
    File.close()

def WriteBinaryToFile(Filepath, Data):
    File=open(Filepath, 'wb')
    File.write(Data)
    File.close()
