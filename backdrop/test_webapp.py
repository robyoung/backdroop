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


    def add_records(self):
        payload = json.dumps([
            {"_timestamp": "2012-12-12T12:12:12+00:00", "unique_visitors": 1234},
            {"_timestamp": "2012-12-13T12:12;12+00:00", "unique_visitors": 4321},
            {"_timestamp": "2012-12-21T12:12;12+00:00", "unique_visitors": 4321},
            {"_timestamp": "2013-02-01T12:12;12+00:00", "unique_visitors": 4321},
        ])
        self.app.post('/data-sets/foobar/data',
                data=payload,
                content_type='application/json')

    def test_raw_query(self):
        self.add_records()
        
        result = self.app.get('/data-sets/foobar/data')
        data = json.loads(result.data)

        assert len(data) == 4
        assert data[0]['_timestamp'] == "2012-12-12T12:12:12+00:00"
        assert data[1]['_timestamp'] == "2012-12-13T12:12:00+00:00"


    def test_group_by(self):
        self.add_records()

        result = self.app.get('/data-sets/foobar/data?group_by=unique_visitors')
        data = json.loads(result.data)
        
        assert len(data) == 2
        assert data[0]['_count'] == 1
        assert data[0]['unique_visitors'] == 1234

    def test_period(self):
        self.add_records()

        result = self.app.get('/data-sets/foobar/data?period=week')
        data = json.loads(result.data)
        
        assert len(data) == 3
        assert data[0]['_start_at'] == "2012-12-10T00:00:00+00:00"
        assert data[1]['_start_at'] == "2012-12-17T00:00:00+00:00"

if __name__ == '__main__':
    unittest.main()
