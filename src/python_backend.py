"""
Usage: python_backend.py <port>

Start a backend backed by in-memory python
"""

from bottle import route, run, template, request
from collections import defaultdict
import time
import sys
import utils
import threading
from backend import InMemoryBackend

#variations = defaultdict(set)

STATS_COLLECTION_EVERY_N_SECONDS = 10

backend = InMemoryBackend()

@route('/log/<variation>/<user>')
def log(variation, user):
    backend.log(variation, user)

@route('/results/<variation>')
def results(variation):
    return {'results' : list(backend.results(variation))}

@route('/clear')
def clear():
    global backend
    backend = InMemoryBackend()

def usage(msg=None):
    if msg is not None:
        print msg + '\n'
    print __doc__
    sys.exit(1)

def main(args):
    if len(args) != 1:
        usage('not enough arguments')

    try:
        port = int(args[0])
    except ValueError:
        usage('bad port parameter (not an int')

    class StatsService:
        running = True

    stats_service = StatsService()

    @utils.loop_at_target_frequency(stats_service, lambda: 1. / STATS_COLLECTION_EVERY_N_SECONDS)
    def collect_stats():
        print 'variation lengths: %s' % sorted([len(v) for v in backend.variations.values()])

    thread = threading.Thread(target=collect_stats)
    thread.start()

    run(host='localhost', port=port)

    stats_service.running = False
    thread.join()

if __name__ == '__main__':
    main(sys.argv[1:])
