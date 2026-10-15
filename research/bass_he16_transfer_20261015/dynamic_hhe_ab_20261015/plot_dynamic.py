"""White SVG diagnostic: photo-only dynamic ghost HeIII fraction, per neutral η."""
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import argparse

def render(source,out):
    d=json.loads(source.read_text())
    cases=d["all_cases"]
    def series(eta):
        row=next(x for x in cases if x["q"]==0 and x["eta"]==eta
                  and x["initial_energy_index"]==32)
        return [(v["steps"],100*v["delta_xHeIII_projected_minus_covariant"]/eta) for v in row["levels"]]
    lines=[("eta = 1e-5",series(1e-5),"#252525",""),
           ("eta = 1e-4",series(1e-4),"#777777","7,5")]
    W,H=850,515
    places={1:135,16:415,128:730}
    ymin,ymax=0.27,0.315
    def y(v):return 345-(v-ymin)/(ymax-ymin)*225
    elems=[
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect x="0" y="0" width="850" height="515" fill="white"/>',
        '<text x="97" y="40" fill="#111" font-family="sans-serif" font-size="19" font-weight="600">Dynamic HeIII excess from source-grid ghost absorption</text>',
        '<text x="97" y="65" fill="#555" font-family="sans-serif" font-size="12">q=0, initial packet E=54.42 eV, zbar 20 to 19.8, no recombination/emission</text>',
        '<text x="97" y="99" fill="#333" font-family="sans-serif" font-size="13">(xHeIII_projected - xHeIII_covariant) / eta  [%]</text>',
        '<path d="M97 120 V345 H760" fill="none" stroke="#444" stroke-width="1.2"/>',
    ]
    for tick in (0.27,0.28,0.29,0.30,0.31):
        yy=y(tick)
        elems.append(f'<line x1="97" x2="760" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#e9e9e9"/>')
        elems.append(f'<text x="89" y="{yy+4:.2f}" fill="#555" text-anchor="end" font-family="sans-serif" font-size="11">{tick:.2f}</text>')
    for steps,x in places.items():
        elems.append(f'<line x1="{x}" x2="{x}" y1="345" y2="352" stroke="#444"/>')
        elems.append(f'<text x="{x}" y="369" text-anchor="middle" fill="#333" font-family="sans-serif" font-size="12">{steps}</text>')
    for name,values,color,dash in lines:
        coords=" ".join(f"{places[step]},{y(v):.2f}" for step,v in values)
        stroke=f' stroke-dasharray="{dash}"' if dash else ""
        elems.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="2.7"{stroke}/>')
        for step,v in values:
            elems.append(f'<circle cx="{places[step]}" cy="{y(v):.2f}" r="4" fill="white" stroke="{color}" stroke-width="2"/>')
    for i,(name,_,color,dash) in enumerate(lines):
        xp=130+290*i
        dash_attr=f' stroke-dasharray="{dash}"' if dash else ""
        elems.append(f'<line x1="{xp}" x2="{xp+28}" y1="406" y2="406" stroke="{color}" stroke-width="2.5"{dash_attr}/>')
        elems.append(f'<text x="{xp+36}" y="410" font-family="sans-serif" fill="#333" font-size="12">{name}</text>')
    elems.extend([
        '<text x="425" y="450" font-family="sans-serif" fill="#333" text-anchor="middle" font-size="12">Geometry-remap/collision time substeps</text>',
        '<text x="97" y="483" font-family="sans-serif" fill="#666" font-size="11">Nuclear and photoheat ledgers close; output is a photo-only source-scoped numerical experiment, not physical EoR predictions</text>',
        '</svg>',
    ])
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(elems)+"\n")
    ET.parse(out)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--analysis",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(render(a.analysis,a.out))
