#!/usr/bin/python3

""" Run as:
python3 thisscript.py "/bundles/directoty" "/website/template/root/directory/
All sub-directories of bundles directory will be scanned for activity
bundles i.e. .xo files.
"""

import glob
import json
import os
import shutil
import sys
from urllib.parse import quote as strToHtmlFmt
import zipfile

from GeneralFunctions.DataStructureManupulations import (
    StrListToDictionary
    )
from GeneralFunctions.InputOutput import (
    WriteTextFiles,
    WriteBinaryToFile
    )
from GeneralFunctions.OS import (
    CallFuncInDir,
    CreateDir
    )


""" FIXME: paths hard coded unix style & most likely will not work on winodws.
Use code written for IMM to handle it.
"""


class extractData:

    def findInfoFiles(self, bundle):
        infoFiles = []
        for File in bundle.namelist():
            if File.endswith("activity/activity.info"):
                infoFiles.append(File)
        return infoFiles

    def copyBundle(self, bundleSrc, activityName):
        CallFuncInDir(
            self.websiteDir,
            shutil.copy2,
            self.bundlesDir+bundleSrc,
            "bundles/"+activityName+".xo"
            )

    def createDirectories(self):
        assert(CreateDir("app"))
        assert(CreateDir("icons"))
        assert(CreateDir("bundles"))
        assert(CreateDir("js"))

    def extractActivityInfo(self, infoFilePath, zipFile):
        infoList = []
        infoList = zipFile.read(
            infoFilePath).decode("utf-8").split('\n')
        return StrListToDictionary(infoList)

    def extractInfoAndIconFromBundles(self):
        for bundlePath in self.activityBundles:
            bundle = zipfile.ZipFile(bundlePath, "r")

            infoFiles = self.findInfoFiles(bundle)
            if len(infoFiles) != 1:
                self.bundlesNotExactlyOneInfoFile.append(bundlePath)
            else:

                infoDict = self.extractActivityInfo(infoFiles[0], bundle)
                self.bundlesInfoList.append(infoDict)

                # FIXME: create seprate function for it
                # extract and copy icon
                activityName = infoDict.get("name")
                if type(activityName) == str:
                    iconRelativePath = infoDict.get("icon")
                    if type(iconRelativePath) == str:
                        iconFolder = infoFiles[0][:infoFiles[0].rfind("/")+1]
                        iconAbsolutePath = (
                            iconFolder+iconRelativePath+".svg")
                        if iconAbsolutePath in bundle.namelist():
                            icon = bundle.read(iconAbsolutePath)
                            iconPath = (
                                "icons/" +
                                activityName
                                + ".svg"
                                )
                            CallFuncInDir(
                                self.websiteDir,
                                WriteBinaryToFile,
                                iconPath,
                                icon
                                )
                        else:
                            # Conitnue without icon since non-fatal error
                            self.iconErroredBundles.append(bundlePath)

                        bundle.close()
                        # FIXME: uncomment below function.
                        # Disabled sometime during devlopment as time consuming
                        self.copyBundle(bundlePath, activityName)
            bundle.close()

    def generateAppsHtmlPages(self):
        iconsDir = "../icons/"
        bundlesDir = "../bundles/"
        for appInfo in self.indexDictList:
            pathName = strToHtmlFmt(appInfo["name"], safe='')

            html = (
                '<!DOCTYPE html>\n<html>\n<head>\n<title>' + appInfo["name"] +
                '</title>\n<meta charset="utf-8"/>\n<link rel="stylesheet" '
                'type="text/css" href="../css/main.css"/>\n</head>\n<body>\n'
                '</body>\n<h1>' + appInfo["name"] + '</h1>\n<p><img src="' +
                str(iconsDir + pathName + '.svg') + '"></img></p>\n'
                '<div id=summary><h2>Summary</h2>\n<p>' + appInfo["summary"] +
                '</p>\n</div>\n<div id=description><h2>Description</h2>\n<p>' +
                appInfo["description"] + '</p>\n</div>\n<div id=tags><h2>Tags'
                '</h2>\n<ul>\n'
                )
            for tag in appInfo["tags"]:
                html += '<li>' + tag + '</li>\n'
            html += (
                '</ul>\n</div>\n<a href="' +
                str(bundlesDir + pathName + '.xo') +
                '"><h2>Download<h2></a>\n</body>\n</html>'
            )

            WriteTextFiles("./app/" + appInfo["name"] + ".html", html)

    """ Only those which are  specified in map will be added to index.
    If an entry or value does not exist in infoJSON than emprty entry will
    be created for it.
    appends keys rather than replacing where mutiple map to same
    """
    def generateIndex(
        self,
        infoToIndexMap={
            "name": ("name", str),
            "summary":  ("summary", str),
            "description": ("description", str),
            "tag": ("tags", list),
            "tags": ("tags", list),
            "categories": ("tags", list),
            "category": ("tags", list)
            }
        ):
            unexpectedInputError = (
                "main.py generateIndex() : expect only str, list or tuple as "
                "kwargs -> value[1] but found "
                )

            i2IMap = infoToIndexMap
            self.indexDictList = []

            for obj in json.loads(self.infoJson):
                indexDict = {}
                for k, v in obj.items():
                    if k in i2IMap:

                        # add new entry/key to app index
                        if k not in indexDict:
                            if i2IMap[k][1] == str:
                                indexDict[i2IMap[k][0]] = v
                            elif (i2IMap[k][1] == list
                                  or i2IMap[k][1] == tuple):
                                if v.find(';') >= 0:
                                    indexDict[i2IMap[k][0]] = v.split(';')
                                else:
                                    indexDict[i2IMap[k][0]] = v.split()

                        # Append to existing entry/key to app index
                        else:
                            if i2IMap[k][1] == str:
                                indexDict[i2IMap[k][0]] += ' '+v
                            elif (i2IMap[k][1] == list
                                  or i2IMap[k][1] == tuple):
                                if v.find(';') >= 0:
                                    indexDict[i2IMap[k][0]] += v.split(';')
                                else:
                                    indexDict[i2IMap[k][0]] += v.split()
                            else:
                                print(unexpectedInputError, i2IMap[k][1])
                                sys.exit(1)

                # Create entry/key with empty value for keys not present
                # in activty.info
                for k, v in i2IMap.items():
                    if v[0] not in indexDict:
                        if v[1] == str:
                            indexDict[v[0]] = ""
                        elif (v[1] == list or v[1] == tuple):
                            indexDict[v[0]] = ()
                        else:
                            print(unexpectedInputError, v[1])
                            sys.exit(1)

                self.indexDictList.append(indexDict)
            self.indexJs = (
                "search.assignIndex(" +
                json.dumps(self.indexDictList, indent=4) +
                ")"
                )

    def generateInfoJson(self):
        self.infoJson = json.dumps(self.bundlesInfoList, indent=4)

    def __init__(self, bundlesDir, websiteDir):
        """ FIXME: WARNING:: some files may be missing such as some app
        may not have icon (use a placeholder icon for them)
        Some bundles are not succesfully processed (html page + bundle copy)
        but are not in error logs as well. There are 495 bundles in
        Tony's repo, 479 sucessfully processed but showing fatal error of
        12 only, i.e. 4 missing.
        """
        self.bundlesDir = bundlesDir
        self.websiteDir = websiteDir
        self.activityBundles = []
        self.bundlesNotZipFiles = []
        self.bundlesNotExactlyOneInfoFile = []
        self.bundlesInfoList = []
        self.infoJson = ''
        self.indexDictList = []
        self.erroredBundles = []
        self.iconErroredBundles = []

        CallFuncInDir(self.websiteDir, self.createDirectories)

        os.chdir(bundlesDir)
        self.activityBundles = glob.glob("**/*.xo", recursive=True)

        self.purgeBundlesNotZipFile()

        self.extractInfoAndIconFromBundles()

        self.generateInfoJson()

        self.generateIndex()

        os.chdir(websiteDir)

        self.generateAppsHtmlPages()

        self.writeFiles()

        #self.copyBundles()

    def purgeBundlesNotZipFile(self):
        activityBundles = []
        for bundle in self.activityBundles:
            if zipfile.is_zipfile(bundle):
                activityBundles.append(bundle)
            else:
                self.bundlesNotZipFiles.append(bundle)
        self.activityBundles = activityBundles

    def writeFiles(self):
        """ Files which are not continously written during the process
        Eg. Html, icon and bundles are written while processing each bundle
        """
        WriteTextFiles("info.json", self.infoJson)
        WriteTextFiles("./js/index.js", self.indexJs)
        WriteTextFiles(
            "bundlesNotExactlyOneInfoFile.txt",
            self.bundlesNotExactlyOneInfoFile
            )
        WriteTextFiles("bundlesNotZipFiles.txt", self.bundlesNotZipFiles)
        WriteTextFiles("erroredBundles.txt", self.erroredBundles)
        WriteTextFiles("iconErroredBundles.txt", self.iconErroredBundles)


def processArguments():
    variables = {}
    if len(sys.argv) == 3:
        variables["programDir"] = os.path.dirname(
            os.path.realpath(sys.argv[0]))+'/'
        variables["bundlesDir"] = os.path.realpath(sys.argv[1])+'/'
        variables["websiteDir"] = os.path.realpath(sys.argv[2])+'/'
    else:
        print(
            "Please give exactly two arguments to program.\n"
            "1. root directory of all activity bundles to be included "
            "in website\n"
            "2. root directory of website template\n"
            )
        sys.exit(1)
    return variables


def main():
    variables = processArguments()
    extractData(variables["bundlesDir"], variables["websiteDir"])


if __name__ == "__main__":
    main()
