"""Source-pinned elemental H/He/Li charge operator and exact isotope quotient."""
from __future__ import annotations

import math
from pathlib import Path
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.constants import c, physical_constants, k as KB

ROOT = Path(__file__).resolve().parents[1]
EV = physical_constants['electron volt'][0]
MU = physical_constants['atomic mass constant'][0]
ELEMENTS = ('H', 'He', 'Li')
ISOTOPES = (('n', 1, 0), ('H1', 1, 1), ('D', 2, 1), ('T', 3, 1),
            ('He3', 3, 2), ('He4', 4, 2), ('Li6', 6, 3), ('Li7', 7, 3))
CHARGE_NAMES = tuple(f'{name}_{q}' for name, _, z in ISOTOPES for q in range(z+1))
OFFSETS = {'H': slice(0,2), 'He': slice(2,5), 'Li': slice(5,9)}
CHANNELS = ((1,1), (2,2), (2,1), (3,3), (3,2), (3,1))
LABELS = ('H I','He I','He II','Li I','Li II','Li III')
RRLABELS = ('H I', 'HeI a', 'HeII', 'LiI', 'LiII', 'LiIII')


def abundance():
    raw = {'n':0., 'H1':1., 'D':2.5e-5, 'T':0., 'He3':1e-5,
           'He4':.245/(4*(1-.245)), 'Li6':1e-14, 'Li7':5e-10}
    denominator = sum(a*raw[name] for name,a,_ in ISOTOPES)
    return {name:raw[name]/denominator for name,_,_ in ISOTOPES}


def thermal_uv(x):
    z = 21*math.exp(-x)-1
    tanh = math.tanh((7.5-z)/1.25)
    f = .5*(1+tanh)
    dtdx = 9900*.5*(1-tanh*tanh)*(1+z)/1.25
    return 100+9900*f, 5e-14*f, dtdx


