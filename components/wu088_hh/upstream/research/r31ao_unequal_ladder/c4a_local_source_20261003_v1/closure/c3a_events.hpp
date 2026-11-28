#pragma once
#include "c3a_exact.hpp"
#include <array>
#include <optional>
namespace c3a {
// Order: H0, Hstar, Hplus, Hminus, free electron. Counts per event, not rates.
using Counts=std::array<int,5>;
enum class EventKind{BoundExcitation,IonPair,GroundNeutralization};
struct Event{std::string name;Counts change;};
inline long long dot(const Counts&a,const Counts&b){long long s=0;for(std::size_t i=0;i<5;++i)s+=static_cast<long long>(a[i])*b[i];return s;}
inline constexpr Counts nuclei{1,1,1,1,0},charge{0,0,1,-1,-1},electrons{1,1,0,2,1};
inline void require_event_conservation(const Event&e){
    if(dot(e.change,nuclei)!=0||dot(e.change,charge)!=0||dot(e.change,electrons)!=0)throw Error("EVENT_CONSERVATION_FAILURE");
}
inline Event event(EventKind k){
    switch(k){
    case EventKind::BoundExcitation:return {"bound_excitation",{-1,1,0,0,0}};
    case EventKind::IonPair:return {"ion_pair",{-2,0,1,1,0}};
    case EventKind::GroundNeutralization:return {"ground_neutralization",{2,0,-1,-1,0}};
    }
    throw Error("UNKNOWN_EVENT");
}
struct EnergyBalance{std::optional<R> heavy_J,electron_J,internal_J,radiation_J,external_work_J;std::string unit="J";};
inline R energy_residual(const EnergyBalance&b){
    if(b.unit!="J")throw Error("ENERGY_UNIT_NOT_JOULE");
    if(!b.heavy_J||!b.electron_J||!b.internal_J||!b.radiation_J||!b.external_work_J)throw Error("ENERGY_OWNERSHIP_UNAVAILABLE");
    return *b.heavy_J+*b.electron_J+*b.internal_J+*b.radiation_J-*b.external_work_J;
}
inline void require_balanced_energy(const EnergyBalance&b){if(energy_residual(b)!=0)throw Error("ENERGY_IMBALANCE");}
inline R pair_defect_J(const R&ionization,const R&affinity,const R&excitation_a,const R&excitation_b){
    if(ionization<=0||affinity<0||excitation_a<0||excitation_b<0)throw Error("INVALID_ENERGY_PARAMETER");
    return ionization-affinity-excitation_a-excitation_b;
}
struct SourceUnavailable : Error { using Error::Error; };
[[noreturn]] inline R request_rate(EventKind k){
    (void)event(k);
    throw SourceUnavailable("HH_ASYMPTOTIC_FLUX_DOMAIN_RATE_AUTHORITY_UNAVAILABLE");
}
} // namespace c3a
