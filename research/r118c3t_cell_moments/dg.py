"""Exact signed cell-affine density overlap; arithmetic cell centers.
N, V are integrals over dq; V centered first q moment.
No node deposition. Strict support and optional full positivity checks.
"""
import numpy as np
T=np.longdouble
def centers(e):return (e[1:]+e[:-1])/2
def remap(src,N,V,dst):
 src=np.asarray(src,dtype=T);dst=np.asarray(dst,dtype=T);N=np.asarray(N,dtype=T);V=np.asarray(V,dtype=T)
 assert len(src)==len(N)+1==len(V)+1 and min(np.diff(src))>0 and min(np.diff(dst))>0
 assert dst[0]<=src[0]+1e-25 and dst[-1]>=src[-1]-1e-25,'target support'
 h=np.diff(src);c=centers(src);d=centers(dst);A=N/h;B=12*V/h**3
 n=np.zeros(len(d),dtype=T);v=n.copy();i=j=0
 while i<len(c) and j<len(d):
  l=max(src[i],dst[j]);r=min(src[i+1],dst[j+1])
  if r>l:
   w=r-l;m=(r+l)/2;s=w*(A[i]+B[i]*(m-c[i]));n[j]+=s;v[j]+=(m-d[j])*s+B[i]*w**3/12
  if src[i+1]<=dst[j+1]:i+=1
  else:j+=1
 den=max(np.sum(abs(N)),T('1e-300'));de=max(np.sum(abs(V))+np.sum(abs(c*N)),T('1e-300'))
 assert abs(np.sum(n)-np.sum(N))<T('1e-14')*den and abs(np.sum(v+d*n)-np.sum(V+c*N))<T('1e-14')*de
 return n,v
def project(e,fun,nq=8):
 from numpy.polynomial.legendre import leggauss
 z,w=leggauss(nq);e=np.asarray(e,dtype=T);c=centers(e);h=np.diff(e);x=c[:,None]+h[:,None]/2*z
 q=fun(x)*w*h[:,None]/2
 return q.sum(axis=-1),(q*(x-c[:,None])).sum(axis=-1)
def density(e,N,V,x):
 e=np.asarray(e,dtype=T);x=np.asarray(x,dtype=T);j=np.clip(np.searchsorted(e,x,side='right')-1,0,len(e)-2);c=centers(e)[j];h=np.diff(e)[j]
 return np.where((x>=e[0])&(x<=e[-1]),N[j]/h+12*V[j]*(x-c)/h**3,0)
def check_full(e,N,V):
 return bool(np.min(N)>=0 and np.min(N*np.diff(e)/6-np.abs(V))>=0)
def update(e,old,inc,reference):
 # transactional: never mutate old on failure.
 N,V=[a+b for a,b in zip(old,inc)]
 if not check_full(e,N+reference[0],V+reference[1]):raise ValueError('affine full realizability')
 return N,V
