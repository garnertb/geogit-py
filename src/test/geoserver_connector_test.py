import unittest
from geogitpy.geoserverconnector import GeoserverConnector
from geogitpy.repo import Repository
from geogitpy.commit import Commit


class Repo(object):
    pass


class GeoserverConnectorTest(unittest.TestCase):

    def setUp(self):
        self.username = None
        self.password = None
        self.gs = GeoserverConnector(username=self.username, password=self.password)
        self.gs.repo = Repo()
        self.gs.repo.url = 'http://dev.rogue.lmnsolutions.com/geoserver/geogit/geonode:copeco_td_repo'

    def test_checkisrepo(self):
        """
        Tests the checkisrepo method.
        """
        self.assertTrue(self.gs.checkisrepo())

    def test_status(self):
        """
        Tests the status method.
        """
        self.assertDictEqual(self.gs.status(), {u'header': {u'branch': u'master'}, u'success': True})

    def test_revparse(self):
        """
        Tests the revparse function.
        """
        response = self.gs.revparse('master')
        self.assertTrue('name' in response)
        self.assertTrue('objectId' in response)
        self.assertEqual(response.get('name'), 'refs/heads/master')

    def test_log(self):
        """
        Tests the log function.
        """

        response = self.gs.log()
        self.assertTrue(len(response))
        self.assertTrue(all(map(lambda c: isinstance(c, Commit), response)))

    def test_version(self):
        """
        Tests the version function.
        """
        response = self.gs.version()
        self.assertTrue('BuildTime' in response)
        self.assertTrue('BuildUserName' in response)
        self.assertTrue('BuildUserEmail' in response)
        self.assertTrue('GitBranch' in response)
        self.assertTrue('GitCommitID' in response)
        self.assertTrue('GitCommitTime' in response)
        self.assertTrue('GitCommitAuthorName' in response)
        self.assertTrue('GitCommitAuthorEmail' in response)
        self.assertTrue('GitCommitMessage' in response)

    def test_transactions(self):
        """
        Tests the begin_transaction method.
        """

        response = self.gs.begin_transaction()
        self.assertTrue('Transaction' in response)
        self.assertTrue('ID' in response['Transaction'])

        id = response['Transaction']['ID']
        response = self.gs.end_transaction(transaction_id=id)
        self.assertTrue(response.get('success'))

    def test_push(self):
        """
        Tests the push/pull operations.
        """
        #TODO: Needs standalone integration test.
        response = self.gs.push(remote='aws', ref='master:master')
        self.assertTrue('Push' in response)
        self.assertTrue('dataPushed' in response)
        self.assertTrue(response.get('success'))

    def test_pull(self):
        """
        Tests the push/pull operations.
        """
        #TODO: Needs standalone integration test.
        response = self.gs.pull(remote='aws', ref='master:master')
        self.assertTrue('Pull' in response)
        self.assertTrue('Fetch' in response['Pull'])
        self.assertTrue(response.get('success'))

    def test_ls_tree(self):
        """
        Tests the ls-tree command.
        """
        response = self.gs.ls_tree()
        self.assertTrue('node' in response)
        self.assertTrue('path' in response['node'][0])


if __name__ == '__main__':
    unittest.main()