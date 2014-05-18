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



if __name__ == '__main__':
    unittest.main()