import unittest
import time

import opentsdb # the module under test

class TestOpentsdb(unittest.TestCase):
    def test_call_frequency_monitoring(self):

        @opentsdb.ConsoleMonitor('testMetric')
        def f():
            pass

        test_frequency = 10.0
        for i in range(10):
            f()
            time.sleep(1. / test_frequency)

        test_metric = opentsdb.metrics['testMetric']
        self.assertAlmostEqual(test_frequency, test_metric.get_call_frequency(), delta=.1)

    def test_call_execution_time_monitoring(self):
        test_execution_time = .1

        @opentsdb.ConsoleMonitor('anotherTestMetric')
        def f():
            time.sleep(test_execution_time)

        test_frequency = 10.0
        for i in range(10):
            f()
            time.sleep(1. / test_frequency)

        test_metric = opentsdb.metrics['anotherTestMetric']
        self.assertAlmostEqual(test_execution_time, test_metric.get_execution_time(), delta=.1)

if __name__ == '__main__':
    unittest.main()



