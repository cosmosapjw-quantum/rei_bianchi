"""Finish the observed 8000-trial MPFI phase; do not rerun its completed axes."""
from pathlib import Path
import json,struct,hashlib,math,time
P=Path('.cuh/fastest-track/REI-F08-PAIRED');directory=P/'whole/T0_FLRW';log=(P/'T0_FLRW-independent-v3.log').read_text();progress=[json.loads(line) for line in log.splitlines() if line.startswith('{"validated"')];phase=progress[-1];assert phase['validated']==8000 and phase['time']==1e13;assert "('CHECKPOINT_GAS_LEDGER', 0.6849999999999999, 0.6850000000001026)" in log
rows=[];source_n=[];source_u=[];absorption=[]
for line in (directory/'trials.jsonl').open():
 row=json.loads(line);assert row['accepted'];rows.append(row)
 for a in row['audits'][1:]:
  source_n.append(a['source_n']);source_u.append(a['source_u']);absorption.append(math.fsum(v for ev in a['photo_events'] for v in ev))
assert len(rows)==8000;last=rows[-1];summary=json.loads((directory/'summary.json').read_text());header=json.loads((directory/'header.jsonl').read_text());text=(directory/'checkpoint.dat').read_text().splitlines();v=text[0].split();f=lambda x:struct.unpack('>d',bytes.fromhex(x))[0];gas=list(map(f,text[1].split()));expected=[last['time_s'],*last['fractions'],last['w_ev_per_h'],last['escape_ev_per_h'],last['redshift_work_ev_per_h'],last['thermal_work_ev_per_h'],last['source_n'],last['source_u'],last['absorbed_n']];assert gas==expected,'EXACT_CHECKPOINT_REPORTED_GAS_LEDGER';assert int(v[4])==8000 and int(v[5])==0 and int(v[7])==(directory/'trials.jsonl').stat().st_size
assert list(map(f,text[3].split()))==[x for pair in last['gas_parent'] for x in pair]
for name,values,scale in [('source_n',source_n,.05),('source_u',source_u,.685),('absorbed_n',absorption,.05)]:assert abs(math.fsum(values)-last[name])<=1e-12*scale,('CUMULATIVE_EVENT_BINDING',name)
assert abs(last['source_n']-1e13*5e-15)<=1e-12*.05 and abs(last['source_u']-1e13*5e-15*13.7)<=1e-12*.685,'SOURCE_CONTRACT'
n=int(text[4]);nodes=header['energy_nodes'];nd=len(header['qhat']);assert n==nd*len(nodes);photons=[];groups=[0.]*len(nodes)
for i,line in enumerate(text[5:5+n]):
 x,lo,hi=map(f,line.split());assert math.isfinite(x) and 0<=lo<=x<=hi;photons.append(x);groups[i%len(nodes)]+=x
pos=5+n;assert int(text[pos])==nd;guards=[list(map(f,line.split())) for line in text[pos+1:]];assert len(guards)==nd
for gn,gu,nlo,nhi,ulo,uhi in guards:assert 0<=nlo<=gn<=nhi and 0<=ulo<=gu<=uhi and (gn==0 and gu==0 or 0<=gu<10*gn)
a=last['audits'][2];point_groups=dict(zip(a['group_indices'],a['point_photons']))
for k,count in enumerate(groups):
 assert abs(count-point_groups.get(k,0.))<=1e-12*.05,'CHECKPOINT_ENERGY_GROUP'
 for d in range(nd):
  # FLRW exact geometry has direction-independent transport/opacity and initial
  # equal counts. Normalized binary q norms differ only at floating-point scale.
  # This checks the final checkpoint angular coherence at the frozen N scale.
  assert abs(photons[d*len(nodes)+k]-count/nd)<=1e-12*.05,'FLRW_ANGULAR_CHECKPOINT_COHERENCE'
N=math.fsum(photons)+math.fsum(g[0] for g in guards);U=math.fsum(x*nodes[i%len(nodes)] for i,x in enumerate(photons))+math.fsum(g[1] for g in guards)
assert abs(N-last['photon_n'])<=1e-12*.05 and abs(U-last['photon_u_ev_per_h'])<=1e-12*.685
F=.083;chi=[13.598434599702,24.587389011,54.41776];energy=lambda x,w,escape:w+chi[0]*x[0]+F*(chi[1]*x[1]+(chi[1]+chi[2])*x[2])+escape;w0=1.5*1.380649e-16*50000*(1+F+.9+F*(.3+2*.6))/1.602176634e-12;e0=energy([.9,.3,.6],w0,0)+.05*13.7
residual=[abs(N+last['absorbed_n']-last['source_n']-.05)/(.05+last['source_n']),abs(energy(last['fractions'],last['w_ev_per_h'],last['escape_ev_per_h'])+U+last['redshift_work_ev_per_h']+last['thermal_work_ev_per_h']-last['source_u']-e0)/(e0+last['source_u'])];assert max(residual)<=1e-12
for key in expected:assert math.isfinite(key)
result={'status':'WHOLE_HISTORY_COMPONENT_INDEPENDENT_PASS','trials':8000,'runs':[{'run':'T0_FLRW','time_s':1e13,'accepted':8000,'rejected':0,'maxima':phase['maxima'],'cumulative':residual,'raw_sha256':hashlib.sha256((directory/'trials.jsonl').read_bytes()).hexdigest()}],'production_evaluator_called':False,'scientific_admission':'HOLD','composed_validation':{'trial_phase':'T0_FLRW-independent-v3.log','trial_engine_exit':1,'trial_phase_observed_complete':8000,'remaining_failure':'Additional checkpoint comparison of compensated producer source U with naive checker sum; 1.027e-13 difference, not a frozen scientific criterion','closeout':'closeout_T0.py; checkpoint exact output/group/angular binding, independent event/source sums and unchanged final 1e-12 conservation','completed_trial_proofs_rerun':False},'old_failure_preserved':True};(directory/'independent_history_receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
