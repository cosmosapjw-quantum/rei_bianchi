// Independent quadrature: 4-point cone source rows, Simpson, long double.
// Not an independent researcher; no outward-error certification.
#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>

constexpr long double pi=3.141592653589793238462643383279502884L;
constexpr std::array<long double,4> theta{46.L,61.L,73.L,87.L};
constexpr std::array<long double,4> lower{0.11L,0.11L,0.02L,0.14L};
constexpr std::array<long double,4> upper{0.17L,0.21L,0.12L,0.24L};
long double cone(long double th,long double L,bool isupper){
    long double val=isupper?1e6L:0.L;
    for(std::size_t i=0;i<4;i++){
        const long double delta=L*std::fabs(th-theta[i]);
        const long double cur=isupper?upper[i]+delta:lower[i]-delta;
        val=isupper?std::min(val,cur):std::max(val,cur);
    }
    return val;
}
long double F(long double b,long double L,bool maximize){
    constexpr int n=32768; // even
    const long double h=90.L/n;
    long double s=0;
    for(int i=0;i<=n;i++){
        long double x=i*h, z=x*pi/180.L;
        bool pos=(std::cos(z)*std::cos(z)>=b);
        bool useupper=(maximize==pos);
        long double f=cone(x,L,useupper);
        long double term=(std::cos(z)*std::cos(z)-b)*std::sin(z)*f*pi/180.L;
        s+=((i==0||i==n)?1.L:((i&1)?4.L:2.L))*term;
    }
    return s*h/3.L;
}
long double root(long double L,bool maximize){
    long double lo=0,hi=1;
    for(int i=0;i<56;i++){
        long double mid=(lo+hi)/2;
        if(F(mid,L,maximize)>=0)lo=mid;
        else hi=mid;
    }
    return (lo+hi)/2;
}
int main(){
    std::cout<<std::setprecision(18);
    for(long double L:{1.L/700.L,1.L/200.L,1.L/100.L})
        std::cout<<L<<" "<<root(L,false)<<" "<<root(L,true)<<"\n";
}
