var miniSearch

function enableFunGradientBackground(){
    console.log("Enabling fun gradient background animation.");
    $("body").addClass("fun-gradient-animation-bg");
    setCookie("saas-fun", "true", 365);
}

function disableFunGradientBackground() {
    console.log("Disabling fun gradient background animation");
    $("body").removeClass("fun-gradient-animation-bg");
    setCookie("saas-fun", "false", 365);
}

function setCookie(cname, cvalue, exdays) {
  // A function to set cookie from document.cookie
  // https://www.w3schools.com/js/js_cookies.asp
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  // A function to get cookie from document.cookie
  // https://www.w3schools.com/js/js_cookies.asp
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function compareAlphabetically(el1, el2, index) {
  // compares el1 and el2 and returns first occuring item according 
  // to ASCII 
  return el1[index] == el2[index] ? 0 : (el1[index] < el2[index] ? -1 : 1);
}

function clearActivityCards() {
    $('#activity-card-column').empty();
}

function getActivityIndex () {
  
}

function addActivityCard(item) {
    var name = item['name'];
    var bundle_id = item['bundle_id']
    var icon_path = item['icon_name'];
    if (icon_path == null) {
        icon_path = 'org.sugarlabs.HelloWorld'
    }
    var summary = item['summary'] != null ? item['summary'] : 'No info provided';
    var url_container
    if ($.trim( item['url']) != ""){
        url_container = `<a href="${item['url']}" class="btn btn-primary"><i class="fa fa-info-circle"></i></a>`
    } else {
        url_container = ""
    }
    var bundle_path = `../bundles/${item['bundle_name']}`
    if (item['exec_type'] == 'web'){
        var exec_type = `<a data-toggle="tooltip" title="Based on WebKit. Works on most platforms"><img src="../img/activity-browse.png" alt="Works with Webkit" height=38px>`
    } else if (item['exec_type'] == 'python2') {
        var exec_type = `<a data-toggle="tooltip" title="Powered by Python2. Supported by older sugar."><img src="../img/python2.png" alt="Powered by Python2.x" height=38px>`
    } else if (item['exec_type'] == 'python3') {
        var exec_type = `<a data-toggle="tooltip" title="Powered by Python3. Supported by Sugar 0.116+"><img src="../img/python3.png" alt="Powered by Python3.x" height=38px ></a>`
    } else {
        var exec_type = ""
    }
    if (item['v']) {
        var version = `<span class="badge badge-secondary">${item['v']}</span>`
    } else {
        var version = ''
    }

    $('#activity-card-column').append(
        `<div class="card saas-card shadow-lg">\
            <img class="card-img-top" \
            style="padding:12%" src="../icons/${icon_path}.svg" alt="Activity Logo of ${name}">\
            <div class="card-body">\
                <h3 class="card-title saas-h1">
                    <a href="../app/${bundle_id}.html" style="color:#000">
                    ${name}</a>  
                    ${version}
                </h3>
                <p class="card-text">${summary}</p>\
                <a href="${bundle_path}" class="btn btn-primary"><i class="fa fa-download"></i></a>\
                ${url_container}
                ${exec_type}
            </div>\
        </div>`
    )
}


function loadAllActivities () {
    // get the json file
    if ($.trim( $('#saas-search-box').val() ) != ''){
        // the user has entered something, filter the list accordingly
        $.getJSON("../index.json", function(data) {
            console.log("Searching using miniSearch");
            if (miniSearch == null){
                // index minisearch once and only once
                // reduces CPU usage

                console.log("minisearch indexed.")
                miniSearch = new MiniSearch({
                    fields: ['name', 'summary'], // fields to index for full-text search
                    storeFields: ['name', 'summary', 'url', 'icon_name', 'bundle_name', 'v', 'bundle_id'], // fields to return with search results
                    searchOptions: {
                        boost: { title: 2 },
                        fuzzy: 0.5
                    }
                });
                // Index all documents
                miniSearch.addAll(data);
            }
            let results = miniSearch.search($('#saas-search-box').val())
            $.each(results, function(i, item){
                addActivityCard(item)
            })
        });
    } else {
        $.getJSON("../index.json", function(data) {
        console.log(data)
        // update the UI with each card

        $.each(
            data.sort(function(el1,el2){
                return compareAlphabetically(el1, el2, "name")
            }),
            function(i, item){
                addActivityCard(item)
            })
        }); 
    }
    

};