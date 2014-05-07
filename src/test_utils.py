import unittest
import inspect

import utils # module under test

class TestUtils(unittest.TestCase):
    def test_keep_signature(self):
        @utils.safe('empty function')
        def f(x):
            pass

        print inspect.getargspec(f)

if __name__ == '__main__':
    unittest.main()