class AtomicQuotient:
    def __init__(self, source):
        self.source=source
        self.Y=abundance()
        self.W=np.array([self.Y['H1']+self.Y['D'],self.Y['He3']+self.Y['He4'],
                         self.Y['Li6']+self.Y['Li7']])
        self.q=np.array([0,1,0,1,2,0,1,2,3],dtype=float)
        self.y0=np.array([1-2e-4,2e-4,1.,0.,0.,0.,1.,0.,0.])
        self.w_element=np.repeat(self.W,[2,3,4])
        self.charge_energy=np.array([0.,13.6,0.,24.59,24.59+54.42,0.,5.392,
                                     5.392+75.64,5.392+75.64+122.5])*EV
        self.photo=self._read_photo()
        self.rr=self._read_rr()
        self.integrals64=self._spectral_integrals(64)
        self.integrals128=self._spectral_integrals(128)
        self.spectral_rel_error=float(np.max(abs(self.integrals64-self.integrals128)/
                       np.maximum(abs(self.integrals128),1e-300)))
        self.integrals=self.integrals64
        self.ratios=self.integrals[:,0]/self.integrals[0,0]
        self.meanE=self.integrals[:,1]/np.maximum(self.integrals[:,0],1e-300)*EV
        self.uv_number_integral=13.6**2*(1/5-1/60)
        self.uv_energy_integral=13.6**2*math.log(60/5)
        nodes,weights=leggauss(64)
        E=27.5*nodes+32.5
        compare=np.array([27.5*sum(weights*(E/13.6)**-2),
                          27.5*sum(weights*(E/13.6)**-2*E)])
        self.uv_integral_error=float(np.max(abs(compare-np.array([
            self.uv_number_integral,self.uv_energy_integral]))/compare))

    def _read_photo(self):
        rows={}
        for line in (ROOT/'data/verner_photo_Z1_Z2_Z3.dat').read_text().splitlines():
            a=list(map(float,line.split()))
            rows[(int(a[0]),int(a[1]))]=np.array(a[2:])
        assert tuple(rows)==CHANNELS and len(rows)==6
        return rows

    def _read_rr(self):
        rows={}
        for line in (ROOT/'data/verner_ferland_rr_table1_original.dat').read_text().splitlines():
            label=line[:8].strip()
            if label in RRLABELS:
                rows[label]=np.array(list(map(float,line[16:].split())))
        assert set(rows)==set(RRLABELS)
        return rows

    def sigma_mb(self, key, energy):
        eth,emax,e0,s0,ya,p,yw,y0,y1=self.photo[key]
        e=np.asarray(energy)
        x=e/e0-y0
        y=np.sqrt(x*x+y1*y1)
        sigma=s0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)
        return np.where((e>=eth)&(e<=emax),sigma,0.)

    def _spectral_integrals(self,n):
        nodes,weights=leggauss(n)
        result=np.zeros((6,2))
        for i,key in enumerate(CHANNELS):
            lo=max(5.,self.photo[key][0]);hi=60.
            if lo>=hi:continue
            E=.5*(hi-lo)*nodes+.5*(hi+lo)
            dE=.5*(hi-lo)*weights
            kernel=self.sigma_mb(key,E)*1e-22*(E/13.6)**-2
            result[i]=[sum(dE*kernel),sum(dE*kernel*E)]
        return result

    @staticmethod
    def rr_scalar(row,T):
        a,b,t0,t1=row
        x=math.sqrt(T/t0)
        return a/(x*(1+x)**(1-b)*(1+math.sqrt(T/t1))**(1+b))

    def nb_cm3(self,a):
        return self.omega_b*self.source.rhocrit_j_m3/(MU*c*c*a**3)/1e6

    @property
    def omega_b(self):
        # Identical pinned background value; import only self-contained donor.
        from compact_transport import cosmology
        return cosmology()['Omega_b']

    def matrices(self,T,gamma_hi):
        P=np.zeros((9,9));R=np.zeros((9,9))
        for sl,indices in ((OFFSETS['H'],(0,)),(OFFSETS['He'],(1,2)),
                           (OFFSETS['Li'],(3,4,5))):
            for q,i in enumerate(indices):
                j=sl.start+q
                beta=gamma_hi*self.ratios[i]
                alpha=self.rr_scalar(self.rr[RRLABELS[i]],T)
                P[j,j]-=beta;P[j+1,j]+=beta
                R[j+1,j+1]-=alpha;R[j,j+1]+=alpha
        return P,R

    def point(self,x,f,a,H):
        T,gamma,dTdx=thermal_uv(x)
        nb=self.nb_cm3(a)
        w=nb*self.w_element*self.q
        ne=float(w@f)
        P,R=self.matrices(T,gamma)
        G=P+ne*R
        F=G@f/H
        return dict(T=T,gamma_hi=gamma,dTdx=dTdx,nb_cm3=nb,w=w,ne_cm3=ne,
                    P=P,R=R,G=G,F=F,Jff=(G+np.outer(R@f,w))/H)

    def lift(self,f):
        chunks=[]
        for name,_,z in ISOTOPES:
            if name in ('n','T'):
                chunks.extend([0.]*(z+1))
            else:
                element='H' if z==1 else 'He' if z==2 else 'Li'
                chunks.extend(self.Y[name]*f[OFFSETS[element]])
        return np.array(chunks)

    def reference_initial(self):
        return np.concatenate([self.y0[OFFSETS['H']]]*2+
                              [self.y0[OFFSETS['He']]]*2+
                              [self.y0[OFFSETS['Li']]]*2)

    def reference_reduce(self,g):
        return np.r_[g[0:2],g[4:7],g[10:14]]

    def reference_point(self,x,g,a,H):
        T,gamma,_=thermal_uv(x)
        nb=self.nb_cm3(a)
        weights=np.r_[np.repeat(self.Y['H1'],2)*[0,1],np.repeat(self.Y['D'],2)*[0,1],
                      np.repeat(self.Y['He3'],3)*[0,1,2],np.repeat(self.Y['He4'],3)*[0,1,2],
                      np.repeat(self.Y['Li6'],4)*[0,1,2,3],np.repeat(self.Y['Li7'],4)*[0,1,2,3]]*nb
        ne=float(weights@g)
        P,R=self.matrices(T,gamma)
        slices=(slice(0,2),slice(0,2),slice(2,5),slice(2,5),slice(5,9),slice(5,9))
        F=np.concatenate([(P[sl,sl]+ne*R[sl,sl])@v/H for sl,v in zip(slices,
                          (g[0:2],g[2:4],g[4:7],g[7:10],g[10:14],g[14:18]))])
        return ne,F

    def reference_electron(self,g,nb):
        weights=np.r_[np.repeat(self.Y['H1'],2)*[0,1],np.repeat(self.Y['D'],2)*[0,1],
                      np.repeat(self.Y['He3'],3)*[0,1,2],np.repeat(self.Y['He4'],3)*[0,1,2],
                      np.repeat(self.Y['Li6'],4)*[0,1,2,3],np.repeat(self.Y['Li7'],4)*[0,1,2,3]]*nb
        return float(weights@g)

    def photo_energy_ledger(self,point,f):
        # A is number density per eV per m^3. c * sigma_m2 * A * dE gives s^-1.
        A=point['gamma_hi']/(c*self.integrals[0,0])
        j=0
        absorbed=0.
        binding=0.
        for sl,inds in ((OFFSETS['H'],(0,)),(OFFSETS['He'],(1,2)),
                        (OFFSETS['Li'],(3,4,5))):
            for q,i in enumerate(inds):
                density=point['nb_cm3']*1e6*self.W[j]*f[sl.start+q]
                beta=point['gamma_hi']*self.ratios[i]
                alpha=self.rr_scalar(self.rr[RRLABELS[i]],point['T'])
                RR=point['ne_cm3']*alpha*point['nb_cm3']*1e6*self.W[j]*f[sl.start+q+1]
                binding+=self.photo[CHANNELS[i]][0]*EV*(density*beta-RR)
                absorbed+=density*beta*self.meanE[i]
            j+=1
        number=self.uv_number_integral*A
        uv=self.uv_energy_integral*A*EV
        return binding,absorbed,uv,number
