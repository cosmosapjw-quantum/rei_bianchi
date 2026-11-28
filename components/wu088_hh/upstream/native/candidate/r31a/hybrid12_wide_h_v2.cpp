#include <cmath>
#include <complex>
#include <cfloat>
#include <cstddef>
#include <limits>
#include <cfenv>
static_assert(LDBL_MANT_DIG >= 64, "64-bit significand required");
static_assert(LDBL_MAX_EXP >= 4096, "wide longdouble exponent required");

using R=long double;
using Z=std::complex<R>;

// Numerical contract is frozen in CONTRACT.json. No fast-math permitted.

// IEEE binary128 is used only for cancellation control in the newly admitted
// compact complex strip. Every series recurrence coefficient is formed in
// binary128. Basic arithmetic is provided by libgcc; no quad transcendental is
// required.  Original longdouble paths remain bit-for-bit unchanged.
#if !defined(__SIZEOF_FLOAT128__) || __FLT128_MANT_DIG__ != 113
#error "IEEE binary128 basic arithmetic is required for the wide strip"
#endif
#if defined(__FAST_MATH__) || (defined(__FINITE_MATH_ONLY__) && __FINITE_MATH_ONLY__)
#error "Strict floating point required"
#endif
using Q=__float128;
struct QZ {Q r,i;};
static Q qa(Q x){return x<0?-x:x;}
static Q qnorm(QZ x){return qa(x.r)+qa(x.i);}
static QZ qadd(QZ a,QZ b){return {a.r+b.r,a.i+b.i};}
static QZ qsub(QZ a,QZ b){return {a.r-b.r,a.i-b.i};}
static QZ qmul(QZ a,QZ b){return {a.r*b.r-a.i*b.i,a.r*b.i+a.i*b.r};}
static QZ qscale(QZ a,Q b){return {a.r*b,a.i*b};}
static int hypergeom_wide(R a,R b,Z z,Z &out){
    QZ term{1,0},sum{1,0},correction{0,0};
    const QZ zz{Q(z.real()),Q(z.imag())};
    const Q eps=Q(ldexpl(1.L,-112));
    for(int k=1;k<=1024;++k){
        const Q ratio=(Q(a)+k-1)/((Q(b)+k-1)*k);
        term=qscale(qmul(term,zz),ratio);
        const QZ y=qsub(term,correction),updated=qadd(sum,y);
        correction=qsub(qsub(updated,sum),y);sum=updated;
        if(Q(k)+a>0){
            Q fac=(Q(k)+a)/(Q(k)+b);if(fac<1)fac=1;
            const Q q=qnorm(zz)/(k+1)*fac;
            // The l1 complex norm is submultiplicative. For subsequent terms,
            // max(1,(k+a)/(k+b)) and 1/(k+1) bound all future ratios.
            if(q<1 && qnorm(term)*q/(1-q)<=eps*qnorm(sum)/8){
                out=Z(R(sum.r),R(sum.i));return k;
            }
        }
    }
    return -1;
}

#include "continuation.hpp"
static int hypergeom(R a,R b,Z z,Z &out) {
    if(fabsl(z.imag())>2.L) return fabsl(z.imag())>=12.0L ? hypergeom_wide(a,b,z,out) : hypergeom_cont(a,b,z,out);
    Z term(1,0),sum(1,0),correction(0,0);
    const R eps=std::numeric_limits<R>::epsilon();
    for(int k=1;k<=1024;++k) {
        term *= z*((a+k-1)/((b+k-1)*k));
        const Z y=term-correction;
        const Z updated=sum+y;
        correction=(updated-sum)-y;
        sum=updated;
        if(k+a>0) {
            const R q=std::abs(z)/(k+1)*std::fmax(R(1),(k+a)/(k+b));
            if(q<1 && std::abs(term)*q/(1-q)<=eps*std::abs(sum)/4) {
                out=sum;
                return k;
            }
        }
    }
    return -1;
}

static Z polynomial(R a,R b,Z z,int degree) {
    R coeff[5]; coeff[0]=1;
    for(int k=1;k<=degree;++k) coeff[k]=coeff[k-1]*(a+k-1)/((b+k-1)*k);
    Z out(coeff[degree],0);
    for(int k=degree-1;k>=0;--k) out=out*z+coeff[k];
    return out;
}


