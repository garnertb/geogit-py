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
    """
    A connector that connects to a GeoGit repo through the Geoserver GeoGit API.
    Implements commands from:

    https://github.com/boundlessgeo/GeoGit/blob/master/src/web/api/src/main/java/org/geogit/web/api/CommandBuilder.java
    """

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

    def base_command(self, command, **kwargs):
        r = self.request(self.repo.url + '/{0}'.format(command), **kwargs)
        response = self.parse_response(r.json())
        return response

    def blame(self, commit, path):
        """
        Returns the output of the blame command.
        """
        return self.base_command('blame', commit=commit, path=path)

    def checkisrepo(self):
        """
        Checks a GeoGit repository by running the status command.
        """
        return self.status().get('success', False)

    def begin_transaction(self):
        """
        Creates a transaction in GeoGit.
        """
        return self.base_command('beginTransaction')

    def ls_tree(self, **kwargs):
        """
        Returns the output of the ls-tree command.
        """

        return self.base_command('ls-tree')

    def end_transaction(self, transaction_id, cancel=True):
        """
        Ends a transaction in GeoGit.
        """
        params = self.default_params(transactionId=transaction_id, cancel=cancel)
        return self.base_command('endTransaction', params=params)

    def status(self):
        """
        Returns the output of the status command.
        """
        return self.base_command('status')

    def revparse(self, rev):
        """
        Returns the output of the refparse command.
        """

        params = self.default_params(name=rev)
        return self.base_command('refparse', params=params).get('Ref')

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

    def push_pull(self, remote, ref, command='push', **kwargs):
        """
        A base method for the push and pull operations.
        """
        kwargs.update(self.default_params(remoteName=remote, ref=ref))
        return self.base_command(command, params=kwargs)

    def pull(self, remote, ref, **kwargs):
        """
        Returns the output of the push command.
        """
        return self.push_pull(remote, ref, command='pull', **kwargs)

    def push(self, remote, ref, **kwargs):
        """
        Returns the output of the push command.
        """
        return self.push_pull(remote, ref, **kwargs)

    def log(self, **kwargs):
        """
        Returns the output of the log command.
        """

        kwargs.update(self.default_params())
        response = self.base_command('log', params=kwargs)
        return map(lambda c: self.parse_commit(c), response.get('commit', []))

    def version(self):
        """
        Returns the output of the version command.
        """

        return self.base_command('version')
