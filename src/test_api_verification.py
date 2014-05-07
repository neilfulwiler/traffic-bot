import unittest
import backend

class TestVerification(unittest.TestCase):
    def test_verification_fail(self):
        """
        pass the verifier a no-op backend, and make sure
        that some no-op things work, but that reading from
        an experiment that should be non-empty fails
        """
        mock_backend = backend.MockBackend()
        verifier = mock_backend.VerifiedBackend(base_backend=mock_backend)

        # logging should be fine
        verifier.log(100, 1)

        # and reading from an empty experiment should be fine (see MockBackendApi)
        verifier.results(99)

        # but reading from a non-empty experiment should throw a verification error
        self.assertRaises(backend.VerificationError, verifier.results, 100)

    def test_verification_fail(self):
        """
        this is kind of a no-op because the verifier internally uses an
        inMemoryBackend anyway, but that might change
        """
        mock_backend = backend.InMemoryBackend()
        verifier = mock_backend.VerifiedBackend(base_backend=mock_backend)

        verifier.log(100, 1)
        verifier.results(100)

if __name__ == '__main__':
    unittest.main()
