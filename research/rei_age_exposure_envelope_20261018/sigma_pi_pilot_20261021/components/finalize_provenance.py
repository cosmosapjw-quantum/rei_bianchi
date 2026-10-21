#!/usr/bin/env python3
"""Metadata-only provider/cutoff closure and deterministic lossless copies."""
import sys,json,csv,gzip,hashlib,time
from pathlib import Path
sys.dont_write_bytecode=True
BEGIN=time.monotonic()
PACKAGE=Path(__file__).resolve().parents[1]
ROOT=next(p for p in PACKAGE.parents if (p/'CASE_PROVENANCE_LEDGER.json').exists())

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_json(path,value):Path(path).write_text(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n')
def main():
    source=ROOT/'CASE_PROVENANCE_LEDGER.json';csv_path=ROOT/'CASE_PROVENANCE_LEDGER.csv';ledger=json.loads(source.read_text());before_sha=sha(source)
    artifacts={
      'A_HISTORICAL_FULL_RAW':{'filename':'REI_BIANCHI_MATTER_RADIATION_FINAL_20261021.tar.gz','size_bytes':37945383,'sha256':'2c1433a92ae68c328436852b2842c9b7c51d30b9ff84a22fe2dffbd04ee4246d','providers':{'drive':{'id':'1i6x-HcPTctzSQwsxkET-CfTGfjpC-Dx7'},'dropbox':{'id':'id:BSpOijBcT10AAAAAAD_fYA'}},'verification':'Both provider ACKs and complete HTTP200 bytes/SHA readbacks verified','scope':'All1231 historical A numerical segments and25 reference aliases'},
      'B_D3_EXECUTION_RAW':{'filename':'REI_UNIFIED_D3_EXECUTION_20261021_20261021T104524Z.tar.gz','size_bytes':31904176,'sha256':'7f3856bceea80f25e1f32d69f61cb40841a8461f66e1257bbd7eb79e01184498','providers':{'drive':{'id':'1_noyMOexSIBbHdWIqkoGsvt3nBxwGZGi'},'dropbox':{'id':'id:BSpOijBcT10AAAAAAD_gNA'}},'verification':'Both provider ACKs and complete HTTP200 bytes/SHA readbacks verified','verification_receipt':'recovery_backups/checkpoints/D3/20261021T104524Z/BACKUP_RECEIPT.json','scope':'All237 B prefixes,237 tails,35 reference aliases and historical failed/repaired receipt provenance'}}
    profile_key='CANONICAL_COMPACTIFIED_FD_PR147'
    profile={'source_file':'vendor/canonical_fv.py','source_sha256':'91c1641b851aa9580141d4423e2579ced5f11b95aa716b3fc2cb0137df344cc5','radial_variable':'dimensionless canonical momentum q','physical_radial_domain':'q in [0,infinity)','physical_high_q_hard_cutoff':None,'compactification':'t=(q-3)/(q+3); q=3*(1+t)/(1-t); t in [-1,1)','radial_profile':'Fermi-Dirac f(q)=exp(-q)/(1+exp(-q))','angular_variable':'mu in [-1,1]','quadrature_scope':'Finite Gauss nodes/cells sample the compactified unbounded physical momentum domain; they do not impose a finite physical high-q cutoff. Per-row config retains radial/angular cells, Gauss order and radiation ellmax closure.'}
    ledger['artifact_map']=artifacts;ledger['physical_profile_map']={profile_key:profile}
    for row in ledger['rows']:
        key='A_HISTORICAL_FULL_RAW' if row['lane']=='A' else 'B_D3_EXECUTION_RAW'
        prior=row.get('archive_sha256')
        if prior and not prior.startswith('PENDING_'):row['historical_source_archive_sha256']=prior
        row['archive_key']=key;row['archive_sha256']=artifacts[key]['sha256'];row['provider_current_archive']=key;row['physical_profile_key']=profile_key
        if row['lane']=='B':row['provider_historical_archive']='Original94 recovered from prior scratch; nested RAW_RESULTS archive SHA verified; all B now preserved in verified D3 dual-provider archive.' if row['case_id'].startswith('Bprefix:') and row.get('wrapper_publication_identity')=='UNPUBLISHED_WITH_SHA256' else 'Verified D3 dual-provider archive; see archive_key.'
    ledger['metadata_finalization']={'source_sha256':sha(__file__),'previous_validated_ledger_sha256':before_sha,'scope':'Only archive/provider and source-backed momentum cutoff metadata updated; prior numerical rows/source-group checks reused. No ODE or physical gate replay.'}
    ledger['notes']=[n for n in ledger.get('notes',[]) if 'Current archive/provider' not in n]+['Verified per-row archive_key resolves through artifact_map. Final source publication identity remains a separate root overlay.','No finite physical high-q cutoff; finite Gauss nodes are quadrature, as specified in physical_profile_map.']
    # Preserve existing column order, append only the authorized metadata columns.
    with csv_path.open(newline='') as f:keys=next(csv.reader(f))
    for row in ledger['rows']:
        for key in row:
            if key not in keys:keys.append(key)
    write_json(source,ledger)
    with csv_path.open('w',newline='') as f:
        writer=csv.DictWriter(f,keys);writer.writeheader();writer.writerows({k:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in ledger['rows'])
    files={}
    for full in (source,csv_path):
        compressed=full.with_name(full.name+'.gz')
        with full.open('rb') as src,compressed.open('wb') as dst:
            with gzip.GzipFile(filename='',mode='wb',fileobj=dst,compresslevel=9,mtime=0) as stream:
                while block:=src.read(1024*1024):stream.write(block)
        digest=hashlib.sha256()
        with gzip.open(compressed,'rb') as stream:
            while block:=stream.read(1024*1024):digest.update(block)
        if digest.hexdigest()!=sha(full):raise ValueError('LOSSLESS_GZIP_ROUNDTRIP_FAILED:'+full.name)
        files[full.name]={'full':{'path':str(full),'size_bytes':full.stat().st_size,'sha256':sha(full)},'gzip':{'path':str(compressed),'size_bytes':compressed.stat().st_size,'sha256':sha(compressed),'mtime':0,'embedded_filename':''},'roundtrip_sha256_match':True}
    index={'schema':'rei.case_provenance_ledger_index.v1','counts':ledger['counts'],'files':files,'artifact_map':artifacts,'physical_profile_map':ledger['physical_profile_map'],'semantics':{'record_kind':'numerical_segment is a numerical integration segment; reference_alias contributes zero IVPs','B_trajectory_vs_segments':'237 unique B trajectories each have a z20→4 prefix and z4→2 tail, totaling474 B numerical segments','reference_relationship':'IDENTICAL_REUSABLE_CASE is restricted to hash-bound same-lane references','A_B_relationship':'Cross-lane equality is never raw reuse; explicit sqrt2 norm transform and matching physical inputs are required for comparability','recovered100':'Original FAILED_WORKER_EXIT/exit124 and immutable failed receipt retained separately from saved-data-only corrected receipt; unsaved solver metadata remains unavailable'},'decompression':['gzip -dk CASE_PROVENANCE_LEDGER.json.gz','gzip -dk CASE_PROVENANCE_LEDGER.csv.gz'],'source_metadata_builder_sha256':sha(PACKAGE/'components/build_provenance_ledger.py'),'source_finalizer_sha256':sha(__file__),'validation':'Previous row-count and actual-source-group check reused; only metadata references and lossless gzip SHA roundtrip checked here.'}
    write_json(ROOT/'CASE_PROVENANCE_LEDGER_INDEX.json',index)
    check_path=ROOT/'CASE_PROVENANCE_LEDGER_CHECK.json';check=json.loads(check_path.read_text());check['ledger_sha256']=files[source.name]['full']['sha256'];check['metadata_closure']={'artifact_keys_resolve':True,'physical_profile_key_present':True,'gzip_roundtrip_SHA_both':True,'no_ODE_or_physical_gate_replay':True};write_json(check_path,check)
    receipt={'profile':'sandbox','controller_elapsed_s':time.monotonic()-BEGIN,'operation':'ledger_metadata_and_lossless_gzip','argv':sys.argv,'scientific_solver_calls':0};write_json(PACKAGE/'z2_extension/results/controllers'/(str(time.time_ns())+'.json'),receipt)
    print(json.dumps({'files':files,'index_sha256':sha(ROOT/'CASE_PROVENANCE_LEDGER_INDEX.json'),'counts':ledger['counts'],'elapsed_s':receipt['controller_elapsed_s']},indent=2))
if __name__=='__main__':main()
