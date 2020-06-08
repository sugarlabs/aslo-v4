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
    'sugar-activity': 'python2 [DEPRECATED]',
    'sugar-activity-web': 'web activity'
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
    <head>
        <title>{title} - Sugar AppStore</title>
        <meta charset="utf-8"/>
        <link rel="stylesheet" type="text/css" href="../css/main.css"/>
    </head>
    <body>
        <h1>{title}</h1>
        <img src="{icon_path}"></img>
        <div id=summary>
            <h2>Summary</h2>
            <p>{summary}</p>
        </div>
        <div id=description>
            <h2>Description</h2>
            <p>{description}</p>
        </div>
        <div id=tags>
            <h2>Tags</h2>
            <ul>
                {tag_list_html_formatted}
            </ul>
        </div>
        <h2 id="downloadButton">
            <a href="{bundle_path}">Download</a>
        </h2>
        <br>
    </body>
</html>

"""