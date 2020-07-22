import flask
from flask import request, Response
import urllib.request

app = flask.Flask(__name__)
app.config["DEBUG"] = True

DOMAIN = "http://sugarstore.netlify.app/api"
OLD_DOMAIN = \
    "http://activities.sugarlabs.org/services/update-aslo.php?id={i}&appVersion={v}"

RDF_HEADERS = """<?xml version="1.0"?>
<RDF:RDF xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#" \
xmlns:em="http://www.mozilla.org/2004/em-rdf#"></RDF:RDF>"""


@app.route('/update-aslo.php', methods=['GET'])
def update_aslo():
    xml = RDF_HEADERS
    bundle_id = request.args.get("id")
    app_version = request.args.get("appVersion")
    try:
        float(app_version)
    except ValueError:
        response = Response(xml, mimetype='text/xml')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    if float(app_version) < 0.116:
        with urllib.request.urlopen(
                OLD_DOMAIN.format(i=bundle_id, v=app_version)
        ) as f:
            xml = f.read().decode('utf-8')
    else:
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

