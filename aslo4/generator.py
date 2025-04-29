"""
Sugar Activities App Store (ASLOv4)
https://github.com/sugarlabs/aslo-v4

Copyright (C) 2020 Sugar Labs
Copyright (C) 2020 Srevin Saju <srevinsaju@sugarlabs.org>
Copyright (C) 2020 Manish <sugar@radii.dev>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import argparse
import html
import json
import os
import time
import shutil
import sys
import zipfile
import logging
import smtplib

from email.message import EmailMessage
from logging.handlers import RotatingFileHandler
from jinja2 import FileSystemLoader

from .bundle.bundle import Bundle
from .catalog import catalog
from .constants import CHANGELOG_HTML_TEMPLATE, NEW_FEATURE_HTML_TEMPLATE
from .constants import SITEMAP_HEADER
from .constants import SITEMAP_URL
from .constants import FLATPAK_HTML_TEMPLATE
from .constants import CAROUSEL_ITEM_HTML_TEMPLATE
from .constants import CAROUSEL_INDICATOR_HTML_TEMPLATE
from .constants import CAROUSEL_HTML_TEMPLATE
from .lib.progressbar import progressbar
from .lib.termcolors import cprint
from .lib.utils import read_parse_and_write_template
from .platform import get_executable_path
from . import __version__
from .rdf.rdf import RDF


parser = argparse.ArgumentParser(
    "Sugar Appstore generator", description="Generates static HTML files for ASLOv4"
)
parser.add_argument(
    "-i",
    "--input-directory",
    default=os.getcwd(),
    help="Provide the directory to scan for Sugar activity bundles *.xo",
)
parser.add_argument(
    "-o",
    "--output-directory",
    default=os.path.join(os.getcwd(), "aslo4-compiled"),
    help="Provide the directory to output the parsed website for ASLOv4",
)
parser.add_argument(
    "-b",
    "--build-xo",
    action="store_true",
    help="Generate XO bundles for a large number of directories",
)
parser.add_argument(
    "--build-entrypoint",
    default="",
    help="Specify a path to any Linux compatible script "
    "which is intended to be executed on every build",
)
parser.add_argument(
    "--build-override",
    action="store_true",
    help="Override `python setup.py dist_xo` with "
    "--build-entrypoint argument shell script",
)
parser.add_argument(
    "--build-chdir", action="store_true", help="Changes directory to Activity dir"
)
parser.add_argument(
    "-l",
    "--list-activities",
    action="store_true",
    help="Lists all the activities available in the directory",
)
parser.add_argument(
    "-g",
    "--generate-static-html",
    action="store_true",
    help="Start the process of HTML generation. "
    "(pass -b, if you are unsure if bundles are already created)",
)
parser.add_argument(
    "-x",
    "--generate-sitemap",
    default="",
    help="Generate a sitemap.xml file to the output directory",
)
parser.add_argument("-v", "--verbose", action="store_true", help="More verbose logging")
parser.add_argument(
    "-p",
    "--pull-static-css-js-html",
    default="",
    help="Provide the path to js, css and index.html (ideally from " "./aslo4-static)",
)
parser.add_argument(
    "-u",
    "--unique-icons",
    action="store_true",
    help="Provides a unique icon name based on bundle id",
)
parser.add_argument(
    "-P",
    "--disable-progress-bar",
    action="store_true",
    help="Provides a unique icon name based on bundle id",
)
parser.add_argument(
    "-s",
    "--include-screenshots",
    action="store_true",
    help="Includes screenshots of activity if its found as"
    " <activity>/screenshots/*.png",
)
parser.add_argument(
    "-f",
    "--include-flatpaks",
    action="store_true",
    help="Includes a flatpak description card if the activity "
    "has a valid flatpak registered under flathub.org",
)
parser.add_argument(
    "-y",
    "--noconfirm",
    action="store_true",
    help="Replace output directory (default: always ask)",
)
parser.add_argument(
    "-C",
    "--always-checkout-latest-tag",
    action="store_true",
    help="Checkout the latest tag when building an activity. Fallback to " "master",
)
parser.add_argument(
    "-e",
    "--email",
    default="",
    help="Email an address, or group of address separated by commas about "
    "status changes in the list of deployed activities.",
)
parser.add_argument(
    "-c",
    "--no-colors",
    action="store_true",
    help="Suppress colors in terminal (default: env ANSI_COLORS_DISABLED)",
)
parser.add_argument(
    "-z",
    "--include-python2",
    action="store_true",
    help="Include python2 support (sugar-activity)",
)
parser.add_argument("--version", action="store_true", help="Show the version")
args = parser.parse_args()


DEPENDENCIES_PYTHON2 = ("python2",)

DEPENDENCIES = (
    "git",
    "python3",
)


if args.no_colors:
    os.environ["ASLOv4_NO_COLORS"] = "true"


if args.version:
    cprint("Sugar Labs Appstore Generator Tool", "green")
    print(__version__)
    print()
    sys.exit()


def debug(x):
    if args.verbose:
        print(x)


def pre_check_dependencies(dependencies=DEPENDENCIES):
    """
    Checks if all the dependencies are met before build
    """
    for dependency in dependencies:
        exe = get_executable_path(dependency)
        logger.debug("{}: Found at {}".format(dependency, exe))


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            try:
                shutil.copytree(s, d, symlinks, ignore)
            except FileExistsError:
                shutil.rmtree(d)
                shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def check_progressbar(*arg, **kwarg):
    if kwarg.pop("enable_progressbar"):
        return progressbar(*arg, **kwarg)
    else:
        return list(*arg)


# initialize the logger
logger = logging.getLogger("aslo4-builder")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(message)s")
log_file = os.getenv("ASLOv4_LOGGER_PATH") or "aslo-build.log"
rotating_file_handler = RotatingFileHandler(log_file, maxBytes=1000000, backupCount=10)
rotating_file_handler.setFormatter(formatter)
rotating_file_handler.setLevel(logging.DEBUG)
logger.addHandler(rotating_file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
logger.addHandler(stream_handler)


if args.verbose:
    stream_handler.setLevel(logging.DEBUG)


class SaaSBuild:
    """
    The helper object to quickly create bundles and generate html web pages
    """

    def __init__(
        self,
        list_activities=False,
        build_xo=False,
        generate_static_html=False,
        progress_bar_disabled=False,
        include_flatpaks=False,
        include_screenshots=False,
        python2=args.include_python2,
        email=args.email,
    ):

        self.emails = args.email.split(",")
        logger.info("***************")
        logger.info("ASLOv4 builder")
        logger.info("Build started on {}".format(time.asctime()))
        logger.info("***************")

        # check if dependencies are met
        self.file_system_loader = FileSystemLoader(
            os.path.join(args.pull_static_css_js_html, "templates")
        )

        dependencies = DEPENDENCIES
        if python2:
            dependencies += DEPENDENCIES_PYTHON2
        pre_check_dependencies(dependencies)

        self.include_screenshots = args.include_screenshots or include_screenshots
        self.include_flatpaks = args.include_flatpaks or include_flatpaks
        self.progress_bar_disabled = args.disable_progress_bar or progress_bar_disabled
        if args.list_activities or list_activities:
            activities = self.list_activities()
            if not activities:
                # return a bad exit code, if no activities were found
                print("No activities found")
                sys.exit(-1)
            print(activities)
        else:
            if args.build_xo or build_xo:
                self.generate_xo_all()
            if args.generate_static_html or generate_static_html:
                self.index = list()
                self.generate_web_page()
            if args.generate_sitemap:
                self.generate_sitemap()

    @staticmethod
    def list_activities(path_to_search_xo=None, do_not_search_for_xo=False):
        """
        Generates a list<Bundle> of detected activities
        >>> sb = SaaSBuild()
        >>> sb.list_activities()
        :return:
        """
        if path_to_search_xo is None:
            path_to_search_xo = args.input_directory

        collected_sugar_activity_dirs = list()

        directory_items = os.listdir(path_to_search_xo)
        directory_items.sort(reverse=True)

        for bundle_dir in directory_items:
            # iterate through each activity in the directory
            full_path = os.path.join(path_to_search_xo, bundle_dir)
            if os.path.isdir(full_path):
                activity_info_path = os.path.join(
                    full_path, "activity", "activity.info"
                )
                if os.path.exists(activity_info_path):
                    # If an activity.info exists, its a valid sugar directory.
                    # We do not need to add other directories
                    collected_sugar_activity_dirs.append(Bundle(full_path))
            elif full_path.endswith(".xo") and not do_not_search_for_xo:
                if zipfile.is_zipfile(full_path):
                    # only add the bundle if its a valid zip file
                    __bundle = Bundle(full_path)
                    if not __bundle.is_invalid:
                        # skip invalid bundles to prevent conflict
                        collected_sugar_activity_dirs.append(__bundle)

        logger.debug(
            "[ACTIVITIES] Collected \n{}\n".format(collected_sugar_activity_dirs)
        )
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

    def generate_xo_all(
        self,
        path_to_search_xo=None,
        checkout_latest_tag=args.always_checkout_latest_tag,
    ):
        """
        Iteratively generate bundle .xo files for all detected activities
        given by self.list_activities()
        >>> sb = SaaSBuild()
        >>> sb.generate_xo_all()
        :return:
        """
        # list activities and store as variable
        activities = self.list_activities(path_to_search_xo)
        logger.debug("Beginning to process... This might take some time..")
        num_encountered_errors = 0
        num_completed_success = 0
        num_completed_warnings = 0
        override = False
        entrypoint_build_script = None

        # check if entrypoint is mentioned
        if args.build_entrypoint:
            entrypoint_build_script = os.path.abspath(args.build_entrypoint)
            if args.build_override:
                override = True

        for i in check_progressbar(
            range(len(activities)),
            redirect_stdout=True,
            enable_progressbar=not self.progress_bar_disabled,
        ):
            logger.info("[BUILD] Building {}".format(activities[i]))
            # Add an option to provide additional build script
            ecode, _, err = activities[i].do_generate_bundle(
                override_dist_xo=override,
                entrypoint_build_command=entrypoint_build_script,
                build_command_chdir=args.build_chdir,
                checkout_latest_tag=checkout_latest_tag,
            )
            if err:
                logger.warning(
                    "[BUILD][W] {} build completed "
                    "with warnings.".format(activities[i])
                )
                num_completed_warnings += 1
            elif ecode:
                logger.error(
                    "[BUILD][E] Error while building {activity} "
                    "E: {err}. Build exited with exit code: {ecode}".format(
                        activity=activities[i], err=err, ecode=ecode
                    )
                )
                num_encountered_errors += 1
            else:
                num_completed_success += 1
        logger.info(
            "[BUILD] Created {success} bundles successfully, "
            "{warn} bundles with warnings and "
            "{failed} with errors".format(
                success=num_completed_success,
                warn=num_completed_warnings,
                failed=num_encountered_errors,
            )
        )

    @staticmethod
    def create_web_static_directories(output_dir):
        """
        Creates the necessary directories
        """
        for directory_path in ("icons", "bundles", "app", "api"):
            rel_path = os.path.join(output_dir, directory_path)
            if os.path.exists(rel_path):
                if not args.noconfirm:
                    # ask user for confirmation before removing directory
                    proceed = input(
                        "The operation will remove {}. "
                        "Are you sure you want to proceed? "
                        "(Y/n) ".format(rel_path)
                    )
                    if proceed not in ("y", "Y"):
                        logger.error("Terminated on user request.")
                        sys.exit(-1)
                shutil.rmtree(rel_path, ignore_errors=True)
            os.makedirs(rel_path)

    @staticmethod
    def _process_tags_html(bundle):
        """
        Extracts tags from tag_bundles and return formatted HTML
        badges
        :param bundle:
        :type bundle:
        :return:
        :rtype:
        """
        # Get the tags and process it
        tags = bundle.get_tags()
        tags_html_list = []
        for tag in tags:
            if all((tag, isinstance(tag, str), tag.strip())):
                # make sure the tag is a valid non empty string
                tags_html_list.append(
                    '<span class="badge badge-primary saas-badge">'
                    "{tag}</span>".format(tag=tag)
                )
        return tags_html_list

    @staticmethod
    def _process_authors_html(bundle):
        """
        Retrieves authors from get_authors, and creates_html
        :param bundle: Bundle
        :type bundle: Bundle
        :return:
        :rtype:
        """
        # Get the authors and process it

        authors = bundle.get_authors()
        authors_html_list = []
        for author in authors:
            authors_html_list.append(
                '<span class="badge badge-secondary saas-badge">{author}  '
                '<span class="badge badge-dark">{commits}</span>'
                "</span>".format(author=author, commits=authors[author])
            )
        return authors_html_list

    @staticmethod
    def _process_changelog_html(changelog_latest_version):
        """
        Process changelog and generate HTML <pre> tags from the bundle
        :param changelog_latest_version: changelog text
        :type changelog_latest_version: str
        :return:
        :rtype: list<str>
        """
        html_changelog_latest_version = list()
        if changelog_latest_version:
            changelog_latest_version = html.escape(changelog_latest_version)
            html_changelog_latest_version = list()
            for log in changelog_latest_version.split("\n"):
                log_parsed = log[0:2].replace("*", "") + log[2:]
                html_changelog_latest_version.append("<li>{}</li>".format(log_parsed))
            if len(html_changelog_latest_version) >= 1:
                if html_changelog_latest_version[-1] == "<li></li>":
                    html_changelog_latest_version.pop()
        return html_changelog_latest_version

    @staticmethod
    def _process_licenses_html(bundle):
        """
        Process licenses and creates static html
        :param bundle:
        :type bundle:
        :return:
        :rtype:
        """
        licenses = bundle.get_license()
        parsed_licenses = list()
        html_parsed_licenses = list()
        
        # Filter out empty or whitespace-only licenses
        for i in licenses:
            if i and not i.isspace():
                parsed_licenses.append(i.strip())
        
        # Create HTML badges for valid licenses only if there are any
        if parsed_licenses:
            for i in parsed_licenses:
                html_parsed_licenses.append(
                    '<span class="badge badge-info">' "{lic}</span>".format(lic=i)
                )
        
        # Return the list of HTML badges (empty if no licenses)
        return html_parsed_licenses

    @staticmethod
    def _process_screenshot_carousel_html(bundle, screenshots_list, output_dir):
        carousel_indicators = list()
        carousel_images = list()
        # copy files to their respective folders
        screenshot_dir = os.path.join(output_dir, "app", bundle.get_bundle_id())
        if os.path.exists(screenshot_dir):
            shutil.rmtree(screenshot_dir, ignore_errors=True)
        os.makedirs(screenshot_dir)
        for i, screenshot in enumerate(screenshots_list):
            active = ""
            if i == 0:
                active = "active"
            carousel_indicators.append(
                CAROUSEL_INDICATOR_HTML_TEMPLATE.format(i=i + 1, active=active)
            )

            _screenshot_path = os.path.sep.join(
                shutil.copy2(screenshot, screenshot_dir, follow_symlinks=True).split(
                    os.path.sep
                )[-2:]
            )

            carousel_images.append(
                CAROUSEL_ITEM_HTML_TEMPLATE.format(
                    i=i + 1,
                    active=active,
                    activity_name=bundle.get_name(),
                    src=_screenshot_path,
                )
            )
        carousel_div = CAROUSEL_HTML_TEMPLATE.format(
            carousel_indicator_divs="".join(carousel_indicators),
            carousel_img_divs="".join(carousel_images),
        )
        return carousel_div

    def generate_sitemap(self, domain=args.generate_sitemap):
        """
        Generates sitemap.xml
        """
        output_dir = args.output_directory

        # get the bundles
        bundles = self.list_activities()
        sitemap_content = list()
        current_formatted_time = time.strftime("%Y-%m-%d")
        for bundle in check_progressbar(
            bundles,
            redirect_stdout=True,
            enable_progressbar=not self.progress_bar_disabled,
        ):

            # get the bundle and icon path
            # bundle_path = bundle.get_bundle_path()
            # icon_path = bundle.get_icon_path()
            sitemap_content.append(
                SITEMAP_URL.format(
                    url="{domain}/app/{bundle_name}.html".format(
                        domain=domain, bundle_name=bundle.get_bundle_id()
                    ),
                    lastmod=current_formatted_time,
                    changefreq="weekly",
                )
            )
        with open(os.path.join(output_dir, "sitemap.xml"), "w") as w:
            w.write(SITEMAP_HEADER.format(content="".join(sitemap_content)))
        logger.info("sitemap.xml written successfully")

    def generate_web_page(
        self,
        output_dir=args.output_directory,
        include_flatpaks=False,
        include_screenshots=False,
    ):
        """
        Generates web page static files
        """
        include_flatpaks = include_flatpaks or self.include_flatpaks
        include_screenshots = include_screenshots or self.include_screenshots
        flatpak_file = os.path.join(os.path.dirname(__file__), "data", "flatpak.json")
        flatpak_bundle_info = dict()

        os.makedirs(output_dir, exist_ok=True)

        # check if feed.json exists, if not create it
        feed_json = os.path.join(output_dir, "feed.json")
        if not os.path.exists(feed_json):
            with open(feed_json, "w") as fp:
                json.dump(
                    {
                        "generated": time.time(),
                        "bundles": {},
                    },
                    fp,
                )

        with open(feed_json) as fp:
            feed_json_data = json.load(fp)

        logger.info("[STATIC] Starting Web Page Static Generation")

        if include_flatpaks and os.path.exists(flatpak_file):
            logger.info("[STATIC] Reading flatpak.json")
            with open(flatpak_file, "r") as r:
                flatpak_bundle_info = json.load(r)
        elif include_flatpaks:
            logger.error(
                "[ERR] flatpak.json was not found in data/.; "
                "Please get a new copy from the source"
            )
            logger.error("[ERR] Ignoring error and continuing to process bundles. ")

        output_icon_dir = os.path.join(output_dir, "icons")
        output_bundles_dir = os.path.join(output_dir, "bundles")
        logger.info("[STATIC] Output directory:{}".format(output_dir))
        logger.info("[STATIC] Output icon directory:{}".format(output_icon_dir))
        logger.info("[STATIC] Output bundle directory:{}".format(output_bundles_dir))

        # create the directories
        logger.info("[STATIC] Creating static directories: [icons, bundles, app]")
        self.create_web_static_directories(output_dir)

        # get the bundles
        bundles = self.list_activities()
        for bundle in check_progressbar(
            bundles,
            redirect_stdout=True,
            enable_progressbar=not self.progress_bar_disabled,
        ):
            logger.debug("[STATIC][{}] Starting build".format(bundle.get_name()))
            # get the bundle and icon path
            bundle_path = bundle.get_bundle_path()
            icon_path = bundle.get_icon_path()

            if not bundle_path:
                logger.debug(
                    "[STATIC][{}] Valid dist *.xo was not found. "
                    "Skipping .".format(bundle.get_name())
                )
                # the path to a bundle does not exist
                # possibly the bundle was not generated / had bugs
                continue

            logger.debug("[STATIC][{}] Processing tags".format(bundle.get_name()))
            tags_html_list = self._process_tags_html(bundle)

            # Get the authors and process it
            logger.debug("[STATIC][{}] Processing authors".format(bundle.get_name()))
            authors_html_list = self._process_authors_html(bundle)

            # Changelog gen
            logger.debug("[STATIC][{}] Processing news".format(bundle.get_name()))
            changelog_latest_version = bundle.get_news()
            new_in_this_version_raw_html = self._process_changelog_html(
                changelog_latest_version
            )

            # changelog all
            logger.debug(
                "[STATIC][{}] " "Processing changelog".format(bundle.get_name())
            )
            changelog = bundle.get_changelog()
            if changelog:
                changelog = html.escape(changelog)

            # get Licenses
            logger.debug("[STATIC][{}] Processing Licenses".format(bundle.get_name()))
            html_parsed_licenses = self._process_licenses_html(bundle)

            # copy deps to respective folders
            logger.debug(
                "[STATIC][{}] " "Copying Dependencies".format(bundle.get_name())
            )
            _bundle_path = shutil.copy2(
                bundle_path, output_bundles_dir, follow_symlinks=True
            )
            if args.unique_icons:
                _icon_path = shutil.copy2(
                    icon_path,
                    os.path.join(
                        output_icon_dir, "{}.svg".format(bundle.get_bundle_id())
                    ),
                    follow_symlinks=True,
                )
            else:
                _icon_path = shutil.copy2(
                    icon_path, output_icon_dir, follow_symlinks=True
                )

            # get git url
            logger.debug(
                "[STATIC][{}] "
                "Getting URL to git repository".format(bundle.get_name())
            )
            bundle_git_url_stripped = bundle.get_git_url()
            if (
                isinstance(bundle_git_url_stripped, str)
                and bundle_git_url_stripped[-4:] == ".git"
            ):
                bundle_git_url_stripped = bundle_git_url_stripped[:-4]

            # check if flatpak is supported
            logger.debug(
                "[STATIC][{}] " "Checking flatpak support".format(bundle.get_name())
            )
            if include_flatpaks and flatpak_bundle_info.get(bundle_git_url_stripped):
                flatpak_html_div = FLATPAK_HTML_TEMPLATE.format(
                    activity_name=bundle.get_name(),
                    bundle_id=flatpak_bundle_info.get(bundle_git_url_stripped)[
                        "bundle-id"
                    ],
                )
            else:
                flatpak_html_div = ""

            # if screenshots need to be added as in a carousel, add them
            logger.debug("[STATIC][{}] Adding screenshots".format(bundle.get_name()))
            carousel_div = ""
            screenshots_list = bundle.get_screenshots()
            if include_screenshots and len(screenshots_list) >= 1:
                carousel_div = self._process_screenshot_carousel_html(
                    bundle, screenshots_list, output_dir
                )

            if len(new_in_this_version_raw_html):
                new_in_this_version_parsed = NEW_FEATURE_HTML_TEMPLATE.format(
                    new_features="".join(new_in_this_version_raw_html)
                )
            else:
                new_in_this_version_parsed = ""

            if changelog and isinstance(changelog, str) and changelog.strip():
                changelog_formatted_html = CHANGELOG_HTML_TEMPLATE.format(
                    changelog=changelog
                )
            else:
                changelog_formatted_html = ""

            # get the HTML_TEMPLATE and annotate with the saved
            # information
            logger.debug(
                "[STATIC][{}] Generating static HTML".format(bundle.get_name())
            )
            output_html_file_name_path = os.path.join(
                output_dir, "app", "{}.html".format(bundle.get_bundle_id())
            )
            # write the html file to specified path
            logger.debug("[STATIC][{}] Writing static HTML".format(bundle.get_name()))
            read_parse_and_write_template(
                file_system_loader=self.file_system_loader,
                html_template_path=os.path.join(
                    args.pull_static_css_js_html, "templates", "app.html"
                ),
                html_output_path=output_html_file_name_path,
                title=bundle.get_name(),
                version=bundle.get_version(),
                summary=bundle.get_summary(),
                description=bundle.get_description(),
                licenses="".join(html_parsed_licenses),
                description_html_div="",
                # TODO: Extract from README.md
                bundle_path="/bundles/{}".format(_bundle_path.split(os.path.sep)[-1]),
                tag_list_html_formatted="".join(tags_html_list),
                author_list_html_formatted="".join(authors_html_list),
                icon_path="/icons/{}".format(_icon_path.split(os.path.sep)[-1]),
                new_feature_html_div=new_in_this_version_parsed,
                changelog_html_div=changelog_formatted_html,
                git_url=bundle.get_git_url(),
                flatpak_html_div=flatpak_html_div,
                carousel=carousel_div,
            )

            logger.debug("[STATIC][{}] Generating RDF data".format(bundle.get_name()))
            domain = (
                args.generate_sitemap
                if args.generate_sitemap
                else "https://activities.sugarlabs.org"
            )
            rdf = RDF(
                bundle_id=bundle.get_bundle_id(),
                bundle_version=bundle.get_version(),
                bundle_path=bundle_path,
                min_version="0.116",
                max_version="0.117",
                base_url="{domain}/bundles".format(domain=domain),
                info_url="{domain}/app".format(domain=domain),
            )
            parsed_rdf = rdf.parse()

            logger.debug("[STATIC][{}] Writing RDF".format(bundle.get_name()))
            with open(
                os.path.join(
                    output_dir, "api", "{}.xml".format(bundle.get_bundle_id())
                ),
                "w",
            ) as w:
                w.write(parsed_rdf)

            # update the index files
            logger.debug("[STATIC][{}] Adding JSON".format(bundle.get_name()))
            
            # Get the bundle_id
            bundle_id = bundle.get_bundle_id()
            
            # Use a dictionary to track bundle_ids for efficient lookup
            # Initialize the dictionary if it doesn't exist yet
            if not hasattr(self, 'bundle_id_index'):
                self.bundle_id_index = {}
                # Populate with existing bundles
                for idx, existing_bundle in enumerate(self.index):
                    if 'bundle_id' in existing_bundle:
                        self.bundle_id_index[existing_bundle['bundle_id']] = idx
            
            # Check if this bundle_id already exists in the index
            if bundle_id in self.bundle_id_index:
                # Update the existing entry instead of adding a duplicate
                idx = self.bundle_id_index[bundle_id]
                self.index[idx] = bundle.generate_fingerprint_json(unique_icons=args.unique_icons)
            else:
                # Add to index if it doesn't already exist
                self.index.append(
                    bundle.generate_fingerprint_json(unique_icons=args.unique_icons)
                )
                # Update the lookup dictionary
                self.bundle_id_index[bundle_id] = len(self.index) - 1

            # check the database and then update if necessary
            # this will help to check if new bundles are created, and then
            # accordingly call a hook.
            bundle_version = bundle.get_version()

            saved_bundle_version = feed_json_data["bundles"].get(bundle_id)
            saved_bundle_version = (
                0 if saved_bundle_version is None else saved_bundle_version
            )
            should_create_release_email = saved_bundle_version != bundle_version
            try:
                should_create_release_email = float(saved_bundle_version) < float(
                    bundle_version
                )
            except ValueError:
                pass

            if should_create_release_email:
                print(
                    "[STATIC][FEED][{}] New release detected {}".format(
                        bundle_id, bundle_version
                    )
                )
                feed_json_data["bundles"][bundle_id] = bundle_version
                # handle any items like sending emails to the respective
                self.new_version_detected_hook(bundle)

        logger.info("[STATIC] Writing Index file (index.json)")
        # write the json to the file
        with open(os.path.join(output_dir, "index.json"), "w") as w:
            json.dump(self.index, w)
        logger.info(
            "Index file containing {n} items have been written "
            "successfully".format(n=len(self.index))
        )

        # pull the files and unpack it if necessary
        if args.pull_static_css_js_html:
            logger.debug("[STATIC] Copying dependant js and css")
            self.unpack_static(extract_dir=output_dir)
        logger.debug("[STATIC] Process Completed")

        # write the feed.json
        feed_json_data["generated"] = time.time()
        with open(feed_json, "w") as fp:
            json.dump(feed_json_data, fp)

    def unpack_static(self, extract_dir):
        """
        copies static js/, css/ from upstream along with bundle
        """
        if not os.path.exists(args.pull_static_css_js_html):
            raise FileNotFoundError(
                "Could not find path {}".format(args.pull_static_css_js_html)
            )
        elif not os.path.isdir(args.pull_static_css_js_html):
            raise IOError(
                "{} is not a directory [20]".format(args.pull_static_css_js_html)
            )
        # unpack files into build_dir
        for i in ("css", "img", "favicon", "js"):
            _dir = os.path.join(args.pull_static_css_js_html, i)
            os.makedirs(_dir, exist_ok=True)
            if sys.version_info.minor >= 8:
                shutil.copytree(
                    _dir,
                    os.path.join(extract_dir, i),
                    symlinks=True,
                    ignore_dangling_symlinks=True,
                    dirs_exist_ok=True,
                )
            else:
                _dest_dir = os.path.join(extract_dir, i)
                if os.path.exists(_dest_dir):
                    logger.info("Going to remove {}".format(_dest_dir))
                    shutil.rmtree(_dest_dir)
                shutil.copytree(
                    _dir, _dest_dir, symlinks=True, ignore_dangling_symlinks=True
                )

        for i in (
            "browserconfig.xml",
            "manifest.json",
            "README.md",
            "LICENSE",
            "favicon.ico",
        ):
            _file = os.path.join(args.pull_static_css_js_html, i)
            _extract_file = os.path.join(extract_dir, i)
            shutil.copyfile(_file, _extract_file, follow_symlinks=True)

        for i in ("about.html", "index.html"):
            # needs additional processing
            _file = os.path.join(args.pull_static_css_js_html, i)
            _extract_file = os.path.join(extract_dir, i)
            read_parse_and_write_template(
                file_system_loader=self.file_system_loader,
                html_template_path=_file,
                html_output_path=_extract_file,
            )

    def new_version_detected_hook(self, bundle):
        # do something like sending emails
        message = EmailMessage()
        release_template = os.path.join(
            args.pull_static_css_js_html, "templates", "release_template.eml"
        )
        news_email_formatted = bundle.get_news()

        content = read_parse_and_write_template(
            file_system_loader=self.file_system_loader,
            html_template_path=release_template,
            news_email_formatted=news_email_formatted,
            release_time=time.asctime(),
            bundle=bundle,
        )
        message.set_content(content)

        message[
            "Subject"
        ] = f"[ASLOv4] [RELEASE] {bundle.get_name()} - {bundle.get_version()}"
        message["From"] = catalog.email
        message["To"] = ", ".join(self.emails)
        if len(self.emails) >= 1:
            message.add_header("reply-to", self.emails[0])
        if not catalog.email:
            # no from address defined.
            # we need to return
            return

        # Send the message via our own SMTP server.
        s = smtplib.SMTP("localhost")
        s.send_message(message)
        s.quit()
