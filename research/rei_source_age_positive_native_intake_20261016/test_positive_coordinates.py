"""Targeted transform/scaling tests using the unchanged native preparation."""
import json,subprocess,sys
from pathlib import Path
import numpy as np
binary=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
p=subprocess.Popen([str(binary),'server','0'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1);setup=json.loads(p.stdout.readline());c=setup['cells'];extra=4+16*c;size=extra+setup['extra']
def send(mode,active,x,z):
 p.stdin.write(f'{mode} {active} {x:.17e} '+' '.join(format(v,'.17e') for v in z)+'\n');p.stdin.flush();line=p.stdout.readline().strip();assert not line.startswith('ERR'),line;return line
z=np.zeros(size);z[:4]=setup['initial'];first=4;z[first:first+2*c]=setup['encoded_births'][0];x=setup['births'][0]
physical=json.loads(send('P',1,x,z));actual=np.array(physical['flat'][4:4+2*c]);expected=np.array(setup['physical_births'][0]);mask=expected>0
recovery=np.max(np.abs(actual[mask]/expected[mask]-1));assert recovery<2e-12,recovery
base=np.fromstring(send('R',1,x,z),sep=' ');indices=np.array(setup['active_indices'][0]);momerr=[];eventerr=[]
for shift in [-100.,-400.]:
 shifted=z.copy();shifted[indices]+=shift;r=np.fromstring(send('R',1,x,shifted),sep=' ')
 positive=np.abs(base[indices])>0
 momerr.append(float(np.max(np.abs(r[indices][positive]/base[indices][positive]-1))))
 expected_events=base[extra+4:extra+7]*np.exp(shift);valid=expected_events>0
 eventerr.append(float(np.max(np.abs(r[extra+4:extra+7][valid]/expected_events[valid]-1))))
assert max(momerr)<2e-10,momerr
assert max(eventerr)<2e-10,eventerr
# Empty and future lanes are exact zero derivatives even when their unused
# coordinate storage contains huge numbers; they are not ODE variables.
inactive=np.setdiff1d(np.arange(4,extra),indices);garbage=z.copy();garbage[inactive]=10000.;r=np.fromstring(send('R',1,x,garbage),sep=' ');assert np.array_equal(r[inactive],np.zeros(inactive.size));assert np.array_equal(r,base)
# Replay the original q0 subnormal moment-fit failure through normalized shape.
old=np.load(out.parent/'q0/first_failed_state_event2_retry0.npy');r=np.fromstring(send('R',2,float(old[0]),old[1:]),sep=' ');assert r.size==size and np.isfinite(r).all()
result=dict(birth_physical_moment_max_relative_recovery=float(recovery),common_log_amplitude_shift= [-100,-400],log_photon_rhs_max_relative_scaling_error=momerr,photo_events_max_relative_scaling_error=eventerr,structural_zero_and_future_lanes='exact zero and omitted from solve state',first_subnormal_failure_replay='finite normalized unchanged-native RHS')
(out/'tests.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));p.stdin.close();p.wait();assert p.returncode==0
