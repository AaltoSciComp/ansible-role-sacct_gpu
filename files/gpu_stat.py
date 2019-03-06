#!/usr/bin/python

# author mhakala
import json
import re
import subprocess
import tempfile
import os

# find slurm-job-ids active on this node
def jobs_running():
   task = subprocess.Popen('ps -ef|grep "/var/spool/slurmd/"|grep job|sed s/.*job//|cut -d"/" -f1', shell=True, stdout=subprocess.PIPE)
   data = task.stdout.read()
   assert task.wait() == 0
   jobs = []

   for row in data.split('\n'):
      if len(row) > 1:
          jobs.append(row)

   return jobs

# convert pid to slurm jobid
def pid2id(pid):
   output = subprocess.check_output("cat /proc/%s/cgroup |grep cpuset" % pid, shell=True)
   m = re.search('.*job_(\d+)\/.*', output)
   if m:
      return m.group(1)
   else:
      return '0'

# get needed slurm values for each running job on the node
def job_info(jobs,current):
   for job in jobs:
      output = subprocess.check_output("scontrol -o show job %s" % job, shell=True)
      cpus   = re.search('.*NumCPUs=(\d+)\s',output)
      gres   = re.search('.*Gres=.*:(\d+)\s',output)
      nodes  = re.search('.*NumNodes=(\d+)\s',output)

      # drop multi-node jobs (will be added later if needed)
      if int(nodes.group(1)) > 1:
         del current[job]
      else:
         current[job]['ngpu']=int(gres.group(1))
         current[job]['ncpu']=int(cpus.group(1))

   return current


def gpu_info(jobinfo):
   import xml.etree.cElementTree as ET

   output = subprocess.check_output(['nvidia-smi', '-q', '-x'])
   root = ET.fromstring(output)

   for gpu in root.findall('gpu'):
      procs = gpu.find('processes')
      mtot = 0.
      # Here we assume that multiple job id's cannot access the same
      # GPU
      for pi in procs.findall('process_info'):
         pid = pi.find('pid').text
         jobid = pid2id(pid)
         # Assume used_memory is of the form '1750 MiB'. Needs fixing
         # if the unit is anything but MiB.
         mtot += float(pi.find('used_memory').text.split()[0])
      util = gpu.find('utilization')
      # Here assume gpu utilization is of the form
      # '100 %'
      gutil = float(util.find('gpu_util').text.split()[0])

      # only update, if jobid not dropped (multinode jobs)
      if jobid in jobinfo.keys():
         jobinfo[jobid]['gpu_util'] += gutil/jobinfo[jobid]['ngpu']
         jobinfo[jobid]['gpu_mem_max'] = max(mtot, jobinfo[jobid]['gpu_mem_max'])

   return jobinfo

def read_shm(fil):
   import os.path
   jobinfo = {}

   if(os.path.exists(fil)):
      with open(fil) as fp:
         jobinfo=json.loads(fp.read())

   return jobinfo


def write_shm(jobinfo, fname):
   with tempfile.NamedTemporaryFile(mode='w', delete=False, \
                     dir=os.path.dirname(os.path.normpath(fname))) as fp:
      json.dump(jobinfo, fp)
   os.rename(fp.name, fname)

def main():
   import sys
   # initialize stats
   current = {}
   jobs    = jobs_running()

   for job in jobs:
      current[job]={'gpu_util': 0, 'gpu_mem_max': 0, 'ngpu': 0, 'ncpu': 0, 'step': 1}

   # get current job info
   current = job_info(jobs, current)
   current = gpu_info(current)

   if len(sys.argv) > 1:
      fname = sys.argv[1]
   else:
      fname = '/run/gpustats.json'

   # combine with previous steps
   prev = read_shm(fname)
   for job in jobs:
      if job in prev.keys():
         n = prev[job]['step']
         current[job]['gpu_util'] = ( float(prev[job]['gpu_util'])*n+float(current[job]['gpu_util']) )/(n+1)
         current[job]['gpu_mem_max']  = max(float(prev[job]['gpu_mem_max']), float(current[job]['gpu_mem_max']))
         current[job]['step'] = n+1

   # write json
   write_shm(current, fname)


if __name__ == '__main__':
    main()

