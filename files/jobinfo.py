#!/usr/bin/python

import json

def getstats(fname):
    with open(fname) as f:
        return json.load(f)

if __name__ == '__main__':
    import sys
    j = getstats(sys.argv[1])
    id = sys.argv[2]
    del j[id]['step']
    print(json.dumps(j[id]))
