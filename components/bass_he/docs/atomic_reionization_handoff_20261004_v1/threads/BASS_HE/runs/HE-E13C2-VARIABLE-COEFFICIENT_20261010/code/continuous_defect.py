"""Continuous photon coefficients on six sealed affine gas paths.

The evolving unknown is the signed defect from a captured frozen-coefficient
curve, not a new gas solution. Source parameters, event masks, and E0 anchors
remain pinned. np.longdouble is an explicitly measured coefficient arithmetic
lane (64-bit significand on this host); the DOP853 state uses binary64.
Neither arithmetic tolerance nor the saved Newton TOL is an error certificate.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp

LD = np.longdouble
SPEC = ('HI', 'HeI', 'HeII')
PARAMS = ((.4298,5.475e4,32.88,2.963,0.,0.,0.),
          (13.61,949.2,1.469,3.188,2.039,.4434,2.136),
          (1.720,1.369e4,32.88,2.963,0.,0.,0.))
CUT = np.array((13.6,24.59,54.42),dtype=LD)
CHI = np.array((13.598434599702,24.587389011,54.41776),dtype=LD)
EPS = LD(1.602176634e-12)
TOL = np.array((1e-14,1e-14,1e-14,1e-26),dtype=LD)
SELECTED = [('OFF',1,0,0),('OFF',1,1162,0),('OFF',1,1976,0),
            ('GM',2,1727,0),('GM',2,2333,0),('OFF',2,700,1)]


def lift(text):
    """Decimal CSV text describes a stored binary64, not an exact decimal."""
    return LD(float(text))


def read_csv(path):
    with Path(path).open(newline='') as handle:
        return list(csv.DictReader(handle))


def verify_inputs(root):
    if np.finfo(LD).nmant+1 < 64:
        raise RuntimeError('coefficient lane requires at least 64 significand bits; no implicit fallback')
    manifest = json.loads((root/'inputs/INPUT_FILES.json').read_text())
    for item in manifest:
        data = (root/item['path']).read_bytes()
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
            raise ValueError('pinned input identity mismatch: '+item['path'])
    return len(manifest)


def background(s):
    h0,orr,om,ol,ob,y,g,mp = map(LD,(2.2e-18,9e-5,.3,.69991,.048,.24,6.67430e-8,1.67262192595e-24))
    rb = ob*LD(3)*h0*h0/(LD(8)*LD(math.pi)*g)
    nh0 = (LD(1)-y)*rb/mp
    nhe0 = y*rb/(LD(4)*mp)
    density = np.exp(-LD(3)*s)
    H = h0*np.sqrt(orr*np.exp(-LD(4)*s)+om*density+ol)
    return nh0*density,nhe0*density,H


def sigma_active(energy,active):
    """One-sided analytic continuation within an already split open segment."""
    answer=[]
    for i,par in enumerate(PARAMS):
        e0,s0,ya,p,yw,y0,y1 = map(LD,par)
        x=energy/e0-y0
        yy=np.sqrt(x*x+y1*y1)
        sig=np.exp(np.log(s0)+np.log((x-LD(1))**2+yw*yw)
                   +(p/LD(2)-LD(5.5))*np.log(yy)
                   -p*np.log1p(np.sqrt(yy/ya))+np.log(LD(1e-18)))
        answer.append(np.where(active[i],sig,LD(0)))
    return np.array(answer,dtype=LD)


class SegmentBatch:
    def __init__(self, records, stage):
        self.records=records
        self.count=len(records)
        self.a=np.array([lift(r['a']) for r in records])
        self.h=np.array([lift(r['h']) for r in records])
        self.b=np.array([lift(r['b']) for r in records])
        self.e0=np.array([lift(r['e0']) for r in records])
        self.f0=np.array([lift(r['f0']) for r in records])
        self.qf=np.array([lift(r['q']) for r in records])
        self.lf=np.array([[lift(r['lambda_'+s]) for r in records] for s in SPEC])
        self.Lf=self.lf.sum(axis=0)
        em=np.array([lift(r['e_mid']) for r in records])
        self.active=em[None,:]>=CUT[:,None]
        self.source_on=np.array([float(r['source_on'])==1. for r in records])
        self.s0=lift(stage['s0']); self.s1=lift(stage['s1'])
        self.old=np.array([lift(stage['old_'+v]) for v in ('x','y','z')])
        self.new=np.array([lift(stage['new_'+v]) for v in ('x','y','z')])
        if np.any(self.h<=0) or np.any(self.e0<=0) or np.any(self.f0<0):
            raise ValueError('invalid segment domain')
        if np.any(self.a<self.s0) or np.any(self.b>self.s1):
            raise ValueError('segment outside saved macro')
        if np.any(self.h!=self.b-self.a):
            raise ValueError('stored h is inconsistent with endpoint subtraction')
        if np.any((self.lf!=0)!=self.active):
            raise ValueError('captured opacity mask disagrees with pinned cutoff')
        if np.any((self.qf>0)!=self.source_on):
            raise ValueError('captured source flag disagrees with q')
        if any(float(r['outn'])!=0. or float(r['oute'])!=0. for r in records):
            raise ValueError('this first-two-cell diagnostic excludes HI-domain outflow')

    def coeff(self,t):
        g=self.h*LD(t)
        s=self.a+g
        theta=(self.a-self.s0+g)/(self.s1-self.s0)
        xyz=self.old[:,None]+(self.new-self.old)[:,None]*theta
        x,y,z=xyz
        if np.any(x<0) or np.any(x>1) or np.any(y<0) or np.any(z<0) or np.any(y+z>1):
            raise ValueError('unphysical prescribed gas state')
        energy=self.e0*np.exp(-g)
        nh,nhe,H=background(s)
        target=np.array((nh*(LD(1)-x),nhe*(LD(1)-y-z),nhe*y))
        lam=LD(2.99792458e10)*target*sigma_active(energy,self.active)/H
        norm=LD(1)/LD(13.7)-LD(1)/LD(100.)
        q=np.where(self.source_on,LD(1e-15)/(norm*energy*H),LD(0))
        return lam,q,energy

    def frozen_stock(self,t):
        g=self.h*LD(t)
        tau=self.Lf*g
        decay=np.exp(-tau)
        integral=np.empty_like(tau)
        active=self.Lf!=0
        integral[active]=-np.expm1(-tau[active])/self.Lf[active]
        integral[~active]=g[~active]
        return self.f0*decay+self.qf*integral

    def rhs(self,t,state):
        Y=state.reshape(16,self.count).astype(LD)
        e=Y[0]
        lam,q,energy=self.coeff(t)
        pf=self.frozen_stock(t)
        dlam=lam-self.lf
        dq=q-self.qf
        direct=dlam*pf
        feedback=lam*e
        out=np.zeros((16,self.count),dtype=LD)
        out[0]=dq-direct.sum(axis=0)-feedback.sum(axis=0)
        out[1:4]=direct
        out[4:7]=feedback
        out[7:10]=energy*direct
        out[10:13]=energy*feedback
        out[13]=energy*e
        out[14]=dq
        out[15]=energy*dq
        return np.asarray(out*self.h,dtype=float).ravel()

    def solve(self,e_initial,rtol):
        Y=np.zeros((16,self.count))
        Y[0]=e_initial
        sol=solve_ivp(self.rhs,(0.,1.),Y.ravel(),method='DOP853',
                      rtol=rtol,atol=1e-25,t_eval=[1.],max_step=.25)
        if not sol.success or sol.y.shape!=(16*self.count,1):
            raise RuntimeError('signed-defect ODE failed: '+sol.message)
        end=sol.y[:,-1].reshape(16,self.count).astype(LD)
        if not np.all(np.isfinite(end)):
            raise ValueError('nonfinite signed defect')
        continuous=self.frozen_stock(1)+end[0]
        if np.any(continuous<0):
            raise ValueError('negative continuous photon endpoint')
        A=end[1:4]+end[4:7]
        B=end[7:10]+end[10:13]
        nledger=end[0]-np.asarray(e_initial,dtype=LD)+A.sum(axis=0)-end[14]
        eledger=self.e0*(np.exp(-self.h)*end[0]-np.asarray(e_initial,dtype=LD))+B.sum(axis=0)+end[13]-end[15]
        lmid,qmid,_=self.coeff(.5)
        def maxrel(a,b):
            nz=b!=0
            if np.any(a[~nz]!=0):raise ValueError('zero branch mismatch')
            return float(np.max(np.abs((a[nz]-b[nz])/b[nz]))) if np.any(nz) else 0.
        meta={'nfev':sol.nfev,'max_number_defect_ledger':float(np.max(np.abs(nledger))),
              'max_energy_defect_ledger_eV':float(np.max(np.abs(eledger))),
              'midpoint_realification_relative_lambda':maxrel(lmid,self.lf),
              'midpoint_realification_relative_q':maxrel(qmid,self.qf),
              'min_continuous_endpoint':float(np.min(continuous))}
        return end,continuous,meta


def projection(A,B_eV,fHe):
    return np.array((A[0],(A[1]-A[2])/fHe,A[2]/fHe,
                     EPS*np.sum(B_eV-CHI*A)),dtype=LD)


def run(root,out,rtol,modes):
    start=time.perf_counter()
    root=Path(root);out=Path(out)
    out.mkdir(parents=True,exist_ok=False)
    ninput=verify_inputs(root)
    upstream=root/'inputs/upstream_e13c1'
    records=[];diagnostics=[];local=[];allnode=[]
    for mode in modes:
        raw=read_csv(upstream/f'evidence/capture/{mode}/SEGMENTS.csv')
        stages=read_csv(upstream/f'inputs/{mode}_STAGES.csv')
        oldresult=json.loads((upstream/f'evidence/independent/{mode}/RESULTS.json').read_text())
        previous={}
        for step in (1,2):
            stage=stages[step-1]
            rows=[r for r in raw if int(r['step'])==step]
            bynode={}
            for r in rows:bynode.setdefault(int(r['node']),[]).append(r)
            sums=np.zeros(16,dtype=LD)
            node_sums={j:np.zeros(16,dtype=LD) for j in bynode}
            for level in sorted(set(int(r['segment']) for r in rows)):
                part=[r for r in rows if int(r['segment'])==level]
                batch=SegmentBatch(part,stage)
                ei=[]
                for r in part:
                    j=int(r['node'])
                    if j in previous:
                        native_end,corr=previous[j]
                        ei.append(corr+native_end-lift(r['f0']))
                    else:
                        if lift(r['f0'])!=0:raise ValueError('missing initial photon stock')
                        ei.append(LD(0))
                end,continuous,meta=batch.solve(np.array(ei,dtype=float),rtol)
                meta.update(mode=mode,step=step,segment_level=level,segment_count=len(part))
                diagnostics.append(meta)
                for k,r in enumerate(part):
                    j=int(r['node']);weight=lift(r['weight'])
                    native_end=lift(r['n'])
                    # Keep the tiny analytical-frozen/native endpoint difference
                    # as a seam correction; do not reset the continuous stock.
                    corr=end[0,k]+batch.frozen_stock(1)[k]-native_end
                    previous[j]=(native_end,corr)
                    node_sums[j][1:]+=end[1:,k]
                    node_sums[j][0]=corr
            for j,vals in node_sums.items():
                weight=lift(bynode[j][0]['weight'])
                sums+=weight*vals
                allnode.append({'mode':mode,'step':step,'node':j,'weight':float(weight),
                                'defect':[float(x) for x in vals]})
            A=sums[1:4]+sums[4:7];B=sums[7:10]+sums[10:13]
            fHe=lift(stage['fHe'])
            proj=projection(A,B,fHe)
            baseline=oldresult['transactions'][step-1]['owners']
            baseA=np.array([LD(baseline['A_'+s]) for s in SPEC])
            baseB=np.array([LD(baseline['B_'+s])/EPS for s in SPEC])
            nativeA=np.array([lift(stage['A_'+s]) for s in SPEC])
            nativeB=np.array([lift(stage['B_'+s])/EPS for s in SPEC])
            record={'mode':mode,'step':step,'delta_photon_endpoint':float(sums[0]),
                    'delta_A_per_H':[float(x) for x in A],
                    'delta_B_eV_per_H':[float(x) for x in B],
                    'delta_heat_eV_per_H':[float(x) for x in B-CHI*A],
                    'delta_A_direct':[float(x) for x in sums[1:4]],
                    'delta_A_feedback':[float(x) for x in sums[4:7]],
                    'delta_heat_direct_eV':[float(x) for x in sums[7:10]-CHI*sums[1:4]],
                    'delta_heat_feedback_eV':[float(x) for x in sums[10:13]-CHI*sums[4:7]],
                    'projected_photo_delta':[float(x) for x in proj],
                    'projected_over_algebraic_TOL':[float(x) for x in proj/TOL],
                    'delta_A_fraction_of_frozen':[float(x) for x in A/baseA],
                    'delta_heat_fraction_of_frozen_total':float(np.sum(B-CHI*A)/np.sum(baseB-CHI*baseA)),
                    'continuous_A_estimate':[float(x) for x in nativeA+A],
                    'continuous_B_eV_estimate':[float(x) for x in nativeB+B],
                    'continuous_absorbed_mean_eV_estimate':[float(x) for x in (nativeB+B)/(nativeA+A)],
                    'baseline_sealed_vs_native_projected_TOL':[float(x) for x in projection(baseA-nativeA,baseB-nativeB,fHe)/TOL],
                    'delta_source_number':float(sums[14]),'delta_source_energy_eV':float(sums[15]),
                    'delta_redshift_eV':float(sums[13])}
            records.append(record)
            print(json.dumps({'mode':mode,'step':step,'rtol':rtol,'delta_A':record['delta_A_per_H'],
                              'heat_delta':sum(record['delta_heat_eV_per_H']),
                              'scaled_defect':record['projected_over_algebraic_TOL']}),flush=True)
        for mode0,step,j,seg in SELECTED:
            if mode0!=mode:continue
            r=next(x for x in raw if int(x['step'])==step and int(x['node'])==j and int(x['segment'])==seg)
            batch=SegmentBatch([r],stages[step-1])
            end,cont,meta=batch.solve(np.array([0.]),rtol)
            local.append({'id':[mode,step,j,seg],'initial':'captured native f0, local control',
                          'delta_P':float(end[0,0]),
                          'delta_A':[float(x) for x in end[1:4,0]+end[4:7,0]],
                          'delta_B_eV':[float(x) for x in end[7:10,0]+end[10:13,0]],
                          'meta':meta})
    result={'task':'E13C2_CONTINUOUS_COEFFICIENT_SIGNED_DEFECT','rtol':rtol,'atol':1e-25,
            'arithmetic':{'Python':sys.version,'NumPy':np.__version__,'SciPy':scipy.__version__,
                          'coefficient_precision_bits':int(np.finfo(LD).nmant+1),'ODE_state':'binary64'},
            'input_hashes_verified':ninput,'records':records,'segment_groups':diagnostics,
            'local_oracle_controls':local,'native_runs':0,'new_gas_steps':0,
            'elapsed_seconds':time.perf_counter()-start,
            'max_rss_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'physical_production':'HOLD','uniform_interval_certificate':False,
            'old_TOL_is_not_discretization_tolerance':True}
    (out/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'NODE_DEFECTS.json').write_text(json.dumps(allnode,separators=(',',':'))+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--rtol',type=float,default=2e-9)
    p.add_argument('--modes',nargs='+',choices=['OFF','KF','GM'],default=['OFF','KF','GM'])
    a=p.parse_args()
    run(a.root,a.output,a.rtol,a.modes)
