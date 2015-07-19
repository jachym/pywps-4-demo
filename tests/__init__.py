import sys
import unittest

from tests import test_capabilities
from tests import test_describe
from tests import test_execute
#from tests import test_exceptions

def load_tests():
    return unittest.TestSuite([
        test_capabilities.load_tests(),
        test_describe.load_tests(),
        test_execute.load_tests()
    ])

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(load_tests())
    if not result.wasSuccessful():
        sys.exit(1)
