"""
Usage:
    traffic.py <traffic.yaml>

replays read/write traffic against a backend specified
by the traffic.yaml file (see traffic.yaml.md)

we currently don't care about experiments (just variations)
"""

import sys
import random
import api
import time
import opentsdb
import threading
import yaml
import os
import signal

# CONSTANTS
# at some point we probably want to transition
# all of these into traffic.yaml
VARIATIONS_PER_EXPERIMENT = 10

def usage(msg=None):
    if msg is not None:
        print msg
        print

    print >>sys.stderr, __doc__
    sys.exit(1)

class TrafficController(object):
    def __init__(self, rps, wps, writes_percent_unique, api, monitor):
        self.rps = rps
        self.wps = wps
        self.writes_percent_unique = writes_percent_unique
        self.variations = range(VARIATIONS_PER_EXPERIMENT)
        self.users = set(range(1000)) # just seed with some users
        self.api = api
        self.running = True

        @monitor('write')
        def write():
            variation = random.choice(self.variations)
            new_user = random.random() < self.writes_percent_unique

            if new_user:
                user = random.randint(0, 10 ** 10)
                self.users.add(user)
            else:
                user = random.choice(users)

            self.api.log(variation, user)
        self.write = write

        @monitor('read')
        def read():
            variation = random.choice(self.variations)
            self.api.results(variation)
        self.read = read

        # register handler so the thread doesn't keep going forever
        def stop_handler(signum, frame):
            self.stop()
        signal.signal(signal.SIGINT, stop_handler)

    def loop(self, target_func, target_frequency):
        def looped_f():
            if target_frequency == 0:
                return

            target_period = 1. / target_frequency
            last = 0
            while self.running:
                now = time.time()
                since_last = now - last
                if since_last > target_period:
                    last = now
                    target_func()
                else:
                    time.sleep(target_period - since_last)
        return looped_f

    def start(self):
        def run():
            read_loop = self.loop(self.read, self.rps)
            write_loop = self.loop(self.write, self.wps)

            read_thread = threading.Thread(target=read_loop)
            write_thread = threading.Thread(target=write_loop)

            read_thread.start()
            write_thread.start()

            read_thread.join()
            write_thread.join()

        self.thread = threading.Thread(target=run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()

def generate_traffic(config, backend_api=None, monitor=None):
    try:
        host = config['host']
        port = int(config['port'])
        rps = int(config['reads_per_second'])
        wps = int(config['writes_per_second'])
        writes_percent_unique = int(config['writes_percent_unique'])
    except Exception as e:
        usage(msg='Malformed traffic config: %s' % e)

    backend_api = backend_api or api.VerifiedBackend(host, port)
    monitor = monitor or opentsdb.ConsoleMonitor
    traffic = TrafficController(rps, wps, writes_percent_unique, backend_api, monitor)
    traffic.start()
    return traffic

def main(args):
    if len(args) != 1:
        usage(msg='wrong number of args')

    if not os.path.exists(args[0]):
        usage(msg='config file %s does not exist' % args[0])

    traffic_yaml = yaml.load(open(args[0]))
    generate_traffic(traffic_yaml)

if __name__ == '__main__':
    main(sys.argv[1:])
