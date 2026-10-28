"""Prepared output-only SVG plot; no rate-function import or rerun."""
import hashlib,json,sys,time,subprocess,resource
from decimal import Decimal,localcontext
from pathlib import Path
from html import escape

ROOT=Path(__file__).resolve().parents[1]


def main():
    if sys.argv[1:]!=['--execute-authorized']:
        raise SystemExit('Prepared only; explicit frozen presentation allowance required')
    out=ROOT/'figures/attempt_01';out.mkdir(parents=True,exist_ok=False)
    start=time.process_time();raw=(ROOT/'execution/attempt_03/STDOUT.json').read_bytes();saved=json.loads(raw)
    if saved.get('success') is not True:raise SystemExit('successful saved selected results required')
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="490" viewBox="0 0 1000 490">',
        '<rect width="1000" height="490" fill="white"/>',
        '<style>text{font-family:DejaVu Sans,sans-serif;fill:#172333;font-size:13px}.title{font-size:18px;font-weight:bold}</style>',
        '<text x="30" y="30" class="title">Actual signed DR fits: represented real formula, conditional loss closure</text>',
        '<text x="30" y="55">No RR, complete callback, fit uncertainty, or actual recipient temperature enclosure</text>',
        '<text x="30" y="90">A. Signed vs clipped alpha at 10⁶ K [m³ s⁻¹]</text>',
        '<text x="520" y="90">B. |Taylor residual| / bound (He+ alpha)</text>']
    colors=['#1769aa','#be3f32']
    rows=[r for r in saved['results']['signed_vs_clipped'] if r['quantity']=='alpha']
    for i,r in enumerate(rows):
        y=145+i*105
        parts.append(f'<text x="30" y="{y}">{escape(r["key"])} signed {Decimal(r["signed"]):.5E}</text>')
        parts.append(f'<text x="30" y="{y+25}">clipped {Decimal(r["clipped"]):.5E}; bias {Decimal(r["positive_bias"]):.5E}</text>')
        with localcontext() as c:
            c.prec=30;ratio=float(Decimal(r['signed'])/Decimal(r['clipped']))
        parts.append(f'<rect x="30" y="{y+38}" width="{350*ratio:.3f}" height="12" fill="#1769aa"/>')
        parts.append(f'<rect x="30" y="{y+53}" width="350" height="6" fill="#be3f32"/>')
    selected=[r for r in saved['results']['taylor'] if r['key']=='2:1' and r['quantity']=='alpha']
    parts.append('<line x1="560" y1="365" x2="930" y2="365" stroke="#888"/>')
    parts.append('<text x="560" y="410">Individual saved log-temperature steps h</text>')
    parts.append('<text x="540" y="370">0</text>')
    parts.append('<text x="540" y="130">1</text>')
    h_labels=['−1/128','+1/128','−1/256','+1/256','−1/512','+1/512']
    for i,r in enumerate(selected):
        with localcontext() as c:
            c.prec=30;ratio=float(Decimal(r['direct_residual']).copy_abs()/Decimal(r['remainder_radius']))
        x=575+i*58;yy=365-240*ratio
        parts.append(f'<rect x="{x}" y="{yy:.3f}" width="26" height="{240*ratio:.3f}" fill="#1769aa"/>')
        parts.append(f'<text x="{x-14}" y="390" style="font-size:11px">{h_labels[i]}</text>')
    parts.extend(['<line x1="560" y1="125" x2="930" y2="125" stroke="#be3f32" stroke-dasharray="5 4"/>',
                  '<text x="560" y="115">upper reference: residual/bound = 1</text>',
                  '<text x="30" y="355">Relative bars: blue signed / red clipped,</text>',
                  '<text x="30" y="375">each normalized to its own clipped value (red=1).</text>',
                  '<text x="30" y="398">0 at left; 1 at full red width.</text>',
                  '<text x="30" y="445">Clipping changes the actual retained fit; no physical fit-error certificate is implied.</text>',
                  '<text x="30" y="470">Right: He+ alpha only; all 36 alpha/loss/source Taylor cases remain in saved raw results.</text>','</svg>'])
    svg=('\n'.join(parts)+'\n').encode();path=out/'DR_SIGNED_AND_TAYLOR.svg';path.write_bytes(svg)
    png=out/'DR_SIGNED_AND_TAYLOR.png'
    argv=['/usr/bin/inkscape',str(path),'--export-type=png','--export-filename='+str(png)]
    conversion=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8)
    (out/'RENDER_STDOUT.txt').write_bytes(conversion.stdout)
    (out/'RENDER_STDERR.txt').write_bytes(conversion.stderr)
    outputs=[{'path':str(path),'bytes':len(svg),'sha256':hashlib.sha256(svg).hexdigest()}]
    if png.exists():
        r=png.read_bytes();outputs.append({'path':str(png),'bytes':len(r),'sha256':hashlib.sha256(r).hexdigest()})
    (out/'PROCESS.json').write_text(json.dumps({'input_sha256':hashlib.sha256(raw).hexdigest(),
        'outputs':outputs,'renderer_argv':argv,'renderer_exit_code':conversion.returncode,
        'CPU_prefix_s':time.process_time()-start,'scope':'saved data conversion/render prefix only',
        'renderer_children_CPU_s':resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime+resource.getrusage(resource.RUSAGE_CHILDREN).ru_stime,
        'accounting':'self prefix and waited renderer are separate; outer whole-command receipt supersedes their sum, never double count',
        'visual_inspection':'PENDING_ACTUAL_PNG_READ','other_cost':'UNKNOWN_NOT_ZERO'},indent=2)+'\n')
    if conversion.returncode:
        raise SystemExit(conversion.returncode)
    if not png.exists():
        raise SystemExit('renderer returned success without PNG output')


if __name__=='__main__':main()
