"""Independent SciPy time integration of the exact native-coefficient gas RHS.

All rates are supplied by a persistent safe Rust process. No atomic fit is
reimplemented in Python. Independence concerns integration and RHS assembly,
not independent atomic measurements or a second reviewer actor.
"""
from __future__ import annotations
import pathlib, subprocess, selectors, time
import numpy as np
from scipy.integrate import solve_ivp
EV_J=1.602176634e-19
# Fixed native 13-state ordering is read and checked by test/protocol receipt.
ROOT=pathlib.Path(__file__).resolve().parents[1]
SERVER=ROOT/'code/rei_bass_coupled/target/release/examples/gas_rhs_server'
class NativeError(RuntimeError): pass
class GasServer:
    def __init__(self,path: pathlib.Path=SERVER):
        self.process=subprocess.Popen([str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.calls=0
    def __enter__(self): return self
    def __exit__(self,*args): self.close()
    def close(self):
        p=self.process
        if p.poll() is None:
            try:p.stdin.write('QUIT\n');p.stdin.flush();p.wait(timeout=2)
            except (BrokenPipeError,subprocess.TimeoutExpired):p.kill();p.wait()
        for stream in [p.stdin,p.stdout,p.stderr]:stream.close()
    def _call(self,tag:str,mask:int,tcmb:float,state:np.ndarray,dt:float|None=None)->np.ndarray:
        if state.shape!=(14,) or not np.isfinite(state).all():raise ValueError('native state is 13 proper densities and u')
        values=[float(mask),float(tcmb)]+([] if dt is None else [float(dt)])+list(state)
        self.process.stdin.write(tag+' '+' '.join(format(x,'.17e') for x in values)+'\n');self.process.stdin.flush()
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout,selectors.EVENT_READ)
            if not selector.select(timeout=10):raise TimeoutError('native RHS response')
        line=self.process.stdout.readline();self.calls+=1
        if not line.startswith('OK '):raise NativeError(line.strip() or 'native process ended')
        out=np.fromstring(line[3:],sep=' ')
        expected=28 if tag=='RHS' else 27
        if len(out)!=expected or not np.isfinite(out).all():raise NativeError('invalid native payload')
        return out
    def rhs(self,state:np.ndarray,tcmb:float,mask:int=7)->np.ndarray:return self._call('RHS',mask,tcmb,state)
    def step(self,state:np.ndarray,tcmb:float,dt:float,mask:int=7,tight:bool=False)->np.ndarray:return self._call('STEP_TIGHT' if tight else 'STEP',mask,tcmb,state,dt)

def scales(state:np.ndarray)->np.ndarray:
    # Native order: neutron0,H0/H+1/2,D0/D+3/4,He4 charges10/11/12.
    nh=float(state[1]+state[2])
    if not nh>0:raise ValueError('reference chart requires positive H nuclei')
    scale=np.full(27,nh);scale[13:16]=nh*EV_J;scale[26]=nh*EV_J
    return scale

def integrate(server:GasServer,state:np.ndarray,tcmb:float,dt:float,method:str='Radau',mask:int=7,rtol:float=3e-11)->tuple[np.ndarray,dict]:
    state=np.asarray(state,dtype=float)
    if not np.isfinite(dt) or dt<=0:raise ValueError('positive proper duration required')
    scale=scales(state);y0=np.zeros(27);y0[:14]=state/scale[:14]
    atol=np.full(27,1e-16);atol[14:]=1e-22
    # Exact inactive spectator columns are retained with zero derivative.
    def rhs(_z,y):return dt*server.rhs(y[:14]*scale[:14],tcmb,mask)[:27]/scale
    start=time.perf_counter();before=server.calls
    sol=solve_ivp(rhs,(0.,1.),y0,method=method,rtol=rtol,atol=atol,max_step=0.25)
    if not sol.success or sol.t[-1]!=1.:raise NativeError(str(sol.message))
    final=sol.y[:,-1]*scale
    if (final[:13]<0).any() or final[13]<=0:raise NativeError('unphysical accepted state')
    for cols in [[1,2],[3,4],[10,11,12]]:
        denom=float(sum(state[i] for i in cols))
        if denom and abs(sum(final[i] for i in cols)-denom)>3e-11*denom:raise NativeError('nucleus invariant')
    return final,{'method':method,'rtol':rtol,'atol':atol.tolist(),'nfev':sol.nfev,'njev':sol.njev,'nlu':sol.nlu,'accepted_nodes':len(sol.t),'native_rhs_calls':server.calls-before,'wall_s':time.perf_counter()-start}

def composite(server,state,tcmb,dt,kind='lie',rtol=3e-11):
    sequence=[(5,dt),(2,dt)] if kind=='lie' else [(5,dt/2),(2,dt),(5,dt/2)]
    current=np.asarray(state,dtype=float).copy();totals=np.zeros(13);receipts=[]
    for mask,h in sequence:
        out,r=integrate(server,current,tcmb,h,mask=mask,rtol=rtol);current=out[:14];totals+=out[14:];receipts.append(r)
    return np.r_[current,totals],receipts
