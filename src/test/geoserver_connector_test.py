import unittest
from geogitpy.geoserverconnector import GeoserverConnector
from geogitpy.repo import Repository


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
        response = self.gs.revparse('master')
        self.assertTrue('Ref' in response)
        self.assertTrue('success' in response)


if __name__ == '__main__':
    unittest.main()