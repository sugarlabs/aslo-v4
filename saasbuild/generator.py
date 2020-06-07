#!/usr/bin/env python
import argparse
import json
import os
import shutil
from urllib.parse import quote

from .bundle.bundle import Bundle
from .constants import HTML_TEMPLATE
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
    '-b', '--build-xo',
    action='store_true',
    help='Generate XO bundles for a large number of directories'
)
parser.add_argument(
    '-l', '--list-activities',
    action='store_true',
    help='Lists all the activities available in the directory'
)
parser.add_argument(
    '-g', '--generate-static-html',
    action='store_true',
    help='Start the process of HTML generation. (pass -b, if you are unsure if bundles are already created)'
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
        if args.build_xo or build_xo:
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

    def get_index(self):
        try:
            return self.index
        except AttributeError:
            raise AttributeError(
                "You have not initialized self.index. "
                "Please initialize with set_index setter method"
            )

    def set_index(self, index: list):
        """
        Sets a public .index variable for modular
        :param index:
        :return:
        """
        self.index = index

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
            )




