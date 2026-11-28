#include "../closure/c3b_reference.hpp"
#include <functional>
#include <iostream>
#include <map>
#include <type_traits>
static_assert(!std::is_convertible_v<c3b::ImpactTail,c3b::EnergyTail>);
using namespace c3b;
void ck(bool ok,const char*m){if(!ok)throw Error(m);}
template<class F>void reject(F f){bool caught=false;try{f();}catch(const Error&){caught=true;}ck(caught,"INVALID INPUT ACCEPTED");}
Key key(){return {"fixture","pair","singlet","matter_rest","reference"};}
Cell cell(R a,R b,Interval p){return {"cell",key(),a,b,p};}
int main(){std::map<std::string,std::function<void()>> t;
t["diagonal_long_range_phase_cancels"]=[]{Mat a(2,2),g(2,2);a(0,0)=1;g(0,0)=C(0,2);g(1,1)=C(0,3);ck(c3a::zero(observable_derivative(a,Mat(2,2),g)),"commuting phase spuriously changes populations");};
t["offdiagonal_commutator_sign"]=[]{Mat a(2,2),g(2,2),expected(2,2);a(0,0)=1;g(0,1)=1;g(1,0)=-1;expected(0,1)=expected(1,0)=1;ck(observable_derivative(a,Mat(2,2),g)==expected,"wrong commutator sign");};
t["moving_effect_derivative_kept"]=[]{Mat a(2,2),d(2,2);a(0,0)=a(1,1)=C(R(1)/2);d(0,1)=d(1,0)=1;ck(observable_derivative(a,d,Mat(2,2))==d,"moving observable omitted");};
t["invalid_generator_or_effect"]=[]{Mat a(2,2),g(2,2);a(0,0)=2;reject([&]{(void)observable_derivative(a,Mat(2,2),g);});a(0,0)=1;g(0,0)=1;reject([&]{(void)observable_derivative(a,Mat(2,2),g);});};
t["tail_inverse_square"]=[]{ck(inverse_square_tail(3,4)==R(3)/4,"tail integral");reject([]{(void)inverse_square_tail(1,0);});};
t["raw_probability_not_clipped"]=[]{Errors e{0,0,0,0,{"a","b","c","d"}};reject([&]{(void)outgoing_bound({-1,1},e);});reject([&]{(void)outgoing_bound({0,2},e);});};
t["a_priori_range_intersection"]=[]{auto p=outgoing_bound({R(1)/2,R(1)/2},{1,0,0,0,{"a","b","c","d"}});ck(p.lo==0&&p.hi==1,"valid error enlargement intersection");};
t["duplicate_error_budget"]=[]{reject([]{(void)outgoing_bound({0,0},{0,0,0,0,{"same","same","c","d"}});});};
t["negative_error_rejected"]=[]{reject([]{(void)outgoing_bound({0,0},{-1,0,0,0,{"a","b","c","d"}});});};
t["missing_tail_stays_partial"]=[]{auto r=annuli(key(),{cell(0,1,{1,1})},1,std::nullopt);ck(!r.full&&r.partial.lo==1,"missing b tail became zero");};
t["finite_gap_stays_partial"]=[]{auto r=annuli(key(),{cell(1,4,{1,1})},4,ImpactTail{"tail",key(),4,{0,0}});ck(!r.full&&r.gaps.size()==1&&r.gaps[0].first==0&&r.gaps[0].second==1,"gap lost");};
t["point_sample_not_whole_cell"]=[]{auto c=cell(0,1,{1,1});c.meaning=Meaning::PointSample;reject([&]{(void)annuli(key(),{c},1,std::nullopt);});};
t["overlap_duplicate_and_outside"]=[]{auto a=cell(0,2,{0,1}),b=cell(1,3,{0,1});b.id="second";reject([&]{(void)annuli(key(),{a,b},3,std::nullopt);});reject([&]{(void)annuli(key(),{a,a},3,std::nullopt);});reject([&]{(void)annuli(key(),{a},1,std::nullopt);});};
t["source_and_tail_binding"]=[]{auto a=cell(0,1,{0,1});a.key.spin="triplet";reject([&]{(void)annuli(key(),{a},1,std::nullopt);});reject([]{(void)annuli(key(),{cell(0,1,{0,1})},1,ImpactTail{"tail",key(),2,{0,1}});});};
t["b_squared_jacobian"]=[]{auto a=cell(0,1,{1,1}),b=cell(1,9,{R(1)/2,R(1)/2});b.id="outer";auto r=annuli(key(),{b,a},9,ImpactTail{"tail",key(),9,{0,0}});ck(r.full&&r.full->lo==5&&r.full->hi==5,"missing pi or radial Jacobian");};
t["spin_weights_and_zero_missing"]=[]{auto r=spin_average({{"s",1,Interval{2,2}},{"t",0,std::nullopt}});ck(r.lo==2,"zero-weight sector");reject([]{(void)spin_average({{"s",2,Interval{2,2}}});});reject([]{(void)spin_average({{"s",1,Interval{1,1}},{"s",0,std::nullopt}});});};
t["explicit_spin_mixture"]=[]{auto r=spin_average({{"s",R(1)/4,Interval{4,4}},{"t",R(3)/4,Interval{8,8}}});ck(r.lo==7&&r.hi==7,"spin mixture");};
t["distinct_beams_not_identical_population"]=[]{ck(event_density_rate(3,{2},{2},PairKind::DistinctPopulations)==12,"distinct beams factor");reject([]{(void)event_density_rate(1,{2},{3},PairKind::SamePopulation);});};
t["stoichiometry_separate_from_pair_count"]=[]{auto nu=c3a::event(c3a::EventKind::IonPair).change;R events=event_density_rate(3,{2},{2},PairKind::SamePopulation);ck(R(nu[0])*events==-12&&R(nu[4])*events==0,"particle loss or electrons counted twice");};
t["mass_and_energy_scaling"]=[]{ck(reduced_mass({2},{6}).value==R(3)/2,"reduced mass");ck(relative_energy_from_speed(4,{2},{6}).value==12,"relative E");ck(relative_energy_from_lab({16},{2},{6}).value==12,"target-rest lab conversion");reject([]{(void)reduced_mass({0},{1});});};
t["threshold_not_driven_clipping"]=[]{reject([]{(void)closed_channel_open({1},{2},EnergyLaw::PrescribedTrajectory);});ck(!closed_channel_open({1},{2},EnergyLaw::ClosedTwoBody),"closed endothermic");ck(closed_channel_open({0},{-1},EnergyLaw::ClosedTwoBody),"exothermic clipped");ck(closed_channel_open({2},{2},EnergyLaw::ClosedTwoBody),"threshold equality");};
t["exp_and_sqrt_exact_limits"]=[]{auto z=exp_minus(0);ck(z.lo==1&&z.hi==1,"exp0");auto q=sqrt_point(4);ck(q.lo==2&&q.hi==2,"sqrt4");auto s=sqrt_point(2);ck(s.lo*s.lo<=2&&s.hi*s.hi>=2,"sqrt rational bounds");};
t["exp_monotone_and_composition"]=[]{auto a=exp_minus(R(1)/2),b=exp_minus(1),aa=product(a,a);ck(a.lo>b.hi,"monotone exp");ck(aa.lo<=b.hi&&b.lo<=aa.hi,"independent exp squaring overlap");ck(b.hi-b.lo<R(1)/R(boost::multiprecision::cpp_int(1)<<100),"exp width");};
t["reference_budget_not_physical_domain"]=[]{reject([]{(void)exp_minus(17);});reject([]{(void)exp_minus(-1);});};
t["pi_and_maxwell_partition"]=[]{auto p=pi_bound();ck(p.lo>R(333)/106&&p.hi<R(355)/113,"pi rational bounds");auto a=maxwell_weight(0,R(1)),b=maxwell_weight(1,std::nullopt);auto w=add(a,b);ck(w.lo<=1&&w.hi>=1,"Maxwell mass normalization");};
t["thermal_missing_energy_tail"]=[]{auto r=maxwell(key(),{cell(0,1,{1,1})},1,std::nullopt);ck(!r.full,"missing energy range set zero");};
t["manufactured_threshold_shape"]=[]{auto a=cell(0,1,{0,0}),b=cell(1,2,{1,1});b.id="above";auto r=maxwell(key(),{a,b},2,EnergyTail{"tail",key(),2,{1,1}});auto truth=scale(exp_minus(1),2);ck(r.full&&r.full->lo<=truth.hi&&truth.lo<=r.full->hi,"threshold fixture functional");};
t["distribution_not_renormalized"]=[]{reject([]{(void)discrete_rate_over_pi(key(),{{"x",key(),R(1)/2,1,{1,1}}});});};
t["second_moment_is_not_distribution"]=[]{auto a=discrete_rate_over_pi(key(),{{"slow",key(),R(2)/3,1,{1,1}},{"fast",key(),R(1)/3,5,{1,1}}});auto b=discrete_rate_over_pi(key(),{{"mono",key(),1,3,{1,1}}});ck(R(2)/3+R(25)/3==9&&a.lo==R(7)/3&&b.lo==3,"same energy moment can have different rate");};
t["si_rate_scaling"]=[]{auto k=rate_si({2,2},{2},{3}),k4=rate_si({2,2},{2},{12});ck(k4.lo<=2*k.hi&&k4.hi>=2*k.lo,"sqrt temperature scaling");auto sig=sigma_si({2,2}),pi=pi_bound();ck(sig.lo==2*pi.lo&&sig.hi==2*pi.hi,"sigma/pi representation");reject([]{(void)rate_si({1,1},{1},{0});});};
t["physical_rate_remains_unavailable"]=[]{bool exact=false;try{request_physical_rate();}catch(const SourceUnavailable&){exact=true;}ck(exact,"physical promotion through reference");};
int bad=0;for(auto&[name,f]:t){try{f();std::cout<<"PASS "<<name<<'\n';}catch(const std::exception&e){++bad;std::cout<<"FAIL "<<name<<' '<<e.what()<<'\n';}}
std::cout<<"TOTAL "<<t.size()<<" FAILED "<<bad<<'\n';return bad?1:0;}
