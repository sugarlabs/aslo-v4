/*
MIT License

Copyright (c) 2020
Srevin Saju <srevinsaju (at) sugarlabs (dot) org>
Manish <sugar (at) radii (dot) dev>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

var miniSearch;


function compareAlphabetically(el1, el2, index) {
  // compares el1 and el2 and returns first occuring item according
  // to ASCII
  return el1[index] == el2[index] ? 0 : (el1[index] < el2[index] ? -1 : 1);
}

function clearActivityCards() {
  $('#activity-card-column').empty();
}

function getActivityIndex() {
  return;
}

function addActivityCard(item) {
  const name = item['name'];
  const bundle_id = item['bundle_id'];
  let icon_path = item['icon_name'];
  if (icon_path == null) {
    icon_path = 'org.sugarlabs.HelloWorld';
  }
  const summary = item['summary'] != null ? item['summary'] : 'No info provided';
  let url_container;
  if ($.trim( item['url']) != '') {
    url_container = `<a href="${item['url']}" class="btn btn-primary"><i class="fa fa-info-circle"></i></a>`;
  } else {
    url_container = '';
  }
  const bundle_path = `../bundles/${item['bundle_name']}`;
  if (item['exec_type'] == 'web') {
    var exec_type = `<a data-toggle="tooltip" title="Based on WebKit. Works on most platforms"><img src="../img/sugarweb-1.svg" alt="Works with Webkit" height=38px>`;
  } else if (item['exec_type'] == 'python2') {
    var exec_type = `<a data-toggle="tooltip" title="Powered by Python2. Supported by older sugar."><img src="../img/sugar2-1.svg" alt="Powered by Python2.x" height=38px>`;
  } else if (item['exec_type'] == 'python3') {
    var exec_type = `<a data-toggle="tooltip" title="Powered by Python3. Supported by Sugar 0.116+"><img src="../img/sugar3-1.svg" alt="Powered by Python3.x" height=38px ></a>`;
  } else {
    var exec_type = '';
  }
  if (item['v']) {
    var version = `<span class="badge badge-secondary">${item['v']}</span>`;
  } else {
    var version = '';
  }
  if ( getCookie('saas-theme') == 'dark') {
    var theme = 'saas-card-dark';
    var themeHeading = 'saas-card-heading-link-dark';
    var themeImage = 'saas-card-image-top-dark';
  } else {
    var theme = '';
    var themeHeading = '';
    var themeImage = '';
  }

  $('#activity-card-column').append(
      `<div class="card saas-card shadow-lg ${theme}">\
            <div class="saas-image-placeholder">
                <img  class="card-img-top saas-card-image-hidden saas-card-image-top ${themeImage}" 
                    style="position:absolute; top:0; left:0; width:100%;" loading="lazy" \
                    onload="fadeIn(this)"
                    src="../icons/${icon_path}.svg" alt="Activity Logo of ${name}"
                    >\
            </div>
            <div class="card-body">\
                <h3 class="card-title saas-h1">
                    <a href="../app/${bundle_id}.html" class="saas-card-heading-link ${themeHeading}">
                    ${name}</a>
                    ${version}
                </h3>
                <p class="card-text">${summary}</p>\
                <a type="application/zip" href="${bundle_path}" class="btn btn-primary"><i class="fa fa-download"></i></a>\
                ${url_container}
                ${exec_type}
            </div>\
        </div>`,
  );
}


function loadAllActivities() {
  // get the json file
  if ($.trim( $('#saas-search-box').val() ) != '') {
    // the user has entered something, filter the list accordingly
    $.getJSON('../index.json', function(data) {
      console.log('Searching using miniSearch');
      if (miniSearch == null) {
        // index minisearch once and only once
        // reduces CPU usage

        console.log('minisearch indexed.');
        miniSearch = new MiniSearch({
          fields: ['name', 'summary'], // fields to index for full-text search
          storeFields: ['name', 'summary', 'url', 'icon_name', 'bundle_name', 'v', 'bundle_id'], // fields to return with search results
          searchOptions: {
            boost: {title: 2},
            fuzzy: 0.5,
          },
        });
        // Index all documents
        miniSearch.addAll(data);
      }
      const results = miniSearch.search($('#saas-search-box').val());
      $.each(results, function(i, item) {
        addActivityCard(item);
      });
    });
  } else {
    $.getJSON('../index.json', function(data) {
      // update the UI with each card
      $.each(
          data.sort(function(el1, el2) {
            return compareAlphabetically(el1, el2, 'name');
          }),
          function(i, item) {
            addActivityCard(item);
          });
    });
  }
};
