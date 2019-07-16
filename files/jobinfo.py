#!/usr/bin/python
#
# This script loads the gpu stats json and prints the output
#

import sys
import json

def getstats(fname):
    with open(fname) as stats_file:
        return json.load(stats_file)

if __name__ == '__main__':
    gpu_stats = getstats(sys.argv[1])
    job_id = sys.argv[2]
    if job_id in gpu_stats:
        del gpu_stats[job_id]['step']
        print(json.dumps(gpu_stats[job_id]))
    else:
        print('No GPU stats found.')

