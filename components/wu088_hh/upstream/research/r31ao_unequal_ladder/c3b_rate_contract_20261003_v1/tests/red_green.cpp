#include "../closure/c3b_reference.hpp"
#include <iostream>
#include <map>
#include <functional>
using namespace c3b;
void ck(bool ok,const char*why){if(!ok)throw Error(why);}
Key k(){return {"manufactured","ion_pair","singlet","matter_rest","synthetic"};}
int main(){std::map<std::string,std::function<void()>> t;
t["endpoint_error_ownership"]=[]{auto p=outgoing_bound({R(2)/5,R(2)/5},{R(1)/100,R(1)/100,0,R(1)/100,{"prep","num","effect","tail"}});ck(p.lo==R(7)/20&&p.hi==R(9)/20,"ASSERT endpoint must propagate norm and tail bounds");};
t["whole_annulus_and_tail"]=[]{auto a=annuli(k(),{{"a",k(),0,4,{R(1)/2,R(1)/2}}},4,ImpactTail{"tail",k(),4,{0,1}});ck(a.full.has_value()&&a.full->lo==2&&a.full->hi==3,"ASSERT integral is sigma/pi, not point sum");};
t["missing_spin_is_not_zero"]=[]{bool no=false;try{(void)spin_average({{"S",R(1)/4,Interval{1,1}},{"T",R(3)/4,std::nullopt}});}catch(const SourceUnavailable&){no=true;}ck(no,"ASSERT positive-weight missing triplet must not disappear");};
t["identical_population_factor"]=[]{ck(event_density_rate(3,{2},{2},PairKind::SamePopulation)==6,"ASSERT identical pairs count once");};
t["relative_not_lab_energy"]=[]{ck(relative_energy_from_lab({10},{1},{1}).value==5,"ASSERT equal-mass relative energy is half lab energy");};
t["maxwell_constant_cross_section"]=[]{auto a=maxwell(k(),{{"e",k(),0,1,{2,2}}},1,EnergyTail{"outer",k(),1,{2,2}});ck(a.full.has_value()&&a.full->lo<=2&&a.full->hi>=2&&a.full->hi-a.full->lo<R(1)/1000000,"ASSERT normalized Maxwell kernel integrates constant exactly up to enclosure");};
t["discrete_anisotropic_functional"]=[]{auto a=discrete_rate_over_pi(k(),{{"x",k(),R(1)/2,2,{1,1}},{"y",k(),R(1)/2,2,{3,3}}});ck(a.lo==4&&a.hi==4,"ASSERT orientation weights retained");};
t["pi_rigorous_enclosure"]=[]{auto a=pi_bound();ck(a.lo>R(314159)/100000&&a.hi<R(314160)/100000,"ASSERT Machin series must bound pi");};
int bad=0;for(auto&[name,f]:t){try{f();std::cout<<"PASS "<<name<<'\n';}catch(const std::exception&e){++bad;std::cout<<"FAIL "<<name<<' '<<e.what()<<'\n';}}std::cout<<"TOTAL "<<t.size()<<" FAILED "<<bad<<'\n';return bad?1:0;}
