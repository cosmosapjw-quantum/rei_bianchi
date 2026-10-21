"""Prepare source deltas and source-bound v7 ZIPs; performs no publication.

Reuse the immutable v6 helper's path checks, Git identities, JSON serialization,
tree reconstruction, large-blob splitting and Git-API request batching.
"""
from pathlib import Path
import argparse
import base64
import importlib.util
import json
import zipfile

HERE=Path(__file__).resolve().parent
TASK=HERE.parent
spec=importlib.util.spec_from_file_location('rei_v6_shipping',TASK/'vigilode_age_transport_20261019/ship_artifacts.py')
core=importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)
core.BASELINE_COMMIT='58dc257d1402daa3d0f64786279e13cd72bfb0c7'
core.BASELINE_ROOT='32bb85c8dc79b45b308602cbfe9de8e94e0cae5b'
core.BASELINE_TASK='1360944eb7e94743c1d5a668e7458f5b4f902d7a'
core.PRIOR_C8_SHA='a2a634f819deb9cc047466274fc655985f9c09a54abc350d7259e402368f24e4'
core.PRIOR_C10_SHA='40910062112b341b10c16e632f821b8e1dac5210299b15c585b39f1cc3b29559'
PREFIX=core.TASK_PREFIX
NEW_PREFIX=PREFIX+HERE.name+'/'
EXISTING_OWNED={PREFIX+p for p in ['README_CURRENT_KO.md','HANDOFF_CODEX_CURRENT_KO.md',
    'HANDOFF_NEW_CHAT_KO.md','contracts/NEXT_DAG_CURRENT.json','DELIVERY_RECEIPT_CURRENT.json',
    'vigilode_age_transport_20261019/rust/src/main.rs','vigilode_age_transport_20261019/rust/src/certified.rs',
    'vigilode_age_transport_20261019/rust/Cargo.toml','vigilode_age_transport_20261019/README.md']}
NEW_REPORT=PREFIX+'RESEARCH_UPDATE_20261020_OPTIMIZATION_KO.md'


def plan(args):
    tree=core.load(args.baseline_tree)
    assert tree['sha']==core.BASELINE_TASK and not tree.get('truncated')
    before={PREFIX+r['path']:r for r in tree['tree'] if r['type']=='blob'}
    assert len(before)==1852
    owned=set(EXISTING_OWNED)|{NEW_REPORT}
    for p in HERE.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc':
            owned.add(core.safe_owned(p.relative_to(core.REPO).as_posix()))
    records=[]
    for path in sorted(set(before)|{p for p in owned if (core.REPO/p).is_file()}):
        core.safe_owned(path)
        local=core.REPO/path
        assert local.is_file(),'Missing baseline source: '+path
        data=local.read_bytes();prior=before.get(path);digest=core.blob_sha(data)
        changed=prior is None or digest!=prior['sha']
        assert not changed or path in owned,'Unowned baseline change: '+path
        try:data.decode('utf-8');encoding='utf-8'
        except UnicodeDecodeError:encoding='base64'
        records.append({'path':path,'mode':prior['mode'] if prior else '100644','bytes':len(data),
            'sha256':core.sha(data),'blob_sha':digest,'origin':'local','encoding':encoding,
            'changed':changed,'owned':path in owned})
    assert core.sha(args.prior_c8.read_bytes())==core.PRIOR_C8_SHA
    assert core.sha(args.prior_c10.read_bytes())==core.PRIOR_C10_SHA
    baseline_rows=[dict(path=path,mode=r['mode'],blob_sha=r['sha']) for path,r in before.items()]
    assert core.tree_sha(baseline_rows)==core.BASELINE_TASK
    changed=[r for r in records if r['changed']]
    output=core.external_output(args.out)
    frozen={'schema':'rei.v7.shipping_plan.v1','baseline_commit':core.BASELINE_COMMIT,
        'baseline_root_tree':core.BASELINE_ROOT,'baseline_task_tree':core.BASELINE_TASK,
        'source_task_tree':core.tree_sha(records),'source_files':len(records),'files':records,
        'changed_files':len(changed),'changed_bytes':sum(r['bytes'] for r in changed),
        'unchanged_baseline_files':sum(not r['changed'] for r in records if r['path'] in before),
        'prior_c8':str(args.prior_c8.resolve()),'prior_c8_sha256':core.PRIOR_C8_SHA,
        'prior_c10':str(args.prior_c10.resolve()),'prior_c10_sha256':core.PRIOR_C10_SHA,
        'scientific_execution':'NOT_RUN_BY_SERIALIZATION','publication':'NOT_RUN'}
    core.write_json(output/'SOURCE_PLAN.json',frozen)
    delta={'schema':'rei.v7.changed_source_base64.v1','baseline_commit':core.BASELINE_COMMIT,
           'expected_task_tree':frozen['source_task_tree'],
           'files':[dict(r,content_base64=base64.b64encode((core.REPO/r['path']).read_bytes()).decode()) for r in changed]}
    core.write_json(output/'CHANGED_SOURCE_BASE64.json',delta)
    print(json.dumps({k:frozen[k] for k in ['source_files','changed_files','changed_bytes','source_task_tree','unchanged_baseline_files']}))


