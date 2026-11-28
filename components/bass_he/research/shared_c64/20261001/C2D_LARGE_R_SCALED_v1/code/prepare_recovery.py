"""Create a partial index and bounded recovery plan, or verify its result."""
import argparse
from pathlib import Path
from mpi_batch import atomic_create,json_bytes
from recovery_support import (derive_partial_index,make_recovery_plan,
                              finalize_plan_source,verify_recovered,read,safe)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--batch',default='evidence/FOLLOWUP_MPI')
    parser.add_argument('--recovery-batch',default='evidence/RECOVERY_MPI')
    parser.add_argument('--manifest',default='inputs/RECOVERY_TASKS.json')
    parser.add_argument('--plan',default='review/RECOVERY_PLAN.json')
    parser.add_argument('--snapshot',default='provenance/FOLLOWUP_CODE_SNAPSHOT.zip')
    parser.add_argument('--cleanup-margin',type=int,default=30)
    parser.add_argument('--classification',help='Explicit immutable timeout-kill classification evidence, if needed')
    parser.add_argument('--verify',action='store_true')
    parser.add_argument('--verification-output',default='review/RECOVERY_VERIFICATION.json')
    args=parser.parse_args();root=args.root.resolve()
    if args.verify:
        result=verify_recovered(root,args.plan)
        atomic_create(safe(root,args.verification_output,exists=False),json_bytes(result))
        print(result['status']);return
    # Preserve partial evidence even when subsequent plan admission fails.
    index=derive_partial_index(root,args.batch)
    index_path=root/args.batch/'PARTIAL_BATCH_INDEX.json'
    if index_path.exists():
        if read(index_path)!=index:raise ValueError('EXISTING_PARTIAL_INDEX_CHANGED')
    else:
        atomic_create(index_path,json_bytes(index))
    index,manifest,plan=make_recovery_plan(root,args.batch,args.manifest,args.recovery_batch,
                                          args.snapshot,args.cleanup_margin,args.classification)
    atomic_create(root/args.manifest,json_bytes(manifest))
    plan=finalize_plan_source(root,plan)
    atomic_create(safe(root,args.plan,exists=False),json_bytes(plan))
    print(json_bytes({'status':plan['status'],'task_count':len(manifest['tasks']),
                      'wall_cap_seconds':plan['wall_budget']['recovery_wall_cap_seconds'],
                      'completed_replays':0,'new_eigenstates':0}).decode(),end='')


if __name__=='__main__':main()
