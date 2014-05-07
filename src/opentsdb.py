import time

REPORT_EVERY_N_SECONDS = 1

class RunningAverage(object):
    """
    bound the RunningAverage if you want a moving window
    """
    def __init__(self, bound=None):
        self.bound = bound

    i = 0.
    running_average = 0.
    def avg(self, value):
        self.running_average = ((self.i * self.running_average) + value) / (self.i + 1)
        self.i += 1

        if self.i > self.bound:
            self.i = self.bound

    def current_value(self):
        return self.running_average

# monitors should register themselves with 'metrics'
metrics = {}

class ConsoleMonitor(object):
    def __init__(self, metric_name, verbose=False):
        self.last_reported_time = 0
        self.metric_name = metric_name
        self.execution_time = RunningAverage(bound=100)
        self.call_frequency = RunningAverage(bound=100)
        self.last_executed = None
        self.verbose = verbose

        metrics[metric_name] = self

    def get_call_frequency(self):
        return self.call_frequency.current_value()

    def get_execution_time(self):
        return self.execution_time.current_value()

    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            if self.last_executed is not None:
                frequency = 1. / (time.time() - self.last_executed)
                self.call_frequency.avg(frequency)
            self.last_executed = time.time()

            start = time.time()
            f(*args, **kwargs)
            end = time.time()
            self.execution_time.avg(end - start)

            if time.time() - self.last_reported_time > REPORT_EVERY_N_SECONDS:
                self.report()

        return wrapped_f

    def report(self):
        if self.verbose:
            self.last_reported_time = time.time()
            print 'metric %s frequency %.3f execution_time %.3f' % \
                (self.metric_name,
                        self.get_call_frequency(),
                        self.get_execution_time())
