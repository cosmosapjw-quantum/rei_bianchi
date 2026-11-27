"""Independent saved-array audit of native birth replay, local weak collision, and PR scope."""
import json,numpy as np
from pathlib import Path
from replay import Owner,ray,KT0,T
D=Path(__file__).resolve().parent
def table(p):return np.genfromtxt(p/'history.csv',names=True,delimiter=',')
def run():
 out={};labs=['512','1024','512_fine','1024_72ray'];rr={}
 for l in labs:
  j=json.loads((D/f'replay_{l}.json').read_text());z=np.load(D/f'replay_{l}.npz');p=D/('birth_'+l.replace('_72ray','')+'_32ray');h=table(p);a=z['rows'];assert j['blocked'] is None and j['accepted_half_steps']==2*(len(h)-1) and np.array_equal(a[:,0],h['a'][1:])
  assert max(abs(a[:,2]+a[:,3]-a[:,4]))<1e-13 and j['max_birth_N_relative']<1e-12 and j['max_birth_U_relative']<1e-12
  o=Owner(z['edges'],z['n'],z['w0']);d,n,w,er=ray(z['F'],z['n'],z['w0'])
  assert o.admit(z['N'],z['V'])>0 and np.max(abs(d-z['d']))<1e-14
  U=(z['V']+z['N']*o.c)*d[:,None]*z['cap']*KT0/h['a'][-1];N=float(np.sum(z['N'])*z['cap']);P=(n.T*np.sum(U,axis=1))@n;Pi=P-np.eye(3)*np.trace(P)/3
  assert abs(N-j['terminal_signed_N'])<1e-18 and abs(float(U.sum())-j['terminal_signed_U'])<1e-18
  rr[l]=dict(**j,native_accepted=int(h['accepted'][-1]),native_rejected=int(h['rejected'][-1]),native_metric=float(max(h['metric'])),native_ledger=float(max(abs(h['ledger']))),terminal_native_U=float(h['spec'][-1]),difference_replay_native_U=float(U.sum()-h['spec'][-1]),max_path_ledger=float(max(abs(a[:,2]+a[:,3]-a[:,4]))),terminal_Pi=np.asarray(Pi,float).tolist())
 out['replays']=rr
 # independently compute vector stress differences, not just norms.
 rows={}
 for lab,p,nm in [('129','1024',32),('258','1024',32),('129_72ray','1024_72ray',72)]:
  z=np.load(D/f'collision_{lab}.npz');r=np.load(D/f'replay_{p}.npz');d,n,w,er=ray(r['F'],r['n'],r['w0']);q=(z['edges'][1:]+z['edges'][:-1])/2;N=z['fine_dN'];V=z['fine_dV'];U=(V+q*N)*d[:,None];P=(n.T*np.sum(U,axis=1))@n;P=np.asarray(P-np.eye(3)*np.trace(P)/3,float)
  nr=float(abs(N.sum())/np.sum(abs(N)));ur=float(abs(U.sum())/np.sum(abs(U)));assert max(nr,ur)<1e-10
  rows[lab]=dict(N_res=nr,U_res=ur,Pi=P.tolist(),Pi_norm=float(np.linalg.norm(P)),rays=nm)
 out['collision']=rows
 a,b,c=[np.array(rows[k]['Pi']) for k in ['129','258','129_72ray']]
 rel=lambda a,b:float(np.linalg.norm(a-b)/np.linalg.norm(b))
 out.update(frequency_Pi_relative=rel(a,b),angular_Pi_relative=rel(a,c),time_replay_N_relative=abs(rr['512']['terminal_signed_N']-rr['512_fine']['terminal_signed_N'])/abs(rr['512_fine']['terminal_signed_N']),time_replay_U_relative=abs(rr['512']['terminal_signed_U']-rr['512_fine']['terminal_signed_U'])/abs(rr['512_fine']['terminal_signed_U']),frequency_replay_U_relative=abs(rr['512']['terminal_signed_U']-rr['1024']['terminal_signed_U'])/abs(rr['1024']['terminal_signed_U']),xmax_eV=float(np.genfromtxt(D/'birth_1024_32ray/spectrum.csv',names=True,delimiter=',')['x'][-1]*KT0/table(D/'birth_1024_32ray')['a'][-1]))
 assert out['xmax_eV']<13.6
 out['scope']='actual native instrumented elastic birth/coframe paths, positive canonical signed reconstruction replay (no angular collision live feedback), local 32/72-ray direct weak projection, independent source owner; no native full live or UV photoionization admission'
 (D/'AUDIT.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':run()
