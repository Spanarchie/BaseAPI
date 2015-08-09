__author__ = 'colinmoore-hill'


import unittest
from flask.ext.testing import TestCase
from BaseAPI import app


class BaseTestCase(TestCase):
    """ The base Test case! """

    def create_app(self):
        app.config.from_object('config.TestConfig')
        return app


    def setUp(self):
        pass
        #db.create_all()

    def tearDown(self):
        pass
        #db.session.remove()
        #db.drop_all

class FlaskTestCase(BaseTestCase):
    """ Initial validation of the page """

    def test_index(self):
        print("Test Starting")
        response = self.client.get("/", content_type='html/text')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()