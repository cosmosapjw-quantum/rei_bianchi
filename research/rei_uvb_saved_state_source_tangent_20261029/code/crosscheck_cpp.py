"""Generate source-locked standalone C++ direct-event comparison without an IVP."""
import sys, subprocess, math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
UNIT=HERE.parent
sys.path.insert(0,str(HERE))
import source17 as s

port,d,p,rows,geo=s.load_parent()
saved=s.saved_rows()
lines=[]
for r in saved:
    z=r['z'];y=np.array(r['y']);mm=port.rate_response(z,geo['a0'],rows)['moments']
    lines.append(' '.join(format(float(x),'.17g') for x in [z,*y,*mm]))
(UNIT/'results/CPP_INPUT.tsv').write_text('\n'.join(lines)+'\n')
exe=UNIT/'results/source17_cpp_reference'
proc=subprocess.run(['g++','-std=c++20','-O2','-Wall','-Wextra','-Werror',str(HERE/'source17_reference.cpp'),'-o',str(exe)],capture_output=True,text=True)
(UNIT/'results/CPP_BUILD_STDOUT.txt').write_text(proc.stdout)
(UNIT/'results/CPP_BUILD_STDERR.txt').write_text(proc.stderr)
if proc.returncode:raise RuntimeError('CPP_BUILD_FAILED '+proc.stderr)
res=subprocess.run([str(exe)],input='\n'.join(lines)+'\n',capture_output=True,text=True)
(UNIT/'results/CPP_REFERENCE_STDOUT.tsv').write_text(res.stdout)
(UNIT/'results/CPP_REFERENCE_STDERR.txt').write_text(res.stderr)
if res.returncode:raise RuntimeError('CPP_REFERENCE_FAILED '+res.stderr)
assert len(res.stdout.splitlines())==len(saved)
max_rel=0.
for row,raw in zip(saved,res.stdout.splitlines()):
    z=row['z']; y=np.array(row['y']);o=s.source17(z,y,geo['a0'],rows,port)
    got=np.array([float(x) for x in raw.split()]);
    want=np.array([z,o['electron_rate_per_Href_s'],o['photoheat_eV_per_Href_s'],*o['electron_jac'],*o['F']]);
    assert len(got)==len(want)==22
    for a,b in zip(got,want):
        err=abs(a-b)/max(abs(b),1e-29)
        max_rel=max(max_rel,err)
        if err>5e-13:raise AssertionError(f'CPP_MISMATCH z={z}, got={a}, expected={b}, rel={err}')
print(f'CPP_PASS rows={len(saved)} max_component_scaled_relative={max_rel:.3e} compiler=g++ c++20 -O2 -Wall -Wextra -Werror')
