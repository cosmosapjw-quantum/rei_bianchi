"""Source-table photo + total-RR isotope census under the frozen test-fluid contract."""
from functools import lru_cache
from pathlib import Path
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
ROOT=Path(__file__).resolve().parents[1]
C_CM=2.99792458e10;C=299792458.;EV=1.602176634e-19;KB=1.380649e-23;MU=1.66053906892e-27
GROUPS=[('n',1,0,0.),('H1',1,1,1.),('D',2,1,2.5e-5),('T',3,1,0.),('He3',3,2,1e-5),('He4',4,2,.245/(4*(1-.245))),('Li6',6,3,1e-14),('Li7',7,3,5e-10)]
NAMES=[];SLICES={};ABUNDANCES={};MASS=[];CHARGE=[];Y=[];ELEMENT=[]
normalization=sum(a*r for _,a,_,r in GROUPS)
for name,a,z,ratio in GROUPS:
 start=len(NAMES);SLICES[name]=slice(start,start+z+1);ABUNDANCES[name]=ratio/normalization
 for q in range(z+1):NAMES.append(name+'_'+str(q));MASS.append(a);CHARGE.append(q);Y.append(ratio/normalization);ELEMENT.append(z)
MASS=np.array(MASS);CHARGE=np.array(CHARGE);Y=np.array(Y);QY=CHARGE*Y
POPULATED=[name for name,_,_,r in GROUPS if r>0]
CHANNELS={(1,0):'HI',(2,0):'HeI',(2,1):'HeII',(3,0):'LiI',(3,1):'LiII',(3,2):'LiIII'}
RR_LABELS=['H I','HeI a','HeII','LiI','LiII','LiIII']

def initial_fractions():
 f=np.zeros(21)
 for name in POPULATED:
  sl=SLICES[name];f[sl.start]=1.
 for name in ('H1','D'):
  sl=SLICES[name];f[sl.start:sl.stop]=[1-2e-4,2e-4]
 for name in ('Li6','Li7'):
  sl=SLICES[name];f[sl.start:sl.stop]=[0.,1.,0.,0.]
 return f

def forcing(z):
 t=math.tanh((7.5-z)/1.25);f=.5*(1+t)
 return f,100+9900*f,9900*.5*(1-t*t)*(1+z)/1.25

class AtomicRates:
 def __init__(self,nodes=64):
  rows=np.loadtxt(ROOT/'data/verner_photo_Z1_Z2_Z3.dat');self.photo={CHANNELS[(int(v[0]),int(v[0]-v[1]))]:v for v in rows}
  self.rr={}
  for line in (ROOT/'data/verner_ferland_rr_table1_original.dat').read_text().splitlines():
   name=line[:8].strip()
   if name in RR_LABELS:self.rr[name.replace(' ','').replace('a','')]=np.array([float(v) for v in line[16:].split()])
  if set(self.rr)!=set(self.photo):raise ValueError('SOURCE_RR_ROW_SELECTION')
  self.photo_integrals={};self.photo_energy_integrals={}
  nodes_,weights=leggauss(nodes)
  for name,row in self.photo.items():
   lo=max(5.,row[2]);hi=60.
   if lo>=hi:self.photo_integrals[name]=0.;self.photo_energy_integrals[name]=0.;continue
   energy=.5*(hi+lo)+.5*(hi-lo)*nodes_;weight=.5*(hi-lo)*weights
   sigma=self.cross_section(name,energy);shape=(energy/13.6)**-2
   self.photo_integrals[name]=float(np.sum(weight*sigma*shape));self.photo_energy_integrals[name]=float(np.sum(weight*sigma*shape*energy))
  denom=self.photo_integrals['HI'];self.ratios=np.array([self.photo_integrals[n]/denom for n in ('HI','HeI','HeII','LiI','LiII','LiIII')])
  self.mean_energy_ev={n:(self.photo_energy_integrals[n]/self.photo_integrals[n] if self.photo_integrals[n]>0 else 0.) for n in self.photo}
  self.binding=np.zeros(21)
  for name,_,z,_ in GROUPS:
   sl=SLICES[name]
   for q in range(1,z+1):self.binding[sl.start+q]=self.binding[sl.start+q-1]+self.photo[CHANNELS[(z,q-1)]][2]*EV
  self.uv_number_integral=13.6**2*(1/5-1/60);self.uv_energy_integral=13.6**2*math.log(60/5)
 def cross_section(self,name,energy):
  v=self.photo[name];e=np.asarray(energy,dtype=float)
  if np.any(e>v[3]) or np.any(e<0):raise ValueError('PHOTO_FIT_ENERGY_DOMAIN')
  e0,sigma0,ya,p,yw,y0,y1=v[4:];x=e/e0-y0;y=np.sqrt(x*x+y1*y1)
  value=sigma0*((x-1)**2+yw*yw)*y**(p/2-5.5)*(1+np.sqrt(y/ya))**(-p)*1e-18
  return np.where(e>=v[2],value,0.)
 def alpha(self,temperature):
  if not 100-1e-10<=temperature<=1e4+1e-10:raise ValueError('PRESCRIBED_TEMPERATURE_DOMAIN')
  result=[]
  for name in ('HI','HeI','HeII','LiI','LiII','LiIII'):
   a,b,t0,t1=self.rr[name];x=math.sqrt(temperature/t0)
   result.append(a/(x*(1+x)**(1-b)*(1+math.sqrt(temperature/t1))**(1+b)))
  return np.array(result)
 def coefficients(self,z):
  f,t,tx=forcing(z);return 5e-14*f*self.ratios,self.alpha(t),t,tx,5e-14*f/(C_CM*self.photo_integrals['HI'])
 def derivatives(self,f,ne_cm3,z):
  beta,alpha,t,tx,uv_a=self.coefficients(z);df=np.zeros(21);pi=np.zeros(21);rr=np.zeros(21)
  for name,_,zcharge,abundance in GROUPS:
   if abundance==0:continue
   sl=SLICES[name]
   for q in range(zcharge):
    channel=list(CHANNELS.values()).index(CHANNELS[(zcharge,q)])
    i=sl.start+q;j=i+1;p=beta[channel]*f[i];r=ne_cm3*alpha[channel]*f[j]
    df[i]-=p-r;df[j]+=p-r;pi[i]=p;rr[i]=r
  return df,pi,rr,(t,tx,uv_a)
 def generator(self,zcharge,beta,alpha,ne):
  g=np.zeros((zcharge+1,zcharge+1))
  for q in range(zcharge):
   i=list(CHANNELS.values()).index(CHANNELS[(zcharge,q)])
   g[q+1,q]=beta[i];g[q,q+1]=ne*alpha[i]
  for q in range(zcharge+1):g[q,q]=-g[:,q].sum()
  return g

@lru_cache(maxsize=1)
def rates():return AtomicRates(64)
