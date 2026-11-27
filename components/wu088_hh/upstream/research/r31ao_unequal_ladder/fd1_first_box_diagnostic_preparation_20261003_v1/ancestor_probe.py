from support import *
from observe import observation
inside=observation();outside=c.load(E/'ANCESTOR_PROBE_OUTSIDE.json');rows=[]
for row in outside['ancestors']:
 p=R/'host_cgroup_view'/Path(row['path']).relative_to('/sys/fs/cgroup')
 if row['path']=='/sys/fs/cgroup':continue
 rows.append(dict(path=str(p),memory_max=(p/'memory.max').read_text().strip(),memory_current=(p/'memory.current').read_text().strip(),cpu_max=(p/'cpu.max').read_text().strip()))
unit=subprocess.check_output(['systemctl','--user','show','wu088-fd1-ancestor-probe-v2.service','--property=RuntimeMaxUSec','--value'],text=True).strip()
assert unit=='1min' and rows[0]['memory_max']=='34359738368' and rows[0]['cpu_max']=='400000 100000'
write(E/'ANCESTOR_READABILITY_PROBE.json',dict(status='PASS',actual_ancestor_paths=rows,inside=inside,unit_runtime_max=unit,HH_evaluations=0,integrations=0,source='Actual metadata; no resource fixtures or injected values'))
print('Actual ancestor read and 60-second unit wall policy PASS; HH=0, integrations=0')
