# ansible-role-sacct_gpu
Add gpu utilization stats to Slurm batch scheduler accounting db. Tested with CentOS-7.

## Background

This is intended to be used with [Slurm](https://slurm.schedmd.com/) to provide insight on job-gpu utilization. This adds short json-formatted string to 
sacct-database comment field containing stats for:

- Number of used gpu's
- Job average gpu utilization reported by nvidia-smi. For a multi-GPU
  job this is the sum of the utilization of all GPU's divided by the
  number of GPU's. So 100 % would mean all GPU's are fully used.
- Job max gpu memory utilization reported by nvidia-smi. For a
  multi-GPU job this is the maximum memory used by any single GPU, not
  the sum.
- Job gpu power usage (W). Average over time. For a multi-GPU job this 
  is the sum of power usage for all used GPUs

## How it works

Basic idea is to run small code in the background that writes the stats every 1min. In Slurm's TaskEpilog (this is still when the db access for writing jobinfo is open) 
this information is collected per jobid and written to Comment-field of jobinfo in Slurm-Accounting-Database. 

## Deployment

Simply apply this ansible-role to your nodes. We are using this together with [OpenHPC](https://openhpc.community/) and use this directly with OHPC-images.
