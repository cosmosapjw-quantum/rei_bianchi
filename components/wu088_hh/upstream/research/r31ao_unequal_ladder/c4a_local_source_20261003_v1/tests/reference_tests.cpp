#include "../closure/c4a_source.hpp"
#include <functional>
#include <iostream>
#include <map>
using namespace c4a;
void ck(bool x,const std::string&m){if(!x)throw Error("ASSERTION: "+m);}
template<class F>void no(F f){bool a=false;try{f();}catch(const Error&){a=true;}ck(a,"rejection absent");}
bool eq(const Interval&a,R l,R h){return a.lo==l&&a.hi==h;}
State state(){State s;s.n={4,0,1,1,2,1,0,1,0};s.u=15;s.nt_comoving=true;return s;}
EnergyModel model(){return {"manufactured-energy",10,3,20,30,2};}
Packet pair(const State&s){return hh(c3a::EventKind::IonPair,s,model(),Interval(1,2),Gains{-7,0,0,0,0,0,0},"fixture:pair");}
int main(){std::map<std::string,std::function<void()>> t;
 t["all_original_16_registry_rows_conserve"]=[](){ck(he_rows().size()==16,"registry size");auto s=state();for(const auto&r:he_rows()){auto p=he(r.id,r.nu[5],0,s,model(),Interval(1,3),std::nullopt,"registry-fixture");auto x=assemble(s,model(),{p});for(auto w:{Hn,Hen,Q,En})ck(izero(linear_count(x,w)),r.id);}};
 t["all_three_HH_events_conserve"]=[](){auto s=state();for(auto k:{c3a::EventKind::BoundExcitation,c3a::EventKind::IonPair,c3a::EventKind::GroundNeutralization}){auto p=hh(k,s,model(),Interval(1,3),std::nullopt,"hh-fixture");auto a=assemble(s,model(),{p});for(auto w:{Hn,Hen,Q,En})ck(izero(linear_count(a,w)),"HH invariant");ck(izero(linear_count(a,Thermal)),"HH event cannot create thermal particles");}};
 t["energy_shared_rate_cancellation"]=[](){auto s=state();auto a=assemble(s,model(),{pair(s)});ck(izero(linear_energy(a,{1,1,1,1,1,1,1,1})),"energy must cancel before enclosing");auto e=energies(a);ck(eq(e[0],-14,-7)&&eq(e[1],7,14),"signed enclosures");};
 t["temperature_shared_rate_cancellation"]=[](){auto s=state();auto p=he("EI_HI",-1,2,s,model(),Interval(1,9),Gains{R(-3)/2,0,0,0,0,0,R(-17)/2},"synthetic-cancellation");auto a=assemble(s,model(),{p});ck(izero(temperature_rate(a,1)),"composition/heat use same random variable");};
 t["Hminus_projection_defect_and_sidecar"]=[](){auto s=state();auto a=assemble(s,model(),{pair(s)});auto b=export_extended(a);ck(b.hminus==1&&eq(b.hminus_source,1,2),"sidecar");auto naive=plus(b.source[0],b.source[1]);ck(eq(naive,-3,0),"marginal intervals lose correlation");V legacyH=Hn;legacyH[3]=0;auto hc=linear_count(a,legacyH);ck(eq(hc,-2,-1),"correlated legacy H nucleus deficit");ck(eq(b.source[1],1,2),"legacy apparent charge");};
 t["strict_legacy_checks_created_not_just_present_Hminus"]=[](){auto s=state();s.n[3]=0;s.n[7]=2;auto a=assemble(s,model(),{pair(s)});no([&](){require_bare_legacy(a);});};
 t["legacy_intersection_is_lossless"]=[](){auto s=state();s.n[3]=0;s.n[7]=2;auto p=he("PI_HI",1,0,s,model(),Interval(1,1),std::nullopt,"intersection");auto a=assemble(s,model(),{p});require_bare_legacy(a);auto b=export_extended(a);ck(b.n[0]==4&&eq(b.source[5],1,1),"legacy mapping");};
 t["bare_nonthermal_export_refused"]=[](){auto s=state();s.n[3]=0;s.n[7]=1;s.n[8]=1;auto p=he("PI_HI",1,0,s,model(),Interval(1,1),std::nullopt,"nt");auto a=assemble(s,model(),{p});no([&](){require_bare_legacy(a);});};
 t["forged_event_stoichiometry_refused"]=[](){auto s=state();auto p=pair(s);p.nu[3]=0;no([&](){(void)assemble(s,model(),{p});});};
 t["forged_same_snapshot_label_not_sufficient"]=[](){auto s=state();auto p=pair(s);p.state.n[0]+=1;no([&](){(void)assemble(s,model(),{p});});};
 t["energy_id_and_values_both_bound"]=[](){auto s=state();auto p=pair(s);p.model.ah+=1;no([&](){(void)assemble(s,model(),{p});});p=pair(s);p.model.id="other";no([&](){(void)assemble(s,model(),{p});});};
 t["negative_rates_refused"]=[](){auto s=state();auto p=pair(s);p.rate=Interval(-1,2);no([&](){(void)assemble(s,model(),{p});});};
 t["missing_vs_known_zero"]=[](){auto s=state();auto p=pair(s);p.rate.reset();no([&](){(void)assemble(s,model(),{p});});p.rate=Interval(0,0);auto a=assemble(s,model(),{p});ck(izero(linear_count(a,Hn)),"known zero");};
 t["partial_source_is_never_inclusive"]=[](){auto s=state();auto p=pair(s);p.complete=false;no([&](){(void)assemble(s,model(),{p});});auto a=assemble(s,model(),{p},false);ck(eq(species(a)[3],1,2),"named partial still usable as partial");};
 t["RR_total_and_DR_double_count_refused"]=[](){auto s=state();auto p=he("RR_HEII",-1,0,s,model(),Interval(1,1),std::nullopt,"rr-total");p.owners.push_back(row("DR_HEII").owner);auto q=he("DR_HEII",-1,0,s,model(),Interval(1,1),std::nullopt,"dr");no([&](){(void)assemble(s,model(),{p,q});});(void)assemble(s,model(),{p});};
 t["unknown_extra_owner_refused"]=[](){auto s=state();auto p=pair(s);p.owners.push_back("receiver:PI_HI");no([&](){(void)assemble(s,model(),{p});});};
 t["unknown_reaction_refused"]=[](){auto s=state();no([&](){(void)he("invented",0,0,s,model(),Interval(0,0),std::nullopt,"x");});};
 t["bad_electron_split_refused"]=[](){auto s=state();no([&](){(void)he("ION",0,0,s,model(),Interval(1,1),std::nullopt,"x");});};
 t["heavy_collision_cannot_shuffle_bath_electrons"]=[](){auto s=state();no([&](){(void)he("NR_CX",-1,1,s,model(),Interval(1,1),std::nullopt,"x");});};
 t["changed_energy_not_auto_repaired"]=[](){auto s=state();auto p=pair(s);(*p.gains)[0]=-6;no([&](){(void)assemble(s,model(),{p});});};
 t["HH_excitation_energy_bound"]=[](){auto s=state();auto p=hh(c3a::EventKind::BoundExcitation,s,model(),Interval(1,1),Gains{-2,2,0,0,0,0,0},"exc");(void)assemble(s,model(),{p});p.gains=Gains{-1,1,0,0,0,0,0};no([&](){(void)assemble(s,model(),{p});});};
 t["C3A_external_work_sign"]=[](){c3a::EnergyBalance b{0,0,7,0,7,"J"};auto g=from_c3a_thermalized(b,7,0,true);ck(g[6]==-7,"external reservoir sign");no([&](){(void)from_c3a_thermalized(b,7,0,false);});};
 t["C3A_missing_energy_stays_unavailable"]=[](){c3a::EnergyBalance b{0,0,7,0,std::nullopt,"J"};no([&](){(void)from_c3a_thermalized(b,7,0,true);});};
 t["photon_primary_rules_not_relabelled"]=[](){auto s=state();auto p=pair(s);p.gains=Gains{-8,0,0,0,0,1,0};no([&](){(void)assemble(s,model(),{p});});ck(row("R_CX").births==1&&row("R_CX").absorption==0&&row("PI_HI").absorption==1,"photon owners");};
 t["thermal_electrons_not_all_electrons"]=[](){auto s=state();s.n[7]=0;s.n[8]=1;ck(temperature(s,1)==R(10)/9,"n thermal=9 not10");};
 t["vacuum_temperature_refused"]=[](){State s;no([&](){(void)temperature(s,1);});};
 t["invalid_state_refused"]=[](){auto s=state();s.n[0]=-1;no([&](){check_state(s);});s=state();s.n[7]=2;no([&](){check_state(s);});s=state();s.u=-1;no([&](){check_state(s);});};
 t["no_silent_temperature_floor"]=[](){auto s=state();s.u=R(3)/20;ck(temperature(s,1)==R(1)/100,"no invented 10K physics");};
 t["nonthermal_current_needed_for_transport_not_counts"]=[](){auto s=state();s.n[7]=0;s.n[8]=1;s.nt_comoving=false;auto a=assemble(s,model(),{pair(s)});(void)species(a);no([&](){(void)bianchi_rhs(a,1,{});});};
 t["fast_ion_heat_closure_refused"]=[](){auto s=state();auto p=pair(s);p.gains=Gains{-8,0,0,1,0,0,0};auto a=assemble(s,model(),{p});no([&](){(void)temperature_rate(a,1);});};
 t["isotropic_shared_heavy_bath_required"]=[](){auto s=state();s.thermal_heavy=false;auto a=assemble(s,model(),{pair(s)});no([&](){(void)temperature_rate(a,1);});};
 t["local_equals_zero_expansion_gamma_one"]=[](){auto s=state();auto a=assemble(s,model(),{pair(s)});auto r=bianchi_rhs(a,1,{});auto local=temperature_rate(a,1);ck(eq(r.dT,local.lo,local.hi),"rest local limit");};
 t["Bianchi_density_volume_identity"]=[](){auto s=state();auto p=pair(s);p.rate=Interval(1,1);auto a=assemble(s,model(),{p});Kinematics k{R(1)/10,R(5)/4,R(1)/8};auto r=bianchi_rhs(a,1,k);auto S=species(a);for(std::size_t i=0;i<9;++i){R lhs=k.gamma*r.dn[i].lo+(3*k.H*k.gamma+k.gamma_dot)*s.n[i];ck(lhs==S[i].lo,"d(V gamma n)=V S");}};
 t["Bianchi_temperature_chain_rule"]=[](){auto s=state();auto p=pair(s);p.rate=Interval(1,1);auto a=assemble(s,model(),{p});Kinematics k{R(1)/10,R(5)/4,R(1)/8};auto r=bianchi_rhs(a,1,k);R ndot=0;for(std::size_t i=0;i<9;++i)ndot+=Thermal[i]*r.dn[i].lo;R nd=dot(Thermal,s.n);R chain=2*r.du.lo/(3*nd)-temperature(s,1)*ndot/nd;ck(chain==r.dT.lo,"chain rule, no extra gamma");};
 t["Bianchi_geometry_and_gamma_guard"]=[](){auto s=state();auto a=assemble(s,model(),{pair(s)});Kinematics k;k.geometry="BianchiV";no([&](){(void)bianchi_rhs(a,1,k);});k.geometry="BianchiI";k.gamma=R(1)/2;no([&](){(void)bianchi_rhs(a,1,k);});};
 t["mass_action_factor_and_zero_density_derivative"]=[](){auto s=state();auto x=hh_mass_action(c3a::EventKind::IonPair,s,Interval(2,2));ck(eq(x.rate,16,16)&&eq(x.fixed_k_gradient[0],8,8),"half once");s.n[0]=0;x=hh_mass_action(c3a::EventKind::IonPair,s,Interval(2,2));ck(izero(x.rate)&&izero(x.fixed_k_gradient[0]),"polynomial at zero");no([&](){(void)hh_mass_action(c3a::EventKind::IonPair,s,std::nullopt);});};
 t["reverse_pair_has_no_half"]=[](){auto s=state();auto x=hh_mass_action(c3a::EventKind::GroundNeutralization,s,Interval(2,2));ck(eq(x.rate,2,2)&&eq(x.fixed_k_gradient[2],2,2),"distinct charges");};
 t["tangent_cone_rejects_negative_boundary"]=[](){auto s=state();s.n[0]=0;auto a=assemble(s,model(),{pair(s)});no([&](){require_tangent_cone(a);});auto p=pair(s);p.rate=hh_mass_action(c3a::EventKind::IonPair,s,Interval(1,1)).rate;require_tangent_cone(assemble(s,model(),{p}));};
 t["post_assembly_mutation_is_revalidated"]=[](){auto s=state();auto a=assemble(s,model(),{pair(s)});a.terms[0].nu[3]=0;no([&](){(void)species(a);});};
 t["missing_recombination_photons_not_zero"]=[](){auto s=state();auto p=he("RR_HII",-1,0,s,model(),Interval(1,1),std::nullopt,"rr");auto a=assemble(s,model(),{p});ck(!photons(a).births,"birth unknown not zero");p.gains=Gains{0,0,0,0,0,10,0};no([&](){(void)assemble(s,model(),{p});});p.photon_births=1;(void)assemble(s,model(),{p});};
 t["photoionization_radiation_ownership"]=[](){auto s=state();auto p=he("PI_HI",1,0,s,model(),Interval(1,1),Gains{0,0,0,0,0,0,-10},"pi");no([&](){(void)assemble(s,model(),{p});});p.gains=Gains{0,0,0,0,0,-10,0};auto a=assemble(s,model(),{p});ck(eq(photons(a).absorptions,1,1),"one primary absorption");};
 t["partial_bianchi_transport_refused"]=[](){auto s=state();auto p=pair(s);p.complete=false;auto a=assemble(s,model(),{p},false);no([&](){(void)bianchi_rhs(a,1,{});});};
 t["gamma_derivative_at_rest_refused"]=[](){auto s=state();auto a=assemble(s,model(),{pair(s)});Kinematics k;k.gamma_dot=1;no([&](){(void)bianchi_rhs(a,1,k);});};
 int failures=0;for(auto&[name,f]:t){try{f();std::cout<<"PASS "<<name<<'\n';}catch(const std::exception&e){++failures;std::cout<<"FAIL "<<name<<" "<<e.what()<<'\n';}}std::cout<<"TOTAL "<<t.size()<<" FAILED "<<failures<<'\n';return failures?1:0;
}
