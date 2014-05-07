"""
Usage:
    traffic.py <zookeeper>

replays read/write traffic against a backend specified
by the zookeeper configurations in <zookeeper> under /traffic

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
from kazoo.client import KazooClient

ZK_NAMESPACE = '/traffic'

def usage(msg=None):
    if msg is not None:
        print msg
        print

    print >>sys.stderr, __doc__
    sys.exit(1)

def generate_traffic(zk, backend_api=None, monitor=None):
    zk = KazooClient(hosts=zk)
    zk.start()

    backend_api = backend_api or api.backend.VerifiedBackendApi
    monitor = monitor or partial(opentsdb.ConsoleMonitor, verbose=True)

    controller = traffic.controller.TrafficController(monitor)

    import signal
    def stop_controller(signum, frame):
        controller.stop()
    signal.signal(signal.SIGINT, stop_controller)

    @zk.DataWatch(ZK_NAMESPACE + '/rps')
    def update_rps(data, stat):
        try:
            controller.set_rps(int(data))
        except Exception as e:
            print 'Error updating rps: %s' % e

    @zk.DataWatch(ZK_NAMESPACE + '/wps')
    def update_wps(data, stat):
        try:
            controller.set_wps(int(data))
        except Exception as e:
            print 'Error updating wps: %s' % e

    @zk.DataWatch(ZK_NAMESPACE + '/host')
    def update_host(data, stat):
        try:
            controller.set_api(backend_api(data))
        except Exception as e:
            print 'Error updating host: %s' % e

    controller_thread = controller.start()
    while controller_thread.isAlive():
        controller_thread.join(1)


def main(args):
    if len(args) != 1:
        usage(msg='wrong number of args')

    generate_traffic(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
