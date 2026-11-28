#include "../closure/c3b_reference.hpp"
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace c3b;
void put(std::ostream&o,const char*name,const Interval&i,bool comma=true){o<<'"'<<name<<"\":{\"lo\":\""<<i.lo<<"\",\"hi\":\""<<i.hi<<"\"}"<<(comma?",\n":"\n");}
int main(int argc,char**argv){try{
if(argc!=2)throw Error("OUTPUT_ARGUMENT_REQUIRED");
Mat o=c3a::eye(2),q(2,1);q(0,0)=q(1,0)=1;auto p=c3a::project(o,c3a::columns(2,{0}));auto e=c3a::compress(o,p,q);Mat a(1,1);a(0,0)=1;
R pop=c3a::probability(e.metric,e.covariant,a);if(pop!=R(1)/2||e.is_projector)throw Error("C3A_EFFECT_BRIDGE");
Key key{"manufactured_not_HH","ion_pair","singlet","matter_rest","analytic_fixture"};
// The fixture DEFINITION is constant population on an entire disk, not a sample extrapolation.
auto area=annuli(key,{{"disk",key,0,4,{pop,pop}}},4,ImpactTail{"b-tail",key,4,{0,0}});
if(!area.full)throw Error("FIXTURE_AREA_MISSING");
auto thermal=maxwell(key,{{"energy",key,0,1,*area.full}},1,EnergyTail{"E-tail",key,1,*area.full});if(!thermal.full)throw Error("FIXTURE_THERMAL_MISSING");
auto rate=rate_si(*thermal.full,{2},{3});auto events=scale(rate,2); // n=2, n²/2=2
c3a::require_event_conservation(c3a::event(c3a::EventKind::IonPair));
std::ofstream out(argv[1]);if(!out)throw Error("CANNOT_WRITE_RESULT");
out<<"{\"fixture\":\"manufactured_SI_not_HH\",\"scientific_admission\":false,\"actual_HH_calls\":0,\"raw_norm\":\"2\",\"raw_weight\":\"1\",\"population\":\"1/2\",\"reduced_operator_is_projector\":false,\n";
put(out,"sigma_over_pi_m2",*area.full);put(out,"maxwell_integral_m2",*thermal.full);put(out,"rate_m3_s",rate);put(out,"event_rate_m_minus3_s_minus1",events);put(out,"free_electron_source",{0,0},false);out<<"}\n";out.close();
std::cout<<"PASS end_to_end_conditional_effect_to_rate TOTAL 1 FAILED 0\n";
// Independent speed-variable Simpson checks: diagnostic floating arithmetic only.
int failures=0;for(int cutoff:{0,1,4,9}){
 const unsigned n=65536;long double lo=std::sqrt(static_cast<long double>(cutoff)),hi=12,h=(hi-lo)/n;
 auto f=[](long double x){return 2*x*x*x*std::exp(-x*x);};
 long double sum=f(lo)+f(hi);for(unsigned j=1;j<n;++j)sum+=(j%2?4:2)*f(lo+j*h);sum*=h/3;
 auto exact=maxwell_weight(R(cutoff),std::nullopt);long double target=((exact.lo+exact.hi)/2).convert_to<long double>();
 long double error=std::abs(sum-target);bool ok=error<1e-12L;failures+=!ok;
 std::cout<<(ok?"PASS":"FAIL")<<" NUMERIC_SPEED_INTEGRAL cutoff="<<cutoff<<" abs_error="<<std::setprecision(12)<<error<<" evaluations="<<n+1<<'\n';
}
std::cout<<"NUMERICAL_DIAGNOSTICS 4 FAILED "<<failures<<'\n';return failures?1:0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
