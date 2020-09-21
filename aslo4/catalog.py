class Catalog:
    def __init__(self):
        self.name = "Sugar App Store"
        self.prefix = "/aslo"
        self.description = "Sugar Labs App Store"
        self.organization = "Sugar Labs"
        self.search_box = {
            "placeholder_text": "Search for Activities!"
        }
        self.org_details = {
            "homepage": "https://sugarlabs.org",
            "wiki": "https://wiki.sugarlabs.org",
            "legacy_appstore": "https://activities.sugarlabs.org/",
        }
        self.git_repository = "https://github.com/sugarlabs/aslo-v4"
        self.is_github = True

    @property
    def bug_tracker(self):
        if self.is_github:
            return "{}/issues".format(self.git_repository)
        else:
            return ""