// Restricted shared-seed sector Re(x)>=-0.5: one Boys seed for the highest requested derivative order.
// Polynomial coefficients are exact integers, ascending in x.
static void poly_derivatives(const R* c,int degree,Z x,Z &f,Z &fp,Z &fpp) {
    f=Z(c[degree],0);fp=0;fpp=0;
    for(int k=degree-1;k>=0;--k) {fpp=fpp*x+R(2)*fp;fp=fp*x+f;f=f*x+c[k];}
}
static int positive_odd(R v,Z x,int order,Z out[3][5]) {
    static const R pi=acosl(-1.L),c=sqrtl(2/pi);
    const R ac[5][5]={{1,0,0,0,0},{1,2,0,0,0},{3,12,4,0,0},
      {15,90,60,8,0},{105,840,840,224,16}};
    const R bc[5][5]={{0,0,0,0,0},{1,0,0,0,0},{5,2,0,0,0},
      {33,28,4,0,0},{279,370,108,8,0}};
    // For a>=64, omit the exponentially small tail and E terms together.
    // Explicit truncation bounds (all n<=2) are documented in DERIVATION.md.
    // Principal sqrt is single-valued in this half-plane; exp(+x) never occurs.
    Z E,F[3]; int it=0;
    if(x.real()>=64.L) {
      E=Z(0,0);
      F[0]=sqrtl(pi)/(R(2)*std::sqrt(x));
      for(int n=1;n<=order;++n)F[n]=R(2*n-1)*F[n-1]/(R(2)*x);
    } else {
      E=std::exp(-x);
      if(fabsl(x.imag())>2.L){
        for(int n=0;n<=order;++n){
          int local=hypergeom(1,R(1.5L)+n,x,F[n]);if(local<0)return local;
          if(local>it)it=local;F[n]*=E/R(2*n+1);
        }
      }else{
      it=hypergeom(1,R(1.5L)+order,x,F[order]);
      if(it<0)return it;
      F[order]*=E/R(2*order+1);
      for(int n=order-1;n>=0;--n)F[n]=(R(2)*x*F[n+1]+E)/R(2*n+1);
      }
    }
    R scale=c/sqrtl(v);
    for(int k=0;k<5;++k) {
      Z A,Ap,App,B,Bp,Bpp;
      poly_derivatives(ac[k],k,x,A,Ap,App);
      poly_derivatives(bc[k],k? k-1:0,x,B,Bp,Bpp);
      out[0][k]=scale*(A*F[0]+B*E);
      if(order>=1)out[1][k]=scale/(2*v)*(Ap*F[0]-A*F[1]+(Bp-B)*E);
      if(order>=2)out[2][k]=scale/(4*v*v)*(App*F[0]-R(2)*Ap*F[1]+A*F[2]+(Bpp-R(2)*Bp+B)*E);
      if(k<4)scale*=v;
    }
    return it;
}

extern "C" int precision_bits() { return LDBL_MANT_DIG; }
extern "C" int radial_entire(std::size_t n,const R* variance,const R* sr,const R* si,
                            int order,R* output,int* maximum_iterations) {
    if(!maximum_iterations)return -4;
    *maximum_iterations=0;
    if(order<0 || order>2)return -4;
    if(n>std::size_t(std::numeric_limits<std::ptrdiff_t>::max())/(60*sizeof(R)))return -4;
    if(n>0 && (!variance || !sr || !si || !output))return -4;
    if(std::fegetround()!=FE_TONEAREST)return -5;
    // All inputs are validated before any output is written, including batched failures.
    for(std::size_t i=0;i<n;++i) {
      const R v=variance[i];
      if(!std::isfinite(v)||v<1e-100L||v>1e100L ||
         !std::isfinite(sr[i])||!std::isfinite(si[i]))return -2;
      const Z x(sr[i]/(2*v),si[i]/(2*v));
      if(!std::isfinite(x.real())||!std::isfinite(x.imag())||
         x.real() < -32 || x.real()>1e12L || fabsl(x.imag())>32)return -2;
    }
    static const R pi=acosl(-1.L),rootpi=sqrtl(pi);
    static const R gamma_ratio[10]={2/rootpi,1,2/rootpi,R(1.5L),4/rootpi,R(3.75L),
                            12/rootpi,R(13.125L),48/rootpi,R(59.0625L)};
    int maxiter=0;
    for(std::size_t i=0;i<n;++i) {
        const R v=variance[i];
        const Z x(sr[i]/(2*v),si[i]/(2*v));
        if(!(v>0) || !std::isfinite(v) || !std::isfinite(x.real()) || !std::isfinite(x.imag())
           || x.real() < -32 || x.real()>1e12L || fabsl(x.imag())>32) return -2;
        Z positive[3][5];
        if(x.real()>=-0.5L) {
          int it=positive_odd(v,x,order,positive);
          if(it<0)return -1;
          if(it>maxiter)maxiter=it;
        }
        // All needed powers are integer recurrences from one square root.
        // Shared-seed odd moments already exist; their generic constants are unused.
        const R twice_v=2*v;
        R powers[10];powers[1]=1;
        for(int idx=3;idx<10;idx+=2)powers[idx]=powers[idx-2]*twice_v;
        const bool shared=x.real()>=-0.5L;
        if(!shared) {
          powers[0]=1/sqrtl(twice_v);
          for(int idx=2;idx<10;idx+=2)powers[idx]=powers[idx-2]*twice_v;
        }
        for(int p=-1;p<=8;++p) {
            const bool is_shared_odd=shared && (p==-1 || p%2==1);
            const R constant=is_shared_odd ? R(0) : powers[p+1]*gamma_ratio[p+1];
            for(int j=0;j<=order;++j) {
                R prefactor=constant;
                if(j==1) prefactor*=R(p)/(6*v);
                if(j==2) prefactor*=R(p*(p-2))/(60*v*v);
                Z out(0,0);
                if((p==-1 || p%2==1) && x.real()>=-0.5L) out=positive[j][(p+1)/2];
                else if(prefactor!=0) {
                    const R a=R(j)-R(p)/2,b=R(1.5L)+j;
                    if(p>=0 && p%2==0) out=polynomial(a,b,-x,p/2-j);
                    else {
                        const bool kummer=x.real()>0;
                        const int it=hypergeom(kummer?R(p+3)/2:a,b,kummer?x:-x,out);
                        if(it<0) return -1;
                        if(it>maxiter) maxiter=it;
                        if(kummer) out*=std::exp(-x);
                    }
                    out*=prefactor;
                }
                if(!std::isfinite(out.real()) || !std::isfinite(out.imag())) return -3;
                const std::size_t loc=2*((std::size_t(j)*10+(p+1))*n+i);
                output[loc]=out.real();output[loc+1]=out.imag();
            }
        }
    }
    *maximum_iterations=maxiter;
    return 0;
}

