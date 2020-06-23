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

FLATPAK_HTML_TEMPLATE = \
"""<div class="card text-white bg-info mb-3" style="border-radius: 1rem;">
  <div class="card-header"><i class="fa fa-box" aria-hidden="true"></i> Flatpak</div>
  <div class="card-body">
    <h5 class="card-title">{activity_name} Activity is also available as a flatpak!</h5>
    <p class="card-text">Installing activities as flatpaks helps to run Activities made for Sugar desktop to be run on any linux.</p>
    <a href="https://flathub.org/repo/appstream/{bundle_id}.flatpakref" class="btn btn-light saas-activity-download-button">
        <i class="fa fa-download" aria-hidden="true"></i> Download .flatpakref
    </a>
    <a href="https://flathub.org/apps/details/{bundle_id}.flatpakref" class="btn btn-light saas-activity-download-button" style="margin-right:0.5rem">
        <i class="fa fa-box" aria-hidden="true"></i> Flathub
    </a>
</div></div>"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>

    <head>
        <title>{title} - Sugar AppStore</title>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <!-- Font Awesome icon pack -->
        <script src="https://kit.fontawesome.com/52ec62d041.js" crossorigin="anonymous" async></script>
        <!-- Open Sans font -->
        <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700;800&display=swap" 
        rel="stylesheet">
        <!-- Mobile Responsive compatibility layer -->
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" 
        integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
        <link rel="stylesheet" type="text/css" href="../css/common.css">
        <link rel="stylesheet" type="text/css" href="../css/main.css"/>
        <link rel="stylesheet" type="text/css" href="../css/fun.css"/>
    </head>
    <body class="boring-gradient-bg">
        <div class="container saas-activity-main">
            <div class="row">
                <div class="col-md-8 mx-auto">
                    <div class="card saas-activity-card-std shadow-lg">
                        <img class="mx-auto saas-activity-card-image" 
                        src="{icon_path}" 
                        alt="Logo of the activity {title}">
                        </img>
                        <h1 class="card-title text-center">{title}</h1>
                        <div class="saas-activity-card-version mx-auto">
                            <span class="badge badge-success saas-badge">
                                Version <span class="badge badge-dark">{version}</span>
                            </span> <span class="badge badge-dark saas-badge">
                                License {licenses}
                            </span>
                        </div>
                        <div class="saas-activity-card-summary" id=summary>
                            <h3>Summary</h3>
                            <p>{summary}</p>
                        </div>
                        <div class="saas-activity-card-description" id=description>
                            <h3>Description</h3>
                            <p>{description}</p>
                        </div>
                        <div class="saas-activity-card-tags" id="authors">
                            <h3>Authors</h3>
                            {author_list_html_formatted}
                        </div>
                        <div class="saas-activity-card-tags" id="tags">
                            <h3>Tags</h3>
                            {tag_list_html_formatted}
                        </div>
                        <div class="saas-activity-new-features">
                            <h4>New in this Version</h4>
                            <ul>
                                {new_features}
                            </ul>
                        </div>
                        <div class="saas-activity-changelog">
                            <h4>Changelog</h4>
                            <pre class="pre-scrollable"><code>{changelog}</code></pre>
                        </div>

                        <a href="{bundle_path}" class="btn btn-primary saas-activity-download-button">
                            <i class="fa fa-download"></i> Download
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </body>
</html>

"""

SITEMAP_HEADER = \
"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{content}
</urlset>
"""

SITEMAP_URL = \
"""<url>
  <loc>{url}</loc>
  <lastmod>{lastmod}</lastmod>
  <changefreq>{changefreq}</changefreq>
  <priority>0.8</priority>
</url>
"""