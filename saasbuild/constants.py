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