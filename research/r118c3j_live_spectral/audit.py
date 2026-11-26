"""Independent half-stage inventory, source identity and dispersion audit."""
from pathlib import Path
import numpy as np,json,hashlib,gzip
from plasma import cutoff,dos
D=Path(__file__).resolve().parent
Y=.08130135170951483
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 rows={}
 for p in sorted(D.glob('live*')):
  if not p.is_dir() or not (p/'RETURN.txt').exists():continue
  a=np.genfromtxt(p/'half.csv',names=True,delimiter=',');mode=int(dict(l.split('=',1) for l in (p/'RETURN.txt').read_text().splitlines())['mode'])
  d=lambda k:np.diff(a[k])
  f=np.stack([a[k] for k in ['xHII','xHeII','xHeIII']],axis=1)
  ev=np.stack([d('photo_'+k)+d('CI_'+k)-d('RR_'+k) for k in ['H','HeI','HeII']],axis=1)
  ev[:,1]-=d('DR');chem=np.c_[ev[:,0],(ev[:,1]-ev[:,2])/Y,ev[:,2]/Y]
  err=float(np.max(abs(np.diff(f,axis=0)-chem)))
  assert err<1e-9
  o=dict(outer=int(a['outer'][-1]),half_rows=len(a)-1,mode=mode,terminal_T=float(a['T'][-1]),terminal_f=f[-1].tolist(),max_species_residual=err,max_native_residual=float(np.max(abs(a['residual']))),half_sha=sha(p/'half.csv'))
  if mode==3:
   q=d('FF_birth')-d('cmb_input');r=a['a'][:-1]/a['a'][1:]
   work=(1-r)*a['spec'][:-1]+(1-np.sqrt(r))*q
   res=d('spec')+work-q
   assert max(abs(res))<1e-14
   N=a['thermal']+a['binding']+a['primary']+a['spec']+a['escaped']-a['FF_birth']+a['thermal_work']+a['photon_work']+a['boundary_u']-a['source_u']+np.r_[0,np.cumsum(work)]
   total=N-N[0];assert max(abs(total))<1e-8
   sp=np.genfromtxt(p/'spectrum.csv',names=True,delimiter=',');x=sp['x'];dl=np.log(x[1]/x[0]);xp=cutoff(a['ne'][-1],2.7255/a['a'][-1]);fctr=dos(x,xp);assert min(x)>xp
   stock=x**3*dl*sp['delta'];power=x*stock
   o.update(max_spectral_residual=float(max(abs(res))),max_total_residual=float(max(abs(total))),terminal_spec=float(a['spec'][-1]),spec_sha=sha(p/'spectrum.csv'),plasma_xp=float(xp),min_dos=float(fctr.min()),signed_number_vacuum=float(stock.sum()),signed_number_dispersion_diagnostic=float((stock*fctr).sum()),signed_energy_relative_dos_change=float((power*fctr).sum()/power.sum()-1))
  rows[p.name]=o
 o=dict(rows=rows,scope='fixed-geometry native live chemical candidate; dispersion DOS diagnostic on vacuum solution only, not dispersive collision solver')
 (D/'AUDIT.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
