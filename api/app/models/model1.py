"""Model1"""
import json

class Model1:
    """
    Model class to map attributes from json/hbase to json/hbase
    """
    def __init__(self, pk, score):
        self.pk = pk # pylint: disable=C0103
        self.score = score

    @classmethod
    def from_json(cls, json): # pylint: disable=W0621
        """Create model1 object from json"""
        return cls(json['pk'], json['score'])

    @classmethod
    def from_hbase(cls, key, value):
        """Create model1 object from hbase"""
        key_str = key if isinstance(key, str) else key.decode()
        return cls(key_str, value[b'score:score'].decode())

    def to_dict(self):
        """returns model1 as dict"""
        return {
            'pk': self.pk,
            'score': self.score
        }

    def to_json(self):
        """returns model1 as json"""
        return json.dumps({
            'pk': self.pk,
            'score': self.score
        })

    def to_hbase(self):
        """returns model1 as hbase dict of bytes"""
        return {
            b'score:score': self.score.encode()
        }
