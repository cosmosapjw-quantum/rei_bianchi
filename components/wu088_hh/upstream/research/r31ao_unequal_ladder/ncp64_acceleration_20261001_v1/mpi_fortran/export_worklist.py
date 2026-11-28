"""Export only the integer dispatch plane from a synthetic task manifest."""
import argparse
import hashlib
import json
from pathlib import Path


def export(manifest, output):
    manifest = Path(manifest)
    if not manifest.is_absolute() or manifest.stat().st_size > 8*1024*1024:
        raise ValueError('bounded absolute manifest required')
    with manifest.open('rb') as f:
        raw = f.read(8*1024*1024+1)
    if len(raw) > 8*1024*1024:
        raise ValueError('manifest grew beyond cap')
    doc = json.loads(raw)
    if doc.get('schema') != 'WU088_NCP64_TASK_MANIFEST_V1' or doc.get('scope') != 'SYNTHETIC_ONLY':
        raise ValueError('synthetic task manifest required')
    tasks = doc['tasks']
    if type(tasks) is not list or len(tasks) > 100000:
        raise ValueError('bounded task list required')
    ids = [task['task_id'] for task in tasks]
    if any(type(x) is not str for x in ids) or len(set(ids)) != len(ids):
        raise ValueError('unique task IDs required')
    for task in tasks:
        cost = task['cost_hint']
        wall = task['limits']['wall_seconds']
        if type(cost) is not int or cost < 0:
            raise ValueError('integer nonnegative cost hint required')
        if type(wall) is not int or not 1 <= wall <= 86400:
            raise ValueError('bounded integer worker deadline required')
    expected = sorted(range(len(tasks)), key=lambda i: (-tasks[i]['cost_hint'], tasks[i]['task_id']))
    order = doc.get('dispatch_order', expected)
    if type(order) is not list or any(type(i) is not int for i in order) or order != expected:
        raise ValueError('dispatch_order must be the longest-cost-first full permutation')
    data = (str(len(tasks))+'\n'+''.join(f"{i} {tasks[i]['limits']['wall_seconds']+10}\n" for i in order)).encode('ascii')
    output = Path(output)
    if not output.is_absolute():
        raise ValueError('absolute create-only output path required')
    with output.open('xb') as f:
        f.write(data)
    return {'schema':'WU088_MPI_INTEGER_WORKLIST_V1','manifest_sha256':hashlib.sha256(raw).hexdigest(),
            'worklist_sha256':hashlib.sha256(data).hexdigest(),'tasks':len(tasks),'dispatch_order':order,
            'worklist':str(output),'scientific_payloads_read':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    try:
        print(json.dumps(export(args.manifest,args.output),sort_keys=True))
    except (OSError,ValueError,TypeError,KeyError) as exc:
        parser.exit(2,'REFUSED: '+str(exc)+'\n')


if __name__=='__main__':
    main()
