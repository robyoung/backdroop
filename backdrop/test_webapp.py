from .webapp import app
import unittest
import json
import pymongo

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pymongo.Connection()['backdroop']['foobar'].drop()

    def test_add(self):
        payload = json.dumps([
            {"_timestamp": "2012-12-12T12:12:12+00:00", "unique_visitors": 1234},
            {"_timestamp": "2012-12-13T12:12;12+00:00", "unique_visitors": 4321},
        ])
        self.app.post('/data-sets/foobar/data',
                data=payload,
                content_type='application/json')
        
        result = self.app.get('/data-sets/foobar/data')
        print(result.data)

if __name__ == '__main__':
    unittest.main()
