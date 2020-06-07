#!/usr/bin/env python
import argparse
import logging
import os
import time

from .bundle.bundle import Bundle
from .lib.progressbar import progressbar

parser = argparse.ArgumentParser(
    'Sugar Appstore generator',
    description='Generates static HTML files for SAAS'
)
parser.add_argument(
    '-i', '--input-directory',
    default=os.getcwd(),
    help='Provide the directory to scan for Sugar Bundle XOs'
)
parser.add_argument(
    '-o', '--output-directory',
    default=os.path.join(os.getcwd(), 'saas_compiled'),
    help='Provide the directory to output the parsed website for SAAS'
)
parser.add_argument(
    '-g', '--generate-xo',
    action='store_true',
    help='Generate XO bundles for a large number of directories'
)
parser.add_argument(
    '-l', '--list-activities',
    action='store_true',
    help='Lists all the activities available in the directory'
)
args = parser.parse_args()


class SaaSBuild:
    """
    The helper object to quickly create bundles and generate html web pages
    """
    def __init__(
            self,
            list_activities=False,
            build_xo=False,
            generate_static_html=False

    ):
        if args.list_activities or list_activities:
            self.list_activities()
        elif args.generate_xo or generate_xo:
            self.generate_xo_all()

    @staticmethod
    def list_activities():
        """
        Generates a list<Bundle> of detected activities
        >>> sb = SaaSBuild()
        >>> sb.list_activities()
        :return:
        """
        path_to_search_xo = args.input_directory
        collected_sugar_activity_dirs = list()
        for bundle_dir in os.listdir(path_to_search_xo):
            full_path = os.path.join(path_to_search_xo, bundle_dir)
            if os.path.isdir(full_path):
                activity_info_path = os.path.join(full_path, 'activity', 'activity.info')
                if os.path.exists(activity_info_path):
                    # If an activity.info exists, its a valid sugar directory.
                    # We do not need to add other directories
                    collected_sugar_activity_dirs.append(Bundle(activity_info_path))
        print("[ACTIVITIES] Collected {}".format(collected_sugar_activity_dirs))
        return collected_sugar_activity_dirs

    def generate_xo_all(self):
        """
        Iteratively generate bundle .xo files for all detected activities
        given by self.list_activities()
        >>> sb = SaaSBuild()
        >>> sb.generate_xo_all()
        :return:
        """

        activities = self.list_activities()
        print("Beginning to process... This might take some time..")
        num_encountered_errors = 0
        num_completed_success = 0
        for i in progressbar(range(len(activities)), redirect_stdout=True):
            print("[BUILD] Building ", activities[i])
            ecode, out, err = activities[i].do_generate_bundle()
            if err or ecode:
                print(
                    "[BUILD][E] Error while building {activity} "
                    "E: {err}. Build exited with exit code: {ecode}".format(
                        activity=activities[i], err=err, ecode=ecode
                    )
                )
                num_encountered_errors += 1
            else:
                num_completed_success += 1
        print(
            "[BUILD] {success} bundles "
            "created with {failed} errors".format(
                success=num_completed_success,
                failed=num_encountered_errors
            )
        )

    def generate_web_page(self):
        pass

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
