#!/usr/bin/env python3
"""Read-only HE37 saved payload/receipt/delivery verification, standard library.

This checks saved bytes and recorded outcomes. It does not import a scientific
component, evaluate a model, run tests/IVPs, benchmark, render, access a network,
or write any file. Historical stage hashes describe their archived snapshots;
they are deliberately not compared against later corrected current documents.
"""
from pathlib import Path, PurePosixPath
import argparse
import csv
import hashlib
import json
import math
import re
import sys

STAGES=['R'+str(i) for i in range(1,11)]+['C'+str(i) for i in range(1,11)]
COMPONENT_COUNTS={'lc_provider':5,'net_bridge':13,'diagnostic':22}
PROVIDER_RECEIPT='components/lc_provider/attempts/attempt_20261023T020616442395Z/RESULT.json'
BRIDGE_RECEIPT='components/net_bridge/attempts/attempt_20261023T022026748127Z/RESULT.json'


class SavedVerifier:
    def __init__(self,root):
        self.root=Path(root).resolve()
        self.errors=[]
        self.notes=[]
        self.counts={}

    def error(self,message):
        self.errors.append(str(message))

    def path(self,relative,base=None):
        if not isinstance(relative,str) or not relative:
            self.error('invalid manifest path: '+repr(relative));return None
        posix=PurePosixPath(relative)
        if posix.is_absolute() or '..' in posix.parts or '\\' in relative:
            self.error('unsafe manifest path: '+relative);return None
        return (self.root if base is None else base)/Path(*posix.parts)

    def read_json(self,relative):
        p=self.path(relative)
        if p is None:return None
        try:
            return json.loads(p.read_text(encoding='utf-8'))
        except (OSError,UnicodeError,json.JSONDecodeError) as exc:
            self.error(relative+': '+type(exc).__name__+': '+str(exc));return None

    def digest(self,relative):
        p=self.path(relative)
        if p is None:return None
        try:return hashlib.sha256(p.read_bytes()).hexdigest()
        except OSError as exc:
            self.error(relative+': '+type(exc).__name__+': '+str(exc));return None

    def identity(self,relative,expected_hash,expected_size=None,base=None):
        p=self.path(relative,base)
        if p is None:return False
        if not isinstance(expected_hash,str) or re.fullmatch('[0-9a-f]{64}',expected_hash) is None:
            self.error('invalid SHA256 for '+relative);return False
        if expected_size is not None and (type(expected_size) is not int or expected_size<0):
            self.error('invalid byte count for '+relative);return False
        try:b=p.read_bytes()
        except OSError as exc:
            self.error(str(p)+': '+type(exc).__name__+': '+str(exc));return False
        if expected_size is not None and len(b)!=expected_size:
            self.error('byte count mismatch: '+str(p));return False
        if hashlib.sha256(b).hexdigest()!=expected_hash:
            self.error('SHA256 mismatch: '+str(p));return False
        return True

    def manifest(self,relative,expected_count=None):
        data=self.read_json(relative)
        if not isinstance(data,dict) or not isinstance(data.get('files'),list):
            self.error('manifest files array missing: '+relative);return 0,None
        rows=data['files'];seen=set();verified=0;base=(self.root/relative).parent
        if not rows:self.error('empty manifest is not a saved-payload certificate: '+relative)
        if expected_count is not None and len(rows)!=expected_count:
            self.error('manifest entry count mismatch: '+relative)
        for row in rows:
            if not isinstance(row,dict):self.error('invalid manifest row: '+relative);continue
            name=row.get('path')
            if name in seen:self.error('duplicate manifest path: '+str(name));continue
            if isinstance(name,str):seen.add(name)
            size=row.get('size',row.get('bytes'))
            if size is None:self.error('manifest byte count missing: '+str(name));continue
            if self.identity(name,row.get('sha256'),size,base):verified+=1
        return verified,data

    def receipts(self):
        p=self.read_json(PROVIDER_RECEIPT)
        b=self.read_json(BRIDGE_RECEIPT)
        if isinstance(p,dict):
            groups=p.get('groups',{})
            if not isinstance(groups,dict):self.error('provider groups is not a mapping');groups={}
            passed=sum(isinstance(v,dict) and v.get('status')=='PASS' for v in groups.values())
            failed=sum(isinstance(v,dict) and v.get('status')=='FAIL' for v in groups.values())
            self.counts.update(provider_groups_passed=passed,provider_groups_failed=failed)
            if p.get('status')!='PASS' or len(groups)!=6 or passed!=6 or failed!=0:
                self.error('provider saved receipt is not the six-group PASS')
            # The original provider format lacks a process-exit field. Never
            # manufacture one from PASS, or modify the immutable old receipt.
            if 'exit_code' in p:
                self.counts['provider_exit_code']=p['exit_code']
                if p['exit_code']!=0:self.error('provider saved process exit is nonzero')
            else:
                self.counts['provider_exit_code']=None
                self.notes.append('provider original receipt records six PASS groups but no process exit_code field')
            ident=p.get('identity_inputs',{})
            if not isinstance(ident,dict):self.error('provider identity missing')
            else:
                self.identity('components/lc_provider/lc_ionization.py',ident.get('code_sha256'))
                self.identity('components/lc_provider/verify_provider.py',ident.get('verifier_sha256'))
        if isinstance(b,dict):
            rows=b.get('results',[])
            if not isinstance(rows,list):self.error('bridge results is not a list');rows=[]
            passed=sum(isinstance(v,dict) and v.get('status')=='PASS' for v in rows)
            failed=sum(isinstance(v,dict) and v.get('status')=='FAIL' for v in rows)
            self.counts.update(bridge_groups_passed=passed,bridge_groups_failed=failed,bridge_exit_code=b.get('exit_code'))
            if len(rows)!=7 or passed!=7 or failed!=0 or b.get('passed')!=7 or b.get('failed')!=0 or b.get('exit_code')!=0:
                self.error('bridge saved receipt is not the seven-group zero-exit PASS')
            hashes=b.get('hashes',{})
            if not isinstance(hashes,dict):self.error('bridge execution code hashes missing')
            else:
                for name,digest in hashes.items():
                    self.identity(name,digest,base=self.root/'components/net_bridge')

    def read_rows(self,relative):
        p=self.path(relative)
        if p is None:return []
        try:
            with p.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        except (OSError,UnicodeError,csv.Error) as exc:
            self.error(relative+': '+type(exc).__name__+': '+str(exc));return []
        temperatures=[]
        try:
            for row in rows:
                for value in row.values():
                    if not math.isfinite(float(value)):raise ValueError('non-finite saved numeric value')
                temperatures.append(float(row['temperature_K']))
        except (TypeError,ValueError,KeyError) as exc:
            self.error(relative+': invalid saved numeric rows: '+str(exc));return rows
        if len(rows)!=129 or len(set(temperatures))!=129:
            self.error(relative+': expected129unique saved temperatures')
        if not temperatures or temperatures[0]!=2000. or temperatures[-1]!=200000.:
            self.error(relative+': temperature endpoints mismatch')
        if any(a>=b for a,b in zip(temperatures,temperatures[1:])):
            self.error(relative+': saved temperatures are not strictly increasing')
        return rows

    def diagnostic(self):
        native=self.read_rows('components/diagnostic/outputs/h1_gain_moments.csv')
        ccc=self.read_rows('components/diagnostic/reused/ccc_moments.csv')
        self.counts.update(saved_native_rows=len(native),saved_CCC_rows=len(ccc))
        if len(native)==len(ccc)==129:
            try:
                for a,b in zip(native,ccc):
                    if float(a['temperature_K'])!=float(b['temperature_K']):raise ValueError('temperature mismatch')
                    mapping={'alpha_CCC_reused_finite_m3_s':'alpha_partial_m3_s','CCC_reused_mean_energy_eV':'reaction_weighted_mean_energy_eV','CCC_reused_kappa2_over_alpha':'kappa2_over_alpha'}
                    if any(float(a[k])!=float(b[v]) for k,v in mapping.items()):raise ValueError('reused CCC column mismatch')
            except (KeyError,TypeError,ValueError) as exc:self.error('saved CCC comparison: '+str(exc))
        d=self.read_json('components/diagnostic/outputs/DIAGNOSTIC.json')
        if isinstance(d,dict):
            if d.get('status')!='PASS_SCOPED' or d.get('exit_code')!=0 or d.get('grid_rows')!=129:
                self.error('diagnostic saved status/exit/row count mismatch')
            ident=d.get('identity',{})
            for path,key in [('run_diagnostic.py','script_sha256'),('vendor/lc_ionization.py','provider_sha256'),('reused/ccc_moments.csv','CCC_saved_csv_sha256'),('CONTRACT.json','contract_sha256')]:
                self.identity('components/diagnostic/'+path,ident.get(key))
        r=self.read_json('components/diagnostic/plots/RENDER_RECEIPT.json')
        if isinstance(r,dict):
            if r.get('status')!='RENDERED' or r.get('exit_code')!=0 or r.get('model_evaluations')!=0:
                self.error('saved render receipt status mismatch')
            self.identity('components/diagnostic/outputs/h1_gain_moments.csv',r.get('input_csv_sha256'))
            self.identity('components/diagnostic/render_diagnostic.py',r.get('script_sha256'))
            payloads=r.get('payloads',[])
            if not isinstance(payloads,list) or len(payloads)!=2:self.error('saved final figure pair missing')
            else:
                for entry in payloads:
                    self.identity(entry.get('path'),entry.get('sha256'),entry.get('bytes'),self.root/'components/diagnostic')
            self.counts['saved_final_figure_pairs']=1 if isinstance(payloads,list) and len(payloads)==2 else 0

    def corrected_documents(self):
        c=self.read_json('evidence/docfix/CORRECTION.json')
        if not isinstance(c,dict):return
        items=c.get('items',[])
        if not isinstance(items,list):self.error('document correction items missing');return
        for item in items:
            if isinstance(item,dict) and item.get('old_sha256') and item.get('new_sha256'):
                self.identity(item.get('before'),item['old_sha256'])
                self.identity(item.get('path'),item['new_sha256'])
        self.notes.append('historical stage hashes refer to archived snapshots; current corrected documents and preserved originals are checked separately')

    def provider_ack(self,ack,label,node=None):
        if not isinstance(ack,dict):self.error(label+': invalid ACK');return
        if not isinstance(ack.get('archive_sha256'),str) or re.fullmatch('[0-9a-f]{64}',ack['archive_sha256']) is None:
            self.error(label+': invalid archive SHA256')
        size=ack.get('archive_size');db=ack.get('dropbox',{})
        if type(size) is not int or size<=0:self.error(label+': invalid archive size')
        if not isinstance(db,dict) or db.get('status')!='completed':
            self.error(label+': provider not completed');return
        f=db.get('file',{})
        if not isinstance(f,dict):self.error(label+': provider file missing');return
        if not isinstance(f.get('file'),dict) or f['file'].get('size')!=size:
            self.error(label+': provider byte count mismatch')
        if not isinstance(f.get('file_id'),str) or not f['file_id'].startswith('id:'):
            self.error(label+': provider file_id missing')
        archive=ack.get('archive_name') or Path(str(ack.get('archive',''))).name
        if f.get('name')!=archive:self.error(label+': provider archive name mismatch')
        if node is not None:
            if ack.get('stage')!=node.get('id'):self.error(label+': stage id mismatch')
            for key in ('commit','archive_sha256'):
                if ack.get(key)!=node.get(key):self.error(label+': '+key+' mismatch')
            if f.get('file_id')!=node.get('dropbox_id'):self.error(label+': provider id does not match DAG')
            if not isinstance(ack.get('commit'),str) or re.fullmatch('[0-9a-f]{40}',ack['commit']) is None:
                self.error(label+': invalid commit identity')

    def delivery(self,require,manifest_digest):
        dag=self.read_json('DAG.json')
        if not isinstance(dag,dict):return
        if dag.get('workflow_version')!='1.0.0' or dag.get('approval_version')!='0.2':
            self.error('DAG workflow/approval mismatch')
        nodes=dag.get('nodes',[])
        if not isinstance(nodes,list):self.error('DAG nodes array missing');return
        if [n.get('id') if isinstance(n,dict) else None for n in nodes]!=STAGES:
            self.error('DAG stage identity/order mismatch');return
        completed=sum(n.get('status')=='complete' for n in nodes)
        delivered=sum(n.get('publication')=='published' and n.get('backup')=='acknowledged' for n in nodes)
        self.counts.update(stage_completed=completed,stage_delivered=delivered,stage_ACKs_checked=0)
        if dag.get('total_nodes')!=20 or dag.get('completed')!=completed:self.error('DAG stage count mismatch')
        for i,node in enumerate(nodes):
            if node.get('depends_on')!=([] if i==0 else [STAGES[i-1]]):self.error('DAG dependency mismatch: '+node['id'])
            if node.get('publication')!='published':continue
            a=self.read_json('delivery/'+node['id']+'_ACK.json')
            if a is not None:
                self.provider_ack(a,node['id'],node);self.counts['stage_ACKs_checked']+=1
        if require and (completed!=20 or delivered!=20 or self.counts['stage_ACKs_checked']!=20):
            self.error('all20 completed/published/backed-up stage ACKs required')
        final_path=self.root/'delivery/FINAL_ACK.json'
        if not final_path.is_file():
            self.counts['final_ACK_checked']=False
            if require:self.error('FINAL_ACK.json is required but absent')
        else:
            a=self.read_json('delivery/FINAL_ACK.json');self.counts['final_ACK_checked']=True
            if isinstance(a,dict):
                self.provider_ack(a,'FINAL_ACK')
                if a.get('science_manifest_sha256')!=manifest_digest:self.error('FINAL_ACK science manifest SHA256 mismatch')
                if a.get('workflow_version')!='1.0.0' or a.get('approval_version')!='0.2':self.error('FINAL_ACK workflow/approval mismatch')
                if a.get('stages_completed')!=20 or a.get('stage_archives_acknowledged')!=20 or a.get('stage_commits_published')!=20:
                    self.error('FINAL_ACK all20 stage delivery counts mismatch')
        record=self.root/'RUN_RECORD.json'
        if record.is_file():
            d=self.read_json('RUN_RECORD.json')
            if isinstance(d,dict) and (d.get('workflow_version')!='1.0.0' or d.get('approval_version')!='0.2'):
                self.error('RUN_RECORD workflow/approval mismatch')

    def run(self,require):
        verified,manifest=self.manifest('SCIENCE_MANIFEST.json')
        digest=self.digest('SCIENCE_MANIFEST.json')
        self.counts['files_verified']=verified
        self.counts['science_manifest_sha256']=digest
        for component,expected in COMPONENT_COUNTS.items():
            checked,_=self.manifest('components/'+component+'/FILE_MANIFEST.json',expected)
            self.counts[component+'_component_files_verified']=checked
        self.receipts();self.diagnostic();self.corrected_documents();self.delivery(require,digest)
        return {'schema':'he37.saved_payload_verification.v1',
                'status':'FAIL' if self.errors else 'REUSED_COMPLETE_VERIFIED_PAYLOAD',
                'verification_scope':'saved payload identities and recorded outcomes only; no new scientific verification',
                'require_delivery':require,**self.counts,
                'new_IVP':0,'new_render':0,'new_benchmark':0,'new_model_evaluation':0,
                'new_moment_evaluation':0,'new_scientific_test':0,'errors':self.errors,'notes':self.notes}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent,
                        help='read this saved unit instead of the directory containing this script')
    parser.add_argument('--require-delivery',action='store_true',
                        help='also require all20 published stage ACKs and the final archive ACK')
    args=parser.parse_args();verifier=SavedVerifier(args.root)
    try:result=verifier.run(args.require_delivery)
    except Exception as exc:
        verifier.error('unexpected saved-file validation error: '+type(exc).__name__+': '+str(exc))
        result={'schema':'he37.saved_payload_verification.v1','status':'FAIL','errors':verifier.errors,
                'new_IVP':0,'new_render':0,'new_benchmark':0,'new_model_evaluation':0,
                'new_moment_evaluation':0,'new_scientific_test':0,**verifier.counts}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 1 if result['errors'] else 0


if __name__=='__main__':sys.exit(main())
