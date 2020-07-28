#!/usr/bin/env python3
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
import os
import shlex
import subprocess

from aslo4.lib.termcolors import cprint
from aslo4.platform import get_executable_path, SYSTEM

split = shlex.split if SYSTEM != 'Windows' else lambda x: x


def decode_each(iterable):
    """
    Decodes each item to 'utf-8' or defaults and returns an iterable
    :param iterable:
    :type iterable:
    :return:
    :rtype:
    """
    return (x.decode() for x in iterable)


def git_checkout_latest_tag(path_to_git_repository):
    if not os.path.exists(os.path.join(path_to_git_repository, '.git')):
        raise ValueError("Invalid git repository")

    git_rev_list_tags_max_count = subprocess.Popen(
        split(
            '{git} -C {activity_path} rev-list --tags --max-count=1'.format(
                git=get_executable_path('git'),
                activity_path=path_to_git_repository
            )),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    e_code = git_rev_list_tags_max_count.wait(50)
    if e_code != 0:
        cprint("FATAL: Could not process `rev-list --tags` for {}".format(
                    path_to_git_repository
        ), "red")
        return 1

    git_commit_sha_of_tag, _ = \
        decode_each(git_rev_list_tags_max_count.communicate())
    git_describe_tags = subprocess.Popen(
        split(
            '{git} -C {activity_path} describe --tags {sha}'.format(
                git=get_executable_path('git'),
                activity_path=path_to_git_repository,
                sha=git_commit_sha_of_tag
            )),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    e_code = git_describe_tags.wait(50)
    if e_code != 0:
        cprint(
            "WARN: git describe --tags for {sha} failed for {git_repo}. "
            "Continuing to build from master...".format(
                sha=git_commit_sha_of_tag,
                git_repo=path_to_git_repository
            ),
            "yellow"
        )
        return 1

    # checkout the tag
    tag, _err = decode_each(git_describe_tags.communicate())
    git_checkout_po = subprocess.Popen(
        split(
            '{git} -C {activity_path} checkout {tag}'.format(
                git=get_executable_path('git'),
                activity_path=path_to_git_repository,
                tag=tag
            )),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    ecode = git_checkout_po.wait(500)
    if ecode != 0:
        cprint("WARN: checking out {} to tag {} failed. Fallback to "
               "master.".format(
                    path_to_git_repository, tag
                ),
               "yellow")
        return 1
    return 0


def git_checkout(path_to_git_repository, branch="master"):
    if not os.path.exists(os.path.join(path_to_git_repository, '.git')):
        raise ValueError("Invalid git repository")

    git_checkout_po = subprocess.Popen(
        split(
            '{git} -C {activity_path} checkout {branch}'.format(
                git=get_executable_path('git'),
                activity_path=path_to_git_repository,
                branch=branch
            )),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    ecode = git_checkout_po.wait(500)

    if ecode != 0:
        cprint("WARN: checking out {} to {} failed.".format(
                    path_to_git_repository, branch
                ),
               "yellow")
        return 1
    return 0
