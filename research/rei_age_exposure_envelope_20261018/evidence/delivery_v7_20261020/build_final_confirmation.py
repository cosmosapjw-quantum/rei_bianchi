"""Encode a task-owned UTF-8 post-publication restore delta; never publish."""
import argparse
import datetime
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode=True
TASK=Path('/workspace/scratch/36ed695112a9/rei_bianchi/research/rei_age_exposure_envelope_20261018')
spec=importlib.util.spec_from_file_location('shipping_v7',TASK/'optimization_20261020/ship_v7.py')
ship=importlib.util.module_from_spec(spec);spec.loader.exec_module(ship);core=ship.core


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plan',type=Path,required=True)
    p.add_argument('--paths',type=Path,required=True,help='JSON list of exact repo-relative changed metadata paths')
    p.add_argument('--source-commit',required=True);p.add_argument('--delivery-head',required=True)
    p.add_argument('--package-receipt',type=Path,required=True);p.add_argument('--readback-receipt',type=Path,required=True)
    p.add_argument('--upload-receipt',type=Path);p.add_argument('--source-publication-receipt',type=Path)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    assert not args.output.exists();plan=core.load(args.plan);rows={r['path']:dict(r) for r in plan['files']}
    paths=core.load(args.paths);assert len(paths)==len(set(paths));delta=[]
    for path in paths:
        core.safe_owned(path);data=(core.REPO/path).read_bytes();text=data.decode('utf-8')
        row={'path':path,'mode':rows.get(path,{}).get('mode','100644'),'type':'blob','encoding':'utf-8',
             'bytes':len(data),'sha256':core.sha(data),'blob_sha':core.blob_sha(data),'content':text}
        delta.append(row);rows[path]=row
    result={'schema':'rei.age.delivery.confirmation.v7','finalized_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_snapshot':{'commit':args.source_commit,'task_tree':plan['source_task_tree'],'source_files':plan['source_files']},
            'delivery_head':args.delivery_head,'archives':core.load(args.package_receipt),
            'full_provider_readback':core.load(args.readback_receipt),
            'restore_delta':{'schema':'rei.task_owned_utf8_restore_delta.v1','required_base_source_commit':args.source_commit,
                'required_base_task_tree':plan['source_task_tree'],'allowed_repo_relative_prefix':core.TASK_PREFIX,
                'allowed_paths_exact':paths,'file_count':len(delta),'encoding_semantics':'Encode exact UTF-8 strings without normalization.',
                'files':delta,'expected_result_task_tree':core.tree_sha(list(rows.values())),'confirmation_self_included':False},
            'scientific_execution':'NOT_RUN_BY_CONFIRMATION','PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED'}
    assert result['full_provider_readback']['status']=='PASS_FOUR_FULL_PROVIDER_READBACKS'
    if args.upload_receipt:result['provider_uploads']=core.load(args.upload_receipt)
    if args.source_publication_receipt:result['source_publication']=core.load(args.source_publication_receipt)
    args.output.write_bytes(core.encoded(result));print(json.dumps({'path':str(args.output),'bytes':args.output.stat().st_size,
        'sha256':core.sha(args.output.read_bytes()),'restore_delta_files':len(delta),'final_task_tree':result['restore_delta']['expected_result_task_tree']}))


if __name__=='__main__':main()
