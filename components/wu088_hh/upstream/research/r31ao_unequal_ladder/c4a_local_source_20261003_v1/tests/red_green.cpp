#include "../closure/c4a_source.hpp"
#include <functional>
#include <iostream>
#include <map>
using namespace c4a;
void ck(bool x,const char*m){if(!x)throw Error(std::string("ASSERTION: ")+m);}
template<class F>void rejects(F f){bool caught=false;try{f();}catch(const Error&){caught=true;}ck(caught,"required rejection absent");}
int main(){
 State s; s.n={4,0,1,1,2,1,0,1,0};s.u=15;s.nt_comoving=true;
 EnergyModel em{"fixture-energy",10,3,20,30,2};
 auto ip=[&](){return hh(c3a::EventKind::IonPair,s,em,Interval(1,2),Gains{-7,0,0,0,0,0,0},"fixture:ip");};
 std::map<std::string,std::function<void()>>t;
 t["pair_source_counts"]= [&](){auto x=species(assemble(s,em,{ip()}));ck(x[0].lo==-4&&x[0].hi==-2&&x[3].lo==1&&x[3].hi==2,"ion pair multiplicity");};
 t["shared_uncertainty_preserves_charge"]= [&](){auto x=linear_count(assemble(s,em,{ip()}),Q);ck(x.lo==0&&x.hi==0,"same rate variable must cancel");};
 t["hidden_hminus_rejected"]= [&](){rejects([&](){require_bare_legacy(assemble(s,em,{ip()}));});};
 t["net_electron_source"]= [&](){auto p=he("EI_HI",-1,2,s,em,Interval(3,3),std::nullopt,"fixture:ei");auto x=species(assemble(s,em,{p}));ck(x[7].lo==-3&&x[8].lo==6,"net thermal vs fast electrons");};
 t["temperature_composition"]= [&](){auto p=he("PI_HI",1,0,s,em,Interval(1,1),Gains{0,0,0,0,0,-10,0},"fixture:pi");auto x=temperature_rate(assemble(s,em,{p}),R(1));ck(x.lo==R(-1)/10&&x.hi==R(-1)/10,"composition term");};
 t["missing_energy_not_zero"]= [&](){auto p=ip();p.gains.reset();rejects([&](){require_energy(assemble(s,em,{p}));});};
 t["duplicate_semantic_owner"]= [&](){auto p=ip(),q=ip();q.source="different-name";rejects([&](){(void)assemble(s,em,{p,q});});};
 t["physical_source_unavailable"]= [&](){rejects([](){require_physical();});};
 int f=0;for(auto&[n,fn]:t){try{fn();std::cout<<"PASS "<<n<<'\n';}catch(const std::exception&e){++f;std::cout<<"FAIL "<<n<<" "<<e.what()<<'\n';}}std::cout<<"TOTAL "<<t.size()<<" FAILED "<<f<<'\n';return f?1:0;
}
