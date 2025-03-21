import json


def ok(data: dict or list or str or None = None) -> str:
    body = {
        'code': 0,
        'msg': "success",
        'data': data
    }
    return json.dumps(body)
