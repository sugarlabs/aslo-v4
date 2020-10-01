![sugarlabs aslo4 logo](assets/aslo4.svg)

# aslo4

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/65d6f5534bb24ea9b2a0ca0075341c2f)](https://www.codacy.com/gh/sugarlabs-appstore/aslo-v4?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=sugarlabs-appstore/aslo-v4&amp;utm_campaign=Badge_Grade)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aslo4?style=flat-square) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/aslo4?style=flat-square) ![PyPI](https://img.shields.io/pypi/v/aslo4?style=flat-square)](https://pypi.org/project/aslo4/)
![GitHub repo size](https://img.shields.io/github/repo-size/sugarlabs-appstore/aslo-v4?style=flat-square) ![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/sugarlabs-appstore/aslo-v4/latest/master?sort=semver&style=flat-square) ![GitHub](https://img.shields.io/github/license/sugarlabs-appstore/aslo-v4?style=flat-square) ![Codecov](https://img.shields.io/codecov/c/gh/sugarlabs-appstore/aslo-v4?style=flat-square)

## Introduction

The ASLO is an acronym for activities.sugarlabs.org. It is an activity store for
Sugar Activities. It is called `aslo4`, 

### Install from PyPI
```bash
pip3 install aslo4
```

## Setup
* Clone the repository
```bash
git clone https://github.com/sugarlabs/aslo-v4
```
For a shallow clone
```bash
git clone https://github.com/sugarlabs/aslo-v4 --depth=1
```

* Change directory to cloned directory
```bash
cd aslo-v4
```
* Run the program
```bash
python3 -m aslo4
```


## Minimal usage

ASLO4 generator (`aslo4`) is highly customizable. A sample usage and explanation have been provided below

### Pre-requisites

* A collection of Sugar Activities in a dedicated folder. (The folder may contain other stuff). `aslo4` technically looks for `activity.info`, but not recursively. If the directory where you have clones is called `repo` (for example), then `aslo4` will only check `repo/**/activity/activity.info` exists.  If, it does not match the pattern, then the folder is ignored. We have avoided recursion through directories, due to the possibility of a longer build time, etc.
* `CPython 3.6+`, To build `python3` activities, you need `python3` executable in `PATH`. To support `python2` activities, you need `python2` on `PATH`.
* `git`executable, should be available in `PATH`
* (optional): `sugar-toolkit-gtk3`, `sugar-toolkit` (to build activities, i.e., to create bundle `.xo`)

> NOTE: Executable `python` is ambiguous. It has different implementations on different linux. So we prefer to stick to stricter executable names. i.e, `python2` or `python3`

### Simple Build Commands (preferred)

0. Clone a few activities, for this test case, I am considering the `Pippy` Activity and `speak` activity
   ```bash
   mkdir activities
   git clone https://github.com/sugarlabs/Pippy.git activities/Pippy
   git clone https://github.com/sugarlabs/speak.git activities/speak
   ```
   
1. To list all activities 
   The `./activities` contains the folders `Pippy` and `speak`. The names could be different too. But each of the
   folder must contain a `./<activity_name>/activity/activity.info` to be detected as an activity.
   ```bash
   python -m aslo4 -i ./activities --list-activities 
   ```

2. To build `.xo`

   ```bash
   python -m aslo4 -i ./activities -b
   ```
   This command will generate `Pippy-9.xo` in `./activities/Pippy/dist/Pippy-9.xo` and `speak-X.xo` in `./activities/speak/dist/speak-X.xo`
   

3. To create ASLO4:

   ```bash
   python -m aslo4 --input-directory ./activities --pull-static-css-js-html ./aslo4-static --generate-static-html --build-xo
   ```
   This command will automatically extract the bundles from the `dist` folders of the respective activities, and parse
   `NEWS` from `./activities/Pippy/NEWS` and get attributes from `./activities/Pippy/activity/activity.info`
   
#### Alternative build method (without Activity Source)

This part provides instructions to build the `aslo4` without cloning the activity / by only providing the finally built
bundle `.xo`.

1. Place all the bundles `*.xo` in a folder, say `bundles`
   ```bash
   mkdir bundles
   cp /path/to/some/bundles/*.xo .  # copies all the bundles from /path/to/some/bundles to the current directory `bundles`
   ```
2. List all the activities to make sure the `*.xo` are detected 
   ```bash
   python3 -m aslo4 -i ./bundles --list-activities 
   ```
3. Now create the appstrore
   ```bash
   python3 -m aslo4 -i ./bundles --generate-sitemap --pull-static-css-js-html ./aslo4-static 
   ```

Both the methods mentioned with build the aslo4 in `aslo4-compiled` directory. (The name `saas` will be changed in future) which can be overriden by using `-o` flag

These commands will create a minimal aslo4 activity library.    

> For advanced usage, see [Usage](#usage)

## Usage

```bash
$ python3 -m aslo4 --help
usage: ASLO4 generator [-h] [-i INPUT_DIRECTORY] [-o OUTPUT_DIRECTORY] [-b]
                                [--build-entrypoint BUILD_ENTRYPOINT] [--build-override]
                                [--build-chdir] [-l] [-g] [-x GENERATE_SITEMAP] [-v]
                                [-p PULL_STATIC_CSS_JS_HTML] [-u] [-P] [-s] [-f] [-y] [-c] [-z]
                                [--version]

Generates static HTML files for ASLOv4

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                        Provide the directory to scan for Sugar activity bundles *.xo
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Provide the directory to output the parsed website for ASLOv4
  -b, --build-xo        Generate XO bundles for a large number of directories
  --build-entrypoint BUILD_ENTRYPOINT
                        Specify a path to any Linux compatible script which is intended to be
                        executed on every build
  --build-override      Override `python setup.py dist_xo` with --build-entrypoint argument shell
                        script
  --build-chdir         Changes directory to Activity dir
  -l, --list-activities
                        Lists all the activities available in the directory
  -g, --generate-static-html
                        Start the process of HTML generation. (pass -b, if you are unsure if
                        bundles are already created)
  -x GENERATE_SITEMAP, --generate-sitemap GENERATE_SITEMAP
                        Generate a sitemap.xml file to the output directory
  -v, --verbose         More verbose logging
  -p PULL_STATIC_CSS_JS_HTML, --pull-static-css-js-html PULL_STATIC_CSS_JS_HTML
                        Provide the path to js, css and index.html (ideally from
                        $PWD/aslo4-static)
  -u, --unique-icons    Provides a unique icon name based on bundle id
  -P, --disable-progress-bar
                        Provides a unique icon name based on bundle id
  -s, --include-screenshots
                        Includes screenshots of activity if its found as
                        <activity>/screenshots/*.png
  -f, --include-flatpaks
                        Includes a flatpak description card if the activity has a valid flatpak
                        registered under flathub.org
  -y, --noconfirm       Replace output directory (default: always ask)
  -c, --no-colors       Suppress colors in terminal (default: env ANSI_COLORS_DISABLED)
  -z, --include-python2
                        Include python2 support (sugar-activity)
  --version             Show the version

```

### Parameters
* `-i INPUT_DIRECTORY`: is a directory containing cloned activities or unzipped bundles. 
                        If bundles are pre-generated, add the activity.info, place the bundles in `dist` directory as
                        convention
* `-o OUTPUT_DIRECTORY` : directory to output the website
* `-b --build-xo` : Iterate through all the directories as provided in the `INPUT_DIRECTORY` abd generate .xo
* `-g --generate-static-html` : compiles the information in `activity.info` to create HTML files

All sub-directories of bundles directory will be scanned for activity
bundles i.e. .xo files.

## TODO
- [x] Create search function js file, JSON data file & html page stitching them together
- [ ] NOTE: how will I ensure that results are presented in  some order when more than one search result is of equal standing in term of keywords match/ranking etc. Popularity/download counts or newest/last updated?
- [x] Python script to automatically add all apps to aslo4, generate html pages and append entry to JSON search index file.
- [x] Create demo website
- [x] Add copyright & license information
- [x] For production version, compress index.json file. Also use compressed version of jquery.
- [ ] in parent directory of website write a script to start static file server serving website sub-directory. This will be used when not using web server such as Nginx or Apache for acting as backend eg. a user can start server from usb stick.
- [x] in live website, a link to download entire website (as pre generated zip file?)

## Design choices

### Relative path of files instead of absolute
Since `aslo4` can be started just by opening index.html or any other html file in browser rather than first starting a server (even simple localhost one), keeping paths relative have advantage over absolute as they won't break and work even when any html file is opened directly in browser. One caveat will be that moving file from one directory to another will break its references. Script generating static pages need to keep this in mind i.e. must calculate references dynamically rather than hard coding them.

### CORS considerations
Since `aslo4` is supposed to work even without starting a static file serving server i.e. by opening absolutely any HTML file in `aslo4` website directory, only way I found that nowadays browsers allow file to be loaded is when it's included by the HTML file opened itself. Files cannot be dynamically loaded later. ~this rules out all ajax calls in design of app store.~ I have used AJAX calls :smile:

Thankfully, we can ask browser to defer loading of some files and wait for those files (search index) to be loaded. Instead of setting a asynchronous sleeping counter to check if search index is loaded, it's better if search index itself tell that it has loaded and we than perform any search in queue.
Credit: sphinx-doc code.

### jQuery framework
jQuery library is used as its lightweight and reduce a lot of code footprint (making project easy to maintain). Its more than enough as per our project requirement.

## Code guide
*Tip: if you don't have many activity bundles to test with than [download](https://github.com/tony37/Sugaractivities/archive/master.zip) or [clone](https://github.com/tony37/Sugaractivities.git) Tony's repo. It contains many (outdated) bundles in /activities directory.*

/generator/main.py (written as generator below) uses /website template to build website in /website directory.

generator takes two arguments
1. directory of bundles - Directory and all sub-directories are recursively scanned for .xo files
2. directory of website template - website will be generated in this directory

# License
AGPL-3.0-or-later. See [LICENSE](LICENSE) for more information.

Copyright (C) 2020 

[Manish](https://github.com/free-libre-software) <sugar@radii.dev>,  
[Srevin Saju](https://github.com/srevinsaju) <srevinsaju@sugarlabs.org>

## Credits
* Includes [jQuery](https://jquery.org/) library (JS Foundation and other contributors)
