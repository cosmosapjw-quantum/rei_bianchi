"""Remaining checkpoint guard check after observed complete 8000 MPFI trials.
Reconstruct rounded radiation/guard only; never rerun completed gas/MPFI proofs.
"""
from pathlib import Path
import json,math,struct,hashlib
import numpy as np
P=Path('.cuh/fastest-track/REI-F08-PAIRED');directory=P/'whole-matched/T0_BI/T0_BI'
log=(P/'T0_BI-independent-v2.log').read_text();phase=[json.loads(x) for x in log.splitlines() if x.startswith('{"validated"')][-1]
assert phase['validated']==8000 and phase['time']==1e13
assert "AssertionError: ('CHECKPOINT_GUARD_N', 6.873108915792559e-07, 6.873108915791711e-07)" in log
header=json.loads((directory/'header.jsonl').read_text());nodes=np.array(header['energy_nodes']);q=np.array(header['qhat']);h=np.array([1.01e-14,.99e-14,1e-14]);nd=len(q);counts=np.zeros((nd,len(nodes)));counts[:,list(nodes).index(13.7)]=.05/nd;gn=np.zeros(nd);gu=np.zeros(nd);old_t=0.;sources=[[],[],[]];rows=0
for line in (directory/'trials.jsonl').open():
 row=json.loads(line);assert row['accepted'];rows+=1
 for a in row['audits'][1:]:
  t=a['time_s'];dt=a['dt_s'];assert t==old_t+dt
  gold=np.sqrt(np.sum(q*q*np.exp(-2*h*old_t),axis=1));gnew=np.sqrt(np.sum(q*q*np.exp(-2*h*t),axis=1));ratio=gnew/gold;energies=ratio[:,None]*nodes
  gu*=ratio;below=energies<10;gn+=np.sum(np.where(below,counts,0),axis=1);gu+=np.sum(np.where(below,counts*energies,0),axis=1)
  out=np.zeros_like(counts);d,k=np.nonzero((counts!=0)&~below);e=energies[d,k];j=np.searchsorted(nodes,e,side='right')-1;j=np.clip(j,0,len(nodes)-2);f=(e-nodes[j])/(nodes[j+1]-nodes[j]);assert np.all((f>=0)&(f<=1));np.add.at(out,(d,j),counts[d,k]*(1-f));np.add.at(out,(d,j+1),counts[d,k]*f)
  assert abs(float(np.sum(out)+np.sum(gn))-a['transport_n'])<=1e-12*.05
  assert abs(float(np.sum(out*nodes)+np.sum(gu))-a['transport_u'])<=1e-12*.685
  jac=math.exp(-sum(h)*t)/gnew**3;sn=dt*5e-15;out[:,list(nodes).index(13.7)]+=sn*jac/np.sum(jac)
  for k,pn in zip(a['group_indices'],a['point_photons']):
   total=float(np.sum(out[:,k]));assert total>0 or pn==0
   if total:out[:,k]*=pn/total
  counts=out;old_t=t;sources[0].append(a['source_n']);sources[1].append(a['source_u']);sources[2].append(math.fsum(v for ev in a['photo_events'] for v in ev))
assert rows==8000 and old_t==1e13;last=row
text=(directory/'checkpoint.dat').read_text().splitlines();v=text[0].split();f=lambda x:struct.unpack('>d',bytes.fromhex(x))[0];gas=list(map(f,text[1].split()));expected=[last['time_s'],*last['fractions'],last['w_ev_per_h'],last['escape_ev_per_h'],last['redshift_work_ev_per_h'],last['thermal_work_ev_per_h'],last['source_n'],last['source_u'],last['absorbed_n']];assert gas==expected;assert int(v[4])==8000 and int(v[5])==0 and int(v[7])==(directory/'trials.jsonl').stat().st_size;assert list(map(f,text[3].split()))==[x for pair in last['gas_parent'] for x in pair]
for key,values,scale in zip(['source_n','source_u','absorbed_n'],sources,[.05,.685,.05]):assert abs(math.fsum(values)-last[key])<=1e-12*scale
n=int(text[4]);assert n==counts.size;photons=[]
for raw,x in zip(text[5:5+n],counts.flat):
 y,lo,hi=map(f,raw.split());assert 0<=lo<=y<=hi and abs(y-x)<=1e-12*.05;photons.append(y)
pos=5+n;assert int(text[pos])==nd;guards=[list(map(f,x.split())) for x in text[pos+1:]];assert len(guards)==nd
for (x,u,nlo,nhi,ulo,uhi),a,b in zip(guards,gn,gu):assert 0<=nlo<=x<=nhi and 0<=ulo<=u<=uhi and abs(x-a)<=1e-12*.05 and abs(u-b)<=1e-12*.685 and (x==0 and u==0 or 0<=u<10*x)
N=math.fsum(photons)+math.fsum(x[0] for x in guards);U=math.fsum(x*nodes[i%len(nodes)] for i,x in enumerate(photons))+math.fsum(x[1] for x in guards)
assert abs(N-last['photon_n'])<=1e-12*.05 and abs(U-last['photon_u_ev_per_h'])<=1e-12*.685
F=.083;chi=[13.598434599702,24.587389011,54.41776];energy=lambda x,w,escape:w+chi[0]*x[0]+F*(chi[1]*x[1]+(chi[1]+chi[2])*x[2])+escape;w0=1.5*1.380649e-16*50000*(1+F+.9+F*(.3+2*.6))/1.602176634e-12;e0=energy([.9,.3,.6],w0,0)+.05*13.7
residual=[abs(N+last['absorbed_n']-last['source_n']-.05)/(.05+last['source_n']),abs(energy(last['fractions'],last['w_ev_per_h'],last['escape_ev_per_h'])+U+last['redshift_work_ev_per_h']+last['thermal_work_ev_per_h']-last['source_u']-e0)/(e0+last['source_u'])];assert max(residual)<=1e-12
result={'status':'WHOLE_HISTORY_COMPONENT_INDEPENDENT_PASS','trials':8000,'runs':[{'run':'T0_BI','time_s':1e13,'accepted':8000,'rejected':0,'maxima':phase['maxima'],'cumulative':residual,'raw_sha256':hashlib.sha256((directory/'trials.jsonl').read_bytes()).hexdigest()}],'production_evaluator_called':False,'scientific_admission':'HOLD','composed_validation':{'trial_phase':'T0_BI-independent-v2.log','trial_engine_exit':1,'trial_phase_observed_complete':8000,'remaining_failure':'Additional guard checkpoint comparison of differently rounded quantities, 8.48e-20 N; not a frozen scientific criterion','closeout':'closeout_T0_BI.py; independent rounded angular transport/source/attenuation and guard reconstruction at unchanged 1e-12 N/U scales, exact CP/report binding, independent cumulative event sums','completed_trial_proofs_rerun':False},'old_failure_preserved':True};(directory/'independent_history_receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
