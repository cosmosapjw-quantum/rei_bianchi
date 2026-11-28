#!/usr/bin/env python3
"""Restore only identity-bound PHYS15--18 cores from the provided archive chain."""
import argparse,hashlib,io,json,pathlib,zipfile
CHAIN=[
("WU088_HH_PHYS18_THEORY_20261013_RESEARCH_BUNDLE.zip",7226960,"356cfbfa7d8fc3613a14d81843fe2b60bef2d006c4c46a8fdc359be29754b8ec","HH_PHYS18_THEORY_20261013_v1"),
("WU088_HH_PHYS17_THEORY_20261013_RESEARCH_BUNDLE.zip",6008925,"4ad08becfd8f7ec07f8a9a7026027b8377d17834c24fe9c2615d19c264076417","HH_PHYS17_THEORY_20261013_v1"),
("WU088_HH_PHYS16_THEORY_20261013_RESEARCH_BUNDLE.zip",4851253,"5899d8fac1db04536c83847b651fa3c982c72d944d5420627057dade404ceb6e","HH_PHYS16_THEORY_20261013_v1"),
("WU088_HH_PHYS15_THEORY_20261013_FULL_SNAPSHOT.zip",3783150,"3e9df6e688e8b707e50c188866e84bc7c95491e6a7bae116d6bbfc97a9e87ffe","HH_PHYS15_THEORY_20261012_v1")]
def main(archive,out):
 data=archive.read_bytes();out.mkdir(parents=True,exist_ok=False);receipt=[]
 for i,(name,size,sha,core) in enumerate(CHAIN):
  assert len(data)==size and hashlib.sha256(data).hexdigest()==sha,("archive identity",name)
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   count=0
   for item in z.infolist():
    part=pathlib.PurePosixPath(item.filename)
    if part.parts[0]!=core or item.is_dir():continue
    assert not part.is_absolute() and ".." not in part.parts
    assert (item.external_attr>>16)&0o170000!=0o120000,"symlink"
    dest=out.joinpath(*part.parts);dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("xb") as f:f.write(z.read(item))
    count+=1
   receipt.append({"name":name,"bytes":size,"sha256":sha,"core":core,"files_restored":count})
   if i+1<len(CHAIN):
    nextname=CHAIN[i+1][0];matches=[n for n in z.namelist() if pathlib.PurePosixPath(n).name==nextname]
    assert len(matches)==1,("nested dependency",nextname,matches);data=z.read(matches[0])
 contract=json.loads((out/CHAIN[0][3]/"contracts/CURVATURE_CONTRACT.json").read_text())
 bindings=[]
 for row in contract["input_bindings"]:
  root=row.get("root");rel=row["path"];p=out/root/rel if root else out/rel
  content=p.read_bytes();expected=row.get("sha256");ok=hashlib.sha256(content).hexdigest()==expected and len(content)==row["bytes"]
  assert ok,("binding",str(p));bindings.append({"path":str(p.relative_to(out)),"match":True})
 result={"status":"restored_and_bound","archives":receipt,"input_bindings":bindings,
 "scope":"File restoration and identity comparison only; no scientific suite or source/root execution."}
 (out/"RESTORATION_RECEIPT.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({"status":result["status"],"archives":len(receipt),"bindings":len(bindings)},indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--archive",type=pathlib.Path,required=True);p.add_argument("--output",type=pathlib.Path,required=True)
 a=p.parse_args();main(a.archive.resolve(),a.output.resolve())
