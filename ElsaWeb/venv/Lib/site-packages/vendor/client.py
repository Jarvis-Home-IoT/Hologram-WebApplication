"""The client module contains the Vendor client for calling the remote Vendor service."""
import requests


class VendorClient(object):
    """The Vendor client."""

    def __init__(self, service_url):
        """Create new instance of Vendor client."""
        self.service_url = service_url
        self.session = requests.Session()
