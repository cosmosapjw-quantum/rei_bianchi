"""C3H chemistry-aware energy inventory and nested grid."""
import numpy as np
CHI=np.array([13.598434599702,24.587389011,54.41776])
KB=8.617333262145e-5
def cv(f,Y):
 f=np.asarray(f);return 1.5*KB*(1+Y+f[...,0]+Y*(f[...,1]+2*f[...,2]))
def binding(f,Y):
 f=np.asarray(f);return CHI[0]*f[...,0]+Y*(CHI[1]*f[...,1]+(CHI[1]+CHI[2])*f[...,2])
def thermal_pred(w,a0,a1):return w*(a0/a1)**2
def gas_residual(T1,C1,w0,B0,B1,a0,a1,Qext,Qrad):
 return C1*T1+B1-thermal_pred(w0,a0,a1)-B0-Qext+Qrad
def nested_edges(n=8192,xmin=1e-10,xmax=60.,cut=None):
 e=np.geomspace(xmin,xmax,n+1)
 if cut is not None:
  k=np.searchsorted(e,cut)
  if k>=len(e)-2:raise ValueError('cutoff outside grid')
  e=e[k:]
 return e
