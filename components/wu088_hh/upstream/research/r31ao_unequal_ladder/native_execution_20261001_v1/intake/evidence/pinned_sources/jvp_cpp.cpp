// Included after the immutable wide radial source by the content-addressed builder.
#include <vector>
#include <array>
#include <cstdint>
#include <new>
#define API extern "C" __attribute__((visibility("default")))
namespace mj {
struct Sum{Z s=0,c=0;void add(Z x){Z t=s+x;c+=Z(std::abs(s.real())>=std::abs(x.real())?(s.real()-t.real())+x.real():(x.real()-t.real())+s.real(),std::abs(s.imag())>=std::abs(x.imag())?(s.imag()-t.imag())+x.imag():(x.imag()-t.imag())+s.imag());s=t;}Z get()const{return s+c;}};
template<class T>bool ptr(const T*p){return p&&reinterpret_cast<std::uintptr_t>(p)%alignof(T)==0;}
bool good(Z x){return std::isfinite(x.real())&&std::isfinite(x.imag());}
// Direct z-JVP of the canonical Gaussian completed square. The Gaussian
// exponents and t nodes are constant, so variance'=0. No G or D formula occurs.
void field(R a,R b,R t,R u,R z,R q,const Z*M,const Z*F1,const Z*F2,Z out[2][2][3]){
 const R A=a+t,B=b+u,pi=acosl(-1.L);
 const Z dx=2*b/B,dz=Z(z*b/B,-q/(2*B));
 const Z n2x=2*u/B,n2z=Z(z*u/B,q/(2*B));
 const R dzprime=b/B,n2zprime=u/B;
 const Z sprime=2.L*dz*dzprime;
 const Z logprime=Z(-2*b*u*z/B,-q*b/B);
 const Z base=powl(pi/A,1.5L)*powl(pi/B,1.5L)*std::exp(Z(-b*u*(4+z*z)/B-q*q/(4*B),-q*z*b/B));
 const Z Mp=(*F1)*sprime,Fp=(*F2)*sprime;
 for(int electron=0;electron<2;++electron){
  out[electron][0][0]=base*(*M);out[electron][1][0]=base*(logprime*(*M)+Mp);
  for(int angle=1;angle<3;++angle){
   const Z delta=angle==1?dx:dz;const R deltap=angle==1?0:dzprime;
   const Z ne=electron==0?Z(0):(angle==1?n2x:n2z);const R nep=electron==0||angle==1?0:n2zprime;
   const R factor=electron==0?1/A:-1/B;
   const Z E=ne*(*M)+factor*delta*(*F1);
   const Z Ep=nep*(*M)+ne*Mp+factor*(deltap*(*F1)+delta*Fp);
   out[electron][0][angle]=base*E;
   out[electron][1][angle]=base*(logprime*E+Ep);
  }
 }
}
}
API int mj_probe(std::uint64_t*out,std::size_t n)noexcept{
 if(!mj::ptr(out)||n!=5)return -401;out[0]=sizeof(R);out[1]=LDBL_MANT_DIG;out[2]=sizeof(Z);out[3]=std::fegetround()==FE_TONEAREST;out[4]=1;return 0;
}
API int mj_pair(std::size_t n,const double*tt,std::size_t nt,const double*ww,std::size_t nw,const double*norm,std::size_t nnormal,const R*par,std::size_t np,R*output,std::size_t no,R*sumabs,std::size_t na)noexcept{
 using namespace mj;
 if(!ptr(tt)||!ptr(ww)||!ptr(norm)||!ptr(par)||!ptr(output)||!ptr(sumabs))return -401;
 if(!n||n>4096||nt!=n||nw!=9*n*n||nnormal!=6||np!=4||no!=24||na!=12)return -402;
 if(std::fegetround()!=FE_TONEAREST)return -403;
 for(std::size_t k=0;k<nt;++k)if(!std::isfinite(tt[k])||tt[k]<0)return -406;
 for(std::size_t k=0;k<nw;++k)if(!std::isfinite(ww[k]))return -406;
 for(int k=0;k<6;++k)if(!std::isfinite(norm[k]))return -406;
 for(int k=0;k<4;++k)if(!std::isfinite(par[k]))return -406;
 const R a=par[0],b=par[1],z=par[2],q=par[3];if(a<=0||b<=0)return -406;
 try{
  const std::size_t nn=n*n;std::vector<R>v(nn),sr(nn),si(nn),mom(60*nn);int iterations=0;
  for(std::size_t i=0;i<n;++i)for(std::size_t j=0;j<n;++j){std::size_t k=i*n+j;R A=a+tt[i],B=b+tt[j];Z dx=2*b/B,dz=Z(z*b/B,-q/(2*B)),s=dx*dx+dz*dz;v[k]=.5L/A+.5L/B;sr[k]=s.real();si[k]=s.imag();}
  int status=radial_entire(nn,v.data(),sr.data(),si.data(),2,mom.data(),&iterations);if(status)return status;
  const Z*rad=reinterpret_cast<const Z*>(mom.data());Sum sums[12];R absolute[12]{};
  for(std::size_t i=0;i<n;++i)for(std::size_t j=0;j<n;++j){std::size_t k=i*n+j,kt=j*n+i;
   for(int power=0;power<9;++power){
    R weights[2]={ww[power*nn+k],ww[power*nn+kt]};if(weights[0]==0&&weights[1]==0)continue;
    Z f[2][2][3];field(a,b,tt[i],tt[j],z,q,rad+(power+1)*nn+k,rad+(11+power)*nn+k,rad+(21+power)*nn+k,f);
    for(int e=0;e<2;++e)for(int d=0;d<2;++d)for(int angle=0;angle<3;++angle){int loc=6*e+3*d+angle;Z term=f[e][d][angle]*weights[e];if(!good(term))return -407;sums[loc].add(term);absolute[loc]+=std::abs(term);}
   }
  }
  Z temp[12];R sa[12];for(int e=0;e<2;++e)for(int d=0;d<2;++d)for(int angle=0;angle<3;++angle){int loc=6*e+3*d+angle;temp[loc]=sums[loc].get()*R(norm[3*e+angle]);sa[loc]=absolute[loc]*fabsl(norm[3*e+angle]);if(!good(temp[loc])||!std::isfinite(sa[loc]))return -407;}
  std::copy(temp,temp+12,reinterpret_cast<Z*>(output));std::copy(sa,sa+12,sumabs);return 0;
 }catch(const std::bad_alloc&){return -404;}catch(...){return -405;}
}
API int mj_point(const R*par,std::size_t np,int power,R*output,std::size_t no)noexcept{
 if(!mj::ptr(par)||!mj::ptr(output)||np!=6||no!=24||power<0||power>8)return -401;
 if(std::fegetround()!=FE_TONEAREST)return -403;for(int k=0;k<6;k++)if(!std::isfinite(par[k]))return -406;
 R a=par[0],b=par[1],t=par[2],u=par[3],z=par[4],q=par[5];if(a<=0||b<=0||t<0||u<0)return -406;
 R A=a+t,B=b+u,v=.5L/A+.5L/B;Z dx=2*b/B,dz=Z(z*b/B,-q/(2*B)),s=dx*dx+dz*dz;R sr=s.real(),si=s.imag(),buf[60];int it=0;int rc=radial_entire(1,&v,&sr,&si,2,buf,&it);if(rc)return rc;
 const Z*rad=reinterpret_cast<const Z*>(buf);Z out[2][2][3];mj::field(a,b,t,u,z,q,rad+power+1,rad+power+11,rad+power+21,out);for(int e=0;e<2;e++)for(int d=0;d<2;d++)for(int k=0;k<3;k++)if(!mj::good(out[e][d][k]))return -407;std::copy(&out[0][0][0],&out[0][0][0]+12,reinterpret_cast<Z*>(output));return 0;
}
