import json
from abc import ABC


class AbsException(Exception, ABC):

    def __init__(self, code=None, msg=None, data=None, http_code=None, headers=None):
        self.code = code
        self.msg = msg
        self.data = data or {}
        self.http_code = http_code or 500
        self.headers = headers or {'Content-Type': 'application/json'}
        super().__init__(self.msg)

    def get_body(self):
        body = {
            'code': self.code,
            'msg': self.msg,
            'data': self.data
        }
        return json.dumps(body)

    def get_headers(self):
        return self.headers


"""404"""


class NotFound(AbsException):
    def __init__(self, msg='the resource are not found', data=None, http_code=None, headers=None):
        super().__init__(code=404, msg=msg, data=data, http_code=http_code, headers=headers)


"""500"""


class InternalError(AbsException):
    def __init__(self, msg='the server internal error', data=None, http_code=None, headers=None):
        super().__init__(code=500, msg=msg, data=data, http_code=http_code, headers=headers)


"""参数异常-400"""


class ParamError(AbsException):
    def __init__(self, msg='user param error', data=None, http_code=None, headers=None):
        super().__init__(code=400, msg=msg, data=data, http_code=http_code, headers=headers)


"""认证/权限异常-401"""


class AuthError(AbsException):
    def __init__(self, msg='user auth error', data=None, http_code=None, headers=None):
        super().__init__(code=401, msg=msg, data=data, http_code=http_code, headers=headers)