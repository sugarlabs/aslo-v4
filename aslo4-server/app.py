import flask
from flask import request, Response
import urllib.request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

DOMAIN = "http://0.0.0.0:9999/api"


@app.route('/update-aslo.php', methods=['GET'])
def update_aslo():
    bundle_id = request.args.get("id")
    app_version = request.args.get("appVersion")
    try:
        if float(app_version) < 0.116:
            return ''
    except ValueError:
        return ''

    with urllib.request.urlopen(
            '{domain}/{bundle_id}.xml'.format(
                domain=DOMAIN, bundle_id=bundle_id)
    ) as f:
        xml = f.read().decode('utf-8')

    response = Response(xml, mimetype='text/xml')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/wake', methods=['GET'])
def wake():
    response = flask.jsonify({"test": "Ok"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response




if __name__ == "__main__":
    app.run()

