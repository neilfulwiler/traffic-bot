"""
Usage:
    traffic.py <traffic.yaml>

replays read/write traffic against a backend specified
by the traffic.yaml file (see traffic.yaml.md)

we currently don't care about experiments (just variations)
"""

import threading
import time
import sys
import os
import yaml
import traffic.controller
import api.backend
from monitoring import opentsdb
from functools import partial

def usage(msg=None):
    if msg is not None:
        print msg
        print

    print >>sys.stderr, __doc__
    sys.exit(1)

def generate_traffic(config, backend_api=None, monitor=None):
    try:
        host = config['host']
        port = int(config['port'])
        rps = int(config['reads_per_second'])
        wps = int(config['writes_per_second'])
        writes_percent_unique = int(config['writes_percent_unique'])
    except KeyError as e:
        raise Exception('missing required configuration parameter %s' % e)
    except ValueError as e:
        raise Exception('malformed configuration parameter: %s' % e)

    backend_api = backend_api or api.backend.VerifiedBackendApi(host, port)
    monitor = monitor or partial(opentsdb.ConsoleMonitor, verbose=True)

    controller = traffic.controller.TrafficController(
            rps,
            wps,
            writes_percent_unique,
            backend_api,
            monitor)

    import signal
    def stop_controller(signum, frame):
        controller.stop()
    signal.signal(signal.SIGINT, stop_controller)

    controller_thread = controller.start()
    while controller_thread.isAlive():
        controller_thread.join(1)


def main(args):
    if len(args) != 1:
        usage(msg='wrong number of args')

    if not os.path.exists(args[0]):
        usage(msg='config file %s does not exist' % args[0])

    traffic_yaml = yaml.load(open(args[0]))
    generate_traffic(traffic_yaml)

if __name__ == '__main__':
    main(sys.argv[1:])
