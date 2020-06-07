import hashlib
import os
import shlex
import subprocess
import uuid
from configparser import ConfigParser

from saasbuild.constants import ACTIVITY_BUILD_CLASSIFIER
from saasbuild.platform import get_executable_path, SYSTEM

# a shorthand for shlex.split on *nix systems
_s = shlex.split if SYSTEM != 'Windows' else lambda x: x


def get_latest_bundle(bundle_path):
    if not os.path.exists(bundle_path):
        return False
    bundles = os.listdir(bundle_path)
    bundles.sort(reverse=True)
    for bundle in bundles:
        return os.path.join(bundle_path, bundle)
    else:
        return False


class BundleError(Exception):
    pass


class Bundle:
    def __init__(self, activity_info_path):
        """
        Generates a information
        :param activity_info_path: A full realpath to activity.info
        """
        self.activity_info_path = activity_info_path

        # Read the activity.info and derive attributes
        config = ConfigParser()
        config.read(self.activity_info_path)
        if 'Activity' not in config:
            # if the activity does not have a section [Activity]
            # it then might be an invalid activity file
            raise BundleError(
                "Invalid activity.info file in {}. "
                "The file does not have a [Activity] section".format(self.activity_info_path)
            )
        bundle_activity_section = config['Activity']
        self._name = bundle_activity_section.get('name')
        self._activity_version = bundle_activity_section.get('activity-version')
        self._bundle_id = bundle_activity_section.get('bundle_id')
        self.icon = bundle_activity_section.get('icon')
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
        self.screenshots = bundle_activity_section.get('screenshots', '').split()

        # bundle specific variables
        self._bundle_path = get_latest_bundle(
            os.path.join(self.get_activity_dir(), 'dist')
        )

    def __repr__(self):
        return '{name} ({path})'.format(name=self._name, path=self.activity_info_path)

    def get_bundle_path(self):
        return self._bundle_path

    def set_bundle_path(self, bundle_path):
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
        else:
            # return a dummy icon because the current icon was missing
            return os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'assets', 'activity-helloworld.svg'
            )

    def get_screenshots(self):
        """
        Returns a list of screenshots packaged in the activity
        TODO: Add support to extract screenshot from the screenshot / image directory
        returns screenshot if screenshot keyword is provided
        :return:
        """
        if self.screenshots:
            return self.screenshots
        else:
            raise NotImplementedError()

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
        return os.path.dirname(os.path.dirname(self.activity_info_path))

    def do_generate_bundle(self, override_dist_xo=False, entrypoint_build_command=None, build_command_chdir=False):
        """
        Generates a .xo file for the activities
        by spawning a subprocess

        Some additional pro level features ;)

        The script file supports python f-strings
        Pass the parameters as named {name}, {v} to get name and version appropriately

        Some important format specifiers
        {name} : Activity Name
        {v} : Activity version
        {activity_dir} : the path of the Activity, i.e ~/FractionBounce.Activity
        {icon_path}: the path of the icon path

        Make sure you add a cd (change directory) function within the shell / python script
        The script is run relative to path of execution.
        To change location each time before command execution, pass --build-chdir
        :return: Tuple (e_code, stdout, stderr)

        """
        if override_dist_xo and not entrypoint_build_command:
            raise ValueError("entrypoint_build_command was not provided")

        current_path_ = os.getcwd()
        if entrypoint_build_command and isinstance(entrypoint_build_command, str):
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

            # restore the current working directory in the case directory was changed
            if build_command_chdir:
                os.chdir(current_path_)

            if override_dist_xo:
                return exit_code, '', ''

        python_exe = get_executable_path('python3', False) or get_executable_path('python')
        proc = subprocess.Popen(
            _s("{} setup.py dist_xo".format(python_exe)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        exit_code = proc.wait(timeout=5000)
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
        flags = '' if system else '--user'
        python_exe = get_executable_path('python3', False) or get_executable_path('python')
        proc = subprocess.Popen(
            _s("{} setup.py install {}".format(python_exe, flags)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        exit_code = proc.wait(timeout=5000)
        out, err = proc.communicate()
        return exit_code, out.decode(), err.decode()

    def generate_fingerprint_json(self):
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

        return {
            "id": hashlib.sha256(self.get_name().encode() + self.get_url().encode()).hexdigest(),
            "name": self.get_name(),
            "tags": self.get_tags(),
            "summary": self.get_summary(),
            "license": self.get_license(),
            "url": self.get_url()
        }

    def is_python3(self):
        if isinstance(self._exec, str) and 'sugar-activity3' in self._exec:
            return True
        else:
            return False

    def get_activity_type(self):
        if not isinstance(self._exec, str):
            return None
        return ACTIVITY_BUILD_CLASSIFIER.get(
            self._exec.split()[0].split(os.path.sep)[-1],
            'unknown'
        )
