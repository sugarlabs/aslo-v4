import os
import flask
from flask import request, Response
import urllib.request

app = flask.Flask(__name__)

# use production
app.config["DEBUG"] = os.getenv("ASLO4_SERVER_DEBUG") or False

# domain names
ASLO4_DOMAIN = os.getenv(
    "ASLO4_DOMAIN") or "https://v4.activities.sugarlabs.org"
ASLO1_DOMAIN = os.getenv("ASLO1_DOMAIN") or "https://activities.sugarlabs.org"

# api end points
ASLO4_DOMAIN_API_ENDPOINT = f"{ASLO4_DOMAIN}" + "/api"
ASLO1_DOMAIN_API_ENDPOINT = f"{ASLO1_DOMAIN}" + \
    "/services/update-aslo.php?id={i}&appVersion={v}"

# headers for RDF output
_RDF_HEADERS = """<?xml version="1.0"?>
<RDF:RDF xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#" \
xmlns:em="http://www.mozilla.org/2004/em-rdf#"></RDF:RDF>"""


@app.route('/services/update-aslo.php', methods=['GET'])
def update_aslo():
    xml = _RDF_HEADERS
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
                ASLO1_DOMAIN_API_ENDPOINT.format(i=bundle_id, v=app_version)
        ) as f:
            xml = f.read().decode('utf-8')
    else:
        aslo4_domain_formatted_endpoint = f"{ASLO4_DOMAIN_API_ENDPOINT}/{bundle_id}.xml"
        print(aslo4_domain_formatted_endpoint)
        with urllib.request.urlopen(aslo4_domain_formatted_endpoint) as f:
            xml = f.read().decode('utf-8')

    response = Response(xml, mimetype='text/xml')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/ping', methods=["GET"])
def wake():
    response = flask.jsonify({"pong": "Ok"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == "__main__":
    app.run()
