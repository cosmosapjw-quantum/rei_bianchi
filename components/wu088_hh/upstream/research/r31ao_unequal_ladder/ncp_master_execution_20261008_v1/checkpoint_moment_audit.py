"""Bounded exact-rational audit of eight existing states, never a history replay.

Uses immutable donor codec/dyadic implementation and compares to independent
Fraction sums. Process parallelism changes only validation scheduling.
"""
from pathlib import Path
from fractions import Fraction
from concurrent.futures import ProcessPoolExecutor
import argparse, hashlib, importlib.util, json, resource, time, sys


def load(path, name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def work(task):
    root, state_path = map(Path,task)
    # Sealed manifest and native restore must have passed before this audit.
    sys.path.insert(0,str(root/'research'))
    codec = load(root/'research/check_extension.py','sealed_checkpoint_codec')
    exact = load(root/'research/exact_dyadic.py','sealed_dyadic')
    data=state_path.read_bytes();s=codec.decode(data)
    photons=s['photons'];nodes=codec.nodes(s['m'])
    n=exact.sum_values(photons);u=exact.sum_products((p,nodes[k%len(nodes)]) for k,p in enumerate(photons))
    sumabs=exact.sum_values(abs(p) for p in photons)
    # Independent exact rational scalar path, in canonical array order.
    refn=sum(map(Fraction,photons),Fraction(0))
    refu=sum((Fraction(p)*Fraction(nodes[k%len(nodes)]) for k,p in enumerate(photons)),Fraction(0))
    refabs=sum((abs(Fraction(p)) for p in photons),Fraction(0))
    assert n==refn and u==refu and sumabs==refabs
    assert all(s['pb'][2*k]<=p<=s['pb'][2*k+1] for k,p in enumerate(photons))
    return {'path':str(state_path),'sha256':hashlib.sha256(data).hexdigest(),'time':s['time'],
            'photon_scalars':len(photons),'directions':s['nd'],'N':str(n),'U_ev_per_H':str(u),
            'sumabs':str(sumabs),'canonical_exact_parity':True,'point_in_box':True}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--final',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    tasks=[(str(a.root),str(folder/f'member{i}.bin')) for folder in [a.root/'seed',a.final] for i in range(4)]
    configurations=[];baseline=None
    for workers in [1,2]:
        walls=[]
        for rep in range(3):
            start=time.monotonic()
            if workers==1:result=list(map(work,tasks))
            else:
                with ProcessPoolExecutor(max_workers=workers) as pool:result=list(pool.map(work,tasks))
            walls.append(time.monotonic()-start)
            if baseline is None:baseline=result
            assert result==baseline
        configurations.append({'workers':workers,'repetitions':3,'wall_seconds':walls})
    output={'scope':'eight stored seed/final checkpoint arrays only','results':baseline,'configurations':configurations,
            'scalar_entries_per_configuration':sum(x['photon_scalars'] for x in baseline),
            'four_assertions_per_state':32,'root_calls':0,'new_cells':0,'new_macros':0,
            'main_max_rss_kb':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'child_max_rss_kb':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            'selected_scientific_kernel_configuration':None,
            'science_host_speedup_certified':False,'precision':'exact rational interpretation of archived binary64 values; no solver precision change'}
    with a.output.open('x') as f:json.dump(output,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in output.items() if k!='results'}))
if __name__=='__main__':main()
