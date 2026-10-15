"""Render white publication-oriented SVG for native MD14 boundary/HeIII defects."""
import argparse,csv,json
from pathlib import Path
from xml.etree import ElementTree as ET

def graph(result,source_only,out):
    data=json.loads(result.read_text())["measured"]
    with source_only.open(newline="") as f: free=list(csv.DictReader(f))
    ns=(1,8,32,128)
    def val(q,eta,n,k):
        return next(r[k] for r in data if r["q_ref"]==q and r["eta"]==eta and r["steps"]==n)
    def transparent(n):
        return next(float(x["boundary_fraction"])*100 for x in free
            if float(x["q_ref"])==0 and int(x["substeps"])==n)
    W,H=900,650
    xs={1:170,8:380,32:585,128:775}
    y1=lambda v:340-v*55
    y2=lambda v:560-v*90
    lines=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
      '<rect width="100%" height="100%" fill="white"/>',
      '<text x="92" y="36" font-family="sans-serif" font-size="19" font-weight="600" fill="#151515">Original MD14 source: boundary loss persists under time refinement</text>',
      '<text x="92" y="58" font-family="sans-serif" font-size="11" fill="#666">Bianchi I q=0, zbar 20 to 19.998, fixed 48-cell spectrum and 8 source angles</text>',
      '<text x="96" y="91" font-family="sans-serif" font-size="12" fill="#222">Numerical lower-energy UV boundary loss / original emitted photons (%)</text>',
      '<path d="M118 115 V340 H800" fill="none" stroke="#4c4c4c" stroke-width="1"/>']
    for v in (0,1,2,3,4):
      yy=y1(v)
      lines+=[f'<line x1="118" y1="{yy}" x2="800" y2="{yy}" stroke="#e9e9e9"/>',
       f'<text x="108" y="{yy+4}" font-family="sans-serif" text-anchor="end" font-size="10" fill="#555">{v}</text>']
    curve1=[(xs[n],y1(transparent(n))) for n in ns]
    curve2=[(xs[n],y1(val(0,0,n,"projected_boundary_ratio_of_births")*100)) for n in ns]
    for pts,color,dash in ((curve1,"#333333",""),(curve2,"#777777","7,5")):
       ds=f' stroke-dasharray="{dash}"' if dash else ""
       lines.append(f'<polyline points="{" ".join(f"{x},{y:.3f}" for x,y in pts)}" fill="none" stroke="{color}" stroke-width="2.5"{ds}/>')
       for x,y in pts:lines.append(f'<circle cx="{x}" cy="{y:.3f}" r="4" fill="white" stroke="{color}" stroke-width="2"/>')
    lines.extend(['<text x="120" y="374" fill="#222" font-family="sans-serif" font-size="11">Solid: no absorption; dashed: original Grackle Case-A gas</text>',
     '<text x="95" y="404" fill="#222" font-family="sans-serif" font-size="12">Absolute transport-induced HeIII fraction difference (x 10^-6)</text>',
     '<path d="M118 425 V560 H800" fill="none" stroke="#4c4c4c" stroke-width="1"/>'])
    for v in (0,.5,1.,1.5):
      yy=y2(v)
      lines.extend([f'<line x1="118" y1="{yy}" x2="800" y2="{yy}" stroke="#eeeeee"/>',
       f'<text x="108" y="{yy+4}" font-family="sans-serif" font-size="10" text-anchor="end" fill="#555">{v:.1f}</text>'])
    h3=[(xs[n],y2(abs(val(0,0,n,"delta_HeIII"))*1e6)) for n in ns]
    lines.append(f'<polyline points="{" ".join(f"{x},{y:.3f}" for x,y in h3)}" stroke="#444" fill="none" stroke-width="2.3"/>')
    for n,x in xs.items():
      lines.extend([f'<text x="{x}" y="589" font-size="11" text-anchor="middle" fill="#333" font-family="sans-serif">{n}</text>'])
    lines.extend([
      '<text x="450" y="614" font-size="11" text-anchor="middle" fill="#444" font-family="sans-serif">Number of physical source/transport steps</text>',
      '<text x="95" y="638" fill="#666" font-family="sans-serif" font-size="10">Source-scoped cold CASE-A; production EoR global error, emitter stress, escaped-photon moments remain unresolved.</text>',
      '</svg>'])
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(lines)+"\n")
    ET.parse(out)
    return out
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--analysis",type=Path,required=True)
 p.add_argument("--source-only",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 print(graph(a.analysis,a.source_only,a.out))
