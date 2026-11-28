// The unchanged reviewed radial_power.cpp is included before this file by the builder.
#include <array>
#include <vector>
#include <cstdint>
#include <climits>
#include <new>
#if defined(__FAST_MATH__) || (defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__)
#error "Strict floating point required"
#endif
#define API extern "C" __attribute__((visibility("default")))
namespace foreign_new {
using P = std::array<Z,10>;
static constexpr std::size_t cap=std::numeric_limits<std::size_t>::max()/sizeof(R);
template<class T> bool ptr(const T*p){return p&&reinterpret_cast<std::uintptr_t>(p)%alignof(T)==0;}
template<class T> bool finite(const T*p,std::size_t n){for(std::size_t i=0;i<n;i++)if(!std::isfinite(p[i]))return false;return true;}
bool good(Z z){return std::isfinite(z.real())&&std::isfinite(z.imag());}
bool domain(Z x){return good(x)&&x.real()>=-32&&x.real()<=1e12L&&std::abs(x.imag())<=32;}
struct Sum{Z s=0,c=0;void add(Z x){Z t=s+x;c+=Z(std::abs(s.real())>=std::abs(x.real())?(s.real()-t.real())+x.real():(x.real()-t.real())+s.real(),std::abs(s.imag())>=std::abs(x.imag())?(s.imag()-t.imag())+x.imag():(x.imag()-t.imag())+s.imag());s=t;} Z get()const{return s+c;}};
P constant(Z a){P p{};p[0]=a;return p;}
P plus(const P&a,const P&b){P c;for(int i=0;i<10;i++)c[i]=a[i]+b[i];return c;}
P scale(const P&a,Z x){P c;for(int i=0;i<10;i++)c[i]=a[i]*x;return c;}
P mul(const P&a,const P&b){P c{};for(int i=0;i<10;i++)if(a[i]!=Z(0))for(int j=0;j<10-i;j++)if(b[j]!=Z(0))c[i+j]+=a[i]*b[j];return c;}
// n<=4, no omitted nonzero degree>9 term occurs in this kernel.
void moments(const P&v,const P&s,P M[5],P D[5]){
 M[0]=constant(1);D[0]=P{};M[1]=plus(s,scale(v,3));D[1]=constant(1);
 P vv=mul(v,v);
 for(int n=1;n<4;n++){
  P a=plus(s,scale(v,4*n+3));R b=2*n*(2*n+1);
  M[n+1]=plus(mul(a,M[n]),scale(mul(vv,M[n-1]),-b));
  D[n+1]=plus(plus(M[n],mul(a,D[n])),scale(mul(vv,D[n-1]),-b));
 }
}
int boys(Z x,Z f[10]){
 if(!domain(x))return -206;
 if(x.real()>=64){
  f[0]=sqrtl(acosl(-1.L))/(R(2)*std::sqrt(x));
  for(int j=1;j<10;j++)f[j]=R(2*j-1)*f[j-1]/(R(2)*x);
 }else if(x.real()>=0 && std::abs(x.imag())>2.L){
  // Independent seeds prevent the unstable order-9 downward recurrence
  // from amplifying longdouble conversion error in the wide imaginary strip.
  const Z E=std::exp(-x);
  for(int j=0;j<10;j++){
   if(hypergeom(R(1),R(j)+R(1.5L),x,f[j])<0)return -209;
   f[j]*=E/R(2*j+1);
  }
 }else if(x.real()<0){
  // Descending recurrence amplifies cancellation in the negative half-plane.
  // Direct positive-real-part series per order preserves the original tolerance.
  for(int j=0;j<10;j++){
   if(hypergeom(R(j)+R(.5L),R(j)+R(1.5L),-x,f[j])<0)return -209;
   f[j]/=R(2*j+1);
  }
 }else{
  Z seed;
  if(hypergeom(R(1),R(10.5L),x,seed)<0)return -209;
  Z E=std::exp(-x);f[9]=E*seed/R(19);
  for(int j=8;j>=0;j--)f[j]=(R(2)*x*f[j+1]+E)/R(2*j+1);
 }
 for(int j=0;j<10;j++)if(!good(f[j]))return -207;
 return 0;
}
Z integrate(const P&p,const Z*f){Sum s;for(int j=0;j<10;j++)s.add(p[j]*f[j]);return s.get();}
int oddmom(R v,Z s,Z M[4],Z D[4]){
 Z x=s/(2*v);if(!std::isfinite(v)||v<1e-100L||v>1e100L||!domain(x))return -206;
 if(x.real()>=-0.5L){
  Z result[3][5];if(positive_odd(v,x,1,result)<0)return -209;
  for(int k=0;k<4;k++){M[k]=result[0][k+1];D[k]=result[1][k+1];}
 }else{
  R rootpi=sqrtl(acosl(-1.L)),sc=R(2)/rootpi*sqrtl(R(2)*v);
  for(int k=0;k<4;k++){
   int p=2*k+1;if(k)sc*=R(2)*v*(k+1);
   if(hypergeom(-R(p)/2,R(1.5L),-x,M[k])<0||hypergeom(R(1)-R(p)/2,R(2.5L),-x,D[k])<0)return -209;
   M[k]*=sc;D[k]*=sc*R(p)/(6*v);
  }
 }
 for(int k=0;k<4;k++)if(!good(M[k])||!good(D[k]))return -207;
 return 0;
}
}
API int fg_probe(std::uint64_t*out,std::size_t n) noexcept{
 using namespace foreign_new;if(!ptr(out)||n!=10)return -201;
 const std::uint64_t v[]={1,sizeof(R),alignof(R),LDBL_MANT_DIG,LDBL_MAX_EXP,sizeof(std::size_t),CHAR_BIT,FLT_RADIX,sizeof(Z),std::fegetround()==FE_TONEAREST};
 for(std::size_t j=0;j<n;j++)out[j]=v[j];return 0;
}
API int fg_layout(R*out,std::size_t n) noexcept{
 using namespace foreign_new;if(!ptr(out)||n!=4)return -201;
 Z*z=reinterpret_cast<Z*>(out);z[0]=Z(1.25L,-2.5L);z[1]=Z(-3.75L,4.5L);return 0;
}
API int fg_boys(std::size_t n,const R*xx,std::size_t nx,R*oo,std::size_t no) noexcept{
 using namespace foreign_new;
 if(!n||!ptr(xx)||!ptr(oo))return -201;
 if(n>cap/20||nx!=2*n||no!=20*n)return -202;
 if(std::fegetround()!=FE_TONEAREST)return -203;
 const Z*x=reinterpret_cast<const Z*>(xx);Z*out=reinterpret_cast<Z*>(oo);
 for(std::size_t i=0;i<n;i++)if(!domain(x[i]))return -206;
 try{std::vector<Z>temp(10*n);for(std::size_t i=0;i<n;i++){int st=boys(x[i],temp.data()+10*i);if(st)return st;}std::copy(temp.begin(),temp.end(),out);return 0;}
 catch(const std::bad_alloc&){return -204;}catch(...){return -205;}
}
API int fg_even(std::size_t n,int which,const R*gg,std::size_t ng,const double*ww,std::size_t nw,
 R*rr,std::size_t nr,R*oo,std::size_t no,R*aa,std::size_t na) noexcept{
 using namespace foreign_new;
 if(!n||which<1||which>2||!ptr(gg)||!ptr(ww)||!ptr(rr)||!ptr(oo)||!ptr(aa))return -201;
 if(n>cap/60||ng!=26*n||nw!=5*n||nr!=60*n||no!=72||na!=36)return -202;
 if(std::fegetround()!=FE_TONEAREST)return -203;
 if(!finite(gg,ng)||!finite(ww,nw))return -206;
 const Z*g=reinterpret_cast<const Z*>(gg);Z*raw=reinterpret_cast<Z*>(rr);Z*out=reinterpret_cast<Z*>(oo);
 for(std::size_t i=0;i<n;i++){
  Z A=g[i],B=g[n+i];if(A.imag()!=0||B.imag()!=0||A.real()<=0||B.real()<=0)return -206;
  Z s=0;for(int a=0;a<3;a++)s+=g[(10+a)*n+i]*g[(10+a)*n+i];
  if(!domain((which==1?A:B)*s))return -206;
 }
 try{
  // Outputs are committed only after the entire call succeeds.
  std::vector<Z>temp(30*n);Sum sums[36];R absolute[36]{};
  for(std::size_t i=0;i<n;i++){
   R A=g[i].real(),B=g[n+i].real(),prec=which==1?A:B;
   R var[2]={R(.5L)/A,R(.5L)/B},vj=var[which-1],sign=which==1?1:-1;
   Z base=g[2*n+i],Rvec[3],d[3],xx=0;P delta[3],s{};
   for(int a=0;a<3;a++){Rvec[a]=g[(10+a)*n+i];d[a]=g[(7+a)*n+i];xx+=Rvec[a]*Rvec[a];delta[a]=constant(d[a]);delta[a][1]=-sign*Rvec[a];s=plus(s,mul(delta[a],delta[a]));}
   P v=constant(var[0]+var[1]);v[1]=-vj;P M[5],Ds[5];moments(v,s,M,Ds);
   Z f[10];int st=boys(prec*xx,f);if(st)return st;
   Z pref=base*(R(2)*sqrtl(prec/acosl(-1.L)));
   for(int k=0;k<5;k++){
    Z value[6];value[0]=value[3]=pref*integrate(M[k],f);
    for(int e=0;e<2;e++){
     P ve=constant(var[e]);if(e==which-1)ve[1]=-vj;
     for(int ang=1;ang<3;ang++){
      int a=ang==1?0:2;P ne=constant(g[(3+2*e+ang-1)*n+i]);if(e==which-1)ne[1]=-Rvec[a];
      P poly=plus(mul(ne,M[k]),scale(mul(mul(ve,delta[a]),Ds[k]),e==0?2:-2));
      value[3*e+ang]=pref*integrate(poly,f);
     }
    }
    for(int a=0;a<6;a++){
     if(!good(value[a]))return -207;temp[30*i+6*k+a]=value[a];Z term=value[a]*R(ww[k*n+i]);if(!good(term))return -207;
     sums[6*k+a].add(term);absolute[6*k+a]+=std::abs(term);sums[30+a].add(term);absolute[30+a]+=std::abs(term);
    }
   }
  }
  for(int a=0;a<36;a++)if(!good(sums[a].get())||!std::isfinite(absolute[a]))return -207;
  std::copy(temp.begin(),temp.end(),raw);for(int a=0;a<36;a++){out[a]=sums[a].get();aa[a]=absolute[a];}return 0;
 }catch(const std::bad_alloc&){return -204;}catch(...){return -205;}
}
API int fg_odd(std::size_t n,const R*gg,std::size_t ng,const double*ww,std::size_t nw,R*oo,std::size_t no,R*aa,std::size_t na) noexcept{
 using namespace foreign_new;
 if(!n||!ptr(gg)||!ptr(ww)||!ptr(oo)||!ptr(aa))return -201;
 if(n>cap/40||ng!=40*n||nw!=4*n||no!=12||na!=6)return -202;
 if(std::fegetround()!=FE_TONEAREST)return -203;
 if(!finite(gg,ng)||!finite(ww,nw))return -206;
 const Z*g=reinterpret_cast<const Z*>(gg);Z*out=reinterpret_cast<Z*>(oo);
 for(std::size_t i=0;i<n;i++)for(int a=0;a<3;a++)if(g[a*n+i].imag()!=0||g[a*n+i].real()<=0)return -206;
 try{
  Sum sums[6];R absolute[6]{};
  for(std::size_t i=0;i<n;i++){
   Z M[4],D[4];int st=oddmom(g[2*n+i].real(),g[3*n+i],M,D);if(st)return st;
   Z A=g[i],B=g[n+i],base=g[4*n+i],dx=g[17*n+i],dz=g[19*n+i];
   Z n1x=g[11*n+i],n1z=g[13*n+i],n2x=g[14*n+i],n2z=g[16*n+i];
   for(int k=0;k<4;k++){
    Z f=base*M[k]*R(ww[k*n+i]),df=base*D[k]*R(ww[k*n+i]);
    Z val[6]={f,n1x*f+dx/A*df,n1z*f+dz/A*df,f,n2x*f-dx/B*df,n2z*f-dz/B*df};
    for(int a=0;a<6;a++){if(!good(val[a]))return -207;sums[a].add(val[a]);absolute[a]+=std::abs(val[a]);}
   }
  }
  for(int a=0;a<6;a++)if(!good(sums[a].get())||!std::isfinite(absolute[a]))return -207;
  for(int a=0;a<6;a++){out[a]=sums[a].get();aa[a]=absolute[a];}return 0;
 }catch(const std::bad_alloc&){return -204;}catch(...){return -205;}
}
