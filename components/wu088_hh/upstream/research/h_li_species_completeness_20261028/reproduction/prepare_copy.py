"""Metadata-only HLI recovery copy; never executes registry or solver code."""
from pathlib import Path
import argparse,shutil,json,hashlib
UID='H_LI_SPECIES_COMPLETENESS_20261028';SHA='89a5ba77efc940bb419d3c45c7603238770f3a1ed9142ad19f06271c6cb83ab7'
def main():
 p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--normalized-full',type=Path,required=True);a=p.parse_args();src=a.package.resolve();dst=a.destination.resolve()
 if dst.exists() or src==dst or src in dst.parents:raise SystemExit('Destination must be new and outside source package')
 raw=a.normalized_full.read_bytes();assert len(raw)==376327 and hashlib.sha256(raw).hexdigest()==SHA
 shutil.copytree(src,dst/'saved_evidence');shutil.copytree(src,dst/'execution');u=dst/'execution/units'/UID;private=u/'private_validation_inputs/NUBASE2020_EXA_NORMALIZED_FULL.txt';private.parent.mkdir(parents=True,exist_ok=True);private.write_bytes(raw)
 assert (u.parents[1]/'helpers/bounded_child.py').exists(),'Relative runner helper layout incomplete'
 mf=u/'INPUT_BINDINGS.json';m=json.loads(mf.read_text());pathmap={};checks=[]
 for row in m['files']:
  q=u/row['unit_relative_path'];data=q.read_bytes();assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'];old=row['path'];pathmap[old]=str(q);row['original_path_preserved']=old;row['historical_copied_path_preserved']=row.get('copied_path');row['path']=str(q);row['copied_path']=str(q);checks.append({'relative_path':row['unit_relative_path'],'sha256':row['sha256'],'match':True})
 mf.write_text(json.dumps(m,indent=2)+'\n')
 # suite.py joins the six authority rows to INPUT_BINDINGS by path. Adapt only
 # their copied locator fields consistently, retaining every source byte/hash.
 af=u/'inputs/AUTHORITY_INPUT_FREEZE.json';authority=json.loads(af.read_text())
 for row in authority['files']:
  old=row['path'];row['original_path_preserved']=old;row['path']=pathmap[old]
 af.write_text(json.dumps(authority,indent=2)+'\n')
 cleared=[]
 for f in u.iterdir():
  if f.is_file() and ((f.suffix=='.json' and f.name not in ['INPUT_BINDINGS.json','PUBLICATION_POLICY.json']) or f.suffix=='.log'):
   cleared.append(f.name);f.unlink()
 report={'science_executed':False,'source_package_unchanged':True,'saved_evidence':str(dst/'saved_evidence'),'execution_unit':str(u),'copied_metadata_adapted':['INPUT_BINDINGS path/copied_path with original locators retained','inputs/AUTHORITY_INPUT_FREEZE six path joins with original locators retained'],'verified_input_files':checks,'private_source_sha256':SHA,'cleared_copied_fresh_attempt_outputs':cleared,'archival_attempts':'Original firstfailure/repair evidence remains immutable in saved_evidence; executioncopy attempts subtree is historical, not a fresh run','new_allocation_required':True,'old_budget_transfer':False}
 (dst/'PREPARATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
