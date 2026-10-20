#!/usr/bin/env python3
"""BR06_THEORY_RECOVERY_R1 independent direct-time frozen operator.

This is explicitly reconstructed source, not restored original source bytes.
Uses original archived native rows, donor Hermite data and physical owner
formulas; does not call Rust or read historical reported answers to integrate.
"""
from __future__ import annotations
import argparse
import csv
import datetime
import hashlib
import json
import math
from pathlib import Path
import platform
import time
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline
from scipy.special import roots_legendre

VERSION = 'BR06_THEORY_RECOVERY_R1'
DONOR_SHA = '5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133'
SPECIES = ('HI', 'HeI', 'HeII', 'DI')
EV_J = 1.602176634e-19
C_LIGHT = 299792458.0
CHI = np.array([13.598434599702, 24.587389011, 54.41776, 13.602134599702])
EDGES = np.array([13.60, 24.59, 54.42, CHI[3]])
FITS = ((13.60,.4298,5.475e4,32.88,2.963,0.,0.,0.),
        (24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136),
        (54.42,1.720,1.369e4,32.88,2.963,0.,0.,0.))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for part in iter(lambda: stream.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()


def first_step(path):
    result = []
    with Path(path).open(newline='') as stream:
        for row in csv.DictReader(stream):
            step = int(row['step'])
            if step == 1:
                result.append(row)
            elif step > 1:
                break
    if not result:
        raise ValueError('missing step1 rows: '+str(path))
    return result


def gauss(n):
    if not 1 <= n <= 256:
        raise ValueError('bounded Gaussian degree must be 1..256')
    x,w=roots_legendre(n)
    u=(x+1)/2; w=w/2
    if np.any(u<=0) or np.any(u>=1) or np.any(w<=0):
        raise ValueError('invalid positive quadrature')
    return u,w


def sfr(volume):
    zp=1/np.cbrt(volume)
    return .015*zp**2.7/(1+(zp/2.9)**5.6)


def verner(energy, channel):
    energy=np.asarray(energy)
    if np.any(~np.isfinite(energy)) or np.any(energy<=0) or np.any(energy>50000):
        raise ValueError('Verner photon domain')
    edge,e0,sigma0,ya,p,yw,y0,y1=FITS[channel]
    x=energy/e0-y0
    y=np.sqrt(x*x+y1*y1)
    value=sigma0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-22
    return np.where(energy>=edge,value,0.)


class Geometry:
    def __init__(self, donor, case, dt):
        with Path(donor).open(newline='') as stream:
            rows=[r for r in csv.DictReader(stream) if r['case']==case]
        if len(rows)!=121:
            raise ValueError('expected actual121-point donor case')
        l,r=rows[:2]
        self.a0=float(l['a']); self.width=float(r['x'])-float(l['x'])
        x=np.array([float(l['x']),float(r['x'])])
        h=np.array([float(v['H_mean_per_s']) for v in (l,r)])
        hp=np.array([float(v['dH_dln_a_per_s']) for v in (l,r)])
        b=np.array([float(v['b']) for v in (l,r)])
        shear=np.array([float(v['s_per_s']) for v in (l,r)])
        self.logh=CubicHermiteSpline(x,np.log(h),hp/h)
        self.b=CubicHermiteSpline(x,b,shear/h)
        self.dt=dt
        self.clock=solve_ivp(lambda q,y:dt*np.exp(self.logh(y)),(0.,1.),[0.],method='DOP853',
                             rtol=3e-14,atol=1e-21,max_step=.125,dense_output=True)
        if not self.clock.success or self.clock.y[0,-1]>=x[-1]:
            raise ValueError('independent first-cell clock domain')
        self.case=case

    def at(self,q):
        q=np.asarray(q,dtype=float)
        if np.any(q<0) or np.any(q>1) or np.any(~np.isfinite(q)):
            raise ValueError('geometry q outside recorded step')
        x=self.clock.sol(q.ravel())[0].reshape(q.shape)
        a=self.a0*np.exp(x); b=self.b(x); h=np.exp(self.logh(x)); s=h*self.b(x,1)
        ap=a*np.exp(-b); az=a*np.exp(2*b)
        axes=np.stack((ap,ap,az),axis=-1)
        hs=np.stack((h-s,h-s,h+2*s),axis=-1)
        if np.any(hs<=0):
            raise ValueError('outside admitted expanding BASS domain')
        return axes,hs,np.prod(axes,axis=-1)


class Fixture:
    def __init__(self,parent,case='SIGNED_MINUS'):
        self.parent=Path(parent)
        native=self.parent/'evidence/native/monitor_n16_r8'
        self.files={k:native/('MONITOR_'+k+'.csv') for k in ('STEPS','TEMPLATES','RULES','BIRTHS')}
        self.files['DONOR']=self.parent/'donor_input/donor/background_968rows_f9f0bfd3.csv'
        if sha(self.files['DONOR'])!=DONOR_SHA:
            raise ValueError('donor hash mismatch')
        self.step=first_step(self.files['STEPS'])[0]
        self.templates=first_step(self.files['TEMPLATES'])
        self.rules=first_step(self.files['RULES'])
        if len(self.templates)!=384 or len(self.rules)!=48:
            raise ValueError('native source label/rule count mismatch')
        self.dt=float(self.step['dt_s']); self.t0=float(self.step['t0_s'])
        if self.t0!=0 or self.dt!=5e11:
            raise ValueError('recorded step contract changed')
        self.anchor=float(self.step['mid_volume'])
        self.density=np.array([float(self.step['rate_'+k+'_m3']) for k in
            ('H1Neutral','He4Neutral','He4SinglyIonized','DNeutral')])
        if np.any(self.density<0) or np.any(~np.isfinite(self.density)):
            raise ValueError('invalid frozen populations')
        self.geometry=Geometry(self.files['DONOR'],case,self.dt)
        self.case=case

    def rates(self,energy,volume):
        h=verner(energy,0)
        cross=np.stack((h,verner(energy,1),verner(energy,2),np.where(energy>=CHI[3],h,0.)),axis=-1)
        return cross*self.density*(C_LIGHT*self.anchor/np.asarray(volume)[...,None])

    def source_ratio(self,q):
        return sfr(self.geometry.at(q)[2])/sfr(self.anchor)

    def template_direction(self,row):
        v=np.array([float(row['raw_birth_direction'+str(j)]) for j in (1,2,3)])
        norm=math.hypot(math.hypot(v[0],v[1]),v[2])
        return v/norm

    def validate_recorded_inputs(self):
        births=first_step(self.files['BIRTHS'])
        q=np.array([float(r['actual_birth_time_s'])/self.dt for r in births])
        aa,hh,_=self.geometry.at(q)
        # Recorded births describe SIGNED_MINUS only; plus uses separate owner probes.
        checks={'case':self.case,'birth_rows':len(births),'clock_nfev':self.geometry.clock.nfev,
                'x_end':float(self.geometry.clock.y[0,-1]),'donor_cell_width':self.geometry.width}
        if self.case=='SIGNED_MINUS':
            oa=np.array([[float(r['birth_a'+str(j)]) for j in (1,2,3)] for r in births])
            oh=np.array([[float(r['birth_H'+str(j)+'_per_s']) for j in (1,2,3)] for r in births])
            sr=np.array([float(r['source_amplitude_ratio']) for r in births])
            checks.update({'max_axes_relative':float(np.max(np.abs(aa/oa-1))),
              'max_H_relative':float(np.max(np.abs(hh/oh-1))),
              'max_source_ratio_relative':float(np.max(np.abs(self.source_ratio(q)/sr-1)))})
            if checks['max_axes_relative']>2e-13 or checks['max_H_relative']>3e-13 or checks['max_source_ratio_relative']>2e-13:
                raise ValueError('reconstructed geometry/source does not match actual records')
        energies=np.array([float(r['energy_ev']) for r in self.rules])
        expected=np.array([[float(r['k_'+sp+'_per_s']) for sp in SPECIES] for r in self.rules])
        actual=self.rates(energies,np.full(48,self.anchor))
        positive=expected>0
        checks['max_midpoint_opacity_relative']=float(np.max(np.abs(actual[positive]/expected[positive]-1)))
        if np.any(actual[~positive]!=0) or checks['max_midpoint_opacity_relative']>2e-13:
            raise ValueError('reconstructed opacity does not match actual native rules')
        return checks


class PathGrid:
    def __init__(self,fixture,q0,event_degree,opacity_degree,q1=None):
        self.f=fixture; self.q0=np.asarray(q0); self.q1=np.ones_like(self.q0) if q1 is None else np.asarray(q1)
        ue,self.we=gauss(event_degree); uo,self.wo=gauss(opacity_degree)
        self.width=self.q1-self.q0
        if np.any(self.width<0):raise ValueError('negative path interval')
        self.qe=self.q0[:,None]+self.width[:,None]*np.append(ue,1.)
        qi=self.q0[:,None,None]+(self.qe-self.q0[:,None])[:,:,None]*uo
        self.ai,self.hi,self.vi=fixture.geometry.at(qi)
        self.ae,self.he,self.ve=fixture.geometry.at(self.qe)
        self.start_axes=fixture.geometry.at(self.q0)[0]

    def evaluate(self,K):
        K=np.asarray(K)
        if K.shape!=(len(self.q0),3) or np.any(~np.isfinite(K)):
            raise ValueError('invalid Killing constants')
        energy_i=np.sqrt(np.sum((K[:,None,None,:]/self.ai)**2,axis=-1))
        tau=np.sum(self.f.rates(energy_i,self.vi),axis=-1)@self.wo
        tau*=self.f.dt*(self.qe-self.q0[:,None])
        survival=np.exp(-tau)
        momentum=K[:,None,:]/self.ae
        energy=np.sqrt(np.sum(momentum*momentum,axis=-1))
        direction=momentum/energy[...,None]
        kp=self.f.rates(energy[:,:-1],self.ve[:,:-1])
        measure=survival[:,:-1,None]*kp*self.we[None,:,None]*(self.f.dt*self.width[:,None,None])
        events=np.sum(measure,axis=1)
        heat=np.sum(measure*(energy[:,:-1,None]-CHI),axis=1)*EV_J
        absorbed=np.sum(measure*energy[:,:-1,None],axis=(1,2))*EV_J
        binding=events*CHI*EV_J
        derivative=-energy*np.sum(self.he*direction*direction,axis=-1)
        work=np.sum(survival[:,:-1]*derivative[:,:-1]*self.we,axis=1)*self.f.dt*self.width*EV_J
        result={'P':survival[:,-1],'tau':tau[:,-1],'events':events,'heat':heat,'binding':binding,
          'absorbed_energy':absorbed,'work':work,'end_energy_ev':energy[:,-1],
          'end_q2':(3*direction[:,-1,2]**2-1)/2}
        for key in ('P','events','heat','binding','absorbed_energy'):
            if np.any(~np.isfinite(result[key])) or np.any(result[key]<0):
                raise ValueError('nonfinite/negative path '+key)
        return result


def reduce_template(f,row,q,born,path):
    weighted=born*path['P']; age=(1-q)*f.dt
    energy=weighted*path['end_energy_ev']*EV_J
    out={'template_id':int(row['template_id']),
      'survival':float(np.sum(weighted)), 'age':float(np.sum(weighted*age)),
      'age2':float(np.sum(weighted*age*age)), 'energy':float(np.sum(energy)),
      'q2':float(np.sum(energy*path['end_q2'])),
      'work':float(np.sum(born*path['work'])),
      'absorbed_energy':float(np.sum(born*path['absorbed_energy'])),
      'source_count':float(np.sum(born)),
      'source_energy':float(np.sum(born)*float(row['energy_ev'])*EV_J)}
    for key in ('events','heat','binding'):
        out[key]={sp:float(np.sum(born*path[key][:,j])) for j,sp in enumerate(SPECIES)}
    return out


def aggregate(rows):
    keys=('survival','age','age2','energy','q2','work','absorbed_energy','source_count','source_energy')
    total={k:math.fsum(r[k] for r in rows) for k in keys}
    for k in ('events','heat','binding'):
        total[k]={sp:math.fsum(r[k][sp] for r in rows) for sp in SPECIES}
    total['mean_age_s']=total['age']/total['survival']
    total['mean_age2_s2']=total['age2']/total['survival']
    total['energy_weighted_q2']=total['q2']/total['energy']
    total['number_ledger_relative']=(total['survival']+math.fsum(total['events'].values())-total['source_count'])/total['source_count']
    total['energy_ledger_relative']=(total['energy']+total['absorbed_energy']-total['source_energy']-total['work'])/total['source_energy']
    return total


def continuous(f,birth,event,opacity):
    q,w=gauss(birth); grid=PathGrid(f,q,event,opacity)
    aa=grid.start_axes; ratio=f.source_ratio(q); rows=[]
    for row in f.templates:
        E=float(row['energy_ev']); n=f.template_direction(row)
        K=aa*E*n
        # The native ordinary spectrum has no gates crossed even for the oldest birth.
        eold=float(np.sqrt(np.sum((f.geometry.at(np.array([0.]))[0][0]*E*n/f.geometry.at(np.array([1.]))[0][0])**2)))
        if np.any((EDGES<E)&(EDGES>eold)):
            raise ValueError('native continuum needs threshold split: '+str(row['template_id']))
        born=float(row['midpoint_rate_com3_s'])*f.dt*w*ratio
        rows.append(reduce_template(f,row,q,born,grid.evaluate(K)))
    return aggregate(rows),rows


def write_template_csv(path,rows):
    flattened=[]
    for row in rows:
        record={k:v for k,v in row.items() if not isinstance(v,dict)}
        for key in ('events','heat','binding'):
            for sp in SPECIES:record[key+'_'+sp]=row[key][sp]
        flattened.append(record)
    with Path(path).open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(flattened[0]));writer.writeheader();writer.writerows(flattened)


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--case',choices=('SIGNED_MINUS','SIGNED_PLUS'),default='SIGNED_MINUS')
    p.add_argument('--orders',default='64:64:8,128:128:16')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    f=Fixture(a.parent,a.case); validation=f.validate_recorded_inputs()
    (a.output/'GEOMETRY_INDEPENDENT.json').write_text(json.dumps(validation,indent=2)+'\n')
    executions=[]
    for text in a.orders.split(','):
        controls=tuple(map(int,text.split(':')))
        if len(controls)!=3:raise ValueError('orders must be birth:event:opacity')
        start=time.perf_counter();result,rows=continuous(f,*controls)
        file=a.output/('continuous_b%d_e%d_o%d.csv'%controls)
        write_template_csv(file,rows)
        record={'controls':{'birth':controls[0],'event':controls[1],'opacity':controls[2]},
            'wall_s':time.perf_counter()-start,'result':result,'templates':384,'csv_sha256':sha(file)}
        executions.append(record)
        print(json.dumps({'version':VERSION,'controls':controls,'survival':result['survival'],
          'mean_age_s':result['mean_age_s'],'number_ledger_relative':result['number_ledger_relative'],
          'energy_ledger_relative':result['energy_ledger_relative'],'wall_s':record['wall_s']}),flush=True)
    source=f.parent/'crate'
    owner_paths=[source/'owner_src'/n for n in ('axbi_bass_background.rs','atomic_provider.rs','axbi_sources.rs','deuterium_atomic.rs','hhe_events.rs','bianchi_i.rs')]
    receipt={'version':VERSION,'status':'COMPLETED_FRESH_RECOVERY_EXECUTION','historical_pass_inherited':False,
      'scope':'Actual BR05 step1 frozen-comoving gas; source-native384labels; reconstructed independent direct-time reference; empirical convergence only',
      'case':a.case,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'source_sha256':sha(__file__),'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
      'inputs':{str(x):sha(x) for x in list(f.files.values())+owner_paths},
      'geometry_validation':validation,'executions':executions}
    out=a.output/'INDEPENDENT_REFERENCE.json';out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'output':str(out),'sha256':sha(out),'executions':len(executions)}),flush=True)


if __name__=='__main__':main()
