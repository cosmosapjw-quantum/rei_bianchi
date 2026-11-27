#include "../radial/radial_wide.cpp"
#include <vector>
#include <cstdint>
#include <new>
namespace h0_fused {
R l1(Z z){return std::abs(z.real())+std::abs(z.imag());}
struct Sum{Z s=0,c=0;void add(Z x){Z t=s+x;c+=Z(std::abs(s.real())>=std::abs(x.real())?(s.real()-t.real())+x.real():(x.real()-t.real())+s.real(),std::abs(s.imag())>=std::abs(x.imag())?(s.imag()-t.imag())+x.imag():(x.imag()-t.imag())+s.imag());s=t;}Z get()const{return s+c;}};
struct V{Z x;R upper;V(Z a=0,R b=0):x(a),upper(b){}};
V operator+(V a,V b){return {a.x+b.x,a.upper+b.upper};}
V operator-(V a,V b){return {a.x-b.x,a.upper+b.upper};}
V operator*(Z a,V b){return {a*b.x,l1(a)*b.upper};}
V operator*(R a,V b){return Z(a)*b;}
V operator-(V a){return {-a.x,a.upper};}
struct Geo{R A;Z m[3],n[3],base;};
Geo geo(R a,R t,R dx,R dz,R q){Geo g;g.A=a+t;g.m[0]=a*dx/g.A;g.m[1]=0;g.m[2]=Z(a*dz/g.A,q/(2*g.A));g.n[0]=g.m[0]-dx;g.n[1]=0;g.n[2]=g.m[2]-dz;g.base=powl(acosl(-1.L)/g.A,1.5L)*std::exp(Z(-a*t*(dx*dx+dz*dz)/g.A-q*q/(4*g.A),q*a*dz/g.A));return g;}
}
extern "C" int mh_h0(std::size_t n,const double*tt,const double*ww,const double*pp,const double*norm,long double*oo,long double*aa)noexcept{
 using namespace h0_fused;
 if(!n||n>192||!tt||!ww||!pp||!norm||!oo||!aa)return -501;
 if(std::fegetround()!=FE_TONEAREST)return -503;
 R a=pp[0],b=pp[1],z=pp[2],v=pp[3],sgn=pp[5],inv=pp[6];int active=int(pp[4]);R f=inv?-1:1;
 if(a<=0||b<=0||(active!=0&&active!=1)||(sgn!=1&&sgn!=-1))return -506;
 R d1x=active?-2*f:0,d1z=active?-z*f:0,d2x=active?0:-2*f,d2z=active?0:-z*f;
 R q1=active?v*sgn*f:0,q2=active?0:v*sgn*f,ka=(active?-v/2:v/2)*sgn*f,kb=-ka;
 const Z I(0,1);std::size_t nn=n*n;Sum total[21];R absum[21]{};
 try{
  std::vector<Geo>ga(n),gb(n);for(std::size_t i=0;i<n;i++){if(tt[i]<=0||!std::isfinite(tt[i]))return -506;ga[i]=geo(a,tt[i],d1x,d1z,q1);gb[i]=geo(b,tt[i],d2x,d2z,q2);}
  for(std::size_t i=0;i<n;i++)for(std::size_t j=0;j<n;j++){
   auto g1=ga[i],g2=gb[j];R A=g1.A,B=g2.A,sig=.5L/A+.5L/B;Z base=g1.base*g2.base;if(base==Z(0))continue;
   Z d[3],s=0;for(int k=0;k<3;k++){d[k]=g1.m[k]-g2.m[k];s+=d[k]*d[k];}
   Z rad[30];R sr=s.real(),si=s.imag();int iterations=0;int status=radial_entire(1,&sig,&sr,&si,2,reinterpret_cast<R*>(rad),&iterations);if(status)return status;
   Sum sums[11];R upper[11]{};std::size_t ij=i*n+j;
   for(int p=0;p<9;p++){
    R w=ww[p*nn+ij],w1=ww[(9+p)*nn+ij],w2=ww[(18+p)*nn+ij];
    Z values[11]={rad[p+1],rad[11+p],rad[21+p],rad[p+1],rad[11+p],rad[p+1],rad[11+p],rad[p+1],rad[11+p],rad[p],rad[10+p]};
    R weights[11]={w,w,w,p*w,p*w,w1,w1,w2,w2,w,w};
    for(int c=0;c<11;c++){sums[c].add(weights[c]*values[c]);upper[c]+=std::abs(weights[c])*l1(values[c]);}
   }
   V u[11];for(int c=0;c<11;c++)u[c]={sums[c].get(),upper[c]};V M=u[0],F=u[1],F2=u[2],Msig=(R(1)/(2*sig))*u[3]-(s/sig)*F,Fsig=(R(1)/(2*sig))*(u[4]-R(2)*F)-(s/sig)*F2;
   Z dp[6][3]{},np[6][3]{},logp[6]{},sgp[6]{},ap[6]{};
   for(int k=0;k<3;k++){dp[0][k]=-g1.n[k]/A;np[0][k]=dp[0][k];dp[1][k]=g2.n[k]/B;logp[0]-=g1.n[k]*g1.n[k];logp[1]-=g2.n[k]*g2.n[k];}
   ap[0]=1;sgp[0]=-.5L/(A*A);sgp[1]=-.5L/(B*B);logp[0]-=1.5L/A;logp[1]-=1.5L/B;
   dp[2][2]=.5L*I/A;np[2][2]=dp[2][2];logp[2]=I*g1.m[2];dp[3][2]=-.5L*I/B;logp[3]=I*g2.m[2];
   dp[4][2]=a/A;np[4][2]=dp[4][2]-R(1);logp[4]=2*a*g1.n[2];dp[5][2]=-b/B;logp[5]=2*b*g2.n[2];
   Z sp[6]{};for(int h=0;h<6;h++)for(int k=0;k<3;k++)sp[h]+=R(2)*d[k]*dp[h][k];
   V E[3]={M,g1.n[0]*M+(d[0]/A)*F,g1.n[2]*M+(d[2]/A)*F};V der[6][3];
   for(int h=0;h<6;h++){
    V Mp=sgp[h]*Msig+sp[h]*F,Fp=sgp[h]*Fsig+sp[h]*F2;der[h][0]=base*(logp[h]*M+Mp);
    for(int ell=1;ell<3;ell++){int k=ell==1?0:2;Z c=d[k]/A,cp=dp[h][k]/A-d[k]*ap[h]/(A*A);der[h][ell]=base*(logp[h]*E[ell]+np[h][k]*M+g1.n[k]*Mp+cp*F+c*Fp);}
   }
   for(int ell=0;ell<3;ell++){
    V O=base*E[ell];V T=R((ell?5:3)*a+3*b+(ka*ka+kb*kb)/2)*O+R(2*a*a)*der[0][ell]+R(2*b*b)*der[1][ell]-R(2*a*ka)*der[2][ell]-R(2*b*kb)*der[3][ell]+(R(2)*I*(a*ka*d1z+b*kb*d2z))*O;
    if(ell==2)T=T+(I*ka*base)*M;
    V vals[7]={O,T,-der[4][ell],-der[5][ell],{}, {}, {}};
    for(int extra=0;extra<3;extra++){int mi=extra==0?5:extra==1?7:9;V val=u[mi];if(ell){int k=ell==1?0:2;val=g1.n[k]*u[mi]+(d[k]/A)*u[mi+1];}vals[4+extra]=base*val;}
    for(int c=0;c<7;c++){if(!std::isfinite(vals[c].x.real())||!std::isfinite(vals[c].x.imag())||!std::isfinite(vals[c].upper))return -507;total[3*c+ell].add(vals[c].x);absum[3*c+ell]+=vals[c].upper;}
   }
  }
  Z*out=reinterpret_cast<Z*>(oo);for(int c=0;c<21;c++){out[c]=R(norm[c%3])*total[c].get();aa[c]=std::abs(R(norm[c%3]))*absum[c];}
 }catch(const std::bad_alloc&){return -504;}catch(...){return -505;}
 return 0;
}
