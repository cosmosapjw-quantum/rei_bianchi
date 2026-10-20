"""Verify four downloaded v8 archives; does not run science, build, upload or Git."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import tomllib
import zipfile

sys.dont_write_bytecode=True
TASK=Path('/workspace/scratch/36ed695112a9/rei_bianchi/research/rei_age_exposure_envelope_20261018')
spec=importlib.util.spec_from_file_location('shipping_v8',TASK/'observable_certificates_20261020/ship_v8.py')
shipping=importlib.util.module_from_spec(spec);spec.loader.exec_module(shipping)
core=shipping.core


def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def same_bytes(a,b):
    with a.open('rb') as first,b.open('rb') as second:
        while True:
            x=first.read(1024*1024);y=second.read(1024*1024)
            if x!=y:return False
            if not x:return True


def verify_one(provider,kind,path,plan,pack,plan_path):
    start=time.monotonic();expected=next(x for x in pack['archives'] if x['kind']==kind)
    local=Path(expected['path']);source={r['path']:r for r in plan['files']}
    assert path.resolve()!=local.resolve()
    assert path.stat().st_size==expected['bytes'] and digest(path)==expected['sha256']
    assert digest(local)==expected['sha256'] and same_bytes(path,local)
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist();assert len(names)==len(set(names))==expected['zip_entries']
        assert archive.testzip() is None
        manifest=json.loads(archive.read('PAYLOAD_SHA256.json'))
        assert manifest['source_commit']==pack['source_commit'] and manifest['task_git_tree']==plan['source_task_tree']
        assert set(names)==set(manifest['files'])|{'PAYLOAD_SHA256.json'}
        for name,identity in manifest['files'].items():
            data=archive.read(name);assert len(data)==identity['size'] and core.sha(data)==identity['sha256']
        receipt=json.loads(archive.read('PACKAGE_RECEIPT.json'))
        assert receipt['schema']=='rei.delivery.package.v8' and receipt['kind']==kind
        assert receipt['source_commit']==pack['source_commit'] and receipt['source_parent']==core.BASELINE_COMMIT
        assert receipt['task_git_tree']==plan['source_task_tree'] and receipt['frozen_source_plan_sha256']==digest(plan_path)
        assert receipt['PRODUCTION_SCIENTIFIC_ADMISSION']=='NOT_ISSUED'
        included={n for n in names if n.startswith(core.TASK_PREFIX)}
        if kind=='C10':expected_source=set(source)
        else:
            with zipfile.ZipFile(plan['prior_c8']) as prior:prior_code={p for p in prior.namelist() if p.startswith(core.TASK_PREFIX)}
            expected_source={p for p in source if p in prior_code or
                (source[p]['changed'] and not p.startswith(shipping.NEW_PREFIX)) or
                (p.startswith(shipping.NEW_PREFIX) and not p[len(shipping.NEW_PREFIX):].startswith('results/'))}
        assert included==expected_source
        assert len(included)==expected['included_source_files']==receipt['included_source_files']
        tree=[]
        for name in sorted(included):
            data=archive.read(name);record=source[name];mode=format(archive.getinfo(name).external_attr>>16,'o')
            assert len(data)==record['bytes'] and core.sha(data)==record['sha256']
            assert core.blob_sha(data)==record['blob_sha'] and mode==record['mode']
            tree.append({'path':name,'mode':mode,'blob_sha':core.blob_sha(data)})
        native_result=None
        extras={n for n in names if n.startswith('archive_only/')}
        assert len(extras)==expected['archive_only_files']==receipt['archive_only_files']
        if kind=='C10':
            assert core.tree_sha(tree)==plan['source_task_tree']
            with zipfile.ZipFile(plan['prior_c10']) as prior:
                assert extras=={n for n in prior.namelist() if n.startswith('archive_only/')}
                for name in extras-{'archive_only/RESTORATION_LAYOUT.md'}:assert archive.read(name)==prior.read(name)
            native=json.loads(archive.read(core.TASK_PREFIX+'contracts/NATIVE_INPUTS.json'))
            assert native['native_sha']==core.NATIVE and len(native['files'])==153
            for name,identity in native['files'].items():
                data=archive.read('archive_only/runtime_base/native_original_35d9747/'+name)
                assert len(data)==identity['size'] and core.sha(data)==identity['sha256']
            binary=archive.read('archive_only/runtime_base/blockmax_B1/positive_native.bin')
            assert core.sha(binary)==core.B1_SHA
            mapping=json.loads(archive.read('archive_only/B1_RESTORATION_MAP.json'))
            assert mapping['binary_sha256']==core.B1_SHA and len(mapping['deduplicated_source_files'])==161
            for record in mapping['deduplicated_source_files']:
                assert core.sha(archive.read(record['source_archive_path']))==record['sha256']
            layout=archive.read('archive_only/RESTORATION_LAYOUT.md').decode()
            assert pack['source_commit'] in layout and str(plan['source_files'])+' task files' in layout
            native_result={'archive_only_members':156,'original_native_files':153,'B1_binary_sha256':core.B1_SHA,
                           'deduplicated_B1_source_files':161,'restoration_layout_source_binding':'PASS'}
        prefix=core.TASK_PREFIX+'vigilode_age_transport_20261019/rust/'
        lock=tomllib.loads(archive.read(prefix+'Cargo.lock').decode())
        packages=[p for p in lock['package'] if p.get('source','').startswith('registry+')];assert len(packages)==22
        files=0
        for package in packages:
            directory=prefix+'vendor/'+package['name']+'/'
            checksum=json.loads(archive.read(directory+'.cargo-checksum.json'));assert checksum['package']==package['checksum']
            for name,value in checksum['files'].items():assert core.sha(archive.read(directory+name))==value;files+=1
        assert files==865
    return {'provider':provider,'kind':kind,'download_path':str(path.resolve()),'bytes':expected['bytes'],
            'sha256':expected['sha256'],'whole_byte_comparison':'PASS','zip_crc':'PASS',
            'zip_entries':len(names),'all_manifest_sizes_sha256':'PASS','source_blob_and_mode_identity':'PASS',
            'source_commit':pack['source_commit'],'source_task_tree':plan['source_task_tree'],
            'included_source_files':len(included),'native156_and_B1':native_result,
            'locked_vendor_packages':22,'vendor_files_rehashed':865,'wall_seconds':time.monotonic()-start}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--package-receipt',type=Path,required=True)
    parser.add_argument('--source-root-tree',required=True);parser.add_argument('--output',type=Path,required=True)
    for provider in ['drive','dropbox']:
        for kind in ['c8','c10']:parser.add_argument('--'+provider+'-'+kind,type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists();args.output.parent.mkdir(parents=True,exist_ok=True)
    assert len({getattr(args,p+'_'+k).resolve() for p in ['drive','dropbox'] for k in ['c8','c10']})==4
    plan=core.load(args.plan);pack=core.load(args.package_receipt)
    assert pack['source_task_tree']==plan['source_task_tree']
    result={'schema':'rei.v8.four_provider_full_readback.v1','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'source_commit':pack['source_commit'],'repository_root_tree':args.source_root_tree,
            'source_task_tree':plan['source_task_tree'],'source_plan_sha256':digest(args.plan),
            'command':sys.argv,'downloads':[],'scientific_execution':'NOT_RUN','publication_or_upload':'NOT_RUN',
            'PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED'}
    start=time.monotonic()
    try:
        for provider in ['drive','dropbox']:
            for kind in ['C8','C10']:result['downloads'].append(verify_one(provider,kind,getattr(args,provider+'_'+kind.lower()),plan,pack,args.plan))
        result['status']='PASS_FOUR_FULL_PROVIDER_READBACKS'
    except Exception as exc:
        result['status']='FAIL';result['error']=type(exc).__name__+': '+str(exc);raise
    finally:
        result['wall_seconds']=time.monotonic()-start;args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'downloads':len(result['downloads']),'receipt':str(args.output),'sha256':digest(args.output)}))


if __name__=='__main__':main()
