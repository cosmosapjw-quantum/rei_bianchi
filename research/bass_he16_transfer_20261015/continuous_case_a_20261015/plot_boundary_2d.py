"""Clean SVG of source-only native MD14 energy and time refinement."""
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET

def render(source,out):
    obj=json.loads(source.read_text())
    cases=obj["grid"]
    xmax=790
    coords={4:145,8:285,16:425,32:565,64:705}
    lo,hi=0.0,14.0
    def y(percent):return 420-305*(percent-lo)/(hi-lo)
    txt=['<svg xmlns="http://www.w3.org/2000/svg" width="870" height="570" viewBox="0 0 870 570">',
      '<rect width="870" height="570" fill="#fff"/>',
      '<text x="110" y="40" font-size="21" font-family="sans-serif" fill="#222" font-weight="600">Native MD14: frequency versus time refinement</text>',
      '<text x="110" y="62" font-size="12" font-family="sans-serif" fill="#555">Source-only Bianchi I, q=0, zbar 20 to 19.998, no H/He absorption</text>',
      '<text x="110" y="96" font-size="13" font-family="sans-serif" fill="#333">Fraction of emitted photons numerically lost below E=13.6 eV (%)</text>',
      '<path d="M110 115 V420 H785" fill="none" stroke="#333" stroke-width="1.2"/>']
    for v in range(0,15,2):
        yy=y(v)
        txt.extend([f'<line x1="110" x2="785" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#eeeeee"/>',
          f'<text x="101" y="{yy+4:.2f}" text-anchor="end" font-size="11" fill="#555" font-family="sans-serif">{v}</text>'])
    for m,x in coords.items():
        txt.extend([f'<line x1="{x}" x2="{x}" y1="420" y2="427" stroke="#777"/>',
          f'<text x="{x}" y="446" font-size="12" text-anchor="middle" fill="#333" font-family="sans-serif">{m}</text>'])
    for k,color,dash in (("loss_percent_one_step","#222222",""),("loss_percent_128_steps","#888888","6,5")):
        pts=[(coords[r["source_cells_per_threshold_segment"]],y(r[k])) for r in cases]
        dashattr=f' stroke-dasharray="{dash}"' if dash else ""
        txt.append(f'<polyline points="{" ".join(f"{x},{yy:.2f}" for x,yy in pts)}" fill="none" stroke="{color}" stroke-width="3"{dashattr}/>')
        for x,yy in pts:
            txt.append(f'<circle cx="{x}" cy="{yy:.2f}" r="4" fill="white" stroke="{color}" stroke-width="2"/>')
    txt += [
      '<text x="440" y="475" text-anchor="middle" font-size="12" fill="#333" font-family="sans-serif">Energy cells per original H/He threshold segment (log-spaced horizontally)</text>',
      '<line x1="122" y1="503" x2="152" y2="503" stroke="#222" stroke-width="2.5"/>',
      '<text x="160" y="507" font-size="11" font-family="sans-serif" fill="#333">One time step</text>',
      '<line x1="410" y1="503" x2="440" y2="503" stroke="#888" stroke-width="2.5" stroke-dasharray="6,5"/>',
      '<text x="450" y="507" font-size="11" font-family="sans-serif" fill="#333">128 time steps</text>',
      '<text x="110" y="544" font-size="10" font-family="sans-serif" fill="#666">Finite source-cell centroid control, not a continuum stellar SED or a global ionization-history convergence certificate.</text>',
      '</svg>']
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(txt)+"\n")
    ET.parse(out)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--json",type=Path,required=True)
    p.add_argument("--svg",type=Path,required=True)
    a=p.parse_args()
    print(render(a.json,a.svg))
