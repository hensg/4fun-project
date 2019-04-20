"""Generic"""
import json

class Generic:
    """
    Model class to map attributes from json/hbase to json/hbase
    """
    def __init__(self, pk, values):
        self.pk = pk # pylint: disable=C0103
        self.values = values

    @classmethod
    def from_json(cls, json): # pylint: disable=W0621
        """Create object from json"""
        return cls(json['pk'], json)

    @classmethod
    def from_hbase(cls, key, value):
        """Create object from hbase"""
        key_str = key if isinstance(key, str) else key.decode()
        return cls(key_str, json.loads(value[b'value:value'].decode()))

    def to_dict(self):
        """returns as dict"""
        return self.values

    def to_json(self):
        """returns as json"""
        return json.dumps(self.values)

    def to_hbase(self):
        return {b'value:value':json.dumps(self.values)}
