"""Dependency-free white-background SVG for verified signed-q tau diagnostics."""
from pathlib import Path
import argparse
import json
import xml.etree.ElementTree as ET

def render(signed,clock,out):
    xs=signed["a_grid"]
    if xs!=clock["mean_a_grid"]:raise ValueError("Cross-report mean-scale mismatch")
    series=[]
    for q in ("0.005","0.01"):
        d=clock["decompositions"][q]
        norm=float(q)**2
        for field,label,color,dash in (
            ("even_mean_a","Total","black","none"),
            ("even_clock_residual","Endpoint clock","#23688b","none"),
            ("even_common_time","Same proper time","#888888","none"),
        ):
            vals=[-float(v)/norm*1000 for v in d[field]]
            series.append((q,label,color,vals,dash))
    W,H=920,760
    xl,xr=105,855
    def xx(a):return xl+(a-xs[0])/(xs[-1]-xs[0])*(xr-xl)
    def yy1(v):return 335-(v/1.3)*240
    def yy2(v):return 645-((v-.84)/.12)*190
    elements=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<text x="105" y="35" font-size="18" font-family="sans-serif" font-weight="600" fill="#111">Signed-q Thomson depth response in cold LRS Bianchi I</text>',
              '<text x="105" y="58" font-size="12" font-family="sans-serif" fill="#444">Read-only stored histories; source-scoped numerical diagnostics, not ODE error certificates</text>']
    for y,value in ((335,0),(335-240*0.5/1.3,.5),(335-240/1.3,1.0)):
        elements.append(f'<line x1="{xl}" y1="{y:.2f}" x2="{xr}" y2="{y:.2f}" stroke="#e8e8e8" stroke-width="1"/>')
        elements.append(f'<text x="78" y="{y+4:.2f}" text-anchor="end" font-size="11" fill="#444">{value:.1f}</text>')
    for val in (.86,.9,.94):
        y=yy2(val)
        elements.append(f'<line x1="{xl}" y1="{y:.2f}" x2="{xr}" y2="{y:.2f}" stroke="#e8e8e8"/>')
        elements.append(f'<text x="78" y="{y+4:.2f}" text-anchor="end" font-size="11" fill="#444">{val:.2f}</text>')
    for yl,yh in ((90,335),(450,645)):
        elements.append(f'<path d="M{xl},{yl} V{yh} H{xr}" fill="none" stroke="#444" stroke-width="1"/>')
    for x in xs:
        pos=xx(x)
        for y in (335,645):
            elements.append(f'<line x1="{pos:.2f}" y1="{y}" x2="{pos:.2f}" y2="{y+5}" stroke="#444"/>')
            elements.append(f'<text x="{pos:.2f}" y="{y+20}" text-anchor="middle" font-size="10" font-family="sans-serif" fill="#555">{x:.3f}</text>')
    elements.extend([
      '<text x="105" y="85" font-size="13" font-family="sans-serif" fill="#111">−E(q)/q² [×10⁻³]</text>',
      '<text x="105" y="435" font-size="13" font-family="sans-serif" fill="#111">Clock contribution / total even response</text>',
      '<text x="430" y="715" font-size="12" font-family="sans-serif" fill="#111">Mean scale factor a</text>'])
    for q,label,color,v,d in series:
        points=" ".join(f"{xx(x):.2f},{yy1(y):.2f}" for x,y in zip(xs,v))
        extra=' stroke-dasharray="7,5"' if q=="0.01" else ""
        elements.append(f'<polyline points="{points}" stroke="{color}" stroke-width="2.1" fill="none"{extra}/>')
        for x,y in zip(xs,v):
            elements.append(f'<circle cx="{xx(x):.2f}" cy="{yy1(y):.2f}" r="2.0" fill="{color}"/>')
    for q,col in (("0.005","#23688b"),("0.01","#777777")):
        vals=[float(v) for v in clock["decompositions"][q]["even_clock_fraction"]]
        points=" ".join(f"{xx(x):.2f},{yy2(y):.2f}" for x,y in zip(xs,vals))
        extra=' stroke-dasharray="7,5"' if q=="0.01" else ""
        elements.append(f'<polyline points="{points}" stroke="{col}" stroke-width="2.2" fill="none"{extra}/>')
    for i,(label,color) in enumerate((("Total","black"),("Endpoint clock","#23688b"),("Same proper time","#888888"))):
        xp=420+i*144
        elements.append(f'<line x1="{xp}" x2="{xp+23}" y1="78" y2="78" stroke="{color}" stroke-width="3"/>')
        elements.append(f'<text x="{xp+28}" y="82" font-size="10" font-family="sans-serif">{label}</text>')
    elements.append('<text x="105" y="736" font-size="10" fill="#666" font-family="sans-serif">Solid q=0.005; dashed q=0.01. Clock split uses earliest proper time across all q at each a.</text>')
    elements.append("</svg>")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text("\n".join(elements)+"\n")
    ET.parse(out)
    return out

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--signed",type=Path,required=True)
    p.add_argument("--clock",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    print(render(json.loads(args.signed.read_text()),
                 json.loads(args.clock.read_text()),args.out))
