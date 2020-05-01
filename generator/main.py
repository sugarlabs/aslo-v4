#!/usr/bin/python3

""" Sugar Activities App Store (SAAS)
https://github.com/free-libre-software/sugarappstore
https://radii.dev/sugarlabs/appstore
Copyright 2020 Manish <sugar@radii.dev>

This file is part of "Sugar Activities App Store" aka "SAAS".

SAAS is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SAAS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with SAAS.  If not, see <https://www.gnu.org/licenses/>.
"""

import glob
import json
import os
import sys
from urllib.parse import quote as strToHtmlFmt
import zipfile

from portableCode.DataStructureManipulations import (
    StrListToDictionary
    )
from portableCode.InputOutput import (
    WriteTextFiles,
    WriteBinaryToFile
    )
from portableCode.OS import (
    CreateDir,
    CopyFile
    )


""" FIXME: paths hard coded UNIX style & most likely will not work on Windows.
Use code written for IMM to handle it.
"""


class extractData:

    def findInfoFiles(self, bundle):
        infoFiles = []
        for File in bundle.namelist():
            if File.endswith("activity/activity.info"):
                infoFiles.append(File)
        return infoFiles

    def copyBundle(self, source, activityName):
        destination = self.websiteDir+"bundles/"+activityName+".xo"
        CopyFile(source, destination)

    def createDirectories(self):
        assert CreateDir(self.websiteDir+"app")
        assert CreateDir(self.websiteDir+"icons")
        assert CreateDir(self.websiteDir+"bundles")
        assert CreateDir(self.websiteDir+"js")

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

                # FIXME: create separate function for it
                # extract and copy icon
                activityName = infoDict.get("name")
                activityVersion = infoDict.get("activity_version")
                if activityVersion is None:
                    activityVersion = ''
                if type(activityName) == str:
                    iconRelativePath = infoDict.get("icon")
                    if type(iconRelativePath) == str:
                        iconFolder = infoFiles[0][:infoFiles[0].rfind("/")+1]
                        iconAbsolutePath = (
                            iconFolder+iconRelativePath+".svg")
                        if iconAbsolutePath in bundle.namelist():
                            icon = bundle.read(iconAbsolutePath)
                            iconPath = (
                                self.websiteDir+"icons/" +
                                activityName
                                + ".svg"
                                )
                            WriteBinaryToFile(iconPath, icon)
                        else:
                            # Continue without icon since non-fatal error
                            self.iconErrorBundles.append(bundlePath)

                        bundle.close()
                        self.copyBundle(
                            bundlePath, activityName+'-'+activityVersion)
            bundle.close()

    def findBundles(self):
        self.activityBundles = glob.glob(
            self.bundlesDir+"**/*.xo",
            recursive=True
            )

    def generateAppsHtmlPages(self):
        iconsDir = "../icons/"
        bundlesDir = "../bundles/"
        for appInfo in self.indexDictList:
            appName = strToHtmlFmt(appInfo["name"], safe='')
            appVersion = strToHtmlFmt(appInfo["version"], safe='')

            html = (
                '<!DOCTYPE html>\n<html>\n<head>\n<title>' + appInfo["name"] +
                '</title>\n<meta charset="utf-8"/>\n<link rel="stylesheet" '
                'type="text/css" href="../css/main.css"/>\n</head>\n<body>\n'
                '</body>\n<h1>' + appInfo["name"] + '</h1>\n<p><img src="' +
                str(iconsDir + appName + '.svg') + '"></img></p>\n'
                '<div id=summary><h2>Summary</h2>\n<p>' + appInfo["summary"] +
                '</p>\n</div>\n<div id=description><h2>Description</h2>\n<p>' +
                appInfo["description"] + '</p>\n</div>\n<div id=tags><h2>Tags'
                '</h2>\n<ul>\n'
                )
            for tag in appInfo["tags"]:
                html += '<li>' + tag + '</li>\n'
            html += (
                '</ul>\n</div>\n<h2 id="downloadButton"><a href="' +
                str(bundlesDir + appName + appVersion + '.xo') +
                '">Download</a></h2>\n<br>\n</body>\n</html>'
            )

            WriteTextFiles(
                self.websiteDir+"./app/" + appInfo["name"] + ".html",
                html
                )

    """ Only those which are  specified in map will be added to index.
    If an entry or value does not exist in infoJSON than empty entry will
    be created for it.
    appends keys rather than replacing where multiple map to same
    """
    def generateIndex(self):
        for activity in json.loads(self.infoJson):
            indexDict = {
                "name": "",
                "summary": "",
                "description": "",
                "tags": (),
                "version": "-"
                }

            name = activity.get("name")
            if name is not None:
                indexDict["name"] = name

            summary = activity.get("summary")
            if summary is not None:
                indexDict["summary"] = summary

            description = activity.get("description")
            if description is not None:
                indexDict["description"] = description

            tags = []
            tagsKeys = ["tag", "tags", "category", "categories"]
            for key in tagsKeys:
                tagsString = activity.get(key)
                if tagsString is not None:
                    if tagsString.find(';') != -1:
                        tagsList = tagsString.split(';')
                    else:
                        tagsList = tagsString.split()
                    for tag in tagsList:
                        tag = tag.casefold().capitalize()
                        if tag not in tags:
                            tags.append(tag)
            indexDict["tags"] = tuple(tags)

            activityVersion = activity.get("activity_version")
            if activityVersion is not None:
                indexDict["version"] += activityVersion

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
        Some bundles are not successfully processed (html page + bundle copy)
        but are not in error logs as well. There are 495 bundles in
        Tony's repo, 479 successfully processed but showing fatal error of
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
        self.miscErrorBundles = []
        self.iconErrorBundles = []

        self.createDirectories()

        self.findBundles()

        self.purgeBundlesNotZipFile()

        self.extractInfoAndIconFromBundles()

        self.generateInfoJson()

        self.generateIndex()

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
        """ Files which are not continuously written during the process
        Eg. Html, icon and bundles are written while processing each bundle
        """
        WriteTextFiles(self.websiteDir+"info.json", self.infoJson)
        WriteTextFiles(self.websiteDir+"js/index.js", self.indexJs)
        WriteTextFiles(
            self.websiteDir+"bundlesNotExactlyOneInfoFile.txt",
            self.bundlesNotExactlyOneInfoFile
            )
        WriteTextFiles(
            self.websiteDir+"bundlesNotZipFiles.txt",
            self.bundlesNotZipFiles
            )
        WriteTextFiles(
            self.websiteDir+"miscErrorBundles.txt",
            self.miscErrorBundles
            )
        WriteTextFiles(
            self.websiteDir+"iconErrorBundles.txt",
            self.iconErrorBundles
            )


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
