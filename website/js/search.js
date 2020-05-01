"use strict";

var similarString = function(a, b) {
    return !a.localeCompare(b, undefined, {sensitivity: 'base'});
}

var countSimilarWordsInStrings = function(str1, str2) {
    var count = 0;
    var array1 = str1.split(' ');
    var array2 = str2.split(' ');
    for (var wordX of array1) {
        for (var wordY of array2) {
            if (similarString(wordX, wordY))
                count++;
        }
    }
    return count;
}

// FIXME: function not yet tested
var partialStrMatch = function(str1, str2) {
    var lengthDiff = str1.length - str2.length;
    
    if (lengthDiff < 0) {
        [str1, str2] = [str2, str1];
        lengthDiff = -lengthDiff;
    }
    
    for (var i=0; i <= lengthDiff; i++) {
        var str1Part = str1.substr(i, i+lengthDiff);
        if (similarString(str1Part, str2))
            return 1;
    }
    return 0;
}

var search = {
    
    _index : null,
    _queuedQuery : null,
    
    appObjToHtml : function(app) {
        var html = '<hr><h1><a href="./app/'+app.name+'.html">'+app.name+'</a></h1>\n<p><img src="./icons/'+app.name+'.svg" style="max-width: 250px"></img></p>\n<div id=summary><h2>Summary</h2>\n<p>'+app.summary+'</p>\n</div>\n<div id=description><h2>Description</h2>\n<p>'+app.description+'</p>\n</div>\n<div id=tags><h2>Tags</h2>\n<ul>\n';
        for (var tag of app.tags)
            html += '<li>'+ tag +'</li>\n';
        html += '</ul>\n</div>\n<h2 id="downloadButton"><a href="' +
                './bundles/' + app.name + '.xo' +
                '">Download</a></h2>\n';
        return html;
    },
    
    assignIndex : function(index) {
        this._index = index;
        if (this._queuedQuery !== null) {
            var queuedQuery = this._queuedQuery;
            this._queuedQuery = null;
            performSearch(queuedQuery);
        }
    },
    
    displayResults : function(results) {
        $("#searchResults").show();
        
        if (results[0][0] <= 0) {
            $(".sR:eq(1)").html("<h1>No search result found</h1>");
            return;
        }
        
        for (var i=0; i <= $(".sR").length; i++) {
            
//           No more entries matching query
            if (results[i][0] <= 0)
                break
                
            var app = this._index[results[i][1]];
            var html = this.appObjToHtml(app);
            $(".sR:eq("+i+")").html(html);
        }
    },
    
    getQueryParameters : function (queryString) {
        var queryString = document.location.search;
        return this.parseQueryParameters(queryString);
    },
    
    indexLoaded : function () {
        return (this._index !== null);
    },
    
    init : function () {
        var params = this.getQueryParameters();
        if (params.q) {
            var query = params.q[0];
            query = query.replace("+", " ");
            $('input[name="q"]')[0].value = query;
            this.performSearch(query);
        }
    },
        
    parseQueryParameters : function (queryString) {
        var parameters = {}
        var parts = queryString.substr(queryString.indexOf('?')+1).split('&');
        for (var pair of parts) {
            var spliter = pair.indexOf('=');
            var key = pair.substr(0, spliter);
            var value = pair.substr(spliter+1);
            if (key in parameters)
                parameters[key].push(value);
            else
            parameters[key] = [value];
        }
        return parameters;
    },
    
    performSearch : function (query) {
        if (this.indexLoaded())
            this.processSearch(query);
        else
            this._queuedQuery = query;
    },
    
    processSearch : function (query) {
        var results = this.rankApps(query);
        
        results.sort(function(a, b) {
            // sort in descending rank order
            return b[0]-a[0];
        });
        
        this.displayResults(results);
    },
    
    rankApp : function(app, query) {
        var rank = 0;
        rank += 10*countSimilarWordsInStrings(app.name, query);
//         rank += partialStrMatch(app.name, query);
        rank += 3*countSimilarWordsInStrings(app.summary, query);
//         rank += partialStrMatch(app.summary, query);
        rank += 2*countSimilarWordsInStrings(app.description, query);
//         rank += partialStrMatch(app.description, query);
        for (var tag of app.tags)
            rank += 5*countSimilarWordsInStrings(tag, query);
        // below statement causes error: tag is undefined when empty?
//             rank += partialStrMatch(tag, query);
        return rank;
    },
    
    rankApps : function(query) {
        var results = [];
        for (var i=0; i < this._index.length; i++) {
            var app = this._index[i];
            var rank = this.rankApp(app, query);
            results.push([rank, i]);
        }
        return results;
    }
  
};

$(document).ready( function() {
    search.init();
});
