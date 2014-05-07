import requests
from collections import defaultdict

class InMemoryBackend(object):
    def __init__(self):
        self.variations = defaultdict(set)

    def log(self, variation, user):
        self.variations[variation].add(user)

    def results(self, variation):
        return self.variations[variation]

class RemoteBackend(object):
    def __init__(self, host):
        self.host = host

    def log(self, variation, user):
        self._rest('log/%d/%s' % (variation, user))

    def results(self, variation):
        return self._rest('results/%d' % variation).json()['results']

    def _rest(self, path):
        return requests.get('http://%s/%s' % (self.host, path))

class VerifiedBackend(object):
    def __init__(self, base_backend):
        self.base_backend = base_backend
        self.verifier = InMemoryBackend()

    def log(self, variation, user):
        self.verifier.log(variation, user)
        self.base_backend.log(variation, user)

    def results(self, variation):
        expected = self.verifier.results(variation)
        actual = self.base_backend.results(variation)

        # is this check ok?
        if len(expected) != len(actual):
            raise VerificationError(variation, expected, actual)

class MockBackend(object):
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
