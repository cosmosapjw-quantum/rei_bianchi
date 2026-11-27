"""Host-only 1/2/4-rank synthetic acceptance through the topology-aware launcher."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent


def stage(argv,root,label):
    # host_plan/launcher owns the job deadline, descendant cleanup and resource guards.
    with (root/(label+'.stdout')).open('xb') as out,(root/(label+'.stderr')).open('xb') as err:
        p=subprocess.run(argv,stdout=out,stderr=err,shell=False)
    if p.returncode:raise ValueError('stage refused/failed: '+label)
    return p.returncode


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mpi-binary',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    p.add_argument('--reserve-gib',type=int,default=16)
    p.add_argument('--worker-mib',type=int,default=1024)
    p.add_argument('--wall-seconds',type=int,default=120)
    p.add_argument('--cpu-units',type=int,default=50000)
    a=p.parse_args();root=a.output_dir
    if not root.is_absolute() or root.exists() or not root.parent.is_dir():p.error('absolute new output directory required')
    if not a.mpi_binary.is_absolute() or not a.mpi_binary.is_file():p.error('built absolute MPI executable required')
    root.mkdir(mode=0o700)
    result={'schema':'WU088_MPI_HOST_SYNTHETIC_SMOKE_V1','status':'INCOMPLETE','rank_runs':[],
            'actual_HH_runs':0,'production_admitted':False,'rigorous':False,'certified_epsilon':None,'certified_eta':None}
    try:
        for ranks in (1,2,4):
            tag='ranks_'+str(ranks);manifest=root/(tag+'.json');worklist=root/(tag+'.worklist')
            stage([sys.executable,str(ROOT/'executor/make_fixture.py'),'--output-manifest',str(manifest),
                   '--output-root',str(root/(tag+'_tasks')),'--task-count','12','--cpu-units',str(a.cpu_units)],root,tag+'_fixture')
            stage([sys.executable,str(HERE/'export_worklist.py'),'--manifest',str(manifest),'--output',str(worklist)],root,tag+'_worklist')
            launch=[sys.executable,str(ROOT/'host_plan/launcher.py'),'--manifest',str(manifest),
                    '--mpi-binary',str(a.mpi_binary),'--worklist',str(worklist),'--output',str(root/(tag+'_host')),
                    '--ranks',str(ranks),'--reserve-gib',str(a.reserve_gib),'--worker-mib',str(a.worker_mib),
                    '--wall-seconds',str(a.wall_seconds),'--execute-synthetic']
            stage(launch,root,tag+'_launch')
            host=json.loads((root/(tag+'_host/HOST_RUN.json')).read_text())
            if host['status']!='EXECUTION_COMPLETE':raise ValueError('host execution incomplete: '+tag)
            collected=host['collector']
            if collected['status']!='COLLECTED' or collected['complete_task_count']!=12:raise ValueError('incomplete collection')
            result['rank_runs'].append({'ranks':ranks,'canonical_payload_digest':collected['canonical_payload_digest'],
                'tasks':12,'host_run_sha256':hashlib.sha256((root/(tag+'_host/HOST_RUN.json')).read_bytes()).hexdigest(),
                'wall_seconds':host['wall_seconds']})
        if len({x['canonical_payload_digest'] for x in result['rank_runs']})!=1:raise ValueError('payload identities differ across ranks')
        result['status']='PASS_SYNTHETIC_MPI_1_2_4_RANKS'
    except (OSError,ValueError,KeyError,TypeError) as exc:
        result['status']='INCONCLUSIVE';result['reason']=str(exc)
    (root/'SMOKE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    return 0 if result['status']=='PASS_SYNTHETIC_MPI_1_2_4_RANKS' else 2


if __name__=='__main__':raise SystemExit(main())
