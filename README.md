# Backendless search and website generator from activity bundles prototype

## Instruction to use

Steps:
1. Download & extract this app store repository
2. run main.py script in generator folder as:

```
$ python3 main.py "/bundles/directory" "/website/template/root/directory/
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
