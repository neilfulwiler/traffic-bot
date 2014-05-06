import requests
from collections import defaultdict

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

class VerifiedBackendApi(object):
    """
    you must either provide a base_api or a host/port
    in which case the default backend api will be assumed
    """
    def __init__(self, host=None, port=None, base_api=None):
        if base_api is None:
            assert host is not None
            assert port is not None
            self.base_api = BackendApi(host, port)
        else:
            self.base_api = base_api

        self.variations = defaultdict(set)

    def log(self, variation, user):
        self.variations[variation].add(user)
        self.base_api.log(variation, user)

    def results(self, variation):
        expected = self.variations[variation]
        actual = self.base_api.results(variation)
        if len(expected) != len(actual):
            raise VerificationError(variation, expected, actual)

class MockBackendApi(object):
    def log(self, variation, user):
        pass

    def results(self, variation):
        return []

class VerificationError(Exception):
    def __init__(self, variation, expected, actual):
        print 'verification error on variation %s. expected %s, got %s' % (variation, expected, actual)
        self.variation = variation
        self.expected = expected
        self.actual = actual
