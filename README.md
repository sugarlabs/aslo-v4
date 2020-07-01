# Backendless search and website generator from activity bundles prototype

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/c61d2501dca44ccbbd8b590470330b32)](https://app.codacy.com/gh/sugarlabs-appstore/sugarappstore?utm_source=github.com&utm_medium=referral&utm_content=sugarlabs-appstore/sugarappstore&utm_campaign=Badge_Grade_Dashboard)

> Looking for the newer version? Click **[here](https://github.com/sugarlabs-appstore/sugarappstore/tree/oop-ss)** to switch deployed branch.

## Instruction to use

Steps:
1. Clone or download & extract this app store repository
2. run main.py script in generator folder as:

```
$ python3 main.py "/bundles/directory" "/website/template/root/directory/"
```

All sub-directories of bundles directory will be scanned for activity
bundles i.e. .xo files.

**WARNING:** for now website template has symblink of search.html as index.html. I do not know if it works in Windows OS. If not, delete index.html and copy search.html as index.html.

**WARNING 2**: error log files and info.json file will be saved in website root directory for now. delete them if not needed.

**WARNING3:** In prototype, paths are written in Unix style so likely won't work on Windows. This will be corrected after some time. For now, you can replace '/' with '\'. Also, I do not think (unsure) current directory is represented as './' (or even '.\') in Windows. So maybe remove that as well.

## Issues
### What should be the license for the project?
I am OK with any FSF approved license which is suitable for Sugarlabs needs.

### Should there be fallback backend when js is disabled in browser for search functionality to work?

## To-DO
- [x] Create search function js file, JSON data file & html page stitching them together
- [ ] NOTE: how will I ensure that results are presented in  some order when more than one search result is of equal standing in term of keywords match/ranking etc. Popularity/download counts or newest/last updated?
- [ ] Python script to automatically add all apps to app store, generate html pages and append entry to JSON search index file.
- [x] Create demo website
- [ ] Add copyright & license information
- [ ] For production version, compress index.json file. Also use compressed version of jquery.
- [ ] in parent directory of website write a script to start static file server serving website sub-directory. This will be used when not using web server such as Nginx or Apache for acting as backend eg. a user can start server from usb stick.
- [x] in live website, a link to download entire website (as pre generated zip file?)

## Design choices

### Relative path of files instead of absolute
Since app store can be started just by opening index.html or any other html file in browser rather than first starting a server (even simple localhost one), keeping paths relative have advantage over absolute as they won't break and work even when any html file is opened directly in browser. One caveat will be that moving file from one directory to another will break its references. Script generating static pages need to keep this in mind i.e. must calculate references dynamically rather than hard coding them.

### CORS considerations
Since apptore is supposed to work even without starting a static file serving server i.e. by opening absolutely any HTML file in app store website directory, only way I found that nowadays browsers allow file to be loaded is when it's included by the HTML file opened itself. Files cannot be dynamically loaded later. This rules out all ajax calls in design of app store.

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

### Generator
/generator directory contains main.py file and GeneralFunctions directory which contains portable code which are not specific to this app store and are written in a way that they can be used in any program.

#### main.py

- starts from main() function (called only if main.py directly executed and not if imported as module)

##### main()
- processArguments() function is called which builds dictionary of program directory, (activity) bundles directory and website (template) directory from arguments given to generator.

- **extractData** is the main function which extract all the data from bundles and writes it to website directory.

##### extractData class
*Tip: all the functions in extractData function are sorted in alphabetical order*

- __init__() declares all object variables and call methods in order of operation

    - self.createDirectories() - create directories used in website directory (if not already present) such as app, bundles, icons, js. Aborts program if fails to create directories eg. if no write permission.
    
    - self.findBundles() - find all activity bundles i.e. .xo files in website directory and stores in self.activityBundles list
    
    - self.purgeBundlesNotZipFile() - test with python standard library method zipfile.is_zipfile() and removes bundles which fails this test from self.activityBundles list
    
    - self.extractInfoAndIconFromBundles() :
        - reads activity.info files in bundles (skips bundles in which find no or more than one activity.info files)
        - create variables dictionary from extracted information and appends dictionary to self.bundlesInfoList
        - Looks for icon variables in dictionary and extracts icon file (skips if fails but continue processing that bundle as icon is not critical).
        - copies bundle to website/directory/bundles
        
    - self.generateInfoJson() - converts self.bundlesInfoList to json format and stores it in self.infoJson variable
    
    - self.generateIndex() :
        - extracts name, summary, description, tag, tags, category, categories from self.infoJson and stores in self.indexDictList in dictionary format and self.indexJs in json (string) format.
        - Since several variables in selfinfoJson can map to one variable in index eg. tag, tags, category, categories all considered tags in index. Therefore, we first check if key already exist in index, if not than add, else append to data of existing value in dictionary.
            - tuple and list are both considered same and treated same i.e. comma separated. while string is space separated.
        - For all keys which are not added to dictionaries in the above process, empty entry is added. Eg. if summary is not written in activty.info file, than empty summary is ultimately added to index.json rather than no entry at all.
        - **NOTE:** self.indexJs is js file string rather than json file. Its contains just a function call search.assignIndex([index json]) . (search is a class in search.js file in website-templates/js/ directory.
        
    - self.generateAppsHtmlPages() - generates html pages from self.indexDictList and simultaneously saves rather than storing in memory.
    
    - self.writeFiles() - info.json, index.js errors....txt files are written to files.
    
### Website template

-  index.html - symblink to search.html for now

- search.html - search page

- /js/search.js - contains search class and general (portable) code which serves the search requests
    - similarString() - case/*base* insensitive comparison of strings eg. 'A' == 'a' == 'à'.
    
    - countSimilarWordsInStrings() - split words and do word by word comparison and count how many are similar by calling similarString()
    
    - partialStrMatch() - Wok-in-progress function. intend is to match eg. 'car' == 'cars' and return .75 as 75% string match. This can possibly be tweaked to also include matches when typing error and suggest closest relevant word based on proportion/percentage match.
    
    - search class - implements search functionality
        - search.init() - called when page completes loading
            - checks if any search query. if yes,
                - fills search query back into search box ($('input[name="q"]')[0].value = query;)
                - calls this.performSearch() withs earch query
        
        - assignIndex() - this is the function called from index.js
            - stores index in this._index variable
                - checks if any query in queue and call this.performSearch is so. Queries can be in queue if this._index was not loaded by that time and searched now when the index is loaded.
                
        - performSearch() - checks if index has loaded. calls processSearch() with query if so, else add query to queue.
        
        - processSearch() - this function calls rankApps() to rank apps (in index) based on their match with query and displays 10 (for now) matched apps by calling displayResults()
        
        - rankApps() - calls rankApp() to rank each app against query and stores in [rank, app index in this_index] array.
        
        - rankApp() - calls countSimilarWordsInStrings() and rewards 10 points for match in name, 3 in summary, 2 in description and 5 in tags.
        
        - displayResults() - unhides #searchResults div in search.html and presents search results or no search result found message.
        
        - appObjToHtml() - generates html to present for matches apps. use index.json as source for generating.

# License
AGPL-3.0-or-later. See [LICENSE](LICENSE) for more information.

Copyright 2020 Manish <sugar@radii.dev>

## Credits
* Includes [jQuery](https://jquery.org/) library (JS Foundation and other contributors)
* Studied but not used [Sphinx](https://www.sphinx-doc.org/) tool (Georg Brandl and the Sphinx team)
