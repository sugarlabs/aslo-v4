from sys import platform as OperatingSystem

Quotes = '"\''

if OperatingSystem == "win32":
    PathSlash = '\\'
else:
    PathSlash = '/'
FileProtocol = "file:" + 2*PathSlash


def ConvertToStandardPathFormat(Path):
    """ Example,
    Input: '"file:///some/path/somefile.extension"
    Output: /some/path/somefile.extension
    """
    Path = Path.strip(Quotes)
    if Path.startswith(FileProtocol):
        Path = Path[len(FileProtocol):]
    return Path


def GetTextAfter(Text, ReadlinesTextFile):
    for Lines in range(len(ReadlinesTextFile)):
        Line = ReadlinesTextFile[Lines].strip('\n')
        if Line.startswith(Text):
            return Line[len(Text):]
    return ''


def SingleQuoteString(String):
    if len(String) > 0:
        if String[0] != '\'' or String[-1] != '\'':
            String = '\'' + String + '\''
    return String


def DoubleQuoteString(String):
    if len(String) > 0:
        if String[0] != '"' or String[-1] != '"':
            String = '"' + String + '"'
    return String


def ListIntoString(List, QuoteItems=0, Seprator=' '):
    if QuoteItems == 2:
        for i in range(len(List)):
            Quoteditem = DoubleQuoteString(List[i])
            List[i] = Quoteditem
    elif QuoteItems == 1:
        for i in range(len(List)):
            Quoteditem = SingleQuoteString(List[i])
            List[i] = Quoteditem
    Stringoflist = (Seprator).join(List)
    return Stringoflist


# strip=0 => remove both ' & ", 1 => remove ', 2 => remove "
def UnquoteString(String, strip=0):
    while True:
        if (
            strip != 2 and
            String.startswith('"') and
            String.endswith('"')
            ):
            String = String.strip('"')
        elif (
            strip != 1
            and String.startswith("'")
            and String.endswith("'")
            ):
            String = String.strip("'")
        else:
            break
    return String


def StandardVariableName(Variable):
    Variable = Variable.casefold()
    Variable = Variable.replace('_', '').replace(' ', '')
    return Variable

"""
def DictionaryToJsonStr(Dict, BaseIndentation=0):
    BI = '\t'*BaseIndentation
    JsonStr = BI+'{\n'
    for k, v in Dict.items():
        JsonStr += BI+'\t"'+k+'" : "'+v+'",\n'
    JsonStr = JsonStr[:-2]
    JsonStr += '\n'+BI+'}'
    return JsonStr
"""

def StringToKeyValuePair(String, Seprator):
    SepratorAt = String.find(Seprator)
    if SepratorAt >= 0:
        Key = String[:SepratorAt]
        Value = String[SepratorAt+1:]
        return Key, Value
    else:
        return "", String


def FormatStrForDictinary(String):
    String = String.strip(" \n\r")
    return UnquoteString(String)


def StrListToDictionary(
    List,
    Seprator='=',
    FormatFunction=FormatStrForDictinary
    ):
    Dictionary = {}
    for i in List:
        k, v = StringToKeyValuePair(i, Seprator)
        k, v = FormatFunction(k), FormatFunction(v)
        if len(k) > 0:
            Dictionary[k] = v
    return Dictionary
