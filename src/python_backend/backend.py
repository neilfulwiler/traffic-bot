from bottle import route, run, template, request
from collections import defaultdict
import threading

variations = defaultdict(set)

@route('/log/<variation>/<user>')
def log(variation, user):
    variation[variation].add(int(user))

@route('/results/<variation>')
def results(variation):
    return variations[variation]


if __name__ == '__main__':
    run(host='localhost', port=8080)
