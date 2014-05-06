import unittest
import backend

class TestVerification(unittest.TestCase):
    def test_verification(self):
        mock_backend = backend.MockBackendApi()
        verifier_api = backend.VerifiedBackendApi(base_api=mock_backend)

        # logging should be fine
        verifier_api.log(100, 1)

        # and reading from an empty experiment should be fine (see MockBackendApi)
        verifier_api.results(99)

        # but reading from a non-empty experiment should throw a verification error
        self.assertRaises(backend.VerificationError, verifier_api.results, 100)

if __name__ == '__main__':
    unittest.main()
