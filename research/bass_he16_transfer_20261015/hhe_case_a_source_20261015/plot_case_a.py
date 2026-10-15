"""Dependency-free white SVG of HeIII transport response and rate decomposition."""
import argparse,csv
from pathlib import Path
from xml.etree import ElementTree as ET

def render(path,out):
    with path.open(newline="") as f:rows=list(csv.DictReader(f))
    def get(eta,n,arm):
        return next(r for r in rows if float(r["q_ref"])==0. and
                  float(r["eta_initial"])==eta and
                  int(r["energy_index"])==32 and
                  int(r["substeps"])==n and
                  r["transport"]==arm)
    steps=(1,16,128)
    X={1:164,16:430,128:705}
    W,H=865,690
    R=[]
    R.extend([f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="865" height="690" fill="white"/>',
       '<text x="105" y="40" font-size="19" font-family="sans-serif" fill="#111" font-weight="600">Cold AXBI: Case-A recombination amplifies source-grid HeII threshold error</text>',
       '<text x="105" y="60" font-size="11" font-family="sans-serif" fill="#666">q=0, zbar 20 to 19.998, original Grackle Case-A + CMB, injected photon E=54.42 eV</text>',
       '<text x="105" y="95" font-size="13" font-family="sans-serif">Magnitude of HeIII fraction response: -Delta xHeIII [x 10^-5]</text>',
       '<text x="105" y="386" font-size="13" font-family="sans-serif">Photo-HeII and extra HeIII recombinations [events per H x 10^-6]</text>'])
    def y1(v):return 326-230*v/5.5
    def y2(v):return 616-190*v/5.5
    for top,bottom,scale,fun in ((112,326,5.5,y1),(403,616,5.5,y2)):
        R.append(f'<path d="M110 {top} V{bottom} H768" fill="none" stroke="#555" stroke-width="1.2"/>')
        for v in (0,1,2,3,4,5):
            yy=fun(v)
            R.append(f'<line x1="110" x2="768" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#ededed"/>')
            R.append(f'<text x="99" y="{yy+4:.2f}" text-anchor="end" font-size="11" fill="#555" font-family="sans-serif">{v}</text>')
        for n,x in X.items():
            R.append(f'<line x1="{x}" x2="{x}" y1="{bottom}" y2="{bottom+5}" stroke="#555"/>')
            R.append(f'<text x="{x}" y="{bottom+20}" text-anchor="middle" font-size="11" font-family="sans-serif">{n}</text>')
    for eta,dash,color in ((0.,"","#252525"),(1e-5,"6,5","#777777")):
        vals=[]
        for n in steps:
            a,b=get(eta,n,"PROJECTED"),get(eta,n,"COVARIANT")
            vals.append(-1e5*(float(a["x_HeIII_final"])-float(b["x_HeIII_final"])))
        poly=" ".join(f"{X[n]},{y1(v):.2f}" for n,v in zip(steps,vals))
        attr=f' stroke-dasharray="{dash}"' if dash else ""
        R.append(f'<polyline points="{poly}" stroke="{color}" stroke-width="2.5" fill="none"{attr}/>')
        for n,v in zip(steps,vals):
            R.append(f'<circle cx="{X[n]}" cy="{y1(v):.2f}" r="3.5" stroke="{color}" stroke-width="2" fill="white"/>')
    x_photo=[];x_rr=[]
    for n in steps:
        a,b=get(0.,n,"PROJECTED"),get(0.,n,"COVARIANT")
        x_photo.append(1e6*(float(a["HeII_absorbed_fraction"])-float(b["HeII_absorbed_fraction"]))*1e-6)
        x_rr.append(1e6*(float(a["RR_HeIII_per_H"])-float(b["RR_HeIII_per_H"])))
    for label,values,color,dash in (("photo-HeII difference",x_photo,"#555555","6,5"),
                                    ("extra HeIII recombinations",x_rr,"#111111","")):
        poly=" ".join(f"{X[n]},{y2(v):.2f}" for n,v in zip(steps,values))
        attr=f' stroke-dasharray="{dash}"' if dash else ""
        R.append(f'<polyline points="{poly}" stroke="{color}" stroke-width="2.5" fill="none"{attr}/>')
        for n,v in zip(steps,values):
            R.append(f'<circle cx="{X[n]}" cy="{y2(v):.2f}" r="3.5" stroke="{color}" fill="white" stroke-width="2"/>')
    R.extend([
      '<text x="150" y="361" font-size="10.5" font-family="sans-serif">solid: initial HeII=0; dashed: initial neutral eta=1e-5</text>',
      '<text x="150" y="655" font-size="10.5" font-family="sans-serif">solid: extra HeIII recombination; dashed: false photo-HeII events</text>',
      '<text x="105" y="675" font-size="9.5" fill="#666" font-family="sans-serif">This is a short source-scoped Case-A experiment, not a long reionization history or certified CMB observable.</text>',
      '</svg>'])
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(R)+"\n")
    ET.parse(out)
    return out
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    print(render(args.csv,args.out))
