// Independently formulated exact rational 2-point and marked-count checks.
// No real detector data, no rate or heating claims.
#include <boost/multiprecision/cpp_int.hpp>
#include <boost/rational.hpp>
#include <cassert>
#include <iostream>
using Z=boost::multiprecision::cpp_int;
using Q=boost::rational<Z>;
Q f(long n,long d=1){return Q(Z(n),Z(d));}
int main(){
  long verified=0;
  for(int plus=1;plus<=11;plus++)for(int minus=1;minus<=11;minus++)
   for(int abs_mu=1;abs_mu<=9;abs_mu++){
    Q qp=f(plus),qm=f(minus),x=f(abs_mu,10);
    Q mu=x*(qp-qm)/(qp+qm),b=x*x;
    Q r=plus>=minus? f(plus,minus):f(minus,plus);
    Q eta=(r-f(1))/(r+f(1));
    assert(mu*mu<=eta*eta*b);
    assert(b-mu*mu >= (f(1)-eta*eta)*b);
    Q k0=f(15),delta=f(3),lambda=f(3),nu=f(3);
    Q v=delta*delta*(b-mu*mu);
    Q yplus=k0+delta*mu,yminus=k0-delta*mu;
    Q cross=-lambda*v+nu*yplus*yminus;
    Q cross_p=lambda*(k0*k0-delta*delta*b);
    assert(cross==cross_p);
    verified++;
   }
  std::cout<<"CPP_PASS exact-rational examples="<<verified<<"\n";
}
