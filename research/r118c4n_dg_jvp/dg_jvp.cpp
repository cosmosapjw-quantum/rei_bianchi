// Direct canonical DG weak pair projection, split all mapped ray edges.
// C ABI, double inputs; long double accumulated stock and energy.
#include <vector>
#include <algorithm>
#include <cmath>
#include <limits>
#include <omp.h>
extern "C" int dg_jvp(int nr,int nc,const double* e,const double* d,const double* n,const double* w,const double* w0,const double* A,const double* B,double ymin,double ymax,double theta,double tr,int ngh,const double* zh,const double* wh,int ngl,const double* zl,const double* wl,double* outN,double* outV,double* diag,const double* dA,const double* dB,double dtr){
 const int L=nr*nc;
 std::vector<double> cc(nc),hh(nc),cuts;cuts.reserve(nr*(nc+1)+2);
 for(int k=0;k<nc;++k){cc[k]=(e[k]+e[k+1])/2;hh[k]=(e[k+1]-e[k])/2;}
 for(int i=0;i<nr;++i)for(int k=0;k<=nc;++k){double t=std::log(e[k]*d[i]);if(t>ymin&&t<ymax)cuts.push_back(t);}
 cuts.push_back(ymin);cuts.push_back(ymax);std::sort(cuts.begin(),cuts.end());cuts.erase(std::unique(cuts.begin(),cuts.end()),cuts.end());
 const int threads=omp_get_max_threads();
 const int nb=cuts.size()-1;std::vector<double> xc(nb);
 for(int k=0;k<nb;++k)xc[k]=std::exp((cuts[k]+cuts[k+1])/2);
 std::vector<std::vector<long double>> MN(threads,std::vector<long double>(nb,0)),MV=MN;
 std::vector<std::vector<long double>> NN(threads,std::vector<long double>(L,0)),VV=NN;
 std::vector<long double> raw(threads,0),ab(threads,0);int fail=0;
 #pragma omp parallel for schedule(dynamic) reduction(|:fail)
 for(int pair=0;pair<nr*nr;++pair){
  int i=pair/nr,j=pair%nr;if(i==j)continue;
  int tid=omp_get_thread_num();auto& N=NN[tid];auto& V=VV[tid];auto& M=MN[tid];auto& X=MV[tid];
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
   int a=0,b=0,bl=0,br=0;
   for(size_t s=0;s+1<cut.size();++s){
    double l=cut[s],r=cut[s+1];if(r<=l)continue;
    double y=(l+r)/2,h=(r-l)/2,xm=std::exp(y),xpm=xm*ex;
    double qi=xm/d[i],qj=xpm/d[j];
    while(a+1<nc&&qi>=e[a+1])++a;
    while(b+1<nc&&qj>=e[b+1])++b;
    if(qi<e[0]||qi>e[nc]||qj<e[0]||qj>e[nc])fail=1;
    while(bl+1<nb&&y>=cuts[bl+1])++bl;
    while(br+1<nb&&y+eta>=cuts[br+1])++br;
    long double mass=0,center=0;
    for(int g=0;g<ngl;++g){
     double dx=xm*std::expm1(h*zl[g]),x=xm+dx,xp=x*ex;
     double q=x/d[i],qp=xp/d[j];
     double ri=w0[i]/(d[i]*d[i]*d[i]*w[i])/std::expm1(q),rj=w0[j]/(d[j]*d[j]*d[j]*w[j])/std::expm1(qp);
     double di=ri*(A[i*nc+a]+B[i*nc+a]*(q-cc[a])/hh[a]),dj=rj*(A[j*nc+b]+B[j*nc+b]*(qp-cc[b])/hh[b]);
     double dg=x*em/tr;
     double C=K*wh[z]*h*wl[g]*std::min(x*x*x,xp*xp*xp*std::exp(-dg));
     long double ddi=ri*(dA[i*nc+a]+dB[i*nc+a]*(q-cc[a])/hh[a]),ddj=rj*(dA[j*nc+b]+dB[j*nc+b]*(qp-cc[b])/hh[b]);
     long double ddg=-(long double)dg*dtr/tr;
     long double v1=x*x*x,v2=xp*xp*xp*std::exp(-dg);
     long double dC=(v2<v1 || (v2==v1 && ddg>0))?-(long double)C*ddg:0;
     long double Q=(long double)dj*(1+ri)+(long double)rj*di+(long double)di*dj;
     long double dQ=ddj*(1+ri+di)+ddi*(rj+dj);
     long double F=dC*((long double)di-dj-std::expm1(dg)*Q)+(long double)C*(ddi-ddj-std::exp(dg)*ddg*Q-std::expm1(dg)*dQ);
     mass+=F;center+=F*dx;raw[tid]+=F*x*em;ab[tid]+=std::abs(F);
    }
    // Direct pair contributions, exactly the same integral as reference.
    N[i*nc+a]-=mass;V[i*nc+a]-=mass*(xm/d[i]-cc[a])+center/d[i];
    N[j*nc+b]+=mass;V[j*nc+b]+=mass*(xpm/d[j]-cc[b])+center*ex/d[j];
    // Common-bin signed angular mean: postpone its per-ray projection.
    M[bl]+=mass;X[bl]+=mass*(xm-xc[bl])+center;
    M[br]-=mass;X[br]-=mass*(xpm-xc[br])+center*ex;
   }
  }
 }
 if(fail)return 1;
 // Every physical bin is bounded by all mapped canonical edges. The
 // same mass/first moment therefore projects exactly to each ray cell.
 std::vector<long double> M(nb,0),X(nb,0);
 for(int j=0;j<nb;++j)for(int t=0;t<threads;++t){M[j]+=MN[t][j];X[j]+=MV[t][j];}
 for(int k=0;k<nr;++k){
  int a=0;
  for(int j=0;j<nb;++j){
   double q=xc[j]/d[k];while(a+1<nc&&q>=e[a+1])++a;
   if(q<e[0]||q>e[nc])return 1;
   NN[0][k*nc+a]+=w[k]*M[j];VV[0][k*nc+a]+=w[k]*(M[j]*(q-cc[a])+X[j]/d[k]);
  }
 }
 long double ns=0,us=0,nl=0,ul=0,vl=0;for(int k=0;k<L;++k){long double a=0,b=0;for(int t=0;t<threads;++t){a+=NN[t][k];b+=VV[t][k];}outN[k]=a;outV[k]=b;long double u=(b+a*cc[k%nc])*d[k/nc];ns+=a;us+=u;nl+=std::abs(a);ul+=std::abs(u);vl+=std::abs(b);}
 long double R=0,F=0;for(int t=0;t<threads;++t){R+=raw[t];F+=ab[t];}
 diag[0]=std::abs(ns)/std::max(nl,1.e-300L);diag[1]=std::abs(us)/std::max(ul,1.e-300L);diag[2]=R;diag[3]=F;diag[4]=nl;diag[5]=vl;return 0;
}
