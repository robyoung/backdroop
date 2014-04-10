
__all__ = ["Data"]

class Data(object):
    def create(self, data_set_id, schema):
        """Create a data set according to a schema"""
        pass

    def exists(self, data_set_id):
        """Check if a data set exists"""
        pass

    def save(self, data_set_id, record):
        """Save a record to the data set"""
        pass

    def query(self, data_set_id, query):
        """Query against a data set"""
        pass
