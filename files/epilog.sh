if nvidia-smi -L|grep -q GPU; then
  /usr/bin/scontrol update jobid=$jobid comment="$(/usr/local/bin/jobinfo.py /run/gpustats.json ${SLURM_JOB_ID})"
fi

