#include <cmath>
#include <vector>
#include <array>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <algorithm>
#include <stdexcept>
struct Step{double a,b,dt,birth,hi,hei,heii;};
double sigma(double E,int i){
 const double fit[3][8]={{13.60,.4298,5.475e4,32.88,2.963,0,0,0},{24.59,13.61,949.2,1.469,3.188,2.039,.4434,2.136},{54.42,1.720,1.369e4,32.88,2.963,0,0,0}};
 const auto*p=fit[i];if(E<p[0])return 0;
 double x=E/p[1]-p[6],y=std::hypot(x,p[7]);
 return 1e-18*p[2]*((x-1)*(x-1)+p[5]*p[5])*std::pow(y,p[4]/2-5.5)*std::pow(1+std::sqrt(y/p[3]),-p[4]);
}
double scale(double a,double b,double m){return (1./21)/a*std::sqrt((1-m*m)*std::exp(2*b)+m*m*std::exp(-4*b));}
int main(int argc,char**argv){
 if(argc!=5)return 2;
 std::ifstream f(argv[1]);std::vector<Step> t;Step r;while(f>>r.a>>r.b>>r.dt>>r.birth>>r.hi>>r.hei>>r.heii)t.push_back(r);
 std::ifstream g(argv[2]);std::vector<double> mu,w;double m,j;while(g>>m>>j){mu.push_back(m);w.push_back(j);}
 int nq=std::stoi(argv[3]);double bf=std::stod(argv[4]);double dq=std::log(767.7437846466551/6.8)/nq;
 std::vector<double> q(nq),qw(nq);for(int i=0;i<nq;i++){double lo=6.8*std::exp(dq*i),hi=6.8*std::exp(dq*(i+1));q[i]=(lo+hi)/2;qw[i]=hi-lo;}
 int n=mu.size();std::vector<double> norms(t.size());
 for(size_t k=0;k<t.size();k++){double sum=0;for(int j=0;j<n;j++){double R=scale(t[k].a,t[k].b,mu[j]);sum+=w[j]*std::pow((1./21)/t[k].a/R,3);}norms[k]=sum;}
 std::vector<std::array<double,5>> out(n);
 #pragma omp parallel for num_threads(4)
 for(int j=0;j<n;j++){
  std::vector<double> N(nq,0),shape(nq);double emittedE=0,emittedN=0;
  for(size_t k=0;k<t.size();k++){
   auto s=t[k];double R=scale(s.a,s.b,mu[j]),w0=w[j]*std::pow((1./21)/s.a/R,3)/norms[k],den=0;
   for(int i=0;i<nq;i++){double e=q[i]*R;shape[i]=(e>=13.6&&e<=100)?e*e/std::expm1(e/(8.617333262145e-5*50000))*R*qw[i]:0;den+=shape[i];}
   if(den<=0)throw std::runtime_error("no source support");
   for(int i=0;i<nq;i++){
    double e=q[i]*R,birth=s.birth*w0*shape[i]/den;double tau=2.99792458e10*s.dt*(s.hi*sigma(e,0)+s.hei*sigma(e,1)+s.heii*sigma(e,2));
    double surv=std::exp(-tau),gain=tau>0?-std::expm1(-tau)/tau:1.;
    N[i]=N[i]*surv+birth*gain;emittedE+=birth*e;emittedN+=birth;
   }
  }
  double R=scale(.2,bf,mu[j]),m=mu[j]*std::exp(-2*bf)*(1./21)/.2/R,Ntot=0,U=0;
  for(int i=0;i<nq;i++){Ntot+=N[i];U+=N[i]*q[i]*R;}
  out[j]={Ntot,U,U*(3*m*m-1)/2,emittedN,emittedE};
 }
 std::array<double,5> s{};for(auto a:out)for(int i=0;i<5;i++)s[i]+=a[i];
 std::cout<<std::setprecision(17)<<"nmu,nq,nt,N,J0,J2,source_N,source_U\n"<<n<<","<<nq<<","<<t.size();for(double x:s)std::cout<<","<<x;std::cout<<"\n";
}
