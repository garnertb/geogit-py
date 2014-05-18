import re
import requests
from connector import Connector
from commit import Commit
import xml.etree.ElementTree as ET
from geogitexception import GeoGitException
import traceback

SHA_MATCHER = re.compile(r"\b([a-f0-9]{40})\b")


class GeoserverConnector(Connector):
    """ A connector that connects to a GeoGit repo through the Geoserver GeoGit API."""

    def __init__(self, username=None, password=None):

        self.password = password
        self.username = username

    @staticmethod
    def parse_response(response):
        """
        Parses a Geoserver GeoGit API response.
        """
        return response.get('response')

    def default_params(self):
        """
        Returns generic parameters used for all requests.
        """
        return dict(output_format='json')

    def checkisrepo(self):
        """
        Checks a GeoGit repository by running the status command.
        """
        return self.status().get('success', False)

    def status(self):
        """
        Returns the output of the status command.
        """
        try:
            url = self.repo.url + '/status'
            r = requests.get(url, auth=(self.username, self.password), params=self.default_params())
            response = self.parse_response(r.json())
            return response
        except Exception, e:
            print traceback.format_exc()
            raise GeoGitException("Unable to get the repo status.")

    def revparse(self, rev):
        try:
            url = self.repo.url + '/refparse'
            params = self.default_params().copy()
            params.update(dict(name=rev))
            r = requests.get(url, params=params)
            response = self.parse_response(r.json())
            print response
            return response
        except Exception, e:
            print traceback.format_exc()
            raise GeoGitException("Reference %s not found" % rev)


    @staticmethod
    def createrepo(url, name):
        r = requests.put(url, data = name)
        r.raise_for_status()
