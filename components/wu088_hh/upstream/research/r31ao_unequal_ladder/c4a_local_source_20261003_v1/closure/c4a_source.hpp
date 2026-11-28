#pragma once
// Conditional exact source algebra. Does not admit physical rates or evolve a history.
#include "c3b_reference.hpp"
#include <array>
#include <optional>
#include <set>
#include <string>
#include <vector>
namespace c4a {
using c3a::R; using c3a::Error; using c3a::SourceUnavailable;
using c3b::Interval;
using V=std::array<R,9>;
using Gains=std::array<R,7>; // thermal, excitation, fast_e, fast_ion, bulk, radiation, external
struct State {V n{};R u=0;bool thermal_heavy=true,nt_comoving=false;};
struct EnergyModel {std::string id;R ih=0,ah=0,hei=0,heii=0,exc=0;};
struct Packet {
    std::string id,source; V nu{}; State state; EnergyModel model;
    std::optional<Interval> rate; std::optional<Gains> gains;
    std::vector<std::string> owners; bool complete=true; std::optional<R> photon_births;
};
struct Sources {State state;EnergyModel model;std::vector<Packet> terms;};
inline const V Hn{1,1,1,1,0,0,0,0,0},Hen{0,0,0,0,1,1,1,0,0},Q{0,0,1,-1,0,1,2,-1,-1},En{1,1,0,2,2,1,0,1,1},Thermal{1,1,1,1,1,1,1,1,0};
inline R dot(const V&a,const V&b){R x=0;for(std::size_t i=0;i<9;++i)x+=a[i]*b[i];return x;}
inline Interval signed_scale(const Interval&v,const R&a){if(v.lo>v.hi)throw Error("REVERSED_INTERVAL");return a>=0?Interval(a*v.lo,a*v.hi):Interval(a*v.hi,a*v.lo);}
inline Interval plus(const Interval&a,const Interval&b){return {a.lo+b.lo,a.hi+b.hi};}
inline bool izero(const Interval&v){return v.lo==0&&v.hi==0;}
inline void identity(const std::string&s){if(s.empty()||s.size()>256)throw Error("INVALID_IDENTITY");}
inline bool same_state(const State&a,const State&b){return a.n==b.n&&a.u==b.u&&a.thermal_heavy==b.thermal_heavy&&a.nt_comoving==b.nt_comoving;}
inline bool same_energy(const EnergyModel&a,const EnergyModel&b){return a.id==b.id&&a.ih==b.ih&&a.ah==b.ah&&a.hei==b.hei&&a.heii==b.heii&&a.exc==b.exc;}
inline void check_state(const State&s){for(const auto&n:s.n)if(n<0)throw Error("NEGATIVE_DENSITY");if(s.u<0)throw Error("NEGATIVE_THERMAL_ENERGY");if(dot(Q,s.n)!=0)throw Error("MISSING_CHARGE_CARRIER");}
inline void check_model(const EnergyModel&m){identity(m.id);if(m.ih<=0||m.ah<0||m.hei<=0||m.heii<=0||m.exc<0)throw Error("INVALID_ENERGY_PARAMETERS");}
inline V chemical_vector(const EnergyModel&m){check_model(m);return {0,0,m.ih,-m.ah,0,m.hei,m.hei+m.heii,0,0};}
struct RegistryRow {std::string id;std::array<int,6>nu;std::string owner;int absorption,births;};
#include "he_registry.inc"
inline const RegistryRow& row(const std::string&id){for(const auto&r:he_rows())if(r.id==id)return r;throw Error("UNKNOWN_HE_REACTION");}
inline std::string hh_id(c3a::EventKind k){
    switch(k){case c3a::EventKind::BoundExcitation:return "HH_EXC";case c3a::EventKind::IonPair:return "HH_PAIR";case c3a::EventKind::GroundNeutralization:return "HH_GROUND_NEUTRALIZATION";}
    throw Error("UNKNOWN_HH_REACTION");
}
inline V hh_nu(const std::string&id){
    c3a::EventKind k;
    if(id=="HH_EXC")k=c3a::EventKind::BoundExcitation;
    else if(id=="HH_PAIR")k=c3a::EventKind::IonPair;
    else if(id=="HH_GROUND_NEUTRALIZATION")k=c3a::EventKind::GroundNeutralization;
    else throw Error("UNKNOWN_HH_REACTION");
    auto a=c3a::event(k).change;return {a[0],a[1],a[2],a[3],0,0,0,a[4],0};
}
inline V he_nu(const RegistryRow&r,const R&et,const R&en){
    if(et+en!=r.nu[5])throw Error("ELECTRON_NET_SPLIT_MISMATCH");
    const std::set<std::string> no_bath_transfer{"NR_CX","R_CX","EXC","REV_NR_CX","ELASTIC_TRANSFER"};
    if(no_bath_transfer.count(r.id)&&(et!=0||en!=0))throw Error("HE_PRIMARY_ELECTRON_SHUFFLE");
    if(r.id=="ION"&&(et<0||en<0))throw Error("ION_IMPACT_HAS_NO_INCOMING_BATH_ELECTRON");
    // Explicit conditional ground-HI lift of the six-species bookkeeping registry.
    return {r.nu[0],0,r.nu[1],0,r.nu[2],r.nu[3],r.nu[4],et,en};
}
inline Packet hh(c3a::EventKind k,const State&s,const EnergyModel&e,std::optional<Interval>r,std::optional<Gains>g,std::string src){
    std::string id=hh_id(k);return {id,std::move(src),hh_nu(id),s,e,std::move(r),std::move(g),{"HH:"+id},true,R(0)};
}
inline Packet he(std::string id,R et,R en,const State&s,const EnergyModel&e,std::optional<Interval>r,std::optional<Gains>g,std::string src){
    const auto&a=row(id);
    std::optional<R> births=(id.rfind("RR_",0)==0||id.rfind("DR_",0)==0)?std::nullopt:std::optional<R>(a.births);
    return {id,std::move(src),he_nu(a,et,en),s,e,std::move(r),std::move(g),{a.owner},true,births};
}
inline void check_packet(const Packet&p,const State&s,const EnergyModel&m){
    identity(p.source);
    if(!same_state(p.state,s))throw Error("ACTUAL_SNAPSHOT_MISMATCH");
    if(!same_energy(p.model,m))throw Error("ENERGY_CONVENTION_MISMATCH");
    if(!p.rate)throw SourceUnavailable("EVENT_RATE_UNAVAILABLE");
    if(p.rate->lo<0||p.rate->lo>p.rate->hi)throw Error("INVALID_EVENT_RATE");
    bool is_hh=p.id.rfind("HH_",0)==0;
    V expected=is_hh?hh_nu(p.id):he_nu(row(p.id),p.nu[7],p.nu[8]);
    if(p.nu!=expected)throw Error("SOURCE_STOICHIOMETRY_CHANGED");
    for(const auto&invariant:{Hn,Hen,Q,En})if(dot(invariant,p.nu)!=0)throw Error("EVENT_CONSERVATION_FAILURE");
    std::set<std::string> own(p.owners.begin(),p.owners.end());
    std::set<std::string> required{is_hh?"HH:"+p.id:row(p.id).owner};
    if(!is_hh&&p.id=="RR_HEII"&&own.count(row("DR_HEII").owner))required.insert(row("DR_HEII").owner);
    if(own!=required||own.size()!=p.owners.size())throw Error("FORGED_PROCESS_OWNERSHIP");
    if(p.photon_births&&*p.photon_births<0)throw Error("NEGATIVE_PHOTON_BIRTH");
    if(is_hh&&(!p.photon_births||*p.photon_births!=0))throw Error("HH_PRIMARY_PHOTON_MISMATCH");
    if(!is_hh&&p.id.rfind("RR_",0)!=0&&p.id.rfind("DR_",0)!=0&&(!p.photon_births||*p.photon_births!=row(p.id).births))throw Error("REGISTRY_PHOTON_BIRTH_MISMATCH");
    if(p.gains){
        R chem=dot(chemical_vector(m),p.nu),sum=chem;
        for(const auto&g:*p.gains)sum+=g;
        if(sum!=0)throw Error("ENERGY_GAIN_IMBALANCE");
        if(is_hh&&(*p.gains)[1]!=m.exc*p.nu[1])throw Error("HH_EXCITATION_ENERGY_MISMATCH");
        if(is_hh&&((*p.gains)[2]!=0||(*p.gains)[5]!=0))throw Error("HH_PRIMARY_HAS_NO_FREE_ELECTRON_OR_RADIATIVE_CHANNEL");
        if(!is_hh&&(p.id=="NR_CX"||p.id=="ION"||p.id=="EXC"||p.id=="REV_NR_CX"||p.id=="ELASTIC_TRANSFER")&&(*p.gains)[5]!=0)throw Error("NONRADIATIVE_PRIMARY_PHOTON_ENERGY");
        if(!is_hh&&p.id=="R_CX"&&(*p.gains)[5]<=0)throw Error("RADIATIVE_CAPTURE_PHOTON_ENERGY_REQUIRED");
        if(!is_hh&&p.id.rfind("PI_",0)==0&&(*p.gains)[5]>=0)throw Error("PHOTOIONIZATION_ABSORPTION_ENERGY_REQUIRED");
        if(!is_hh&&(p.id.rfind("RR_",0)==0||p.id.rfind("DR_",0)==0)&&((*p.gains)[5]<=0||!p.photon_births||*p.photon_births<=0))throw SourceUnavailable("RECOMBINATION_PHOTON_MOMENTS_REQUIRED");
    }
}
inline void validate(const Sources&s,bool full=false){
    check_state(s.state);check_model(s.model);
    if(s.terms.empty()||s.terms.size()>64)throw Error("EVENT_COUNT_BOUND");
    std::set<std::string> owners;
    for(const auto&p:s.terms){
        check_packet(p,s.state,s.model);
        if(full&&!p.complete)throw SourceUnavailable("PARTIAL_PROCESS_IS_NOT_INCLUSIVE");
        for(const auto&o:p.owners)if(!owners.insert(o).second)throw Error("DUPLICATE_SEMANTIC_OWNER");
    }
}
inline Sources assemble(const State&s,const EnergyModel&e,std::vector<Packet>p,bool require_full=true){Sources x{s,e,std::move(p)};validate(x,require_full);return x;}
inline Interval linear_count(const Sources&s,const V&weights){validate(s);Interval a(0,0);for(const auto&p:s.terms)a=plus(a,signed_scale(*p.rate,dot(weights,p.nu)));return a;}
inline std::array<Interval,9> species(const Sources&s){std::array<Interval,9>x{};for(std::size_t j=0;j<9;++j){V w{};w[j]=1;x[j]=linear_count(s,w);}return x;}
inline void require_energy(const Sources&s){validate(s);for(const auto&p:s.terms)if(!p.gains)throw SourceUnavailable("COUNT_ONLY_ENERGY_MOMENTS_UNAVAILABLE");}
// Reservoir order: thermal, chemical, excitation, fast_e, fast_ion, bulk, radiation, external.
inline std::array<R,8> energy_coefficients(const Packet&p){if(!p.gains)throw SourceUnavailable("ENERGY_MOMENTS_UNAVAILABLE");const auto&g=*p.gains;return {g[0],dot(chemical_vector(p.model),p.nu),g[1],g[2],g[3],g[4],g[5],g[6]};}
inline Interval linear_energy(const Sources&s,const std::array<R,8>&w){require_energy(s);Interval a(0,0);for(const auto&p:s.terms){const auto&q=energy_coefficients(p);R c=0;for(std::size_t i=0;i<8;++i)c+=w[i]*q[i];a=plus(a,signed_scale(*p.rate,c));}return a;}
inline std::array<Interval,8> energies(const Sources&s){std::array<Interval,8>x{};for(std::size_t i=0;i<8;++i){std::array<R,8>w{};w[i]=1;x[i]=linear_energy(s,w);}return x;}
inline R temperature(const State&s,const R&kb){check_state(s);if(!s.thermal_heavy)throw Error("COMMON_THERMAL_HEAVY_CLOSURE_UNAVAILABLE");R n=dot(Thermal,s.n);if(n<=0||kb<=0)throw Error("INVALID_THERMAL_DENOMINATOR");return 2*s.u/(3*kb*n);}
inline void thermal_ready(const Sources&s,const R&kb){require_energy(s);(void)temperature(s.state,kb);for(const auto&p:s.terms)if((*p.gains)[3]!=0)throw SourceUnavailable("FAST_ION_RECOIL_NEEDS_SEPARATE_BATH");}
inline Interval temperature_rate(const Sources&s,const R&kb){
    thermal_ready(s,kb);R n=dot(Thermal,s.state.n),T=temperature(s.state,kb);Interval a(0,0);
    for(const auto&p:s.terms){R coeff=2*(*p.gains)[0]/(3*kb*n)-T*dot(Thermal,p.nu)/n;a=plus(a,signed_scale(*p.rate,coeff));}return a;
}
struct PhotonSources {std::optional<Interval> births;Interval absorptions{0,0};};
inline PhotonSources photons(const Sources&s){validate(s);PhotonSources out;Interval b(0,0);bool known=true;for(const auto&p:s.terms){if(p.photon_births)b=plus(b,signed_scale(*p.rate,*p.photon_births));else known=false;if(p.id.rfind("HH_",0)!=0)out.absorptions=plus(out.absorptions,signed_scale(*p.rate,R(row(p.id).absorption)));}if(known)out.births=b;return out;}
struct LegacySidecar {std::array<R,6>n{};std::array<Interval,6>source{};R hminus=0,hstar=0,eth=0,ent=0;Interval hminus_source{0,0},hstar_source{0,0},eth_source{0,0},ent_source{0,0};};
inline LegacySidecar export_extended(const Sources&s){
    const auto v=species(s);const auto&n=s.state.n;LegacySidecar a;
    a.n={n[0]+n[1],n[2],n[4],n[5],n[6],n[7]+n[8]};
    V hi{};hi[0]=hi[1]=1;V ee{};ee[7]=ee[8]=1;
    a.source={linear_count(s,hi),v[2],v[4],v[5],v[6],linear_count(s,ee)};
    a.hminus=n[3];a.hstar=n[1];a.eth=n[7];a.ent=n[8];a.hminus_source=v[3];a.hstar_source=v[1];a.eth_source=v[7];a.ent_source=v[8];return a;
}
inline void require_bare_legacy(const Sources&s){
    auto v=species(s);for(auto i:{1U,3U,8U})if(s.state.n[i]!=0||!izero(v[i]))throw SourceUnavailable("HMINUS_EXCITATION_OR_FAST_ELECTRON_SIDECAR_REQUIRED");
}
struct Kinematics {R H=0,gamma=1,gamma_dot=0;std::string geometry="BianchiI",time_unit="s";};
struct RHS {std::array<Interval,9>dn{};Interval du{0,0},dT{0,0};R A=0;};
inline RHS bianchi_rhs(const Sources&s,const R&kb,const Kinematics&k){
    thermal_ready(s,kb);validate(s,true);
    if(k.geometry!="BianchiI"||k.time_unit!="s"||k.gamma<1||(k.gamma==1&&k.gamma_dot!=0))throw Error("KINEMATIC_SCOPE_MISMATCH");
    auto ds=species(s);
    if(!s.state.nt_comoving&&(s.state.n[8]!=0||!izero(ds[8])))throw SourceUnavailable("NONTHERMAL_CURRENT_NOT_COMOVING");
    RHS out;out.A=3*k.H+k.gamma_dot/k.gamma;
    for(std::size_t i=0;i<9;++i)out.dn[i]=plus(signed_scale(ds[i],1/k.gamma),Interval(-out.A*s.state.n[i],-out.A*s.state.n[i]));
    const auto heat=linear_energy(s,{1,0,0,0,0,0,0,0});R expansion=-out.A*5*s.state.u/3;
    out.du=plus(signed_scale(heat,1/k.gamma),Interval(expansion,expansion));
    R cooling=-R(2)*out.A*temperature(s.state,kb)/3;
    out.dT=plus(signed_scale(temperature_rate(s,kb),1/k.gamma),Interval(cooling,cooling));return out;
}
struct MassAction {Interval rate{0,0};std::array<Interval,9>fixed_k_gradient{};};
inline MassAction hh_mass_action(c3a::EventKind k,const State&s,const std::optional<Interval>&coef){
    check_state(s);if(!coef)throw SourceUnavailable("COEFFICIENT_UNAVAILABLE_EVEN_AT_ZERO_DENSITY");if(coef->lo<0||coef->lo>coef->hi)throw Error("INVALID_COEFFICIENT");
    MassAction x;
    if(k==c3a::EventKind::BoundExcitation||k==c3a::EventKind::IonPair){x.rate=signed_scale(*coef,s.n[0]*s.n[0]/2);x.fixed_k_gradient[0]=signed_scale(*coef,s.n[0]);}
    else if(k==c3a::EventKind::GroundNeutralization){x.rate=signed_scale(*coef,s.n[2]*s.n[3]);x.fixed_k_gradient[2]=signed_scale(*coef,s.n[3]);x.fixed_k_gradient[3]=signed_scale(*coef,s.n[2]);}
    else { throw Error("UNKNOWN_HH_REACTION"); }
    return x;
}
inline void require_tangent_cone(const Sources&s){auto x=species(s);for(std::size_t i=0;i<9;++i)if(s.state.n[i]==0&&x[i].lo<0)throw Error("BOUNDARY_SOURCE_NOT_QUASIPOSITIVE");}
inline Gains from_c3a_thermalized(const c3a::EnergyBalance&b,const R&chemical,const R&excitation,bool all_kinetic_is_thermal){
    if(!all_kinetic_is_thermal)throw SourceUnavailable("KINETIC_TO_HEAT_OWNERSHIP_REQUIRED");
    c3a::require_balanced_energy(b);
    if(*b.internal_J!=chemical+excitation)throw Error("INTERNAL_SPLIT_MISMATCH");
    return {*b.heavy_J+*b.electron_J,excitation,0,0,0,*b.radiation_J,-*b.external_work_J};
}
[[noreturn]] inline void require_physical(){throw SourceUnavailable("C0_DOMAIN_HH_RATE_AND_RECEIVER_AUTHORITY_UNBOUND");}
} // namespace c4a
