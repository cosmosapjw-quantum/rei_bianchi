#pragma once
#include "c3a_events.hpp"
#include <array>
#include <optional>
#include <set>
#include <string>
#include <vector>
namespace c3b {
using c3a::R;using c3a::Mat;using c3a::C;using c3a::Error;using c3a::SourceUnavailable;
struct Interval{R lo,hi;Interval(R l=0,R h=0):lo(std::move(l)),hi(std::move(h)){if(lo>hi)throw Error("REVERSED_INTERVAL");}};
struct Key{std::string model,event,spin,frame,domain;bool operator==(const Key&)const=default;};
enum class Meaning{WholeCellBound,PointSample};
struct Cell{std::string id;Key key;R left,right;Interval bound;Meaning meaning=Meaning::WholeCellBound;};
struct ImpactIntegralTag {}; struct EnergyEnvelopeTag {};
template<class Tag> struct TailRecord{std::string id;Key key;R from;Interval bound;};
using ImpactTail=TailRecord<ImpactIntegralTag>;
using EnergyTail=TailRecord<EnergyEnvelopeTag>;
struct Integral{Key key;Interval partial;std::optional<Interval> full;std::vector<std::pair<R,R>> gaps;};
struct Errors{R preparation,state,effect,tail;std::array<std::string,4> owners;};
struct SpinTerm{std::string sector;R weight;std::optional<Interval> value;};
struct RelativeAtom{std::string id;Key key;R weight,speed_m_s;Interval sigma_over_pi_m2;};
struct Kg{R value;};struct J{R value;};struct Density{R value;};
enum class PairKind{SamePopulation,DistinctPopulations};
enum class EnergyLaw{ClosedTwoBody,PrescribedTrajectory};
// Public routines manipulate conditional represented inputs; strings bind identities,
// not scientific authority. Physical promotion is deliberately not implemented.
inline void nonnegative(const R&x){if(x<0)throw Error("NEGATIVE_INPUT");}
inline void positive(const R&x){if(x<=0)throw Error("NONPOSITIVE_INPUT");}
inline void bounded_size(std::size_t n){if(n==0||n>1024)throw Error("REFERENCE_WORKLOAD_BOUND");}
inline void key_ok(const Key&k){for(const auto*s:{&k.model,&k.event,&k.spin,&k.frame,&k.domain})if(s->empty()||s->size()>256)throw Error("EMPTY_OR_LONG_IDENTITY");}
inline void id_ok(const std::string&s){if(s.empty()||s.size()>256)throw Error("EMPTY_OR_LONG_ID");}
inline void nonnegative(const Interval&i){if(i.lo>i.hi)throw Error("REVERSED_INTERVAL");nonnegative(i.lo);}
inline void probability_ok(const Interval&i){nonnegative(i);if(i.hi>1)throw Error("RAW_PROBABILITY_OUT_OF_RANGE");}
inline Interval add(const Interval&a,const Interval&b){return {a.lo+b.lo,a.hi+b.hi};}
inline Interval scale(const Interval&a,const R&w){nonnegative(w);return {w*a.lo,w*a.hi};}
inline Interval product(const Interval&a,const Interval&b){nonnegative(a);nonnegative(b);return {a.lo*b.lo,a.hi*b.hi};}
inline void binding(const Key&a,const Key&b){key_ok(a);key_ok(b);if(!(a==b))throw Error("IDENTITY_MISMATCH");}
inline Interval outgoing_bound(const Interval&p,const Errors&e){
    probability_ok(p);std::set<std::string> owners;
    for(const auto&s:e.owners){id_ok(s);if(!owners.insert(s).second)throw Error("DUPLICATE_ERROR_OWNER");}
    for(const auto*x:{&e.preparation,&e.state,&e.effect,&e.tail})nonnegative(*x);
    R r=2*e.preparation+2*e.state+e.effect+e.tail;
    // Intersection with a proven a priori range, NOT clipping an invalid raw value.
    R lo=p.lo-r,hi=p.hi+r;if(lo<0)lo=0;
    if(hi>1)hi=1;
    return {lo,hi};
}
inline std::vector<Cell> ordered_cells(const Key&k,std::vector<Cell> cells,const R&end){
    key_ok(k);positive(end);bounded_size(cells.size());std::set<std::string> ids;
    for(const auto&c:cells){id_ok(c.id);binding(k,c.key);if(!ids.insert(c.id).second)throw Error("DUPLICATE_CELL");
        if(c.meaning!=Meaning::WholeCellBound)throw Error("POINT_SAMPLE_IS_NOT_A_CELL_BOUND");
        if(c.left<0||c.right<=c.left||c.right>end)throw Error("INVALID_CELL_RANGE");
        nonnegative(c.bound);}
    std::sort(cells.begin(),cells.end(),[](const Cell&a,const Cell&b){return a.left<b.left;});
    R previous=0;for(const auto&c:cells){if(c.left<previous)throw Error("OVERLAPPING_CELLS");previous=c.right;}return cells;
}
template<class Tag> inline void tail_ok(const Key&k,const TailRecord<Tag>&t,const R&end,const std::vector<Cell>&cells){
    id_ok(t.id);binding(k,t.key);if(t.from!=end)throw Error("TAIL_BOUNDARY_MISMATCH");nonnegative(t.bound);
    for(const auto&c:cells)if(t.id==c.id)throw Error("DUPLICATE_TAIL_SOURCE");
}
inline Integral annuli(const Key&k,const std::vector<Cell>&in,const R&end,const std::optional<ImpactTail>&tail){
    auto cells=ordered_cells(k,in,end);Integral out{k,{},std::nullopt,{}};R previous=0;
    for(const auto&c:cells){probability_ok(c.bound);if(c.left>previous)out.gaps.emplace_back(previous,c.left);
        out.partial=add(out.partial,scale(c.bound,c.right-c.left));previous=c.right;}
    if(previous<end)out.gaps.emplace_back(previous,end);
    if(tail){tail_ok(k,*tail,end,cells);if(out.gaps.empty())out.full=add(out.partial,tail->bound);}return out;
}
inline Interval spin_average(const std::vector<SpinTerm>&terms){
    bounded_size(terms.size());std::set<std::string> sectors;R sum=0;Interval value;
    for(const auto&t:terms){id_ok(t.sector);if(!sectors.insert(t.sector).second)throw Error("DUPLICATE_SPIN_SECTOR");nonnegative(t.weight);sum+=t.weight;
        if(t.value){nonnegative(*t.value);value=add(value,scale(*t.value,t.weight));}
        else if(t.weight>0)throw SourceUnavailable("POSITIVE_WEIGHT_SPIN_SECTOR_UNAVAILABLE");}
    if(sum!=1)throw Error("SPIN_WEIGHTS_NOT_NORMALIZED");
    return value;
}
inline R event_density_rate(const R&k,Density na,Density nb,PairKind kind){
    nonnegative(k);nonnegative(na.value);nonnegative(nb.value);
    switch(kind){case PairKind::SamePopulation:if(na.value!=nb.value)throw Error("SAME_POPULATION_DENSITY_MISMATCH");return na.value*na.value*k/2;
        case PairKind::DistinctPopulations:return na.value*nb.value*k;}throw Error("INVALID_PAIR_KIND");
}
inline J relative_energy_from_lab(J lab,Kg a,Kg b){nonnegative(lab.value);positive(a.value);positive(b.value);return {lab.value*b.value/(a.value+b.value)};}
inline Kg reduced_mass(Kg a,Kg b){positive(a.value);positive(b.value);return {a.value*b.value/(a.value+b.value)};}
inline J relative_energy_from_speed(const R&g,Kg a,Kg b){nonnegative(g);return {reduced_mass(a,b).value*g*g/2};}
inline Interval atan_small(const R&z){
    if(z<=0||z>1)throw Error("ATAN_REFERENCE_ARGUMENT");
    R sum=0,p=z,z2=z*z;for(int n=0;n<48;++n){R t=p/(2*n+1);if(n%2)sum-=t;else sum+=t;p*=z2;}return {sum,sum+p/97};
}
inline Interval pi_bound(){static const Interval p=[](){auto a=atan_small(R(1)/5),b=atan_small(R(1)/239);return Interval{16*a.lo-4*b.hi,16*a.hi-4*b.lo};}();return p;}
inline Interval exp_minus(const R&x){
    nonnegative(x);if(x>16)throw Error("REFERENCE_EXP_ARGUMENT_ABOVE_16");
    using boost::multiprecision::numerator;using boost::multiprecision::denominator;using boost::multiprecision::msb;
    if((x!=0&&msb(numerator(x))>80)||msb(denominator(x))>80)throw Error("REFERENCE_EXP_INPUT_BITS");
    if(x==0)return {1,1};
    R z=x;unsigned squarings=0;while(z>1){z/=2;++squarings;}
    // S_32 is an upper, S_33 a lower alternating Taylor bound for 0<z<=1.
    R t=1,sum=1;for(unsigned n=1;n<=32;++n){t*=z;t/=n;if(n%2)sum-=t;else sum+=t;}
    R next=t*z/33;Interval out{sum-next,sum};
    for(unsigned j=0;j<squarings;++j)out=product(out,out);
    return out;
}
inline Interval maxwell_weight(const R&a,const std::optional<R>&b){
    nonnegative(a);if(b&&*b<=a)throw Error("INVALID_MAXWELL_BIN");auto x=scale(exp_minus(a),1+a);
    if(!b)return x;
    auto y=scale(exp_minus(*b),1+*b);R lo=x.lo-y.hi,hi=x.hi-y.lo;
    // The exact integral of x exp(-x) is nonnegative and <=1.
    if(lo<0)lo=0;
    if(hi>1)hi=1;
    return {lo,hi};
}
inline Integral maxwell(const Key&k,const std::vector<Cell>&in,const R&end,const std::optional<EnergyTail>&tail){
    auto cells=ordered_cells(k,in,end);Integral out{k,{},std::nullopt,{}};R previous=0;
    for(const auto&c:cells){if(c.left>previous)out.gaps.emplace_back(previous,c.left);
        out.partial=add(out.partial,product(c.bound,maxwell_weight(c.left,c.right)));previous=c.right;}
    if(previous<end)out.gaps.emplace_back(previous,end);
    if(tail){tail_ok(k,*tail,end,cells);if(out.gaps.empty())out.full=add(out.partial,product(tail->bound,maxwell_weight(end,std::nullopt)));}return out;
}
inline Interval discrete_rate_over_pi(const Key&k,const std::vector<RelativeAtom>&atoms){
    key_ok(k);bounded_size(atoms.size());std::set<std::string> ids;R weights=0;Interval sum;
    for(const auto&a:atoms){id_ok(a.id);binding(k,a.key);if(!ids.insert(a.id).second)throw Error("DUPLICATE_RELATIVE_ATOM");
        nonnegative(a.weight);nonnegative(a.speed_m_s);nonnegative(a.sigma_over_pi_m2);weights+=a.weight;
        sum=add(sum,scale(a.sigma_over_pi_m2,a.weight*a.speed_m_s));}
    if(weights!=1)throw Error("DISTRIBUTION_NOT_NORMALIZED");
    return sum;
}
inline Interval sqrt_point(const R&x){
    nonnegative(x);using boost::multiprecision::cpp_int;using boost::multiprecision::numerator;using boost::multiprecision::denominator;
    cpp_int grid=cpp_int(1)<<80;cpp_int q=numerator(x)*grid*grid/denominator(x);cpp_int f=boost::multiprecision::sqrt(q);
    R lo=R(f)/R(grid);R hi=(lo*lo==x)?lo:R(f+1)/R(grid);return {lo,hi};
}
inline Interval rate_si(const Interval&area_over_pi,Kg mu,J theta){
    nonnegative(area_over_pi);positive(mu.value);positive(theta.value);
    auto a=scale(pi_bound(),8*theta.value/mu.value);Interval speed{sqrt_point(a.lo).lo,sqrt_point(a.hi).hi};
    return product(area_over_pi,speed);
}
inline Interval sigma_si(const Interval&sigma_over_pi){nonnegative(sigma_over_pi);return product(pi_bound(),sigma_over_pi);}
inline Mat observable_derivative(const Mat&a,const Mat&adot,const Mat&g){
    c3a::require_psd(a);c3a::require_psd(c3a::eye(a.nr)-a);if(!c3a::hermitian(adot))throw Error("INVALID_EFFECT_DERIVATIVE");
    if(!c3a::zero(c3a::adj(g)+g))throw Error("GENERATOR_NOT_SKEW_HERMITIAN");
    return adot+a*g-g*a;
}
inline R inverse_square_tail(const R&coefficient,const R&time){nonnegative(coefficient);positive(time);return coefficient/time;}
inline bool closed_channel_open(J e,J defect,EnergyLaw law){
    nonnegative(e.value);switch(law){case EnergyLaw::ClosedTwoBody:return e.value>=std::max(R(0),defect.value);
        case EnergyLaw::PrescribedTrajectory:throw SourceUnavailable("DRIVEN_MODEL_HAS_NO_AUTOMATIC_CLOSED_COLLISION_THRESHOLD");}throw Error("INVALID_ENERGY_LAW");
}
[[noreturn]] inline void request_physical_rate(){throw SourceUnavailable("HH_CHANNEL_FLUX_DOMAIN_INPUTS_NOT_CERTIFIED");}
} // namespace c3b
