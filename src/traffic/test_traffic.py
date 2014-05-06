import unittest
import traffic # the module under test
import mock
import opentsdb

import time

class TestTraffic(unittest.TestCase):
    def test_stop_traffic(self):
        config = {
                'host' : 'doesnt matter',
                'port' : 1234,
                'reads_per_second' : 10,
                'writes_per_second' : 10,
                'writes_percent_unique' : 1234
                }

        api = mock.BackendApi()

        traffic_controller = traffic.generate_traffic(config, api)

        start = time.time()
        traffic_controller.stop()
        elapsed_time = time.time() - start
        self.assertLess(elapsed_time, 2) # it should stop immediately

    def test_approximate_rate(self):
        config = {
                'host' : 'doesnt matter',
                'port' : 1234,
                'reads_per_second' : 0,
                'writes_per_second' : 100,
                'writes_percent_unique' : 1234
                }

        api = mock.BackendApi()

        traffic_controller = traffic.generate_traffic(config, api)
        time.sleep(3)
        traffic_controller.stop()

        read_monitor = opentsdb.metrics['read']
        write_monitor = opentsdb.metrics['write']

        self.assertEqual(0.0, read_monitor.call_frequency.current_value())

        actual_value = write_monitor.call_frequency.current_value()
        expected_value = 100

        # make sure error is less than 10%
        self.assertLess((actual_value - expected_value) / expected_value, .1)

if __name__ == '__main__':
    unittest.main()
