#!/usr/bin/env bash
cd /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/source_tree/research/rei_age_exposure_envelope_20261018
export PATH=/root/REI_AGE_ENVELOPE_20261018T132700Z/venv/bin:/root/.cargo/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export REI_TRANSPORT_THREADS=48
export REI_REPO=/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/repo NEW_SCRATCH=/root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/run
date -u +%FT%T.%NZ > /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/START_UTC
/usr/bin/time -v -o /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/TIME_V.txt bash scripts/run_accuracy_followup.sh "$REI_REPO" "$NEW_SCRATCH" age64-block-max > /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/followup_stdout.log 2> /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/followup_stderr.log
echo $? > /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/EXIT_CODE
date -u +%FT%T.%NZ > /root/REI_AGE_BLOCKMAX_AGE64_20261019T084150Z/END_UTC
