"""Affected numerical guard: unit-conversion order at tiny cross section."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import mpmath as mp
from maxwellian_moments import PreparedMaxwellianMoments

parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
out=Path(args.output)
if out.exists():raise FileExistsError(out)
mp.mp.dps=80
t=2000.;lo=1.;hi=1.001
kernel=PreparedMaxwellianMoments([lo,hi],[1e-300,1e-300],lo,'manufactured tiny-sigma conditional mean')
got=float(kernel.evaluate(t).conditional_mean_energy_J[0])
ev=mp.mpf('1.602176634e-19');theta=mp.mpf('1.380649e-23')*t/ev
expected=float(ev*theta*mp.gammainc(3,mp.mpf(lo)/theta,mp.mpf(hi)/theta)/mp.gammainc(2,mp.mpf(lo)/theta,mp.mpf(hi)/theta))
relative=abs(got/expected-1.)
passed=relative<2e-9
record=dict(schema='he36.affected_extreme_mean.v1',status='PASS' if passed else 'FAIL',
  code_sha256=hashlib.sha256((Path(__file__).parent/'maxwellian_moments.py').read_bytes()).hexdigest(),
  check_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  temperature_K=t,finite_band_eV=[lo,hi],sigma_m2=1e-300,
  numerical_fixture_only=True,mean_J=got,independent80decimal_mean_J=expected,
  relative=relative,gate_relative=2e-9,new_IVP=0,CCC_replay=0)
temporary=out.with_name(out.name+'.tmp')
with temporary.open('x') as f:json.dump(record,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
os.link(temporary,out);temporary.unlink()
print(json.dumps(record));sys.exit(0 if passed else 1)
