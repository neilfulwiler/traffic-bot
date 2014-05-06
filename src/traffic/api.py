import requests

class BackendApi(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def log(self, variation, user):
        self._rest('log/%d/%s' % (variation, user))

    def results(self, variation):
        return self._rest('results/%d' % variation).json()['results']

    def _rest(self, path):
        return requests.get('http://%s:%d/%s' % (self.host, self.port, path))
