if nvidia-smi -L|grep -q GPU; then
  /usr/bin/scontrol update jobid=${SLURM_JOB_ID} comment="$(/usr/local/bin/jobinfo.py /run/gpustats.json ${SLURM_JOB_ID})"
fi

