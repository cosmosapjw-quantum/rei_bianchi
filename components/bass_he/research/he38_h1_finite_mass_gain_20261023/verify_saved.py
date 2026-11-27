#!/usr/bin/env python3
"""Validate HE38 saved identities and recorded receipts; never run scientific code."""
from pathlib import Path
import argparse,csv,hashlib,json,math,re,sys,tarfile

STAGES=[f'R{i}' for i in range(1,11)]+[f'C{i}' for i in range(1,11)]
class Verifier:
    def __init__(self,root):
        self.root=root.resolve();self.errors=[];self.counts={};self.notes=[]
    def error(self,s):self.errors.append(str(s))
    def path(self,relative):
        q=(self.root/relative).resolve()
        if not q.is_relative_to(self.root):raise ValueError('path escapes unit: '+str(relative))
        return q
    def read(self,relative):return json.loads(self.path(relative).read_text())
    def digest(self,q):return hashlib.sha256(q.read_bytes()).hexdigest()
    def identity(self,relative,digest,size=None):
        q=self.path(relative)
        if not q.is_file():self.error('missing '+str(relative));return False
        if not isinstance(digest,str) or self.digest(q)!=digest:self.error('hash '+str(relative));return False
        if size is not None and q.stat().st_size!=size:self.error('size '+str(relative));return False
        return True
    def science(self):
        data=self.read('SCIENCE_MANIFEST.json');rows=data['files']
        paths=[r['path'] for r in rows]
        if len(set(paths))!=len(paths):self.error('duplicate science path')
        self.counts['science_files_verified']=sum(self.identity(r['path'],r['sha256'],r['size']) for r in rows)
        self.counts['science_manifest_sha256']=self.digest(self.path('SCIENCE_MANIFEST.json'))
        contract=self.read('CONTRACT.json')
        if contract['workflow_version']!='1.0.0' or contract['approval_version']!='0.2':self.error('workflow/approval changed')
        donor=self.read('components/finite_mass/DONOR_PROVENANCE.json')
        self.counts['byte_preserved_donors_verified']=sum(self.identity('components/finite_mass/'+r['destination_relative'],r['sha256']) for r in donor['files'])
        if self.counts['byte_preserved_donors_verified']!=6:self.error('six donor identities required')
    def receipt(self,path,statuses=('PASS','PASS_SCOPED'),require_exit=True):
        record=self.read(path)
        if record.get('status') not in statuses:self.error('saved status '+path)
        if require_exit and record.get('exit_code')!=0:self.error('saved exit '+path)
        return record
    def outcomes(self):
        run=self.read('RUN_RECORD.json')
        for key in ['old_IVP_replays','old_suite_replays','old_diagnostic_replays','old_provider_benchmarks','new_IVP']:
            if run.get(key)!=0:self.error('unexpected execution '+key)
        theory=self.receipt('theory/CHECKS.json')
        imp=self.receipt(run['saved_receipts']['implementation'])
        if imp.get('controls')!=107 or not all(x.get('passed') is True for x in imp['checks']):self.error('affected controls107 not all PASS')
        probe=self.receipt('evidence/review/PROBE_RESULT.json')
        raw=self.receipt(run['saved_receipts']['raw_oracle'],require_exit=False)
        launch=self.read('evidence/raw_controls/LAUNCH_RECEIPT.json')
        if launch.get('returncode')!=0:self.error('raw oracle launcher exit')
        self.notes.append('Raw RESULT has no exit_code field; the unmodified launcher receipt supplies returncode0.')
        diagnostic=self.receipt(run['saved_receipts']['diagnostic'])
        metric=self.read('components/diagnostic/outputs/METRICS.json')
        bench=self.read('components/diagnostic/outputs/BENCHMARK.json')
        if diagnostic.get('new_api_evaluations')!=1 or metric.get('grid_count')!=129:self.error('new129T diagnostic identity/count')
        if bench.get('batches')!=7 or not bench.get('not_a_full_provider_or_IVP_speedup'):self.error('benchmark scope/count')
        rows=list(csv.DictReader(self.path('components/diagnostic/outputs/finite_mass_moments.csv').open()))
        ts=[float(r['temperature_K']) for r in rows]
        if len(ts)!=129 or ts[0]!=2000.0 or ts[-1]!=200000.0 or any(a>=b for a,b in zip(ts,ts[1:])):self.error('saved diagnostic grid')
        if any(not math.isfinite(float(v)) for r in rows for v in r.values()):self.error('nonfinite saved table')
        accepted=self.read('figures/ACCEPTED_FIGURE.json')
        for r in accepted['payloads']:self.identity(r['path'],r['sha256'],r['size'])
        if len(accepted['payloads'])!=2 or accepted['model_evaluations']!=0:self.error('accepted plot pair/scope')
        qa=self.read('evidence/review/FINAL_REVIEW.json')
        if qa.get('status')!='PASS_SCOPED' or qa.get('blocking_findings')!=0 or qa.get('open_findings')!=0:self.error('independent review findings remain')
        self.counts.update(affected_controls=imp['controls'],independent_interface_probes=probe['probe_count'],saved_diagnostic_rows=len(rows),accepted_figure_pairs=1,new_science_executed_by_verifier=0)
        self.notes.append('Recorded outcomes and file identities are checked; their scientific calculations are not re-executed.')
    def ack(self,record,label,node=None):
        sha=record.get('archive_sha256','');size=record.get('archive_size');db=record.get('dropbox',{})
        if not re.fullmatch('[0-9a-f]{64}',sha):self.error(label+': archive digest')
        if db.get('status')!='completed':self.error(label+': provider ACK not completed')
        f=db.get('file',{})
        if f.get('file',{}).get('size')!=size:self.error(label+': provider size')
        if f.get('name')!=Path(record.get('archive','')).name:self.error(label+': provider filename')
        if not f.get('file_id','').startswith('id:'):self.error(label+': provider id')
        if node:
            if record.get('stage')!=node['id'] or record.get('commit')!=node.get('commit') or sha!=node.get('archive_sha256') or f.get('file_id')!=node.get('dropbox_id'):self.error(label+': DAG/ACK binding')
    def archive(self,record,archive_root=None):
        q=(archive_root/Path(record['archive']).name) if archive_root else Path(record['archive'])
        if not q.is_file():self.error('local archive absent '+str(q));return 0
        if self.digest(q)!=record['archive_sha256'] or q.stat().st_size!=record['archive_size']:self.error('archive bytes '+str(q));return 0
        prefix='research/'+self.root.name+'/'
        manifest_name=prefix+record['manifest']
        checked=0
        with tarfile.open(q,'r:gz') as tar:
            members=tar.getmembers();names=[x.name for x in members]
            if len(set(names))!=len(names):self.error('duplicate tar member '+q.name)
            mf=tar.extractfile(manifest_name)
            if mf is None:self.error('archive payload manifest absent '+q.name);return 0
            manifest=json.load(mf)
            for r in manifest['files']:
                f=tar.extractfile(prefix+r['path'])
                if f is None:self.error(q.name+': payload absent '+r['path']);continue
                b=f.read()
                if len(b)!=r['size'] or hashlib.sha256(b).hexdigest()!=r['sha256']:self.error(q.name+': payload mismatch '+r['path'])
                else:checked+=1
            if checked!=record['payload_count']:self.error(q.name+': payload count')
        return checked
    def delivery(self,require,archives,archive_root):
        dag=self.read('DAG.json');nodes=dag['nodes']
        if [x['id'] for x in nodes]!=STAGES:self.error('DAG stage order')
        completed=sum(x.get('status')=='complete' for x in nodes)
        delivered=sum(x.get('publication')=='published' and x.get('backup')=='acknowledged' for x in nodes)
        if dag.get('completed')!=completed:self.error('DAG completed count')
        count=0;payload_count=0
        for i,n in enumerate(nodes):
            if n['depends_on']!=([] if i==0 else [STAGES[i-1]]):self.error('DAG dependency '+n['id'])
            if n.get('publication')!='published':continue
            a=self.read('delivery/'+n['id']+'_ACK.json');self.ack(a,n['id'],n);count+=1
            snapshot={r['path']:r['sha256'] for r in self.read(a['manifest'])['files']}
            for e in n.get('evidence',[]):
                if snapshot.get(e['path'])!=e['sha256']:self.error('stage snapshot evidence '+n['id']+': '+e['path'])
            if archives:payload_count+=self.archive(a,archive_root)
        self.counts.update(stages_completed=completed,stages_delivered=delivered,stage_ACKs_checked=count)
        if require and (completed!=20 or delivered!=20 or count!=20):self.error('20 completed/delivered/ACK required')
        if archives:self.counts['new_stage_archive_payload_hashes_checked']=payload_count
        self.notes.append('Stage evidence hashes refer to their immutable archived snapshots; current science files are checked by SCIENCE_MANIFEST, so later README/delivery updates are not mistaken for scientific corruption.')
        final=self.path('delivery/FINAL_ACK.json')
        if final.is_file():
            a=self.read('delivery/FINAL_ACK.json');self.ack(a,'FINAL_ACK')
            if a.get('science_manifest_sha256')!=self.counts['science_manifest_sha256']:self.error('final manifest binding')
            if any(a.get(k)!=20 for k in ['stages_completed','stage_archives_acknowledged','stage_commits_published']):self.error('final stage totals')
            if archives:self.counts['final_archive_payload_hashes_checked']=self.archive(a,archive_root)
            self.counts['final_ACK_checked']=True
        else:
            self.counts['final_ACK_checked']=False
            if require:self.error('FINAL_ACK missing')
    def run(self,args):
        try:self.science();self.outcomes();self.delivery(args.require_delivery,args.archives,args.archive_root)
        except Exception as exc:self.error(type(exc).__name__+': '+str(exc))
        return {'schema':'he38.saved_evidence_verification.v1','status':'FAIL' if self.errors else 'REUSED_COMPLETE_VERIFIED_PAYLOAD','require_delivery':args.require_delivery,'local_archives_checked':args.archives,**self.counts,'new_IVP':0,'new_render':0,'new_benchmark':0,'new_model_evaluation':0,'new_scientific_test':0,'errors':self.errors,'notes':self.notes}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);ap.add_argument('--require-delivery',action='store_true');ap.add_argument('--archives',action='store_true',help='also hash locally available new HE38 stage/final archive payloads');ap.add_argument('--archive-root',type=Path)
    args=ap.parse_args();out=Verifier(args.root).run(args);print(json.dumps(out,ensure_ascii=False,indent=2));return bool(out['errors'])
if __name__=='__main__':sys.exit(main())
