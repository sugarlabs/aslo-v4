"""
Sugar Activities App Store (ASLOv4)
https://github.com/sugarlabs-appstore/aslo-v4

Copyright (C) 2020 Srevin Saju <srevinsaju@sugarlabs.org>

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

import hashlib
import os
import shlex
import subprocess
import tempfile
import zipfile
from configparser import ConfigParser
from pathlib import Path

from aslo4.constants import ACTIVITY_BUILD_CLASSIFIER
from aslo4.platform import get_executable_path, SYSTEM

# a shorthand for shlex.split on *nix systems
_s = shlex.split if SYSTEM != 'Windows' else lambda x: x


def get_latest_bundle(bundle_path):
    """
    Semantically searches the dist directory for the latest
    bundle.
    :param bundle_path:
    :type bundle_path:
    :return:
    :rtype:
    """
    if not os.path.exists(bundle_path):
        return False
    bundles = os.listdir(bundle_path)
    bundles.sort(reverse=True)
    for bundle in bundles:
        return os.path.join(bundle_path, bundle)
    return False  # if nothing is found


def wait_for_process_completion(proc, retry=False, timeout=120):
    """
    Waits for process completion first for 120 seconds
    and then for 240 seconds by default
    """
    try:
        exit_code = proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        if not retry:
            return -99
        # try once again. Hopefully it works
        try:
            exit_code = proc.wait(timeout=timeout * 2)
        except subprocess.TimeoutExpired:
            # Tried for total of 360 seconds == 6 minutes
            # skip install, to prevent build stash
            print("[ERR] TimeoutExpired: "
                  "Skipping activity install.")
            return -99
    return exit_code


class BundleError(Exception):
    """
    Raised when the activity.info does not
    contain the minimum required attributes
    """
    pass


class InvalidBundleError(BundleError):
    """
    Raised when the bundle (.xo) is not a
    valid packaged bundle
    """
    pass


class Bundle:
    def __init__(self, activity_path):
        """
        Generates a information
        :param activity_path: A full realpath to the bundle.
        The bundle should have activity/activity.info
        """
        # initialize config parser
        config = ConfigParser()
        self._is_xo = False
        self._is_invalid = False
        # path to activity dir / .xo
        self.activity_path = activity_path

        if str(activity_path).endswith('.xo'):
            self._is_xo = True
            # its a zipped .xo
            # read the contents from the zip file
            self.archive = zipfile.ZipFile(activity_path)

            # extract temporary activity name from the archive
            __activity_name = \
                '-'.join(activity_path.split(os.path.sep)[-1].split('-')[:-1])

            self.bundle_prefix = "{}.activity".format(__activity_name)
            self.activity_info_path = \
                os.path.join(self.bundle_prefix, 'activity', 'activity.info')
            try:
                activity_info_file = \
                    self.archive.read(self.activity_info_path).decode()
            except KeyError:
                # raises KeyError if the bundle does not have
                # an activity.info file
                self._is_invalid = True
                print(
                    "[ERR][BUNDLE] {} is an invalid bundle. "
                    "Provided bundle does not contain activity.info file"
                    .format(__activity_name)
                )
                return
            config.read_string(activity_info_file)

        else:
            self._is_xo = False
            self.activity_info_path = \
                os.path.join(activity_path, 'activity', 'activity.info')
            # not a bundle. This is a directory
            config.read(self.activity_info_path)

        # Read the activity.info and derive attributes
        if 'Activity' not in config:
            # if the activity does not have a section [Activity]
            # it then might be an invalid activity file
            raise BundleError(
                "Invalid activity.info file in {}. "
                "The file does not have a [Activity] section".format(
                    self.activity_info_path))
        bundle_activity_section = config['Activity']
        self._name = bundle_activity_section.get('name')
        self._activity_version = \
            bundle_activity_section.get('activity_version') or \
            bundle_activity_section.get('activity-version')
        self._bundle_id = bundle_activity_section.get('bundle_id')
        self.icon = bundle_activity_section.get('icon', 'activity-helloworld')
        self._exec = bundle_activity_section.get('exec')
        self.license = bundle_activity_section.get('license', '').split(';')
        self.repository = bundle_activity_section.get('repository')
        self.summary = bundle_activity_section.get('summary')
        self.url = bundle_activity_section.get('url', '')
        self.tags = \
            bundle_activity_section.get('tags', '').split(';') or \
            bundle_activity_section.get('category', '').split(';') or \
            bundle_activity_section.get('tag', '').split(';') or \
            bundle_activity_section.get('categories', '').split(';')
        self.screenshots = bundle_activity_section.get(
            'screenshots', '').split()

        # bundle specific variables
        self._bundle_path = self.activity_path \
            if self.is_xo else get_latest_bundle(
                os.path.join(self.get_activity_dir(), 'dist')
            )

        self.temp = list()

    def __repr__(self):
        """
        Represents the bundle in a human readable format
        >>> Bundle('path/to/bundle')
        Pippy Activity ('path/to/bundle', is_xo=True)
        :return:
        :rtype:
        """
        return '{name} ({path}, xo={is_xo})'.format(
            name=self._name, path=self.activity_info_path, is_xo=self.is_xo)

    @property
    def is_xo(self):
        """
        Property which returns self._is_xo which implies if the current
        activity bundle is an xo or an activity_dir
        :return:
        :rtype:
        """
        return self._is_xo

    @property
    def is_invalid(self):
        """
        Returns true if the zipped bundle is invalid, else false
        :return:
        :rtype:
        """
        return self._is_invalid

    def get_bundle_path(self):
        """
        Returns the full path to the bundle
        :return: bundle path
        :rtype: str
        """
        return self._bundle_path

    def set_bundle_path(self, bundle_path):
        """
        Explicitly set the bundle path
        :param bundle_path: new bundle path
        :type bundle_path:
        :return: None
        :rtype: None
        """
        self._bundle_path = bundle_path

    def get_tags(self):
        """
        gets the list of tags in an activity
        :return:
        """
        return self.tags

    def get_name(self):
        """
        Get the name of the bundle
        :return:
        """
        return self._name

    def get_version(self):
        """
        Get the version of the bundle
        :return:
        """
        return self._activity_version

    def get_bundle_id(self):
        """
        Get the unique identifier of the activity bundle
        :return:
        """
        return self._bundle_id

    def get_icon_name(self):
        """
        Get the name of the icon provided in the activity.info
        :return:
        """
        return self.icon

    def get_icon_path(self):
        """
        Get the path to the icon path
        If the icon does not exist, a fallback icon is used
        :return:
        """
        icon_path = os.path.join(
            os.path.dirname(self.activity_info_path),
            "{}.svg".format(self.icon)
        )
        if self.icon and os.path.exists(icon_path):
            return icon_path
        elif self.is_xo and self.icon:
            temp_folder = tempfile.TemporaryDirectory(prefix='saas-icon')
            self.archive.extract(
                os.path.join(
                    self.bundle_prefix,
                    'activity',
                    '{}.svg'.format(self.icon)
                ),
                path=temp_folder.name
            )
            self.temp.append(temp_folder)
            return os.path.join(
                temp_folder.name,
                self.bundle_prefix,
                'activity',
                '{}.svg'.format(self.icon)
            )
        else:
            # return a dummy icon because the current icon was missing
            return os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'assets', 'activity-helloworld.svg'
            )

    def get_screenshots(self, use_activity_info=False):
        """
        Returns a list of screenshots packaged in the activity
        returns screenshot if screenshot keyword is provided.
        scans for the screenshot in the screenshot/ dir using recursive glob
        :return:
        """
        if self.screenshots and use_activity_info:
            return self.screenshots  # likely to be live URLs
        else:
            screenshots = []

            if self.is_xo:
                temp_folder = tempfile.TemporaryDirectory(prefix='saas-scr')
                try:
                    self.archive.extract(
                        os.path.join(self.bundle_prefix, 'screenshots'),
                        path=temp_folder.name
                    )
                except KeyError:
                    # the screenshots directory does not exists
                    # skip it
                    return []

                screenshot_directory = os.path.join(
                    temp_folder.name, self.bundle_prefix, 'screenshots')
                self.temp.append(temp_folder)
            else:
                screenshot_directory = os.path.join(
                    self.get_activity_dir(), 'screenshots')

            for path in Path(screenshot_directory).rglob('*.png'):
                screenshots.append(path.resolve())
            return screenshots

    def get_license(self):
        """
        Return the str of open source license by which the
        activity's source code is published
        :return:
        """
        return self.license

    def get_url(self):
        """
        Extract the url if it exists
        Returns str, url
        Returns None, if no url is provided
        :return:
        """
        return self.url

    def get_summary(self):
        """
        Extract the summary if it exists
        Returns str, if summary can be derived.
        Returns None, if no summary is provided
        :return:
        """
        return self.summary

    def get_activity_dir(self):
        """
        Returns the activity directory where the activity.info is placed
        >>> a = Bundle('path/to/bundle-activity/activity/activity.info')
        >>> a.get_activity_dir()
        'path/to/bundle-activity'

        :return: path to bundle activity : str
        """
        return self.activity_path

    def do_generate_bundle(
            self,
            override_dist_xo=False,
            entrypoint_build_command=None,
            build_command_chdir=False
    ):
        """
        Generates a .xo file for the activities
        by spawning a subprocess

        Some additional pro level features ;)

        The script file supports python f-strings
        Pass the parameters as named {name}, {v} to get name and version
        appropriately

        Some important format specifiers
        {name} : Activity Name
        {v} : Activity version
        {activity_dir} : the path of the Activity,
        i.e ~/FractionBounce.Activity
        {icon_path}: the path of the icon path

        Make sure you add a cd (change directory) function within the
        shell / python script
        The script is run relative to path of execution.
        To change location each time before command execution,
        pass --build-chdir
        :return: Tuple (e_code, stdout, stderr)

        """
        if self.is_xo:
            # I am already a xo. Why build me? duh
            return 0, '[xo] Already Built.', ''

        if override_dist_xo and not entrypoint_build_command:
            raise ValueError("entrypoint_build_command was not provided")

        current_path_ = os.getcwd()
        if entrypoint_build_command and isinstance(
                entrypoint_build_command, str):
            # read the shell / python script
            with open(entrypoint_build_command, 'r') as r:
                commands_to_pre_execute = r.read()

            # change dir, if necessary:
            if build_command_chdir:
                os.chdir(self.get_activity_dir())

            # execute the commands, format the f-strings before execution
            exit_code = os.system(commands_to_pre_execute.format(
                name=self.get_name(),
                v=self.get_version(),
                activity_dir=self.get_activity_dir(),
                icon_path=self.get_icon_path()
            ))

            # restore the current working directory in the case directory was
            # changed
            if build_command_chdir:
                os.chdir(current_path_)

            if override_dist_xo:
                return exit_code, '', ''

        python3_exe = get_executable_path(
            'python3', False) or get_executable_path('python')
        python2_exe = get_executable_path(
            'python2', False) or get_executable_path('python')

        # check the type of activity
        if self.get_activity_type() == 'python2':
            # in the case the software to be used is sugar-activity
            # use python2 in that case.
            python_exe = python2_exe
        else:
            # use the python3 version to build all the rest of the
            # types of the activities
            python_exe = python3_exe

        proc = subprocess.Popen(
            _s("{} setup.py dist_xo".format(python_exe)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

        # wait for process to complete
        exit_code = wait_for_process_completion(proc)
        if exit_code:
            # process did not complete successfully
            return exit_code, '', ''

        # read the stdout and stderr
        out, err = proc.communicate()

        if not exit_code:
            dist_path = os.path.join(self.get_activity_dir(), 'dist')
            bundle = get_latest_bundle(dist_path)
            if bundle:
                self.set_bundle_path(bundle)
        return exit_code, out.decode(), err.decode()

    def do_install_bundle(self, system=False):
        """
        Install the activity to a user level, if system
        keyword argument is provided to be False,
        otherwise installed to system `/usr` level
        :return:
        """
        # get optional flags
        flags = '' if system else '--user'

        # check if the current activity is already a bundle
        if self.is_xo:
            # I am a bundle. Install it by sugar-install-build provided
            # by the sugar-toolkit-gtk3 package
            sugar_install_bundle_exe = \
                get_executable_path('sugar-install-bundle')
            proc = subprocess.Popen(
                _s("{exe} {activity_xo} {flag}".format(
                    exe=sugar_install_bundle_exe,
                    activity_xo=self.activity_path,
                    flag=flags)),
                cwd=self.get_activity_dir(),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE
            )
            exit_code = wait_for_process_completion(proc, retry=True)
            out, err = proc.communicate()
            return exit_code, out.decode(), err.decode()

        python_exe = get_executable_path(
            'python3', False) or get_executable_path('python')
        proc = subprocess.Popen(
            _s("{} setup.py install {}".format(python_exe, flags)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        exit_code = proc.wait(timeout=120)
        out, err = proc.communicate()
        return exit_code, out.decode(), err.decode()

    def generate_fingerprint_json(self, unique_icons=False):
        """
        Creates a json file which uniquely identifies each activity
        by its
        Each activity is identified by a random uuid
        For example
        >>> a = Bundle()
        >>> a.generate_fingerprint_json()
        {
            "id":
        :return:
        """
        bundle_path = self.get_bundle_path()
        if bundle_path:
            bundle_path = bundle_path.split(os.path.sep)[-1]
        else:
            bundle_path = None
        return {
            "id": hashlib.sha256(
                self.get_name().encode() +
                self.get_url().encode()).hexdigest(),
            "name": self.get_name(),
            "tags": self.get_tags(),
            "summary": self.get_summary(),
            "license": self.get_license(),
            "url": self.get_url(),
            "icon_name":
                self.get_bundle_id() if unique_icons else self.get_icon_name(),
            "bundle_name": bundle_path,
            "bundle_id": self.get_bundle_id(),
            "exec_type": self.get_activity_type(),
            "v": self.get_version()
        }

    def is_python3(self):
        """
        Returns true if the activity is build on python3 else False
        :return:
        :rtype:
        """
        if isinstance(self._exec, str) and 'sugar-activity3' in self._exec:
            return True
        else:
            return False

    def create_authors_log_file(self):
        """
        Creates the log file generated by

        $ git -P log --pretty=format:"%an"

        and returns it as string

        This can be used programmatically to create log files
        from many clones. A sample code is provided below

        >>> from aslo4.generator import SaaSBuild
        >>> sb = SaaSBuild()
        >>> all_activities = sb.list_activities()
        >>>
        >>> def write_log_file(bundle_name, data):
        ...     with open(os.path.join('/foo/bar', "{}.log".format(
        ...         bundle_name))  # noqa:
        ...     ) as w:
        ...         w.write(data)  # noqa:
        >>>
        >>> for activity in all_activities:
        ...     write_log_file(
        ...         activity.get_bundle_id(),
        ...         activity.create_authors_log_file()
        ...     )
        :return: string of all the authors
        :rtype: str
        """
        author_raw = subprocess.Popen(
            _s('{git} -C {activity_path} -P log --pretty=format:"%an"'.format(
                git=get_executable_path('git'),
                activity_path=self.get_activity_dir()
            )),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        author_raw.wait(timeout=10)
        out, _ = author_raw.communicate()
        authors = out.decode()
        return authors

    def get_authors(self):
        """
        Does minor checking if the word is like a NAME; Might have bugs.
        Returns a set `<set>`
        If the provided bundle inherits properties from a .xo file, then
        using git to extract commits is not sensible. A developer can tweak
        this by setting environment variable ASLOv4_ACTIVITY_XO_AUTHORS to
        a list of authors contributed in a *.log file

        For example, if the app is called Pippy Activity, name the file
        org.laptop.Pippy.log, where org.laptop.Pippy is the bundle name.

        use
        $ git -P --log --pretty=format:"%an" > org.laptop.Pippy.log

        To extract the list of members who contributed to the project
        in the past, (PS: do not take a shallow clone, as it would lose some
        contributors)

        Finally place these information in a folder, say `foobar`
        then

        $ export ASLOv4_ACTIVITY_XO_AUTHORS="/path/to/foobar"
        $ aslo4 --parameters-here

        This will automatically parse the information in the .log files
        inherited from git and then create bootstrap badges in the static
        files generated

        :return set
        """
        if self.is_xo:
            # bundles does not have .git directory, skip
            if not os.getenv("ASLOv4_ACTIVITY_XO_AUTHORS"):
                return {0: 'No authors found'}

            saas_activity_xo_authors = os.path.join(
                os.getenv('ASLOv4_ACTIVITY_XO_AUTHORS'),
                "{}.log".format(self.get_bundle_id())
            )
            if not os.path.exists(saas_activity_xo_authors):
                return {0: 'No authors found'}
            with open(saas_activity_xo_authors, 'r') as fp:
                authors = fp.read().split('\n')

        else:
            authors = self.create_authors_log_file().split('\n')
        unique_authors = set(authors)
        author_db = dict()
        for author in unique_authors:
            author_db[author] = authors.count(author)
        return author_db

    def get_activity_type(self):
        """
        Returns the type of activity, which inherits values from the Exec
        attribute of the activity.info
        :return:
        :rtype: str
        """
        if not isinstance(self._exec, str):
            return None
        return ACTIVITY_BUILD_CLASSIFIER.get(
            self._exec.split()[0].split(os.path.sep)[-1],
            'other'
        )

    def get_news(self):
        """
        Returns the NEWS corresponding to the current tagged release
        :return:
        :rtype: str
        """
        news_file_instance = self.get_changelog()
        if not news_file_instance:
            return
        news_parsed = news_file_instance.split('\n\n')
        try:
            for i, item in enumerate(news_parsed):
                if item == self.get_version():
                    return news_parsed[i + 1]
                elif item == 'v{}'.format(self.get_version()):
                    return news_parsed[i + 1]

            for i, item in enumerate(news_parsed):
                # as we iterated through the news file,
                # we can try this again; but with lesser confidence
                if len(item) < 6 and \
                        self.get_version() in item:
                    return news_parsed[i + 1]

        except IndexError:
            return

        return

    def get_changelog(self):
        """
        Reads the NEWS file in a directory; if it does not exist return None
        """
        if self.is_xo:
            try:
                return self.archive.read(
                    os.path.join(self.bundle_prefix, 'NEWS')).decode()
            except KeyError:
                return
        news_file = os.path.join(self.get_activity_dir(), 'NEWS')
        if not os.path.exists(news_file):
            return
        with open(news_file, 'r') as r:
            news_file_instance = r.read()

        return news_file_instance

    def get_git_url(self):
        """
        Returns git url  by `git config --get remote.origin.url`

        If the provided bundle inherits properties from a .xo file, then
        using git to extract commits is not sensible. A developer can tweak
        this by setting environment variable ASLOv4_ACTIVITY_XO_GITURL to
        a get the remote origin in a *.git file

        For example, if the app is called Pippy Activity, name the file
        org.laptop.Pippy.log, where org.laptop.Pippy is the bundle name.

        use
        $ git config --get remote.origin.url > org.laptop.Pippy.git

        Finally place these information in a folder, say `foobar`
        then

        $ export ASLOv4_ACTIVITY_XO_GITURL="/path/to/foobar"
        $ aslo4 --parameters-here

        This will automatically parse the information in the .git files
        inherited from git and then annotate "Source Code" button with
        the right link.
        """

        if self.is_xo:
            if not os.getenv("ASLOv4_ACTIVITY_XO_GITURL"):
                return  # bundles does not have .git directory, skip
            saas_activity_xo_giturl = os.path.join(
                os.getenv("ASLOv4_ACTIVITY_XO_GITURL"),
                "{}.git".format(self.get_bundle_id())
            )
            if not os.path.exists(saas_activity_xo_giturl):
                return
            with open(saas_activity_xo_giturl, 'r') as r:
                url = r.read()
            return url
        url_process = subprocess.Popen(
            _s('{git} -C {path} config --get remote.origin.url'.format(
                git=get_executable_path('git'),
                path=self.get_activity_dir()
            )),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        ecode = url_process.wait(timeout=5)
        if ecode != 0:
            # process did not complete successfully
            # hence no git url
            return None
        out, _ = url_process.communicate()
        url = out.decode().split('\n')
        if len(url) >= 1:
            return url[0]
