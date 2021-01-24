import os

import yaml

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import Loader


class CatalogBase:
    def __init__(
        self,
        protocol: str = "",
        name: str = "",
        domain: str = "",
        email: str = "",
        prefix: str = "",
        description: str = "",
        organization: str = "",
        search_box: dict = None,
        org_details: dict = "",
        git_repository: str = "",
        is_github: bool = False,
    ):
        self.protocol = protocol or "https://"
        self.name = name or "Sugar Activity Library"
        self.domain = domain or ""
        self.email = email or ""
        self.prefix = prefix or ""
        self.description = (
            description or "Curated collection of amazing Sugar Activities"
        )
        self.organization = organization or "Sugar Labs"
        self.search_box = search_box or {"placeholder_text": "Search for Activities!"}
        self.org_details = org_details or {
            "homepage": "https://sugarlabs.org",
            "wiki": "https://wiki.sugarlabs.org",
            "legacy_appstore": "https://activities.sugarlabs.org/",
        }
        self.git_repository = git_repository or "https://github.com/sugarlabs/aslo-v4"
        self.is_github = is_github or True

    @property
    def bug_tracker(self):
        if self.is_github:
            return "{}/issues".format(self.git_repository)
        else:
            return ""

    @property
    def url(self):
        return self.protocol + self.domain + self.prefix


class CatalogLoader:
    @classmethod
    def from_yaml(cls, path_to_yaml) -> CatalogBase:
        with open(path_to_yaml) as fp:
            data = yaml.load(fp, Loader=Loader)
        protocol = data["webpage"]["url"]["protocol"]
        domain = data["webpage"]["url"]["domain"]
        prefix = data["webpage"]["url"]["prefix"]
        email = data["webpage"]["email"]
        name = data["name"]
        description = data["description"]
        search_box = data["homepage"]["search_box"]
        organization = data["organization"]["name"]
        org_details = data["organization"]
        git_repository = data["source"]["git_repository"]
        is_github = data["source"]["is_github"]
        return CatalogBase(
            protocol=protocol,
            name=name,
            domain=domain,
            email=email,
            prefix=prefix,
            description=description,
            organization=organization,
            org_details=org_details,
            search_box=search_box,
            git_repository=git_repository,
            is_github=is_github,
        )


if os.getenv("CI"):
    catalog = CatalogBase()
else:
    path = os.getenv("ASLOv4_CONFIG_YML")
    if not path:
        raise RuntimeError("$ASLOv4_CONFIG_YML is not defined as env var.")
    catalog = CatalogLoader.from_yaml(path)
