"""Dependency-free, white-background SVG of nine native AXBI convergence runs."""
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree

def chart(result, outfile):
    r=json.loads(result.read_text())
    levels=["1e-5","3e-6","1e-6"]
    h0=r["per_case_state_endpoint_attentuation"]["ZERO"]["x_HII"]
    # Actual ultra value and chained endpoint differences are source-bound.
    xultra=0.00021553672988191408
    d23=h0["delta_level2_to_level3"]
    d12=h0["delta_level1_to_level2"]
    vals_x=[xultra-d23-d12,xultra-d23,xultra]
    values=r["sampled_goal_difference_attenuation"][-1]
    goal3=float(values["odd_tau_quadrupole_ultra"])
    goal2=goal3-float(values["odd_tau_quadrupole_delta_refined_to_ultra"])
    goal1=goal2-float(values["odd_tau_quadrupole_delta_baseline_to_refined"])
    odd=[goal1,goal2,goal3]
    w,h=900,640
    x=[150,440,730]
    parts=[
       f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
       '<rect width="100%" height="100%" fill="white"/>',
       '<text x="80" y="35" font-family="sans-serif" font-size="20" fill="#111">AXBI native three-level convergence: short z=20 to 19.99 history</text>',
       '<text x="80" y="57" font-family="sans-serif" font-size="12" fill="#555">Frozen identical Rust binary, physics and endpoint; local tolerance varied. No global error certificate.</text>',
       '<text x="80" y="90" font-family="sans-serif" font-size="13" fill="#222">ZERO x_HII at the common native endpoint</text>',
       '<text x="80" y="352" font-family="sans-serif" font-size="13" fill="#222">Odd directional Thomson quadrupole, z_relative=0.0004</text>',
    ]
    panels=[(vals_x,100,288,lambda y: f"{y:.9f}"),
            (odd,363,555,lambda y: f"{y*1e10:.5f} ×10⁻¹⁰")]
    for values,top,bottom,fmt in panels:
        ymin=min(values);ymax=max(values)
        spread=ymax-ymin
        padding=.22*spread if spread else .1*abs(ymax)+1e-30
        lo=ymin-padding;hi=ymax+padding
        xy=lambda v:bottom-(v-lo)/(hi-lo)*(bottom-top)
        parts.append(f'<path d="M100 {top} V{bottom} H795" fill="none" stroke="#555" stroke-width="1.1"/>')
        for i in range(4):
            vv=lo+(hi-lo)*i/3
            yy=xy(vv)
            parts.append(f'<line x1="100" x2="795" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#e6e6e6"/>')
            parts.append(f'<text x="91" y="{yy+4:.2f}" text-anchor="end" font-size="10" fill="#666" font-family="sans-serif">{fmt(vv)}</text>')
        poly=" ".join(f"{xx},{xy(v):.3f}" for xx,v in zip(x,values))
        parts.append(f'<polyline points="{poly}" fill="none" stroke="#263f62" stroke-width="2.3"/>')
        for xx,label,v in zip(x,levels,values):
            yy=xy(v)
            parts.append(f'<circle cx="{xx}" cy="{yy:.2f}" r="5" fill="white" stroke="#263f62" stroke-width="2"/>')
            parts.append(f'<text x="{xx}" y="{yy-12:.2f}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#111">{fmt(v)}</text>')
    for xx,label in zip(x,levels):
        parts.append(f'<text x="{xx}" y="575" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#222">{label}</text>')
    parts+=[
        '<text x="430" y="597" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#222">Adaptive local_target (coarse to refined)</text>',
        '<text x="100" y="622" font-family="sans-serif" font-size="11" fill="#555">Increased accepted steps 972 → 1797 → 3706; local differences are not monotone-contracting.</text>',
        '</svg>']
    outfile.parent.mkdir(parents=True,exist_ok=True)
    outfile.write_text("\n".join(parts)+"\n")
    ElementTree.parse(outfile)
    return outfile

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--analysis",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    print(chart(a.analysis,a.out))
