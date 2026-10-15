"""Render a white, dependency-free SVG for source-scoped frozen HeII A/B events."""
import csv
import math
from pathlib import Path
from xml.etree import ElementTree
import argparse

def plot(source,out):
    with source.open(newline="") as f: rows=list(csv.DictReader(f))
    def get(q,n,arm):
        return next(r for r in rows if float(r["q_ref"])==q
                    and float(r["eta_neutral"])==1e-5 and int(r["e_index"])==32
                    and int(r["steps"])==n and r["arm"]==arm)
    W,H=900,650
    xs={1:165,32:450,256:755}
    def yf(v):
        return 305-(v/.0028)*185
    def yl(v):
        return 550-(v-.13)/.17*155
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<rect width="900" height="650" fill="white"/>',
       '<text x="95" y="34" font-family="sans-serif" font-size="19" font-weight="600" fill="#111">Frozen H/He absorption: false HeII events from energy-grid reprojection</text>',
       '<text x="95" y="54" font-family="sans-serif" font-size="11" fill="#555">Matched zbar20→19.8 LRS Bianchi I, eta=10^-5, initial E=54.42 eV; covariant benchmark below threshold</text>',
       '<text x="95" y="92" font-family="sans-serif" font-size="13" fill="#222">HeII photon absorptions / initial photons</text>',
       '<text x="95" y="375" font-family="sans-serif" font-size="13" fill="#222">Binding energy transferred to gas (eV / initial photon), q=0</text>',
       '<text x="95" y="617" font-family="sans-serif" font-size="12" fill="#222">Number of time-subdivisions (2 fixed-energy remaps per step in projected arm)</text>',
      ]
    for top,bottom,ylab in ((120,305,"HeII event share"),(395,550,"Binding energy")):
        s.append(f'<path d="M108 {top} V{bottom} H810" fill="none" stroke="#444" stroke-width="1.2"/>')
        for n,x in xs.items():
            s.append(f'<line x1="{x}" y1="{bottom}" x2="{x}" y2="{bottom+5}" stroke="#555"/>')
            s.append(f'<text x="{x}" y="{bottom+20}" font-size="11" text-anchor="middle" font-family="sans-serif">{n}</text>')
    for zval in (0,.001,.002,.0025):
        y=yf(zval)
        s.append(f'<line x1="108" x2="810" y1="{y:.2f}" y2="{y:.2f}" stroke="#e7e7e7"/>')
        s.append(f'<text x="98" y="{y+4:.2f}" text-anchor="end" font-size="11" font-family="sans-serif">{zval:.4f}</text>')
    for zval in (.15,.20,.25,.30):
        y=yl(zval)
        s.append(f'<line x1="108" x2="810" y1="{y:.2f}" y2="{y:.2f}" stroke="#e7e7e7"/>')
        s.append(f'<text x="98" y="{y+4:.2f}" text-anchor="end" font-size="11" font-family="sans-serif">{zval:.2f}</text>')
    # Distinct line styles and shaded reference rather than relying only on color.
    for q,color,dash,label in [(-.005,"#111111","", "q = -0.005"),
                                (0.,"#33678a","6,4","q = 0"),
                                (.005,"#777777","2,4","q = +0.005")]:
        pairs=[(xs[n],yf(float(get(q,n,"PROJECTED")["HeII_absorbed_per_initial"]))) for n in xs]
        coords=" ".join(f"{x},{y:.2f}" for x,y in pairs)
        extra=f' stroke-dasharray="{dash}"' if dash else ''
        s.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"{extra}/>')
        for x,y in pairs: s.append(f'<circle cx="{x}" cy="{y:.2f}" r="3.5" fill="white" stroke="{color}" stroke-width="2"/>')
    s.append('<line x1="108" y1="305" x2="810" y2="305" stroke="#bd3333" stroke-width="1.5" stroke-dasharray="8,5"/>')
    s.append('<text x="568" y="298" font-size="10" fill="#9b3030" font-family="sans-serif">Exact covariant HeII = 0</text>')
    for arm,color,dash in (("PROJECTED","#222222",""),("COVARIANT","#777777","6,5")):
        vals=[(xs[n],yl(float(get(0.,n,arm)["binding_eV_per_initial"]))) for n in xs]
        ext=f' stroke-dasharray="{dash}"' if dash else ''
        coords=" ".join(f"{x},{y:.2f}" for x,y in vals)
        s.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.5"{ext}/>')
        for x,y in vals:s.append(f'<circle cx="{x}" cy="{y:.2f}" r="3" fill="{color}"/>')
        s.append(f'<text x="780" y="{yl(float(get(0.,256,arm)["binding_eV_per_initial"]))-11:.2f}" font-size="11" fill="{color}" text-anchor="end" font-family="sans-serif">{arm.capitalize()}</text>')
    s += [
      '<text x="95" y="642" font-size="10" fill="#666" font-family="sans-serif">Source-scoped frozen-gas photon test. Not a time-dependent ionization-history or full CMB optical-depth prediction.</text>',
      '</svg>'
    ]
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(s)+"\n")
    ElementTree.parse(out)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(plot(a.source,a.out))
