import time

SLEEP_PENALTY = .0001 # penalty in second for sleeping / context switching, etc.

class loop_at_target_frequency(object):
    """
    a decorator for executing a function in a loop at
    a specified frequency

    params:
        service     the thing that needs to be running
                    for this loop to be executing. The loop
                    will continue to execute until <service>.running
                    is False-ish

        target_frequency    the target frequency at which the
                            function should be executed
    """
    def __init__(self, service, target_frequency):
        self.service = service
        self.target_frequency = target_frequency

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            if self.target_frequency == 0:
                return

            target_period = 1. / self.target_frequency
            last = 0
            while self.service.running:
                now = time.time()
                since_last = now - last
                if since_last > target_period:
                    last = now
                    f()
                else:
                    sleep_for = target_period - since_last - SLEEP_PENALTY
                    if sleep_for > 0:
                        time.sleep(sleep_for)
        return wrapped_f

