if nvidia-smi -L|grep -q GPU; then
  if [ -z "${SLURM_ARRAY_TASK_ID}" ]; then
    jobid=$SLURM_JOBID
  else
    jobid=${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}
  fi
  /usr/bin/scontrol update jobid=$jobid comment="`/usr/local/bin/jobinfo.py /run/gpustats.json $jobid`"
fi

