"""Create a symlink-only view of the first and collision-safe continuation runs."""
import csv, sys
from pathlib import Path

root=Path(sys.argv[1])
view=root/'combined'
view.mkdir(exist_ok=False)
records=[]
for folder in ('first','resume'):
    source=root/folder
    for row in csv.DictReader((source/'exits.csv').open()):
        case_id='_'.join(row[k] for k in ('mode','case','steps'))
        link=view/case_id
        if link.exists() or link.is_symlink(): raise RuntimeError(f'duplicate completed case {case_id}')
        link.symlink_to((source/case_id).resolve(),target_is_directory=True)
        records.append(row)
with (view/'exits.csv').open('x',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=('mode','case','steps','exit_code'))
    writer.writeheader();writer.writerows(records)
print({'runs':len(records),'failures':[r for r in records if r['exit_code']!='0']})
