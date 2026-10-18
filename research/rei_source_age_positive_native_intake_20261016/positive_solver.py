"""Positive coordinates; independent SciPy DOP853, unchanged native physics.
Structural empty/future cells are excluded from every solve_ivp state vector.
"""
import argparse,json,subprocess,time,resource
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
p=argparse.ArgumentParser();p.add_argument('binary',type=Path);p.add_argument('out',type=Path);p.add_argument('--q',type=float,default=0.);p.add_argument('--tight',action='store_true');p.add_argument('--old-regression',type=Path);p.add_argument('--birth-panels',type=int,default=8);p.add_argument('--n-mu',type=int,default=8);p.add_argument('--source-subdivisions',type=int,default=8);p.add_argument('--transport-cells',type=int,default=16);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen([str(a.binary),'server',str(a.q),str(a.birth_panels),str(a.n_mu),str(a.source_subdivisions),str(a.transport_cells)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
setup=json.loads(server.stdout.readline());(a.out/'setup.json').write_text(json.dumps(setup)+'\n')
started=time.monotonic();calls=0;errors=[]
observations=[]
common_x=[setup['x0']+(setup['x1']-setup['x0'])*(i+.5)/8 for i in range(8)]+[setup['x1']]
class DomainError(RuntimeError):pass
def send(mode,active,x,y):
    server.stdin.write(f'{mode} {active} {x:.17e} '+' '.join(format(v,'.17e') for v in y)+'\n');server.stdin.flush()
    line=server.stdout.readline()
    if not line:raise RuntimeError(server.stderr.read())
    return line.strip()
if a.old_regression:
    old=np.load(a.old_regression);reply=send('OLD',8,float(old[0]),old[1:]);assert reply.startswith('ERR'),reply
    (a.out/'original_negative_RK_regression.json').write_text(json.dumps(dict(reply=reply,min_state=float(old[5:].min()),scope='unchanged raw original call291 native positive-state guard'))+'\n')
cells=setup['cells'];size=4+2*len(setup['births'])*cells+setup['extra'];extra_start=size-setup['extra'];y=np.zeros(size);y[:4]=setup['initial'];active=0;start=setup['x0'];interval_records=[];status='ERROR';failure=None
try:
    for event,stop in enumerate([*setup['births'],setup['x1']]):
        indices=np.array([*range(4),*[k for group in setup['active_indices'][:active] for k in group],*range(extra_start,size)],dtype=int)
        base=y.copy();initial=y[indices].copy();max_step=np.inf
        for retry in range(13):
            def rhs(x,z):
                global calls
                calls+=1
                if calls>200000 or time.monotonic()-started>600:raise RuntimeError('frozen RHS/time cap')
                whole=base.copy();whole[indices]=z
                answer=send('R',active,x,whole)
                if answer.startswith('ERR'):
                    np.save(a.out/f'first_failed_state_event{event}_retry{retry}.npy',np.r_[x,whole])
                    errors.append(dict(event=event,retry=retry,x=x,message=answer,calls=calls))
                    (a.out/'provider_errors.json').write_text(json.dumps(errors,indent=2)+'\n')
                    raise DomainError(answer)
                result=np.fromstring(answer,sep=' ');assert result.size==size,result.size
                return result[indices]
            try:
                atol=np.full(size,1e-12 if a.tight else 1e-11)
                atol[extra_start:extra_start+4]=1e-15 if a.tight else 1e-14
                atol[extra_start+4:]=1e-17 if a.tight else 1e-16
                sol=solve_ivp(rhs,(start,stop),initial,method='DOP853',rtol=2e-11 if a.tight else 2e-10,atol=atol[indices],max_step=max_step,dense_output=True)
                if not sol.success:raise RuntimeError(sol.message)
                y=base.copy();y[indices]=sol.y[:,-1];break
            except DomainError as error:
                # Rejection restores exact same interval input. Coordinate
                # underflow/unsupported boundary is a typed scientific HOLD.
                if 'underflow' in str(error) or 'MOMENT_FIT' in str(error):raise
                if retry==12:raise
                max_step=(stop-start)/2**(retry+2)
        for ox in common_x:
            if ox>start and ox<=stop:
                observed=base.copy();observed[indices]=sol.sol(ox)
                state=json.loads(send('P',active,ox,observed));observations.append(dict(x=ox,side='pre',active=active,physical=state))
                if ox!=stop or event>=len(setup['births']):observations.append(dict(x=ox,side='post',active=active,physical=state))
        physical=json.loads(send('P',active,stop,y))
        np.save(a.out/f'accepted_coordinates_event{event}.npy',y)
        interval_records.append(dict(event=event,x=stop,active=active,solver_steps=sol.t.size-1,calls=calls,dimension=indices.size,N=physical['N'],U=physical['U']))
        if event<len(setup['births']):
            y[4+2*cells*event:4+2*cells*(event+1)]=setup['encoded_births'][event];active+=1
            if stop in common_x:observations.append(dict(x=stop,side='post',active=active,physical=json.loads(send('P',active,stop,y))))
        start=stop
    (a.out/'observations.json').write_text(json.dumps(observations)+'\n')
    physical=json.loads(send('P',active,start,y));(a.out/'endpoint.json').write_text(json.dumps(physical)+'\n')
    flat=np.array(physical['flat']);gas=flat[:4];he=setup['he_h'];chi=setup['binding_ev'];initial=np.array(setup['initial_physical'])
    binding=lambda f:chi[0]*f[0]+he*(chi[1]*f[1]+(chi[1]+chi[2])*f[2])
    e0=initial[3]+binding(initial);led=np.array(physical['ledgers']);source=np.array(setup['source_inventory']).sum(axis=0)
    er=gas[3]+binding(gas)+physical['U']+led[0]+led[2]+led[3]-led[1]-source[1]-e0
    eg=abs(gas[3])+abs(binding(gas))+abs(physical['U'])+abs(led[0])+abs(led[1])+abs(led[2])+abs(led[3])+source[1]+abs(e0)
    nr=physical['N']+led[4:7].sum()-source[0];ng=physical['N']+abs(led[4:7]).sum()+source[0]
    photo=led[4:7];rr=led[7:10];ci=led[10:13];dr=led[13];net=photo+ci-rr
    charge=lambda f:f[0]+he*(f[1]+2*f[2]);qr=charge(gas)-charge(initial)-net.sum()+dr
    species=(gas[:3]-initial[:3])*np.array([1,he,he])-np.array([net[0],net[1]-net[2]-dr,net[2]])
    ledger=dict(energy_residual=er,energy_gross=eg,energy_normalized=abs(er)/eg,photon_residual=nr,photon_gross=ng,photon_normalized=abs(nr)/ng,charge_residual=qr,species_residual=species.tolist(),source_N_U=source.tolist())
    (a.out/'ledgers.json').write_text(json.dumps(ledger,indent=2)+'\n')
    assert abs(er)<=1e-8*eg and abs(nr)<=1e-8*ng,ledger
    status='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
except Exception as error:
    failure=repr(error);status='HOLD_POSITIVE_NATIVE_REFERENCE';raise
finally:
    server.stdin.close();server.wait(timeout=30)
    (a.out/'solver_return.json').write_text(json.dumps(dict(status=status,failure=failure,q=a.q,tight=a.tight,birth_panels=a.birth_panels,n_mu=a.n_mu,source_subdivisions=a.source_subdivisions,transport_cells=a.transport_cells,calls=calls,wall_s=time.monotonic()-started,python_peak_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,errors=errors,intervals=interval_records,server_exit=server.returncode),indent=2)+'\n')
