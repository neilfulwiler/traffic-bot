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
from functools import partial
from kazoo.client import KazooClient

from controller import TrafficController
import backend
import opentsdb
import utils

ZK_NAMESPACE = '/traffic'

def usage(msg=None):
    if msg is not None:
        print msg
        print

    print >>sys.stderr, __doc__
    sys.exit(1)

def generate_traffic(zk):
    """
    generates traffic against the host as specified
    by the zookeeper quorum this is pointed to.

    the current important znodes are

        /traffic/rps
        /traffic/wps
        /traffic/host
        /traffic/verify # attempts to verify the results

    when these hosts are updated the corresponding
    functionality is similarly updated
    """
    zk = KazooClient(hosts=zk)
    zk.start()

    monitor = partial(opentsdb.ConsoleMonitor, verbose=True)
    controller = TrafficController(monitor)

    # stop the controller on interrupt
    import signal
    def stop_controller(signum, frame):
        controller.stop()
    signal.signal(signal.SIGINT, stop_controller)

    #
    # these watchers are all called immediately and then
    # whenever the node is changed. We're assuming
    # all events are going to be changes (not deletions, etc).
    # But we still want to be nice and stay alive in case
    # a configuration is poorly set
    #

    @zk.DataWatch(ZK_NAMESPACE + '/rps')
    @utils.safe('updating rps') # just catches exceptions
    def update_rps(data, stat, event):
        controller.set_rps(int(data))

    @zk.DataWatch(ZK_NAMESPACE + '/wps')
    @utils.safe('updating wps') # just catches exceptions
    def update_wps(data, stat, event):
        controller.set_wps(int(data))

    @zk.DataWatch(ZK_NAMESPACE + '/host')
    @utils.safe('updating host') # just catches exceptions
    def update_host(data, stat, event):
        host = data
        remote = backend.RemoteBackend(host)
        controller.set_backend(backend.VerifiedBackend(remote))

    @zk.DataWatch(ZK_NAMESPACE + '/verify')
    @utils.safe('setting verification') # just catches exceptions
    def update_verify(data, stat, event):
        host = data
        controller.get_backend().set_verified(bool(data))

    # the join was to be called in a loop otherwise
    # the main thread blocks and signals don't get through
    controller_thread = controller.start()
    while controller_thread.isAlive():
        controller_thread.join(1)


def main(args):
    if len(args) != 1:
        usage(msg='wrong number of args')

    generate_traffic(args[0])

if __name__ == '__main__':
    main(sys.argv[1:])
else:
    raise Exception('please dont tell me you put general' +
            ' functionality in the main module')
