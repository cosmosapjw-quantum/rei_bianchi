#include "../closure/c3a_events.hpp"
#include <functional>
#include <iostream>
#include <map>
using namespace c3a;
void ck(bool b,const std::string&m){if(!b)throw Error("ASSERTION: "+m);}
template<class F>void no(F f){bool hit=false;try{f();}catch(const Error&){hit=true;}ck(hit,"invalid input accepted");}
Mat metric(){Mat o=eye(2);o(0,1)=o(1,0)=C(R(1)/2);return o;}
Mat vector(C a,C b){Mat c(2,1);c(0,0)=a;c(1,0)=b;return c;}
int main(){std::map<std::string,std::function<void()>> t;
 t["complex_conjugation"]=[](){C z(R(2),R(3));ck(z*conj(z)==C(13),"complex conjugate");ck((z/z)==C(1),"division");};
 t["zero_division"]=[](){no([](){(void)(C(1)/C(0));});};
 t["exact_linear_solve"]=[](){Mat a=metric();Mat b=vector(C(1,2),C(3,-1));ck(a*solve(a,b)==b,"solve residual");};
 t["pivoted_linear_solve"]=[](){Mat a(2,2);a(0,1)=a(1,0)=1;auto b=vector(2,3);ck(a*solve(a,b)==b,"pivot");};
 t["singular_solve"]=[](){no([](){(void)solve(Mat(2,2),eye(2));});};
 t["dimension_guard"]=[](){no([](){(void)Mat(0,2);});no([](){(void)Mat(65,1);});no([](){(void)(eye(2)*eye(3));});};
 t["duplicate_channel"]=[](){no([](){(void)columns(2,{0,0});});};
 t["empty_channel"]=[](){no([](){(void)columns(2,{});});};
 t["channel_out_of_range"]=[](){no([](){(void)columns(2,{2});});};
 t["nonhermitian_metric"]=[](){auto a=eye(2);a(0,1)=1;no([&](){(void)project(a,columns(2,{0}));});};
 t["indefinite_metric"]=[](){auto a=eye(2);a(1,1)=-1;no([&](){(void)project(a,columns(2,{0}));});};
 t["complex_hpd_metric"]=[](){auto a=eye(2);a(0,1)=C(0,R(1)/2);a(1,0)=conj(a(0,1));auto p=project(a,columns(2,{0}));ck(p.coefficient*p.coefficient==p.coefficient,"complex projector");ck(adj(p.coefficient)*a==p.covariant,"metric adjoint");};
 t["rank_deficient_channel"]=[](){Mat z(2,2);z(0,0)=z(0,1)=1;no([&](){(void)project(eye(2),z);});};
 t["zero_state_norm"]=[](){auto o=eye(2);no([&](){(void)probability(o,o,Mat(2,1));});};
 t["nonhermitian_effect"]=[](){auto o=eye(2),k=o;k(0,1)=1;no([&](){(void)probability(o,k,columns(2,{0}));});};
 t["negative_effect"]=[](){auto o=eye(2);Mat k(2,2);k(1,1)=-1;no([&](){(void)probability(o,k,columns(2,{0}));});};
 t["zero_pivot_coupling"]=[](){Mat k(2,2);k(0,1)=k(1,0)=1;no([&](){require_psd(k);});};
 t["exact_nearsingular_no_cutoff"]=[](){Mat o=eye(2);o(1,1)=C(R("1/1000000000000000000000000000000"));auto p=project(o,columns(2,{1}));ck(p.coefficient==columns(2,{1})*adj(columns(2,{1})),"positive metric must not be truncated");};
 t["overlap_not_coefficient_sum"]=[](){auto o=metric();auto p=project(o,columns(2,{1}));ck(probability(o,p.covariant,columns(2,{0}))==R(1)/4,"overlap diagnostic 1/4 not zero");};
 t["separate_probabilities_sum_5_over_4"]=[](){auto o=metric(),c=columns(2,{0});R sum=0;for(std::size_t j=0;j<2;++j)sum+=probability(o,project(o,columns(2,{j})).covariant,c);ck(sum==R(5)/4,"overlap sum");};
 t["projector_identities_and_complement"]=[](){auto o=metric();auto p=project(o,columns(2,{0}));auto r=eye(2)-p.coefficient;ck(p.coefficient*p.coefficient==p.coefficient,"idempotence");ck(adj(p.coefficient)*o==o*p.coefficient,"O self adjoint");ck(zero(p.coefficient*r),"orthogonal complement");auto c=vector(C(2,1),C(-1,3));ck(probability(o,p.covariant,c)+probability(o,o-p.covariant,c)==1,"probability complement");};
 t["schur_complement_norm"]=[](){auto o=metric();auto p=project(o,columns(2,{0}));auto c=vector(2,3);ck(quadratic(c,o-p.covariant)==C(R(27)/4),"Schur norm exact");};
 t["unnormalized_norm_exposed"]=[](){auto o=eye(2),c=vector(2,0);auto k=project(o,columns(2,{0})).covariant;ck(quadratic(c,o)==C(4),"raw norm must remain 4");ck(quadratic(c,k)==C(4)&&probability(o,k,c)==1,"normalized value cannot overwrite raw norm");};
 t["subspace_basis_scaling"]=[](){auto o=metric(),z=vector(1,2),w=vector(C(0,3),C(0,6));ck(project(o,z).covariant==project(o,w).covariant,"complex scaling changes span");};
 t["coordinate_covariance_16_cases"]=[](){for(int j=1;j<=16;++j){Mat a=eye(3);a(0,1)=C(j,R(j)/3);a(1,2)=C(R(1)/j,-1);a(2,2)=2;Mat o=adj(a)*a,z=columns(3,{0,2}),c(3,1);c(0,0)=C(j,1);c(1,0)=2;c(2,0)=C(-2,j);Mat u=eye(3);u(0,2)=C(R(1)/j,1);u(1,1)=2;auto p=project(o,z);auto op=adj(u)*o*u;auto zp=solve(u,z),cp=solve(u,c);auto pp=project(op,zp);ck(probability(o,p.covariant,c)==probability(op,pp.covariant,cp),"coordinate probability covariance");ck(pp.coefficient==solve(u,p.coefficient*u),"coefficient similarity");}};
 t["complete_partition"]=[](){require_partition(eye(3),{columns(3,{0,1}),columns(3,{2})},true);};
 t["incomplete_partition"]=[](){no([](){require_partition(eye(3),{columns(3,{0})},true);});require_partition(eye(3),{columns(3,{0})},false);};
 t["empty_partition"]=[](){no([](){require_partition(eye(2),{},false);});};
 t["compression_invariant_union"]=[](){Mat q(3,2);q(0,0)=q(1,0)=1;q(2,1)=2;auto p=project(eye(3),columns(3,{0,1}));auto e=compress(eye(3),p,q);ck(e.is_projector&&e.subspace_preserved,"invariant union");};
 t["compression_probabilities_agree"]=[](){Mat q(3,2);q(0,0)=q(1,0)=1;q(2,1)=2;auto o=eye(3);auto p=project(o,columns(3,{0}));auto e=compress(o,p,q);auto c=vector(C(1,2),3);ck(probability(e.metric,e.covariant,c)==probability(o,p.covariant,q*c),"compressed observable");};
 t["compression_povm_not_pvm"]=[](){auto o=eye(2);auto q=vector(1,1);auto a=compress(o,project(o,columns(2,{0})),q);auto b=compress(o,project(o,columns(2,{1})),q);ck(!a.is_projector&&!b.is_projector,"half effects");ck(a.covariant+b.covariant==a.metric,"POVM completeness");};
 t["forged_projection_rejected"]=[](){auto o=eye(2);Projection p{o,Mat(2,2)};no([&](){(void)compress(o,p,o);});};
 t["rank_deficient_parity_map"]=[](){Mat q(2,2);q(0,0)=q(0,1)=1;no([&](){(void)compress(eye(2),project(eye(2),columns(2,{0})),q);});};
 t["event_conservation_all_three"]=[](){for(auto k:{EventKind::BoundExcitation,EventKind::IonPair,EventKind::GroundNeutralization}){auto e=event(k);require_event_conservation(e);ck(e.change[4]==0,"no free-electron source");}};
 t["ion_pair_inverse"]=[](){auto f=event(EventKind::IonPair),b=event(EventKind::GroundNeutralization);for(std::size_t i=0;i<5;++i)ck(f.change[i]+b.change[i]==0,"reverse stoichiometry");};
 t["hminus_omission_rejected"]=[](){no([](){require_event_conservation({"wrong",{-2,0,1,0,1}});});};
 t["unknown_event_rejected"]=[](){no([](){(void)event(static_cast<EventKind>(99));});};
 t["closed_collision_energy_balance"]=[](){EnergyBalance b{-7,0,7,0,0,"J"};require_balanced_energy(b);};
 t["driven_collision_energy_balance"]=[](){EnergyBalance b{0,0,7,0,7,"J"};require_balanced_energy(b);};
 t["energy_mismatch_not_repaired"]=[](){EnergyBalance b{-6,0,7,0,0,"J"};ck(energy_residual(b)==1,"residual");no([&](){require_balanced_energy(b);});};
 t["missing_energy_components_rejected"]=[](){for(int j=0;j<5;++j){EnergyBalance b{-7,0,7,0,0,"J"};std::array<std::optional<R>*,5>x{&b.heavy_J,&b.electron_J,&b.internal_J,&b.radiation_J,&b.external_work_J};x[j]->reset();no([&](){(void)energy_residual(b);});}};
 t["energy_units_rejected"]=[](){EnergyBalance b{-7,0,7,0,0,"eV"};no([&](){(void)energy_residual(b);});};
 t["symbolic_parameter_defect"]=[](){ck(pair_defect_J(10,1,2,3)==4,"conditional defect formula");ck(pair_defect_J(10,1,5,5)==-1,"exothermic not clamped");};
 t["invalid_energy_parameters"]=[](){no([](){(void)pair_defect_J(0,1,0,0);});no([](){(void)pair_defect_J(10,-1,0,0);});};
 t["rates_unavailable_all_events"]=[](){for(auto k:{EventKind::BoundExcitation,EventKind::IonPair,EventKind::GroundNeutralization}){bool hit=false;try{(void)request_rate(k);}catch(const SourceUnavailable&){hit=true;}ck(hit,"no admitted physical provider");}};
 t["complex_golden_projector"]=[](){auto o=eye(2);o(0,1)=C(0,R(1)/2);o(1,0)=conj(o(0,1));auto p=project(o,columns(2,{0}));Mat expected(2,2);expected(0,0)=1;expected(0,1)=C(0,R(1)/2);ck(p.coefficient==expected,"independent exact complex golden matrix");};
 t["subspace_two_column_mixing"]=[](){auto o=eye(3),z=columns(3,{0,2});Mat u=eye(2);u(0,1)=C(0,1);u(1,1)=2;ck(project(o,z).covariant==project(o,z*u).covariant,"two-column channel basis invariance");};
 int failures=0;for(auto&[name,f]:t){try{f();std::cout<<"PASS "<<name<<'\n';}catch(const std::exception&e){++failures;std::cout<<"FAIL "<<name<<' '<<e.what()<<'\n';}}
 std::cout<<"TOTAL "<<t.size()<<" FAILED "<<failures<<'\n';return failures?1:0;
}
