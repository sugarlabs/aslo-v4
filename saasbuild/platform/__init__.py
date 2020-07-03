"""
Sugar Activities App Store (SAAS)
https://github.com/sugarlabs-appstore/sugarappstore

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

import os
import platform

# gets the PATH environment variable
PATH = os.getenv('PATH').split(os.pathsep)
SYSTEM = platform.system()


def get_executable_path(executable, raise_error=True):
    """
    Returns the absolute path of the executable
    if it is found on the PATH,
    if it is not found raises a FileNotFoundError
    :param executable:
    :return:
    """
    if SYSTEM == 'Windows':
        executable = "{}.exe".format(executable)
    for i in PATH:
        if os.path.exists(os.path.join(i, executable)):
            return os.path.join(i, executable)
    if raise_error:
        raise FileNotFoundError(
            "Could not find {p} on PATH. "
            "Make sure {p} is added to path and try again".format(
                p=executable))
    else:
        return False
