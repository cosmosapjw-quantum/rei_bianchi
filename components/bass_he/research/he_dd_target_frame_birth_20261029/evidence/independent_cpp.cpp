// Independent decimal100 four-vector check; not a distinct-author R6/C9 review.
#include <boost/multiprecision/cpp_dec_float.hpp>
#include <iostream>
#include <array>
#include <iomanip>
#include <string>
using boost::multiprecision::cpp_dec_float_100;
int main() {
    using V=cpp_dec_float_100;
    const V M("3727.3794118"), m("1875.61294500");
    V maxerr=0;
    for (const char* estr : {"213", "330"}) {
        V E(estr), s=M*M+2*M*E, sq=sqrt(s),q=sqrt(s-4*m*m)/2;
        for(const char* mstr : {"-1", "0", "0.3333333333333333333333333333333333333333333333333333333333333333", "1"}) {
            V mu(mstr), gamma=(M+E)/sq;
            V Ep=(M+E)/2+E*q*mu/sq;
            V Em=(M+E)/2-E*q*mu/sq;
            V pzp=E/2+gamma*q*mu, pzm=E/2-gamma*q*mu;
            V pt2=q*q*(1-mu*mu);
            for(V res:std::array<V,5>{V(Ep*Ep-pzp*pzp-pt2-m*m),V(Em*Em-pzm*pzm-pt2-m*m),
                           V(Ep+Em-(M+E)),V(pzp+pzm-E),V((Ep-m)+(Em-m)-(M+E-2*m))}){
                auto a=abs(res);if(a>maxerr)maxerr=a;
            }
        }
    }
    std::cout<<std::scientific<<std::setprecision(30)<<maxerr<<"\n";
    return maxerr<V("1e-75")?0:1;
}
