import os
import hashlib
import uuid

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
RDF_TEMPLATE = """<?xml version="1.0"?>
<RDF:RDF xmlns:RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#" \
xmlns:em="http://www.mozilla.org/2004/em-rdf#">
    <RDF:Description about="urn:mozilla:extension:{bundle_id}">
        <em:updates>
            <RDF:Seq>
                <RDF:li resource=\
"urn:mozilla:extension:{bundle_id}:{version}"/>
            </RDF:Seq>
        </em:updates>
    </RDF:Description>
    <RDF:Description about="urn:mozilla:extension:{bundle_id}:{version}">
        <em:version>{version}</em:version>
        <em:targetApplication>
            <RDF:Description>
                <em:id>{uuid}</em:id>
                <em:minVersion>{min_version}</em:minVersion>
                <em:maxVersion>{max_version}</em:maxVersion>
                <em:updateLink>{update_link}</em:updateLink>
                <em:updateSize>{update_size}</em:updateSize>
                <em:updateInfoURL>{update_info}</em:updateInfoURL>
                <em:updateHash>{sha_type}:{sha_hash}</em:updateHash>
            </RDF:Description>
        </em:targetApplication>
    </RDF:Description>
</RDF:RDF>"""


def get_sha256(filepath):
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()

    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
            sha256.update(data)
    return {"md5": md5.hexdigest(), "sha256": sha256.hexdigest()}


class RDF:
    def __init__(
        self,
        bundle_id,
        bundle_version,
        bundle_path,
        min_version="0.116",
        max_version="0.117",
        base_url="http://activities.sugarlabs.org/bundles",
        info_url="https://activities.sugarlabs.org/activity",
    ):
        """
        Generates a RDF file based on the properties of the activity Bundle
        :param bundle_id: recognized bundle id of the Activity
        :type bundle_id: str
        :param bundle_version: version of the activity
        :type bundle_version: str
        :param bundle_path: absolute path to the bundle
        :type bundle_path: str
        :param min_version: minimum version of sugar os required to run the
        activity
        :type min_version: str
        :param max_version: maximum version of sugar os required to run the
        activity
        :type max_version: str
        :param base_url: url to download activities
        :type base_url: str
        :param info_url: url to provide information about the activities
        :type info_url: str
        """
        self.bundle_id = bundle_id
        self.bundle_version = bundle_version
        self.bundle_path = bundle_path
        self.base_url = base_url
        self.info_url = info_url
        if self.base_url.endswith("/"):
            # remove trailing slash
            self.base_url = self.base_url[:-1]

        self.compatibility = {"min": min_version, "max": max_version}

    @property
    def bundle_file_name(self):
        return self.bundle_path.split(os.path.sep)[-1]

    @property
    def url(self):
        return "{base_url}/{bundle_dist_xo}".format(
            base_url=self.base_url, bundle_dist_xo=self.bundle_file_name
        )

    def __repr__(self):
        return "RDF ({})".format(self.bundle_id)

    def get_bundle_size(self):
        return os.path.getsize(self.bundle_path) // 1000

    def parse(self):
        return RDF_TEMPLATE.format(
            bundle_id=self.bundle_id,
            version=self.bundle_version,
            uuid="{{{}}}".format(uuid.uuid4()),
            min_version=self.compatibility["min"],
            max_version=self.compatibility["max"],
            update_link=self.url,
            sha_type="sha256",
            sha_hash=get_sha256(self.bundle_path)["sha256"],
            update_size=self.get_bundle_size(),
            update_info="{}/{}.html".format(self.info_url, self.bundle_id),
        )
