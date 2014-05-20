import logging
import re
import requests
from connector import Connector
from commit import Commit
import xml.etree.ElementTree as ET
from geogitexception import GeoGitException
import traceback

logger = logging.getLogger(__name__)

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

    def default_params(self, **kwargs):
        """
        Returns generic parameters used for all requests.
        """
        kwargs.setdefault('output_format', 'json')
        return kwargs

    def request(self, url, method='get', **kwargs):
        """
        A convenience method for making requests to the Geoserver GeoGit API.
        """
        kwargs.setdefault('params', self.default_params())
        kwargs.setdefault('auth', (self.username, self.password))

        logger.debug('Making a {0} request, with the following parameters: {1}'.format(method.upper(), kwargs))

        return getattr(requests, method)(url, **kwargs)

    def checkisrepo(self):
        """
        Checks a GeoGit repository by running the status command.
        """
        return self.status().get('success', False)

    def begin_transaction(self):
        """
        Creates a transaction in GeoGit.
        """

        r = self.request(self.repo.url + '/beginTransaction')
        response = self.parse_response(r.json())
        return response

    def end_transaction(self, transaction_id, cancel=True):
        """
        Ends a transaction in GeoGit.
        """
        params = self.default_params(transactionId=transaction_id, cancel=cancel)
        r = self.request(self.repo.url + '/endTransaction', params=params)
        response = self.parse_response(r.json())
        return response

    def status(self):
        """
        Returns the output of the status command.
        """
        try:
            r = self.request(self.repo.url + '/status')
            response = self.parse_response(r.json())
            return response
        except Exception, e:
            print traceback.format_exc()
            raise GeoGitException("Unable to get the repo status.")

    def revparse(self, rev):
        """
        Returns the output of the refparse command.
        """
        try:
            url = self.repo.url + '/refparse'
            r = self.request(url, params=self.default_params(name=rev))
            response = self.parse_response(r.json()).get('Ref')
            return response
        except Exception, e:
            print traceback.format_exc()
            raise GeoGitException("Reference %s not found" % rev)

    def parse_commit(self, commit):
        """
        Parses the web response into a Commit object.
        """

        author = commit.get('author', {})
        committer = commit.get('committer', {})

        return Commit(self.repo,
                      commitid=commit.get('id'),
                      treeid=commit.get('tree'),
                      parents=commit.get('parents'),
                      message=commit.get('message'),
                      authorname=author.get('name'),
                      authordate=author.get('timestamp'),
                      committername=committer.get('name'),
                      committerdate=committer.get('timestamp')
                      )

    def log(self, **kwargs):
        """
        Returns the output of the log command.
        """

        try:
            kwargs.update(self.default_params())
            r = self.request(self.repo.url + '/log', params=kwargs)
            response = self.parse_response(r.json())
            commits = response.get('commit', [])
            return map(lambda c: self.parse_commit(c), commits)

        except Exception, e:
            print traceback.format_exc()
            raise GeoGitException("Unable to retrieve the repositories log.")

    def version(self):
        """
        Returns the output of the version command.
        """
        try:
            r = self.request(self.repo.url + '/version')
            return self.parse_response(r.json())

        except Exception, e:
            print traceback.format_exc()
            raise GeoGitException("Unable to retrieve version output.")