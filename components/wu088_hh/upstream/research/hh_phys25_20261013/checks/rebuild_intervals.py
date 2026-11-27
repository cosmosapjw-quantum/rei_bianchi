"""Reproduce only the new PHYS25 interval calculations, not predecessor ODEs."""
from pathlib import Path
import sys,json
from mpmath import mp,iv
D=Path(__file__).resolve().parents[1];sys.path.insert(0,str(D/'src'))
import sheldon_model as M
mp.dps=65;iv.dps=50
(a,b),rows,proof=M.partial_rate_monotonic_enclosure(512)
out={'method':'positive bins; certified sigma monotonicity; E1 alternating series with analytic tail','cells':512,'interval_rational':[str(a),str(b)],'monotonicity_certificate':proof,'rows':rows}
# Writes a separate replay result; the adopted evidence is immutable.
(D/'results/PARTIAL_RATE_INTERVAL_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
old=json.loads((D/'results/PARTIAL_RATE_INTERVAL.json').read_text())
from fractions import Fraction as F
# Different original working precision can give tighter replay endpoints.
L,U=map(F,old['interval_rational']);assert L<=a<b<=U or (abs(float(a-L))+abs(float(b-U))<1e-45)
print('REPLAY_PASS',float(a),float(b))
