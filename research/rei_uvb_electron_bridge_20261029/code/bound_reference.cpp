// Independent long-double oracle for seven source-only T-event upper bounds.
// No ODE/IVP, no physical tau. Compare a T event within common HI triplet.
#include <cmath>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
int main(int argc, char** argv) {
 if (argc!=2) return 2;
 std::ifstream is(argv[1]);if (!is) return 3;
 std::string s;int n=0;long double maxrel=0;
 std::cout << std::setprecision(22);
 while(std::getline(is,s)) {
   if(s.empty() || s[0]=='#')continue;
   std::istringstream line(s);
   long double z,h,d,t,reference;
   if(!(line>>z>>h>>d>>t>>reference))return 4;
   if(!(h>0) || !(d>=0) || !(t>0) || !(reference>0))return 5;
   const long double e=t/(h+d+t);
   const long double rel=std::abs((e-reference)/reference);
   if (rel>5e-16L) return 6;
   maxrel=std::max(maxrel,rel);n++;
   std::cout << z << '\t' << e << '\t' << rel << '\n';
 }
 if(n!=7) return 7;
 std::cerr << "CPP_PASS rows=" << n << " max_relative=" << maxrel << "\n";
 return 0;
}
