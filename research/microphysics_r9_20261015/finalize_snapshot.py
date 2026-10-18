#!/usr/bin/env python3
"""Generate a report snapshot from actual receipts; no new physics solve."""
import csv,hashlib,json,subprocess
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parent
N=R/'ncp_results'
rows=[];full=[]
for p in sorted((N/'runs').glob('*/*/receipt.json')):
 j=json.loads(p.read_text());c=j.get('case',{})
 checks=[j.get('checks',{})]+[j.get(k,{}).get('checks',{}) for k in ('parent','daughter')]
 def mx(k):
  v=[s[k] for s in checks if isinstance(s,dict) and isinstance(s.get(k),(int,float))]
  return max(v) if v else None
 r=dict(run=p.parent.parent.name,case=p.parent.name,kind=c.get('kind'),basis=c.get('basis'),species=c.get('species'),status=j.get('status'),finite_model_numerics_passed=j.get('finite_model_numerics_passed'),E_electronic_Eh=j.get('E_electronic_Eh'),P_ground=j.get('P_ground'),TRK_diagnostic=j.get('TRK_diagnostic'),ao_rank=j.get('ao_rank'),retained_rank=j.get('retained_ao_rank',j.get('norb')),residual_max_Eh=mx('original_H_residual_Eh'),metric_max=mx('orthogonality_inf'),spin_error_max=mx('spin_error'),wall_s=j.get('wall_s'),source_sha256=j.get('runtime',{}).get('source_sha256'),data_sha256=j.get('data_sha256'),receipt=str(p.relative_to(R)))
 rows.append(r);full.append((p,j))