def payload(args):
    core.make_payload(args)


def package(args):
    frozen=core.load(args.plan)
    assert args.published_task_tree==frozen['source_task_tree']
    assert len(args.source_commit)==40 and all(c in '0123456789abcdef' for c in args.source_commit)
    output=core.external_output(args.out);source={r['path']:r for r in frozen['files']};receipts=[]
    with zipfile.ZipFile(frozen['prior_c8']) as old_code,zipfile.ZipFile(frozen['prior_c10']) as prior:
        assert core.sha(Path(frozen['prior_c8']).read_bytes())==core.PRIOR_C8_SHA
        assert core.sha(Path(frozen['prior_c10']).read_bytes())==core.PRIOR_C10_SHA
        previous_code={p for p in old_code.namelist() if p.startswith(PREFIX)}
        archive_original={p:prior.read(p) for p in prior.namelist() if p.startswith('archive_only/')}
        assert len(archive_original)==156
        native_prefix='archive_only/runtime_base/native_original_35d9747/'
        native=core.load(TASK/'contracts/NATIVE_INPUTS.json')
        assert native['native_sha']==core.NATIVE and len(native['files'])==153
        for name,identity in native['files'].items():
            data=archive_original[native_prefix+name]
            assert len(data)==identity['size'] and core.sha(data)==identity['sha256']
        assert core.sha(archive_original['archive_only/runtime_base/blockmax_B1/positive_native.bin'])==core.B1_SHA
        restoration=json.loads(archive_original['archive_only/B1_RESTORATION_MAP.json'])
        for row in restoration['deduplicated_source_files']:
            assert source[row['source_archive_path']]['sha256']==row['sha256']
        for kind in ['C8','C10']:
            selected=set(source) if kind=='C10' else {p for p in source if p in previous_code or
                (source[p]['changed'] and not p.startswith(NEW_PREFIX)) or
                (p.startswith(NEW_PREFIX) and not p[len(NEW_PREFIX):].startswith('results/'))}
            data_map={p:core.source_bytes(source[p],prior) for p in selected}
            if kind=='C10':
                data_map.update(archive_original)
                layout='archive_only/RESTORATION_LAYOUT.md'
                text=data_map[layout].decode().replace(
                    '1844 task files committed in source commit 50bc41f6b6aea05f67c03ab3ad23bb118d574622',
                    f"{len(source)} task files committed in source commit {args.source_commit}")
                data_map[layout]=text.encode()
            receipt={'schema':'rei.delivery.package.v7','kind':kind,'source_commit':args.source_commit,
                'source_parent':core.BASELINE_COMMIT,'task_git_tree':frozen['source_task_tree'],
                'source_files':len(source),'included_source_files':len(selected),
                'archive_only_files':156 if kind=='C10' else 0,'omitted_source_paths':sorted(set(source)-selected),
                'vigilode_vendor_copies_in_archive':1,'frozen_source_plan_sha256':core.sha(args.plan.read_bytes()),
                'restoration':'archive_only/RESTORATION_LAYOUT.md' if kind=='C10' else 'Use C10 for full inputs/results/native153/B1 restoration.',
                'scientific_execution':'NOT_RUN_BY_PACKAGING','remote_upload':'NOT_RUN_BY_PACKAGING',
                'final_delivery_receipt':'Later post-publication/provider receipt and confirmation are outside this immutable archive.',
                'PRODUCTION_SCIENTIFIC_ADMISSION':'NOT_ISSUED'}
            data_map['PACKAGE_RECEIPT.json']=core.encoded(receipt)
            manifest={'schema':'rei.package.payload_sha256.v2','source_commit':args.source_commit,
                'task_git_tree':frozen['source_task_tree'],'files':{p:{'size':len(data),'sha256':core.sha(data)} for p,data in sorted(data_map.items())},
                'manifest_self_hash':'EXCLUDED_NO_RECURSIVE_SELF_HASH'}
            data_map['PAYLOAD_SHA256.json']=core.encoded(manifest)
            name='REI_AGE_ENVELOPE_'+('C8_CODE' if kind=='C8' else 'EXECUTION_READY')+'_20261020_v7.zip'
            dest=output/name
            with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
                for path,data in sorted(data_map.items()):
                    info=zipfile.ZipInfo(path,date_time=(2026,10,20,0,0,0));info.create_system=3
                    mode=source[path]['mode'] if path in source else '100755' if path.endswith('positive_native.bin') else '100644'
                    info.external_attr=int(mode,8)<<16;info.compress_type=zipfile.ZIP_DEFLATED
                    archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
            with zipfile.ZipFile(dest) as archive:
                assert archive.testzip() is None
                assert set(archive.namelist())==set(data_map)
                for path,expected in manifest['files'].items():
                    data=archive.read(path);assert len(data)==expected['size'] and core.sha(data)==expected['sha256']
            receipts.append({'kind':kind,'path':str(dest),'bytes':dest.stat().st_size,
                'sha256':core.sha(dest.read_bytes()),'zip_crc':'PASS','all_payload_sha256':'PASS',
                'included_source_files':len(selected),'source_task_tree':frozen['source_task_tree'],
                'archive_only_files':156 if kind=='C10' else 0,'zip_entries':len(data_map)})
    core.write_json(output/'PACKAGE_BUILD_RECEIPT_20261020_v7.json',{'schema':'rei.C8_C10.package_build_receipt.v7',
        'source_commit':args.source_commit,'source_task_tree':frozen['source_task_tree'],'archives':receipts,
        'baseline_native_inputs_preserved':153,'B1_binary_sha256':core.B1_SHA,
        'native_runtime_reused_from_verified_v6':True,'scientific_execution':'NOT_RUN','remote_upload':'NOT_RUN'})
    print(json.dumps({'status':'PACKAGED_LOCAL_ONLY','archives':receipts}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('plan');p.add_argument('--baseline-tree',type=Path,required=True)
    p.add_argument('--prior-c8',type=Path,required=True);p.add_argument('--prior-c10',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p=commands.add_parser('git-payload');p.add_argument('--plan',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--chunk-bytes',type=int,default=40000)
    p=commands.add_parser('package');p.add_argument('--plan',type=Path,required=True);p.add_argument('--source-commit',required=True);p.add_argument('--published-task-tree',required=True);p.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();{'plan':plan,'git-payload':payload,'package':package}[args.command](args)


if __name__=='__main__':main()
