// Direct canonical DG weak pair projection, split all mapped ray edges.
// C ABI, double inputs; long double accumulated stock and energy.
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
#include <omp.h>
extern "C" int dg_rhs(int nr,int nc,const double* e,const double* d,const double* n,const double* w,const double* w0,const double* A,const double* B,double ymin,double ymax,double theta,double tr,int ngh,const double* zh,const double* wh,int ngl,const double* zl,const double* wl,double* outN,double* outV,double* diag){
 const int L=nr*nc;
 std::vector<double> cc(nc),hh(nc),cuts;cuts.reserve(nr*(nc+1)+2);
 for(int k=0;k<nc;++k){cc[k]=(e[k]+e[k+1])/2;hh[k]=(e[k+1]-e[k])/2;}
 for(int i=0;i<nr;++i)for(int k=0;k<=nc;++k){double t=std::log(e[k]*d[i]);if(t>ymin&&t<ymax)cuts.push_back(t);}
 std::sort(cuts.begin(),cuts.end());cuts.erase(std::unique(cuts.begin(),cuts.end()),cuts.end());
 const int threads=omp_get_max_threads();
 std::vector<std::vector<long double>> NN(threads,std::vector<long double>(L,0)),VV=NN;
 std::vector<long double> raw(threads,0),ab(threads,0);int fail=0;
 #pragma omp parallel for schedule(dynamic) reduction(|:fail)
 for(int pair=0;pair<nr*nr;++pair){
  int i=pair/nr,j=pair%nr;if(i==j)continue;
  int tid=omp_get_thread_num();auto& N=NN[tid];auto& V=VV[tid];
  double mu=0.;for(int k=0;k<3;++k)mu+=n[3*i+k]*n[3*j+k];
  mu=std::clamp(mu,-1.,1.);if(mu>=1.-1e-14)continue;
  double sig=std::sqrt(4*theta*(1-mu)),K=.75*(1+mu*mu)*w[i]*w[j];
  for(int z=0;z<ngh;++z){
   if(zh[z]<=0)continue;
   double eta=sig*zh[z],ex=std::exp(eta),em=std::expm1(eta),hi=ymax-eta;
   if(hi<=ymin)continue;
   std::vector<double> cut;cut.reserve(cuts.size()*2+2);cut.push_back(ymin);cut.push_back(hi);
   for(double c:cuts){if(c>ymin&&c<hi)cut.push_back(c);double v=c-eta;if(v>ymin&&v<hi)cut.push_back(v);}
   std::sort(cut.begin(),cut.end());cut.erase(std::unique(cut.begin(),cut.end()),cut.end());
   std::vector<int> il(nr,0),ir(nr,0);
   for(size_t s=0;s+1<cut.size();++s){
    double l=cut[s],r=cut[s+1];if(r<=l)continue;
    double y=(l+r)/2,h=(r-l)/2,xm=std::exp(y),xpm=xm*ex;
    for(int k=0;k<nr;++k){
     double q=xm/d[k],qp=xpm/d[k];
     while(il[k]+1<nc&&q>=e[il[k]+1])++il[k];
     while(ir[k]+1<nc&&qp>=e[ir[k]+1])++ir[k];
     if(q<e[0]||q>e[nc]||qp<e[0]||qp>e[nc])fail=1;
    }
    int a=il[i],b=ir[j];long double mass=0,center=0;
    for(int g=0;g<ngl;++g){
     double dx=xm*std::expm1(h*zl[g]),x=xm+dx,xp=x*ex;
     double q=x/d[i],qp=xp/d[j];
     double ri=w0[i]/(d[i]*d[i]*d[i]*w[i])/std::expm1(q),rj=w0[j]/(d[j]*d[j]*d[j]*w[j])/std::expm1(qp);
     double di=ri*(A[i*nc+a]+B[i*nc+a]*(q-cc[a])/hh[a]),dj=rj*(A[j*nc+b]+B[j*nc+b]*(qp-cc[b])/hh[b]);
     double dg=x*em/tr;
     double C=K*wh[z]*h*wl[g]*std::min(x*x*x,xp*xp*xp*std::exp(-dg));
     long double F=(long double)C*((long double)di-dj-std::expm1(dg)*((long double)dj*(1+ri)+(long double)rj*di+(long double)di*dj));
     mass+=F;center+=F*dx;raw[tid]+=F*x*em;ab[tid]+=std::abs(F);
    }
    // Direct pair plus continuous local-frequency angular mean subtraction.
    for(int k=0;k<nr;++k){
     int a0=il[k],b0=ir[k];long double left=w[k]-(k==i?1.:0.),right=(k==j?1.:0.)-w[k];
     N[k*nc+a0]+=left*mass;V[k*nc+a0]+=left*(mass*(xm/d[k]-cc[a0])+center/d[k]);
     N[k*nc+b0]+=right*mass;V[k*nc+b0]+=right*(mass*(xpm/d[k]-cc[b0])+center*ex/d[k]);
    }
   }
  }
 }
 if(fail)return 1;
 long double ns=0,us=0,nl=0,ul=0,vl=0;for(int k=0;k<L;++k){long double a=0,b=0;for(int t=0;t<threads;++t){a+=NN[t][k];b+=VV[t][k];}outN[k]=a;outV[k]=b;long double u=(b+a*cc[k%nc])*d[k/nc];ns+=a;us+=u;nl+=std::abs(a);ul+=std::abs(u);vl+=std::abs(b);}
 long double R=0,F=0;for(int t=0;t<threads;++t){R+=raw[t];F+=ab[t];}
 diag[0]=std::abs(ns)/std::max(nl,1.e-300L);diag[1]=std::abs(us)/std::max(ul,1.e-300L);diag[2]=R;diag[3]=F;diag[4]=nl;diag[5]=vl;return 0;
}
