"""Prepared once-only saved RR/Mao data SVG+PNG; no rate-function import."""
from decimal import Decimal as D,localcontext
from pathlib import Path
from html import escape
import hashlib,json,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]


def main():
    if sys.argv[1:]!=['--execute-authorized']:raise SystemExit('NOT_AUTHORIZED_NEW_RESOURCE')
    out=ROOT/'figures/attempt_01';out.mkdir(parents=True,exist_ok=False)
    start=time.process_time();raw=(ROOT/'execution/attempt_01/STDOUT.json').read_bytes();d=json.loads(raw)
    if not d.get('success'):raise SystemExit('successful new saved results required')
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="570" viewBox="0 0 1100 570">',
       '<rect width="1100" height="570" fill="white"/>',
       '<style>text{font:13px DejaVu Sans,sans-serif;fill:#172333}.t{font-size:18px;font-weight:bold}</style>',
       '<text x="25" y="30" class="t">Actual six-row RR / Mao2017 hybrid: saved represented-real controls</text>',
       '<text x="25" y="55">No full native FP callback, physical fit uncertainty or recipient-temperature enclosure</text>',
       '<text x="25" y="90">A. At 15000 K: alpha [m³/s], L [J m³/s]</text>',
       '<text x="575" y="90">B. |Taylor residual| / uniform remainder bound</text>']
    for i,r in enumerate(d['results']['point_derivatives']):
        y=125+55*i
        p.append(f'<text x="25" y="{y}">{escape(r["key"])}  alpha={D(r["direct"]["alpha"]):.5E}</text>')
        p.append(f'<text x="25" y="{y+20}">L Mao={D(r["direct"]["loss"]):.5E}; f={D(r["direct"]["factor"]):.4E}</text>')
    rows=[r for r in d['results']['taylor'] if r['key']=='3:1' and r['quantity']=='loss' and D(r['radius'])>0]
    labels=['−1/128','+1/128','−1/256','+1/256']
    p+=['<line x1="610" y1="420" x2="1040" y2="420" stroke="#777"/>',
        '<line x1="610" y1="140" x2="1040" y2="140" stroke="#bc4135" stroke-dasharray="5 4"/>',
        '<text x="585" y="425">0</text>','<text x="585" y="145">1</text>',
        '<text x="610" y="120">Li+ selected Mao loss; bound=1 reference</text>']
    for i,r in enumerate(rows):
        with localcontext() as c:
            c.prec=30;ratio=float(D(r['residual']).copy_abs()/D(r['radius']))
        x=645+i*95;h=280*ratio
        p.append(f'<rect x="{x}" y="{420-h:.3f}" width="40" height="{h:.3f}" fill="#1769aa"/>')
        p.append(f'<text x="{x-5}" y="448">{labels[i]}</text>')
    p+=['<text x="610" y="480">Saved log-temperature steps h (dimensionless)</text>',
        '<text x="25" y="515">Left: native RR rate times actual selected Mao factor; derivative-moment closure is not substituted.</text>',
        '<text x="25" y="540">Right: source with nonzero C, a2 and c0; complete raw records retain all rows, signs and zero steps.</text>','</svg>']
    svg=out/'RR_MAO_CONTROLS.svg';svg.write_text('\n'.join(p)+'\n');png=out/'RR_MAO_CONTROLS.png'
    argv=['/usr/bin/inkscape',str(svg),'--export-type=png','--export-filename='+str(png)]
    r=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10)
    (out/'RENDER_STDOUT.txt').write_bytes(r.stdout);(out/'RENDER_STDERR.txt').write_bytes(r.stderr)
    files=[]
    for path in (svg,png):
        if path.exists():
            b=path.read_bytes();files.append({'path':str(path),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
    (out/'PROCESS.json').write_text(json.dumps({'input_sha256':hashlib.sha256(raw).hexdigest(),
        'outputs':files,'renderer_argv':argv,'renderer_exit':r.returncode,
        'self_CPU_prefix_s':time.process_time()-start,'visual_inspection':'PENDING_ACTUAL_PNG_READ',
        'whole_command_accounting':'Outer supervisor includes waited renderer; do not add self/child prefixes again',
        'unknown_tail':'UNKNOWN_NOT_ZERO'},indent=2)+'\n')
    if r.returncode or not png.exists():raise SystemExit(r.returncode or 1)


if __name__=='__main__':main()