#include "../radial/analytic_wide.cpp"

extern "C" int ws_hg(int method,long double a,long double b,long double xr,long double xi,long double*out){
 Z value;int rc=method?hypergeom_cont(a,b,Z(xr,xi),value):hypergeom_wide(a,b,Z(xr,xi),value);
 out[0]=value.real();out[1]=value.imag();return rc;
}


// R31K-B candidate. Scalar algorithms and analytic even-power kernel above remain unchanged.
// Independent gamma planes are evaluated in parallel, then merged in canonical h order.
#include <omp.h>
static thread_local int hh_threads=1;
static thread_local int hh_used_threads=1;
extern "C" int hh_set_num_threads(int n) { if(n<1||n>1024)return -1;hh_threads=n;return 0; }
extern "C" int hh_last_team_size() { return hh_used_threads; }

extern "C" int mh_wide_foreign(std::size_t n,std::size_t ngamma,const double*tt,const double*gs,const double*gw,const double*ww,const double*pars,long double*oo,long double*aa) noexcept {
 using namespace foreign_new;
 if(!n||!ngamma||!tt||!gs||!gw||!ww||!pars||!oo||!aa)return -301;
 if(std::fegetround()!=FE_TONEAREST)return -303;
 const R a=pars[0],b=pars[1],z=pars[2],q=pars[3],pi=acosl(-1.L),rr=4+z*z;
 if(a<=0||b<=0)return -306;
 if(ngamma>std::size_t(PTRDIFF_MAX))return -302;
 const std::size_t nn=n*n;Z*out=reinterpret_cast<Z*>(oo);
 try {
  std::vector<Z> packed(13*nn),raw(30*nn);std::vector<double>we(5*nn);Z ev[36];R ea[36];
  // Hoist only identical subexpressions, without changing multiplication association.
  std::vector<R> pa(n),pb(n);std::vector<Z> phase(n);
  std::vector<std::size_t> active;active.reserve(nn);
  for(std::size_t i=0;i<n;i++){
   R t=tt[i],A=a+t,B=b+t;
   pa[i]=powl(pi/A,1.5L);pb[i]=powl(pi/B,1.5L);
   phase[i]=std::exp(Z(-b*t*rr/B-q*q/(4*B),-q*z*b/B));
  }
  for(std::size_t i=0;i<n;i++)for(std::size_t j=0;j<n;j++){
   std::size_t k=i*n+j;R t=tt[i],u=tt[j],A=a+t,B=b+u;
   Z m1[3]={0,0,0},m2[3]={-2*b/B,0,Z(-z*b/B,q/(2*B))};
   Z n1[3]={0,0,0},n2[3]={2*u/B,0,Z(z*u/B,q/(2*B))};
   Z base=(pa[i]*pb[j])*phase[j];
   packed[k]=A;packed[nn+k]=B;packed[2*nn+k]=base;
   packed[3*nn+k]=n1[0];packed[4*nn+k]=n1[2];packed[5*nn+k]=n2[0];packed[6*nn+k]=n2[2];
   for(int d=0;d<3;d++)packed[(7+d)*nn+k]=m1[d]-m2[d];
   for(int p=0;p<5;p++)we[p*nn+k]=ww[2*p*nn+k];
   bool needed=false;for(int p=0;p<4;p++)needed=needed||(ww[(2*p+1)*nn+k]!=0);
   if(needed)active.push_back(k); // exact zeros only; no physical screening or tolerance.
  }
  struct GammaPlane { Z value[6]{};R absolute[6]{};int status=0; };
  for(int side=1;side<=2;side++){
   for(std::size_t i=0;i<n;i++)for(std::size_t j=0;j<n;j++){
    std::size_t k=i*n+j;R B=b+tt[j];
    packed[10*nn+k]=side==1?Z(2):Z(2*R(tt[j])/B);packed[11*nn+k]=0;
    packed[12*nn+k]=side==1?Z(z):Z(z*R(tt[j])/B,q/(2*B));
   }
   int status=fg_even(nn,side,reinterpret_cast<R*>(packed.data()),26*nn,we.data(),5*nn,reinterpret_cast<R*>(raw.data()),60*nn,reinterpret_cast<R*>(ev),72,ea,36);if(status)return status;
   Sum total[6];R absolute[6]{};
   for(int c=0;c<6;c++){total[c].add(ev[30+c]);absolute[c]=ea[30+c];}
   std::vector<GammaPlane> planes(ngamma);
   const int team=hh_threads;int used=1;
   #pragma omp parallel for schedule(dynamic,1) num_threads(team) if(team>1) reduction(max:used)
   for(std::ptrdiff_t ih=0;ih<static_cast<std::ptrdiff_t>(ngamma);ih++){
    used=omp_get_num_threads();std::size_t h=static_cast<std::size_t>(ih);
    // Exceptions and FP environment failures must not escape an OpenMP region.
    try {
     auto compute_plane=[&]() -> int {
      if(std::fegetround()!=FE_TONEAREST)return -303;
      R e=R(gs[h])*R(gs[h]),e1=side==1?e:0,e2=side==2?e:0;Sum plane[6];R planeabs[6]{};
      std::vector<R> av(n),bv(n),n1xv(n),n1zv(n),n2xv(n),dz1v(n),dz2v(n),imv(n),base1(n);std::vector<Z> n2zv(n),base2(n);
      for(std::size_t i=0;i<n;i++){
       R t=tt[i],A=a+t+e1,B=b+t+e2;av[i]=A;bv[i]=B;
       n1xv[i]=-2*e1/A;n1zv[i]=-z*e1/A;n2xv[i]=2*t/B;n2zv[i]=Z(z*t/B,q/(2*B));
       dz1v[i]=-z*e1/A;dz2v[i]=z*(b+e2)/B;imv[i]=-q/(2*B);
       base1[i]=powl(pi/A,1.5L)*expl(-e1*(t+a)*rr/A);
       base2[i]=powl(pi/B,1.5L)*std::exp(Z(-(b+e2)*t*rr/B-q*q/(4*B),-q*z*(b+e2)/B));
      }
      for(std::size_t k:active){
       std::size_t i=k/n,j=k%n;
       R A=av[i],B=bv[j],v=.5L/A+.5L/B;
       Z n1x=n1xv[i],n1z=n1zv[i],n2x=n2xv[j],n2z=n2zv[j];
       Z dx=n1xv[i]+2*(b+e2)/B,dz(dz1v[i]+dz2v[j],imv[j]),s=dx*dx+dz*dz;
       Z base=base1[i]*base2[j];if(base==Z(0))continue;
       Z M[4],D[4];int st=oddmom(v,s,M,D);if(st)return st;
       for(int p=0;p<4;p++){
        R weight=ww[(2*p+1)*nn+k];Z f=base*M[p]*weight,df=base*D[p]*weight;
        Z vals[6]={f,n1x*f+dx/A*df,n1z*f+dz/A*df,f,n2x*f-dx/B*df,n2z*f-dz/B*df};
        for(int c=0;c<6;c++){if(!good(vals[c]))return -307;plane[c].add(vals[c]);planeabs[c]+=std::abs(vals[c]);}
       }
      }
      for(int c=0;c<6;c++){planes[h].value[c]=plane[c].get();planes[h].absolute[c]=planeabs[c];}
      return 0;
     };
     planes[h].status=compute_plane();
    }catch(const std::bad_alloc&){planes[h].status=-304;}catch(...){planes[h].status=-305;}
   }
   hh_used_threads=used;
   for(std::size_t h=0;h<ngamma;h++){
    if(planes[h].status)return planes[h].status;
    R gweight=gw[h];
    for(int c=0;c<6;c++){total[c].add(gweight*planes[h].value[c]);absolute[c]+=std::abs(gweight)*planes[h].absolute[c];}
   }
   for(int c=0;c<6;c++){out[(side-1)*6+c]=total[c].get();aa[(side-1)*6+c]=absolute[c];}
  }
 }catch(const std::bad_alloc&){return -304;}catch(...){return -305;}
 return 0;
}
