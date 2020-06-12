"""
Sugar Activities App Store (SAAS)
https://github.com/sugarlabs-aslo/sugarappstore

Copyright 2020 SugarLabs
Copyright 2020 Srevin Saju <srevinsaju@sugarlabs.org>
Copyright 2020 Manish <sugar@radii.dev>

This file is part of "Sugar Activities App Store" aka "SAAS".

SAAS is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

SAAS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with SAAS.  If not, see <https://www.gnu.org/licenses/>.
"""

ACTIVITY_BUILD_CLASSIFIER = {
    'sugar-activity3': 'python3',
    'sugar-activity': 'python2',
    'sugar-activity-web': 'web'
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>

    <head>
        <title>{title} - Sugar AppStore</title>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <!-- Font Awesome icon pack -->
        <link href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" rel="stylesheet">
        <!-- Open Sans font -->
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700;800&display=swap" rel="stylesheet"> 
        <!-- Mobile Responsive compatibility layer -->
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

        <link rel="stylesheet" type="text/css" href="../css/main.css"/>
    </head>
    <body>
        <div class="container saas-activity-main">
            <div class="row">
                <div class="col-md-8 mx-auto"> 
                    <div class="card saas-activity-card-std shadow-lg">
                        <img class="mx-auto saas-activity-card-image" src="{icon_path}"></img>
                        <h1 class="card-title text-center">{title}</h1>
                        
                        <div class="saas-activity-card-summary" id=summary>
                            <h3>Summary</h3>
                            <p>{summary}</p>
                        </div>
                        <div class="saas-activity-card-description" id=description>
                            <h3>Description</h3>
                            <p>{description}</p>
                        </div>
                        <div class="saas-activity-card-tags"  id="tags">
                            <h3>Tags</h2>
                            {tag_list_html_formatted}
                        </div>
                        <a href="{bundle_path}" class="btn btn-primary saas-activity-download-button">
                            <i class="fa fa-download"></i>Download
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>

"""