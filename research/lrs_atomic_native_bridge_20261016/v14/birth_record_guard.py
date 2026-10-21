"""Validate the actual birth clock, not only total source-number bookkeeping."""
import csv, math
from pathlib import Path

MODES=('be_control','common_combined','physical_midpoint','physical_gl2',
       'source_off','source_off_midpoint','source_off_gl2')

def validate_birth_records(path):
    path=Path(path)
    with path.open(newline='') as f: rows=list(csv.DictReader(f))
    if not rows: raise ValueError('empty history')
    limits={}
    for row in rows:
        n=int(row['N']); end=float(row['Xend']); key=(row['mode'],n)
        if n<8 or n>2048 or n&(n-1) or not math.isfinite(end) or end<=0:
            raise ValueError('invalid history grid')
        if key in limits and limits[key]!=end:raise ValueError('changing Xend')
        limits[key]=end
    side=Path(str(path)+'.births.csv')
    if not side.exists():raise ValueError('missing actual birth records')
    c=(1-1/math.sqrt(3))/2
    seen=set();counts={}
    with side.open(newline='') as f:
        for row in csv.DictReader(f):
            if any(v is None or not math.isfinite(float(v)) for k,v in row.items() if k!='mode'):
                raise ValueError('nonfinite birth record')
            mode=row['mode'];n=int(row['N']);step=int(row['step']);idx=int(row['birth'])
            if any(float(row[k])!=int(row[k]) for k in ('N','step','birth')):
                raise ValueError('noninteger birth index')
            key=(mode,n);unique=(mode,n,step,idx)
            if key not in limits:raise ValueError('orphan birth')
            if unique in seen:raise ValueError('duplicate birth index')
            seen.add(unique);counts[key]=counts.get(key,0)+1
            nodes=(() if mode=='source_off' else (c,1-c) if mode in ('physical_gl2','source_off_gl2')
                   else (.5,.5) if mode=='common_combined' else (.5,))
            if not 1<=step<=n or not 0<=idx<len(nodes):raise ValueError('birth index range')
            dx=limits[key]/n;target=(step-1+nodes[idx])*dx
            a=float(row['a']);weight=float(row['weight_dln_a']);dt=float(row['proper_time_weight_s'])
            if a<=0 or weight<=0 or dt<=0:raise ValueError('nonpositive birth clock')
            if abs(math.log(a*21)-target)>2e-14:raise ValueError('birth node mismatch')
            if not math.isclose(weight,dx/len(nodes),rel_tol=2e-12,abs_tol=1e-25):
                raise ValueError('birth quadrature weight')
            if min(float(row['added_N']),float(row['added_U']))<0:raise ValueError('negative source')
            if mode.startswith('source_off') and (float(row['added_N'])!=0 or float(row['added_U'])!=0):
                raise ValueError('disabled source injection')
    for (mode,n),_ in limits.items():
        count=0 if mode=='source_off' else 2 if mode in ('common_combined','physical_gl2','source_off_gl2') else 1
        if counts.get((mode,n),0)!=count*n:raise ValueError('birth record count')

def validate_matrix(path,max_n):
    """Run receipt cannot promote a smaller but complete-looking matrix."""
    with Path(path).open(newline='') as f:actual={(r['mode'],int(r['N'])) for r in csv.DictReader(f)}
    if max_n<8 or max_n>2048 or max_n&(max_n-1):raise ValueError('expected grid')
    expected={(m,2**j) for m in MODES for j in range(3,max_n.bit_length())}
    if actual!=expected:raise ValueError('incomplete requested matrix')
