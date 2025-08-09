from tdigest import TDigest
import json

def serialize_tdigest(td: TDigest):
    return json.dumps(td.__getstate__())

def deserialize_tdigest(s: str):
    td = TDigest()
    td.__setstate__(json.loads(s))
    return td
