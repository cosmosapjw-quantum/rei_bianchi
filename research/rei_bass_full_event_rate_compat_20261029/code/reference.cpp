#include <array>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
struct Row{long double z,h,he,he2;};
static long double det3(const std::array<Row,3>& r){
  const auto& a=r[0]; const auto& b=r[1]; const auto& c=r[2];
  return a.h*(b.he*c.he2-b.he2*c.he)
       -a.he*(b.h*c.he2-b.he2*c.h)
       +a.he2*(b.h*c.he-b.he*c.h);
}
int main(int argc,char** argv){
  if(argc!=2){std::cerr<<"usage: reference RATES_11.tsv\n";return 2;}
  std::ifstream in(argv[1]); if(!in){std::cerr<<"input missing\n";return 2;}
  std::vector<Row> v;Row a{};
  while(in>>a.z>>a.h>>a.he>>a.he2){
    if(!(a.h>0 && a.he>0 && a.he2>0))return 3;
    v.push_back(a);
  }
  if(v.size()!=11){std::cerr<<"expected 11 source rows\n";return 3;}
  auto find=[&](long double z){for(auto r:v)if(std::abs(r.z-z)<1e-12L)return r;throw std::runtime_error("required knot missing");};
  const auto first=find(2.48L),mid=find(3.64L),last=find(4.62L);
  const auto r1=first.he2/first.h,r2=last.he2/last.h;
  const auto rmax=std::max(r1,r2), rmin=std::min(r1,r2);
  const auto amax=std::sqrt(rmax),amin=std::sqrt(rmin);
  const auto k=amax*amin;
  const auto worst=(amax-amin)/(amax+amin);
  const auto t_hi=2*rmax/(rmax+k),t_lo=2*rmin/(rmin+k);
  const auto e_hi=std::max(std::abs(t_hi-1.L),std::abs(t_hi*k/rmax-1.L));
  const auto e_lo=std::max(std::abs(t_lo-1.L),std::abs(t_lo*k/rmin-1.L));
  auto determinant=det3({first,mid,last});
  std::cout<<std::setprecision(24);
  std::cout<<"RATIO_FACTOR "<<(rmax/rmin)<<"\n";
  std::cout<<"OPTIMAL_K "<<k<<"\n";
  std::cout<<"MINIMAX_REL "<<worst<<"\n";
  std::cout<<"ATTAINED_HIGH "<<e_hi<<"\n";
  std::cout<<"ATTAINED_LOW "<<e_lo<<"\n";
  std::cout<<"DETERMINANT3_E36 "<<determinant*1e36L<<"\n";
  if(!std::isfinite(static_cast<double>(worst))||worst<=0||std::abs(e_hi-worst)>1e-15L||std::abs(e_lo-worst)>1e-15L||determinant==0){std::cerr<<"independent C++ check failed\n";return 4;}
  return 0;
}
