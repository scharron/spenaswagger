import requests
from urllib.parse import urljoin
import json


class API:
    class Error(Exception):
        def __init__(self, code, message, normal_error):
            self.code = code
            self.message = message
            self.normal_error = normal_error

    def __init__(self, base_url, user, password):
        self.session = requests.Session()
        self.session.auth = (user, password)
        self.base_url = base_url

    def do_request(self, method, path, query_args, body, error_codes):
        path = urljoin(self.base_url, path[1:])

        if hasattr(body, "asdict"):
            body = body.asdict()
        if body is not None:
            body = json.dumps(body)

        ret = self.session.request(method, path, params=query_args, data=body, headers={"Content-type": "application/json"})

        if ret.status_code not in error_codes:
            raise API.Error(ret.status_code, "Status code %i not expected %s\n%s" % (ret.status_code, list(error_codes.keys()), ret.content), False)

        if ret.status_code >= 200 and ret.status_code < 300:
            if len(ret.content) == 0:
                return None
            return ret.json()
        else:
            raise API.Error(ret.status_code, error_codes[ret.status_code], True)