(R/'results').mkdir(exist_ok=True)
(R/'results/EXECUTION_INDEX.json').write_text(json.dumps(rows,indent=2)+'\n')
with (R/'results/EXECUTION_INDEX.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
counts={}
for r in rows:
 counts.setdefault(r['run'],Counter());counts[r['run']]['receipts']+=1
 counts[r['run']]['passed' if r['finite_model_numerics_passed'] else 'not_accepted']+=1
def get(c):return next(j for p,j in full if p.parent.name==c)
IQ=get('atomic_Li_plus_core_QZ_final')['E_electronic_Eh']-get('atomic_Li_core_QZ_final')['E_electronic_Eh']
IT=-7.276559599088856+7.474251419701423
PQ=get('quench_He_Li_union_aug_QZ_cond1e_7')['P_ground'];PT=.7089407395627837
conv={'core_valence_ionization':{'I_T_Eh':IT,'I_Q_Eh':IQ,'absolute_T_Q_change_Eh':abs(IQ-IT),'target_Eh':1e-4,'target_met':False},'He_Li_union':{'P_T':PT,'P_Q_retained124':PQ,'absolute_T_Q_change':abs(PQ-PT),'target':1e-4,'target_met':False,'scope':'basis change and Q metric truncation; not a rigorous error bound'},'physical_closure':dict.fromkeys(['li_bound','li_continuum','molecular_lowT','daughter_correlated','nuclear_precision','atomic_charge_cascade','bbn17','full_transport'],'open')}
(R/'results/CONVERGENCE_STATUS.json').write_text(json.dumps(conv,indent=2)+'\n')
rust={'host':'s1a0e5abed09','source_commit':'54dd5352672127e77970eb06f3dda027f2aee275','rustc':'rustc 1.99.0 (b940084d7 2026-09-28)','cargo':'cargo 1.99.0 (5f94df478 2026-08-27)','manifest':'rust_native/rust/rei_microphysics/Cargo.toml','build_command':'/root/.cargo/bin/cargo check --locked --offline --lib --manifest-path rust_native/rust/rei_microphysics/Cargo.toml --target-dir rust_native/target -j4','test_command':'/root/.cargo/bin/cargo test --locked --offline --manifest-path rust_native/rust/rei_microphysics/Cargo.toml --target-dir rust_native/target -j4 --test deuterium_atomic','build_exit':0,'integration_tests_passed':8,'integration_tests_failed':0,'scope':'Existing standalone D provider, not completed 17-state cosmological evolution','evidence':{}}
for name in ['rust_native_build.log','rust_native_build_repaired.log','rust_deuterium_test.log','rust_deuterium_integration_test.log']:
 p=N/name
 if p.exists():rust['evidence'][name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
assert '8 passed; 0 failed' in (N/'rust_deuterium_integration_test.log').read_text()
(R/'results/NCP_RUST_VERIFICATION.json').write_text(json.dumps(rust,indent=2)+'\n')
base=(R/'REPORT_EN.md').read_text().split('\n# Numerical appendix: actual NCP snapshot')[0]
base=base.replace('A further Q calculation tests the remaining basis sensitivity.','The retained Q-space calculation gives 0.7086682802. Its T-to-Q change still exceeds the selected probability target; the numerical appendix records the overlap truncation.')
base=base.replace('The aug-DZ result is about 1.11126, substantially below three.','The aug-DZ and aug-TZ results are about 1.11126 and 1.65647, respectively, both substantially below three.')
ap=['\n# Numerical appendix: actual NCP snapshot\n','These tables are generated from actual saved receipts. Counts refer to attempts, including diagnostic repeats and preserved failures, rather than distinct physical systems. A successful finite-model calculation does not establish complete-basis convergence.\n','| Run | Receipts | Accepted solves | Other attempts |\n|:--|--:|--:|--:|']
for k,v in counts.items():ap.append(f"| {k.replace('_',' ')} | {v['receipts']} | {v['passed']} | {v['not_accepted']} |")
ap+=['\n## Atomic energies\n','| Case | Energy (Hartree) | Residual (Hartree) |\n|:--|--:|--:|']
for r in rows:
 if r['kind']=='atomic' and r['finite_model_numerics_passed']:ap.append(f"| {r['case'].replace('_',' ')} | {r['E_electronic_Eh']:.12f} | {r['residual_max_Eh']:.3g} |")
ap += [f'\nThe matched core-valence T and Q ionization energies are {IT:.12f} and {IQ:.12f} Hartree. The change, {abs(IQ-IT):.9g} Hartree, exceeds the frozen $10^{{-4}}$ Hartree criterion. The bound-state basis target remains unmet.\n','## Shared-space daughter projections\n','| Case | Ground probability | AO / retained rank |\n|:--|--:|--:|']
for r in rows:
 if 'union' in r['case'] and r['finite_model_numerics_passed']:ap.append(f"| {r['case'].replace('_',' ')} | {r['P_ground']:.12f} | {r['ao_rank']} / {r['retained_rank']} |")
ap += [r'''
The untruncated He+Li aug-Q union had 126 retained directions and failed the orbital-metric and original-H residual gates. The bounded repair used relative overlap cutoffs $10^{-7}$ and $10^{-6}$ and eigensolver tolerance $10^{-13}$. Both cutoffs retained the same 124-dimensional space from 126 AOs. Both gave $P_0=0.7086682802176386$, parent energy $-2.90273212428737\,E_h$, and daughter energy $-7.27709543375322\,E_h$. Their largest metric defect was $6.58\times10^{-11}$ and largest residual $8.91\times10^{-12}\,E_h$.

Identical probabilities show reproducibility in the same retained space. They do not establish convergence to the discarded two directions. The T-to-Q probability change is $2.72459345\times10^{-4}$, above the selected $10^{-4}$ criterion. The failed 126-direction attempts remain archived separately.

## Projected response

| Basis | TRK diagnostic | Largest 64-to-128 difference | Wall time (s) |
|:--|--:|--:|--:|
''']
for p,j in full:
 if p.parent.parent.name=='response_v4' and j.get('finite_model_numerics_passed'):
  d=max(x['L64_L128_relative_L1'] for x in j['response_krylov_convergence'])
  ap.append(f"| {j['case']['basis']} | {j['TRK_diagnostic']:.12f} | {d:.3g} | {j['wall_s']:.3f} |")
ap += [r'''
The internal Krylov criterion is satisfied at the declared broadenings. The TRK deficit and missing outgoing-wave provider prevent physical continuum closure.

## Rust execution on NCP

The NCP installation reports \texttt{rustc 1.99.0 (b940084d7 2026-09-28)} and \texttt{cargo 1.99.0 (5f94df478 2026-08-27)}. We staged the native microphysics crate and its compile-time contract inputs from the same pinned PR150 commit. The locked, offline library check succeeded. The explicit \texttt{deuterium\_atomic} integration-test target ran eight tests: all eight passed.

An earlier library-only test filter selected zero tests and is retained in the logs but is not counted. Initial incomplete staging omitted compile-time contract files; staging them from the same commit resolved the build failure. No scientific implementation was changed for the build.

This establishes the native Rust toolchain and verifies the existing standalone D provider on the target host. It does not activate the 17-state solver. A next native implementation can consume the versioned microscopic tables through the existing isotope, charge and energy conventions, while expensive wavefunction construction remains a separately validated producer.

## Acceptance and continuation

The independent reviews and machine-readable convergence records accompany this report. All eight programme completion flags remain open for the physical reasons stated in the main text. This iteration supplies new finite-model calculations, executable source code, raw states, and explicit next dependencies.
''']
three=[r for r in rows if r['run']=='threeelectron_v6']
if three:
 r=three[0];ap += ['\nThe large three-electron Li+Be aug-TZ attempt ended with status '+str(r['status'])+'. '+(f"Its accepted ground projection is {r['P_ground']:.12f}. " if r['finite_model_numerics_passed'] else 'It is not promoted to an accepted projection. ')+'See its preserved receipt for residual, spin and resource evidence.\n']
else:ap+=['\nAt this snapshot, the large three-electron Li+Be aug-TZ attempt is still running under frozen wall-time and memory limits. Completed DZ/aug-DZ projections and the independently completed 84-orbital Li core-Q solve remain available. No result for the running attempt is inferred.\n']
(R/'REPORT_EN.md').write_text((base+'\n'.join(ap)).replace('|:--|--:|--:|--:|\n\n|','|:--|--:|--:|--:|\n|'))
rm=(R/'README.md').read_text().split('\n## Unit2 snapshot')[0]
rm+=f"\n## Unit2 snapshot\n\n{len(rows)} archived solver receipts; {sum(bool(r['finite_model_numerics_passed']) for r in rows)} accepted finite-model calculations. See [English report](REPORT_EN.pdf), [LaTeX source](REPORT_EN.tex), [execution index](results/EXECUTION_INDEX.csv), and [convergence status](results/CONVERGENCE_STATUS.json).\n\nCore-valence Li ionization I_Q={IQ:.12f} Eh; T-to-Q change={abs(IQ-IT):.8g} Eh exceeds the target. He/Li retained Q-space projection P={PQ:.12f}; its basis target remains unmet. NCP Rust1.99 locked offline crate check and8 deuterium integration tests passed. The report records the current large3e run status. All8 physical closure conditions remain open.\n"
(R/'README.md').write_text(rm)
subprocess.run(['pandoc','REPORT_EN.md','--from=markdown+tex_math_single_backslash','--standalone','--include-in-header=report_header.tex','-o','REPORT_EN.tex'],cwd=R,check=True,capture_output=True)
for _ in range(2):
 t=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','REPORT_EN.tex'],cwd=R,capture_output=True,text=True)
 (R/'REPORT_BUILD.log').write_text(t.stdout+t.stderr)
 if t.returncode:raise RuntimeError(t.stdout[-4000:])
out=R/'pdf_preview';out.mkdir(exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','1200','-png',str(R/'REPORT_EN.pdf'),str(out/'page')],check=True,capture_output=True)
from PIL import Image,ImageDraw
images=[Image.open(p).convert('RGB') for p in sorted(out.glob('page-*.png'))]
contact=Image.new('RGB',(1320,630*((len(images)+2)//3)),'white')
for i,im in enumerate(images):
 im.thumbnail((420,600));tile=Image.new('RGB',(440,630),'#dddddd');tile.paste(im,((440-im.width)//2,25));ImageDraw.Draw(tile).text((12,6),f'Page {i+1}',fill='black');contact.paste(tile,((i%3)*440,(i//3)*630))
contact.save(out/'contact.jpg',quality=92)
print(json.dumps({'receipts':len(rows),'passed':sum(bool(r['finite_model_numerics_passed']) for r in rows),'threeelectron_finished':bool(three),'pages':len(images),'pdf_bytes':(R/'REPORT_EN.pdf').stat().st_size,'counts':counts,'convergence':conv},indent=2))
