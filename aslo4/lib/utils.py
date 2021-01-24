#!/usr/bin/env python3
"""
Sugar Activities App Store (ASLOv4)
https://github.com/sugarlabs/aslo-v4

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
import logging

from jinja2 import Environment
from aslo4.catalog import catalog
from aslo4.platform import get_executable_path, SYSTEM

split = shlex.split if SYSTEM != "Windows" else lambda x: x

logger = logging.getLogger("aslo-builder")


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
    if not os.path.exists(os.path.join(path_to_git_repository, ".git")):
        raise ValueError("Invalid git repository")

    git_rev_list_tags_max_count = subprocess.Popen(
        split(
            "{git} -C {activity_path} rev-list --tags --max-count=1".format(
                git=get_executable_path("git"), activity_path=path_to_git_repository
            )
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    e_code = git_rev_list_tags_max_count.wait(50)
    if e_code != 0:
        logger.error(
            "FATAL: Could not process `rev-list --tags` for {}".format(
                path_to_git_repository
            )
        )
        return 1

    git_commit_sha_of_tag, _ = decode_each(git_rev_list_tags_max_count.communicate())
    git_describe_tags = subprocess.Popen(
        split(
            "{git} -C {activity_path} describe --tags {sha}".format(
                git=get_executable_path("git"),
                activity_path=path_to_git_repository,
                sha=git_commit_sha_of_tag,
            )
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    e_code = git_describe_tags.wait(50)
    if e_code != 0:
        logger.warn(
            "WARN: git describe --tags for {sha} failed for {git_repo}. "
            "Continuing to build from master...".format(
                sha=git_commit_sha_of_tag, git_repo=path_to_git_repository
            ),
            "yellow",
        )
        return 1

    # checkout the tag
    tag, _err = decode_each(git_describe_tags.communicate())
    git_checkout_po = subprocess.Popen(
        split(
            "{git} -C {activity_path} checkout {tag}".format(
                git=get_executable_path("git"),
                activity_path=path_to_git_repository,
                tag=tag,
            )
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    ecode = git_checkout_po.wait(500)
    if ecode != 0:
        logger.warn(
            "WARN: checking out {} to tag {} failed. Fallback to "
            "master.".format(path_to_git_repository, tag)
        )
        return 1
    return 0


def git_checkout(path_to_git_repository, branch="master"):
    if not os.path.exists(os.path.join(path_to_git_repository, ".git")):
        raise ValueError("Invalid git repository")

    git_checkout_po = subprocess.Popen(
        split(
            "{git} -C {activity_path} checkout {branch}".format(
                git=get_executable_path("git"),
                activity_path=path_to_git_repository,
                branch=branch,
            )
        ),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    ecode = git_checkout_po.wait(500)

    if ecode != 0:
        logger.warn(
            "WARN: checking out {} to {} failed.".format(path_to_git_repository, branch)
        )
        return 1
    return 0


def read_parse_and_write_template(
    file_system_loader, html_template_path, html_output_path=None, **kwargs
):
    """
    Read HTML Template, parse the HTML template with jinja template
    renderer and write the formatted jinja template to html_output_path with
    kwargs as the argument
    :param file_system_loader: jinja2 FileSystemLoader
    :type file_system_loader: jinja2.FileSystemLoader
    :param html_template_path: Path to the HTML template
    :type html_template_path: str
    :param html_output_path: Path to write the parsed HTML template
    :type html_output_path: str
    :param kwargs:
    :type kwargs:
    :return:
    :rtype:
    """
    if html_output_path is not None:
        output_path_file_name = html_output_path.split(os.path.sep)[-1]
    else:
        output_path_file_name = html_template_path

    logger.info("[STATIC] Reading template: {}".format(output_path_file_name))
    with open(html_template_path, "r") as _buffer:
        html_template = Environment(loader=file_system_loader).from_string(
            _buffer.read()
        )

    logger.info("[STATIC] Writing parsed template: {}".format(output_path_file_name))

    rendered = html_template.render(**kwargs, catalog=catalog)
    if html_output_path is not None:
        with open(html_output_path, "w") as w:
            w.write(rendered)
    else:
        return rendered
