import hashlib
import os
import shlex
import subprocess
import uuid
from configparser import ConfigParser

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

    def __repr__(self):
        return '{name} ({path})'.format(name=self._name, path=self.activity_info_path)

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

    def do_generate_bundle(self):
        """
        Generates a .xo file for the activities
        by spawning a subprocess
        :return:
        """
        python_exe = get_executable_path('python3', False) or get_executable_path('python')
        proc = subprocess.Popen(
            _s("{} setup.py dist_xo".format(python_exe)),
            cwd=self.get_activity_dir(),
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        exit_code = proc.wait(timeout=5000)
        out, err = proc.communicate()
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
