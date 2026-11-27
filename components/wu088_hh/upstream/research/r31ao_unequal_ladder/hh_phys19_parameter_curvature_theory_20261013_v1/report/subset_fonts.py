#!/usr/bin/env python3
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont
import hashlib,json,string,argparse
p=argparse.ArgumentParser();p.add_argument("--font-root",type=Path,required=True);a=p.parse_args()
here=Path(__file__).resolve().parent
texfiles=sorted(here.glob("*.tex"));text="\n".join(p.read_text() for p in texfiles)+string.printable+"그림표목차참고문헌증명–—‘’“”"
records=[]
for name in ["NotoSerifCJKkr-Regular.otf","NotoSerifCJKkr-Bold.otf"]:
 source=a.font_root/name;full=TTFont(source);cmap=full.getBestCmap()
 options=subset.Options();options.layout_features=["*"];options.name_IDs=["*"]
 ss=subset.Subsetter(options=options);ss.populate(text=text);ss.subset(full)
 dest=here/"fonts"/name;full.save(dest)
 actual=TTFont(dest).getBestCmap();required=set(map(ord,text)).intersection(cmap)
 missing=sorted(required.difference(actual));assert not missing
 records.append({"name":name,"full_source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
  "full_cmap_entries":len(cmap),"subset_cmap_entries":len(actual),"bytes":dest.stat().st_size,
  "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),"requested_supported_glyphs_lost":missing})
(here/"FONT_SUBSET_MANIFEST.json").write_text(json.dumps({"purpose":"Fresh subset from full Noto CJK fonts for every current report TeX file",
 "tex_source_sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in texfiles},"fonts":records},indent=2)+"\n")
print(json.dumps(records,indent=2))
