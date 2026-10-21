"""Descriptive memory measurements with a small C parent; separate from speed pairs."""
import experiment as e
import json
helper=e.W/'wait4_probe'
e.run('memory_helper_build',['cc','-O2','-std=c11','-o',helper,e.W/'wait4_probe.c'],30)
identity={'source_sha256':e.sha(e.W/'wait4_probe.c'),'helper_binary_sha256':e.sha(helper),'candidate_binary_sha256':e.sha(e.CAND),'cpu':e.CPU}
(e.E/'MEMORY_HELPER_IDENTITY.json').write_text(json.dumps(identity,indent=2))
rows=[]
for index,variant in enumerate(['legacy','cell-cache','cell-cache','legacy']):
 name=f'memory_c_{index}_{variant}';d=e.E/name
 e.run(name,[helper,d/'rusage.json','taskset','-c',str(e.CPU),e.CAND,d/'raw.json','fixed','radau','16','--native-eval',variant],30)
 row=json.loads((d/'rusage.json').read_text());row.update(index=index,variant=variant,**identity);rows.append(row)
# Compare only after all child helpers finish. Python never forks scientific children.
for row in rows:
 d=e.E/f"memory_c_{row['index']}_{row['variant']}"
 issues=e.compare(json.loads((e.E/'baseline_fixed/raw.json').read_text()),json.loads((d/'raw.json').read_text()))
 (d/'comparison.json').write_text(json.dumps(issues));assert not issues
(e.E/'MEMORY_C_SUMMARY.json').write_text(json.dumps({'observations':rows,'scope':'descriptive four observations; no memory-reduction claim'},indent=2))
