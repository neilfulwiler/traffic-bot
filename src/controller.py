import random
import time
import threading
import signal

from utils import loop_at_target_frequency

# CONSTANTS
# at some point we probably want to transition
# all of these into traffic.yaml
VARIATIONS_PER_EXPERIMENT = 10
WRITES_PERCENT_UNIQUE = .1

class TrafficController(object):
    def __init__(self, monitor):
        self.users = set(range(1000)) # just seed with some users
        self.running = True
        self.monitor = monitor

        # these will be defaulted
        self.wps = self.rps = 0

        # this needs to be set before start()
        self.backend = None

    def get_wps(self):
        return self.wps

    def get_rps(self):
        return self.rps

    def get_backend(self):
        return self.backend

    def set_wps(self, wps):
        self.wps = wps

    def set_rps(self, rps):
        self.rps = rps

    def set_backend(self, backend):
        self.backend = backend


    def start(self):
        if self.backend is None: raise Exception('Please call set_backend first')

        variations = range(VARIATIONS_PER_EXPERIMENT)

        @loop_at_target_frequency(self, self.get_wps)
        @self.monitor('write')
        def write():
            variation = random.choice(variations)
            new_user = random.random() < WRITES_PERCENT_UNIQUE

            if new_user:
                user = random.randint(0, 10 ** 10)
                self.users.add(user)
            else:
                user = random.choice(list(self.users))

            try:
                self.backend.log(variation, user)
            except Exception as e:
                print '[ERROR]' * 3, 'caught exception trying to write: %s' % e, '[ERROR]' * 3

        @loop_at_target_frequency(self, self.get_rps)
        @self.monitor('read')
        def read():
            variation = random.choice(variations)
            try:
                self.backend.results(variation)
            except Exception as e:
                print '[ERROR]' * 3, 'caught exception trying to read: %s' % e, '[ERROR]' * 3

        def run():
            read_thread = threading.Thread(target=read)
            write_thread = threading.Thread(target=write)

            read_thread.start()
            write_thread.start()

            read_thread.join()
            write_thread.join()

        self.thread = threading.Thread(target=run)
        self.thread.start()
        return self.thread

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
