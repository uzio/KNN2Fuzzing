from bson import ObjectId

import datetime
import json


class JSONEncoder(json.JSONEncoder):
    """
    extend json-encoder class
    """
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)
