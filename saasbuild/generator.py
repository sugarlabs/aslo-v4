#!/usr/bin/env python
"""
Sugar Activities App Store (SAAS)
https://github.com/sugarlabs-aslo/sugarappstore

Copyright 2020 SugarLabs
Copyright 2020 Srevin Saju <srevinsaju@sugarlabs.org>
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

import argparse
import json
import os
import time
import shutil
import sys
from urllib.parse import quote

from .bundle.bundle import Bundle
from .constants import HTML_TEMPLATE, SITEMAP_HEADER, SITEMAP_URL
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
    '--build-entrypoint',
    default='',
    help='Specify a path to any Linux compatible script which is intended to be executed on every build'
)
parser.add_argument(
    '--build-override',
    action='store_true',
    help='Override `python setup.py dist_xo` with --build-entrypoint argument shell script'
)
parser.add_argument(
    '--build-chdir',
    action='store_true',
    help='Changes directory to Activity dir'
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
parser.add_argument(
    '-x', '--generate-sitemap',
    default='',
    help='Generate a sitemap.xml file to the output directory'
)
parser.add_argument(
    '-p',
    '--pull-static-css-js-html',
    default='',
    help="Provide the path to js, css and index.html "
    "(ideally from https://github.com/sugarlabs-appstore/sugarappstore-static)")
parser.add_argument(
    '-u', '--unique-icons',
    action='store_true',
    help="Provides a unique icon name based on bundle id"
)
parser.add_argument(
    '-y', '--noconfirm',
    action='store_true',
    help="Replace output directory (default: always ask)"
)
args = parser.parse_args()


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except FileExistsError:
                pass
        else:
            shutil.copy2(s, d)


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
            activities = self.list_activities()
            if not activities:
                # return a bad exit code, if no activities were found
                sys.exit(-1)
        else:
            if args.build_xo or build_xo:
                self.generate_xo_all()
            if args.generate_static_html or generate_static_html:
                self.index = list()
                self.generate_web_page()
            if args.generate_sitemap:
                self.generate_sitemap()

    @staticmethod
    def list_activities(path_to_search_xo=None):
        """
        Generates a list<Bundle> of detected activities
        >>> sb = SaaSBuild()
        >>> sb.list_activities()
        :return:
        """
        if path_to_search_xo is None:
            path_to_search_xo = args.input_directory

        collected_sugar_activity_dirs = list()

        for bundle_dir in os.listdir(path_to_search_xo):
            # iterate through each activity in the directory
            full_path = os.path.join(path_to_search_xo, bundle_dir)
            if os.path.isdir(full_path):
                activity_info_path = os.path.join(
                    full_path, 'activity', 'activity.info')
                if os.path.exists(activity_info_path):
                    # If an activity.info exists, its a valid sugar directory.
                    # We do not need to add other directories
                    collected_sugar_activity_dirs.append(
                        Bundle(activity_info_path))

        print("[ACTIVITIES] Collected \n{}\n".format(
            collected_sugar_activity_dirs))
        return collected_sugar_activity_dirs

    def get_index(self):
        """
        Gets the index which is indexed
        """
        try:
            return self.index
        except AttributeError:
            raise AttributeError(
                "You have not initialized self.index. "
                "Please initialize with set_index setter method"
            )

    def set_index(self, index):
        """
        Sets a public .index variable for modular
        :param index:
        :return:
        """
        self.index = index

    def generate_xo_all(self, path_to_search_xo=None):
        """
        Iteratively generate bundle .xo files for all detected activities
        given by self.list_activities()
        >>> sb = SaaSBuild()
        >>> sb.generate_xo_all()
        :return:
        """
        # list activities and store as variable
        activities = self.list_activities(path_to_search_xo)
        print("Beginning to process... This might take some time..")
        num_encountered_errors = 0
        num_completed_success = 0
        override = False
        entrypoint_build_script = None

        # check if entrypoint is mentioned
        if args.build_entrypoint:
            entrypoint_build_script = os.path.abspath(args.build_entrypoint)
            if args.build_override:
                override = True

        for i in progressbar(range(len(activities)), redirect_stdout=True):
            print("[BUILD] Building ", activities[i])
            # Add an option to provide additional build script
            ecode, out, err = activities[i].do_generate_bundle(
                override_dist_xo=override,
                entrypoint_build_command=entrypoint_build_script,
                build_command_chdir=args.build_chdir
            )
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

    @staticmethod
    def create_web_static_directories(output_dir):
        """
        Creates the necessary directories
        """
        for directory_path in ('icons', 'bundles', 'app'):
            rel_path = os.path.join(output_dir, directory_path)
            if os.path.exists(rel_path):
                if not args.noconfirm:
                    # ask user for confirmation before removing directory
                    proceed = input(
                        "The operation will remove {}. Are you sure you want to proceed? (Y/n) ".format(rel_path))
                    if proceed not in ('y', 'Y'):
                        print("Terminated on user request.")
                        sys.exit(-1)
                shutil.rmtree(rel_path, ignore_errors=True)
            os.makedirs(rel_path)

    def generate_sitemap(self, domain=args.generate_sitemap):
        """
        Generates sitemap.xml
        """
        output_dir = args.output_directory

        # get the bundles
        bundles = self.list_activities()
        sitemap_content = list()
        current_formatted_time = time.strftime('%Y-%m-%d')
        for bundle in progressbar(bundles, redirect_stdout=True):

            # get the bundle and icon path
            bundle_path = bundle.get_bundle_path()
            icon_path = bundle.get_icon_path()
            sitemap_content.append(
                SITEMAP_URL.format(
                    url="{domain}/app/{bundle_name}.html".format(
                        domain=domain,
                        bundle_name=bundle.get_bundle_id()
                    ),
                    lastmod=current_formatted_time,
                    changefreq="weekly"
                )
            )
        with open(os.path.join(output_dir, 'sitemap.xml'), 'w') as w:
            w.write(SITEMAP_HEADER.format(content=''.join(sitemap_content)))
        print("sitemap.xml written successfully")

    def generate_web_page(self, output_dir=None):
        """
        Generates web page static files
        """
        if output_dir is None:
            output_dir = args.output_directory

        output_icon_dir = os.path.join(output_dir, 'icons')
        output_bundles_dir = os.path.join(output_dir, 'bundles')

        # create the directories
        self.create_web_static_directories(output_dir)

        # get the bundles
        bundles = self.list_activities()
        for bundle in progressbar(bundles, redirect_stdout=True):

            # get the bundle and icon path
            bundle_path = bundle.get_bundle_path()
            icon_path = bundle.get_icon_path()

            if not bundle_path:
                # the path to a bundle does not exist
                # possibly the bundle was not generated / had bugs
                continue

            # format the title to remove bad chars
            title = quote(bundle.get_name(), safe='')

            # Get the tags and process it
            tags = bundle.get_tags()
            tags_html_list = []
            for tag in tags:
                tags_html_list.append(
                    '<span class="badge badge-primary saas-badge">{tag}</span>'.format(tag=tag)
                )

            # Get the authors and process it
            authors = bundle.get_authors()
            authors_html_list = []
            for author in authors:
                authors_html_list.append(
                    '<span class="badge badge-secondary saas-badge">{author}</span>'.format(author=author)
                )

            # copy deps to respective folders
            _bundle_path = shutil.copy2(
                bundle_path, output_bundles_dir, follow_symlinks=True)
            if args.unique_icons:
                _icon_path = shutil.copy2(
                    icon_path,
                    os.path.join(
                        output_icon_dir,
                        "{}.svg".format(
                            bundle.get_bundle_id())),
                    follow_symlinks=True)
            else:
                _icon_path = shutil.copy2(
                    icon_path, output_icon_dir, follow_symlinks=True)

            # get the HTML_TEMPLATE and annotate with the saved
            # information
            parsed_html = HTML_TEMPLATE.format(
                title=bundle.get_name(),
                summary=bundle.get_summary(),
                description='Nothing here yet!',  # TODO: Extract from README.md
                bundle_path='../bundles/{}'.format(
                    _bundle_path.split(os.path.sep)[-1]),
                tag_list_html_formatted=''.join(tags_html_list),
                author_list_html_formatted=''.join(authors_html_list),
                icon_path='../icons/{}'.format(
                    _icon_path.split(os.path.sep)[-1])
            )

            # write the html file to specified path
            with open(os.path.join(
                    output_dir,
                    'app',
                    '{}.html'.format(bundle.get_bundle_id())
            ), 'w') as w:
                w.write(parsed_html)

            # update the index files
            self.index.append(
                bundle.generate_fingerprint_json(
                    unique_icons=args.unique_icons))

        # write the json to the file
        with open(os.path.join(output_dir, 'index.json'), 'w') as w:
            json.dump(self.index, w)
        print(
            "Index file containing {n} items have been written successfully".format(
                n=len(
                    self.index)))

        # pull the files and unpack it if necessary
        if args.pull_static_css_js_html:
            self.unpack_static(extract_dir=output_dir)

    @staticmethod
    def unpack_static(extract_dir):
        """
        copies static js/, css/ from upstream along with bundle
        """
        if not os.path.exists(args.pull_static_css_js_html):
            raise FileNotFoundError(
                "Could not find path {}".format(
                    args.pull_static_css_js_html))
        elif not os.path.isdir(args.pull_static_css_js_html):
            raise IOError(
                "{} is not a directory [20]".format(
                    args.pull_static_css_js_html))
        # unpack files into build_dir
        copytree(args.pull_static_css_js_html, extract_dir, True)
