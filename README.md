![sugarlabs appstore logo](https://raw.githubusercontent.com/sugarlabs-appstore/appstore-assets/master/sugarappstore.svg)

# sugarappstore

[![Netlify Status](https://api.netlify.com/api/v1/badges/4f6dde9a-8b1c-4e8e-9f2f-13f453988e82/deploy-status)](https://app.netlify.com/sites/sugarstore/deploys)

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c61d2501dca44ccbbd8b590470330b32)](https://app.codacy.com/gh/sugarlabs-appstore/sugarappstore?utm_source=github.com&utm_medium=referral&utm_content=sugarlabs-appstore/sugarappstore&utm_campaign=Badge_Grade_Dashboard)

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sugarstore-generator?style=flat-square) ![PyPI - Wheel](https://img.shields.io/pypi/wheel/sugarstore-generator?style=flat-square) ![PyPI](https://img.shields.io/pypi/v/sugarstore-generator?style=flat-square)](https://pypi.org/project/sugarstore-generator/)
![GitHub repo size](https://img.shields.io/github/repo-size/sugarlabs-appstore/sugarappstore?style=flat-square) ![GitHub commits since latest release (by SemVer)](https://img.shields.io/github/commits-since/sugarlabs-appstore/sugarappstore/latest/master?sort=semver&style=flat-square) ![GitHub](https://img.shields.io/github/license/sugarlabs-appstore/sugarappstore?style=flat-square) ![Codecov](https://img.shields.io/codecov/c/gh/sugarlabs-appstore/sugarappstore?style=flat-square)

## Introduction

Sugar App Store is an app store to distribute apps
and games made for sugar, which are commonly known as sugar-activities.

### Install from PyPI
```bash
pip3 install sugarstore-generator
```

## Setup
* Clone the repository
```bash
git clone https://github.com/sugarlabs-appstore/sugarappstore
```
For a shallow clone
```bash
git clone https://github.com/sugarlabs-appstore/sugarappstore --depth=1
```

* Change directory to cloned directory
```bash
cd sugarappstore
```
* Run the program
```bash
python3 -m sugarstore_generator
```



## Minimal usage

Sugar Labs appstore generator (`sugarstore_generator`) is highly customizable. A sample usage and explanation have been provided below

### Pre-requisites

* A collection of Sugar Activities in a dedicated folder. (The folder may contain other stuff). `sugarstore_generator` technically looks for `activity.info`, but not recursively. If the directory where you have clones is called `repo` (for example), then `sugarstore_generator` will only check `repo/**/activity/activity.info` exists.  If, it does not match the pattern, then the folder is ignored. We have avoided recursion through directories, due to the possibility of a longer build time, etc.
* `CPython 3.6+`, To build `python3` activities, you need `python3` executable in `PATH`. To support `python2` activities, you need `python2` on `PATH`.
* `git`executable, should be available in `PATH`
* (optional): `sugar-toolkit-gtk3`, `sugar-toolkit` (to build activities, i.e., to create bundle `.xo`)

> NOTE: Executable `python` is ambiguous. It has different implementations on different linux. So we prefer to stick to stricter executable names. i.e, `python2` or `python3`

### Simple Build Commands

1. To list all activities 

   ```bash
   python -m sugarstore_generator -i /path/to/repository --list-activities 
   ```

2. To build `.xo`

   ```bash
   python -m sugarstore_generator -i /path/to/repository -b
   ```

3. To create appstore

   ```bash
   git clone https://github.com/sugarlabs-appstore/sugarappstore-static path/to/save/static/files
   python -m sugarstore_generator -i /path/to/repository -b -p path/to/save/static/files -o path/to/website/save/directory
   ```

   

> For advanced usage, see [Usage](#usage)

## Usage

```bash
$ python3 -m sugarstore_generator --help
usage: Sugar Appstore generator [-h] [-i INPUT_DIRECTORY] [-o OUTPUT_DIRECTORY] [-b]
                                [--build-entrypoint BUILD_ENTRYPOINT] [--build-override]
                                [--build-chdir] [-l] [-g] [-x GENERATE_SITEMAP] [-v]
                                [-p PULL_STATIC_CSS_JS_HTML] [-u] [-P] [-s] [-f] [-y] [-c] [-z]
                                [--version]

Generates static HTML files for SAAS

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_DIRECTORY, --input-directory INPUT_DIRECTORY
                        Provide the directory to scan for Sugar activity bundles *.xo
  -o OUTPUT_DIRECTORY, --output-directory OUTPUT_DIRECTORY
                        Provide the directory to output the parsed website for SAAS
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
                        https://github.com/sugarlabs-appstore/sugarappstore-static)
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
- [x] Python script to automatically add all apps to app store, generate html pages and append entry to JSON search index file.
- [x] Create demo website
- [x] Add copyright & license information
- [x] For production version, compress index.json file. Also use compressed version of jquery.
- [ ] in parent directory of website write a script to start static file server serving website sub-directory. This will be used when not using web server such as Nginx or Apache for acting as backend eg. a user can start server from usb stick.
- [x] in live website, a link to download entire website (as pre generated zip file?)

## Design choices

### Relative path of files instead of absolute
Since app store can be started just by opening index.html or any other html file in browser rather than first starting a server (even simple localhost one), keeping paths relative have advantage over absolute as they won't break and work even when any html file is opened directly in browser. One caveat will be that moving file from one directory to another will break its references. Script generating static pages need to keep this in mind i.e. must calculate references dynamically rather than hard coding them.

### CORS considerations
Since appstore is supposed to work even without starting a static file serving server i.e. by opening absolutely any HTML file in app store website directory, only way I found that nowadays browsers allow file to be loaded is when it's included by the HTML file opened itself. Files cannot be dynamically loaded later. This rules out all ajax calls in design of app store.

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
