#!/usr/bin/env bash
# Optional: only for an NCP installation that already provides Slurm.
#SBATCH --job-name=rei-cell-hpc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=120G
#SBATCH --time=12:30:00
#SBATCH --signal=B:TERM@300
#SBATCH --output=rei-hpc-%j.log
set -euo pipefail
: "${REI_REPO:?Set REI_REPO to the public checkout with the private seed restored}"
: "${REI_TRANSITION:?Set REI_TRANSITION to the prepared private HPC transition JSON}"
cd -- "${REI_REPO}"
exec bash research/accel02_20261011/q1b/hpc/run_ncp.sh \
    --transition-bundle "${REI_TRANSITION}" --new-attempt-cap 10000 --wall-s 43200
