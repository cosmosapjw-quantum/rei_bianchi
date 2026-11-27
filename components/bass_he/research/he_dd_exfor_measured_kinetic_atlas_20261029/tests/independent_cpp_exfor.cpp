// Independently parse original M0475 and verify high precision two-body mass shell.
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <cmath>
#include <stdexcept>
using H=boost::multiprecision::cpp_dec_float_100;
int main(int argc, char**argv){
 if(argc!=2) throw std::runtime_error("Expected original M0475.x4 path");
 std::ifstream in(argv[1]);if(!in)throw std::runtime_error("source missing");
 const H M("3727.3794118"),m("1875.61294500"),Q=2*m-M;
 const H pi=acos(H(-1));
 const H thr=((2*m)*(2*m)-M*M)/(2*M);
 if(abs(thr-Q-Q*Q/(2*M))>H("1e-80"))throw std::runtime_error("threshold identity");
 std::string line,sub;int remaining=0,headerSkip=0,da=0,sig=0;
 H maxShell=0,maxKPair=0;
 while(std::getline(in,line)){
  if(line.rfind("SUBENT",0)==0){std::istringstream ss(line);std::string tag;ss>>tag>>sub;}
  if(line.rfind("DATA ",0)==0){std::istringstream ss(line);std::string tag;int cols=0;ss>>tag>>cols>>remaining;headerSkip=2;
   if((sub=="M0475002"&&cols!=4)||(sub=="M0475003"&&cols!=3))throw std::runtime_error("bad grid");
   continue;}
  if(headerSkip>0){--headerSkip;continue;}
  if(remaining<=0)continue;
  --remaining;
  std::istringstream ss(line);std::string st,sa,sv,se;ss>>st>>sa>>sv;
  H E(st);
  if(sub=="M0475002"){
   ss>>se;
   if(se.empty())throw std::runtime_error("DA parsing");
   H angle(sa),v(sv),err(se);
   if(!(E>thr&&angle>=0&&angle<=180&&v>=0&&err>=0))throw std::runtime_error("invalid DA physical range");
   H s=M*M+2*M*E,q=sqrt(s/4-m*m),beta=E/(M+E),gamma=(M+E)/sqrt(s);
   H mu=cos(pi*angle/180),sinx=sin(pi*angle/180);
   H K0=(M+E)/2-m,delta=beta*gamma*q;
   H Eplus=m+K0+delta*mu,Eminus=m+K0-delta*mu;
   H zplus=E/2+gamma*q*mu,zminus=E/2-gamma*q*mu;
   H px=q*sinx;
   H rr1=abs(Eplus*Eplus-zplus*zplus-px*px-m*m),rr2=abs(Eminus*Eminus-zminus*zminus-px*px-m*m);
   if(rr1>maxShell)maxShell=rr1;
   if(rr2>maxShell)maxShell=rr2;
   H rr3=abs((Eplus-m)+(Eminus-m)-(E-Q));if(rr3>maxKPair)maxKPair=rr3;
   if(rr1>H("1e-70")||rr2>H("1e-70")||rr3>H("1e-70"))throw std::runtime_error("four-vector residual");
   ++da;
   if(E==330&&angle==46)std::cout<<std::setprecision(55)<<"K330_46="<<(Eplus-m)<<","<<(Eminus-m)<<"\n";
  }else if(sub=="M0475003"){
   H v(sa),err(sv);
   if(E==330)throw std::runtime_error("330MeV SIG must not be claimed measured");
   if(!(E>thr&&v>=0&&err>=0))throw std::runtime_error("invalid SIG row");
   H weighted=v*(E-Q);
   H weightedError=err*(E-Q);
   if(weighted<0||weightedError<0)throw std::runtime_error("negative kinetic weight");
   
   ++sig;
  }
 }
 if(da!=12||sig!=6)throw std::runtime_error("source row counts mismatch");
 std::cout<<std::setprecision(28)<<"CPP_PASS DA="<<da<<" SIG="<<sig<<" threshold_MeV="<<thr
    <<" max_mass_shell_MeV2="<<maxShell<<" max_Kpair_MeV="<<maxKPair<<"\n";
}
