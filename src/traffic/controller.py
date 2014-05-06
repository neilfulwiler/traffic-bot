import random
import time
import threading
import signal

from utils import loop_at_target_frequency

# CONSTANTS
# at some point we probably want to transition
# all of these into traffic.yaml
VARIATIONS_PER_EXPERIMENT = 10

class TrafficController(object):
    def __init__(self,
            rps=10, # reads per second
            wps=100, # writes per second
            writes_percent_unique=.1,
            api=None,
            monitor=None):

        assert api is not None
        assert monitor is not None

        self.variations = range(VARIATIONS_PER_EXPERIMENT)
        self.users = set(range(1000)) # just seed with some users
        self.api = api
        self.running = True

        @loop_at_target_frequency(self, wps)
        @monitor('write')
        def write():
            variation = random.choice(self.variations)
            new_user = random.random() < writes_percent_unique

            if new_user:
                user = random.randint(0, 10 ** 10)
                self.users.add(user)
            else:
                user = random.choice(list(self.users))

            self.api.log(variation, user)
        self.write = write

        @loop_at_target_frequency(self, rps)
        @monitor('read')
        def read():
            variation = random.choice(self.variations)
            self.api.results(variation)
        self.read = read

    def start(self):
        def run():
            read_thread = threading.Thread(target=self.read)
            write_thread = threading.Thread(target=self.write)

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
