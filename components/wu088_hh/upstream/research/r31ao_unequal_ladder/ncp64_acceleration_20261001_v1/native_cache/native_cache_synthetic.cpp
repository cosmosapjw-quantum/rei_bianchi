#include "cached_callback.hpp"
#include <flint/acb_calc.h>
#include <flint/flint.h>
#include <chrono>
#include <cerrno>
#include <cstdlib>
#include <fcntl.h>
#include <iomanip>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unistd.h>
#ifdef NDEBUG
#error "Synthetic exact-equality checks must not be disabled"
#endif

// SYNTHETIC ONLY: no project input loader and no actual HH parameters.
namespace {
struct Value {
    acb_t v;
    Value() { acb_init(v); }
    ~Value() { acb_clear(v); }
    Value(const Value &)=delete;
    Value &operator=(const Value &)=delete;
};
void require(bool condition,const std::string &message) {
    if (!condition) throw std::runtime_error(message);
}
std::string quoted(const std::string &s) {
    std::ostringstream out;
    out << '"';
    for (unsigned char ch:s) {
        if (ch=='"' || ch=='\\') out << '\\' << static_cast<char>(ch);
        else if (ch<32) out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<unsigned>(ch) << std::dec;
        else out << static_cast<char>(ch);
    }
    out << '"'; return out.str();
}
std::string dump_real(arb_srcptr x) {
    char *raw=arb_dump_str(x);
    if (!raw) throw std::runtime_error("arb_dump_str allocation failed");
    std::string result(raw); flint_free(raw); return result;
}
std::string dump(const acb_t x) {
    return "{\"real_arb_dump\":"+quoted(dump_real(acb_realref(x)))+
        ",\"imag_arb_dump\":"+quoted(dump_real(acb_imagref(x)))+"}";
}
void same(const acb_t baseline,const acb_t cached,bool finite) {
    require(dump(baseline)==dump(cached),"component ball dumps differ");
    if (finite) {
        require(acb_is_finite(baseline) && acb_is_finite(cached),"successful result is nonfinite");
        require(acb_equal(baseline,cached),"acb_equal failed (overlap is insufficient)");
    } else require(!acb_is_finite(baseline) && !acb_is_finite(cached),"failure did not invalidate both results");
}
void same_contract(const wu088::Contract &a,const wu088::Contract &b) {
    require(a.calls==b.calls && a.failures==b.failures && a.last_error==b.last_error,
            "contract counters or error message differ");
}
void set_component(arb_ptr out,const char *text,slong precision) {
    wu088::Rational q(text); arb_set_fmpq(out,q.value,precision);
}
void set_box(acb_t t,acb_t u,const std::string &id,slong precision) {
    acb_set_si(t,2); acb_set_si(u,3);
    if (id=="complex_point107" || id=="complex_box107") {
        set_component(acb_imagref(t),"1/8",precision);
        set_component(acb_imagref(u),"-1/16",precision);
    }
    if (id=="complex_box107") {
        arb_add_error_2exp_si(acb_realref(t),-10);
        arb_add_error_2exp_si(acb_imagref(t),-11);
        arb_add_error_2exp_si(acb_realref(u),-11);
        arb_add_error_2exp_si(acb_imagref(u),-10);
    }
}
wu088::Parameters parameters() {
    wu088::Parameters p;
    p.a.set("3/2"); p.b.set("5/4"); p.mu.set("7/5");
    p.q1.set("1/3"); p.q2.set("-2/5");
    p.d1[0].set("1/4"); p.d1[1].set("-1/5"); p.d1[2].set("1/3");
    p.d2[0].set("-1/3"); p.d2[1].set("1/7"); p.d2[2].set("-1/4");
    return p;
}
std::vector<wu088::Term> terms107() {
    std::vector<wu088::Term> terms(107);
    for (unsigned n=0;n<107;++n) {
        terms[n].i=n%9; terms[n].j=(n/9)%9; terms[n].k=(5*n+3)%9;
        const std::string coeff=(n%2 ? "-" : "")+std::to_string(n%7+1)+"/"+std::to_string(n%5+2);
        terms[n].coefficient.set(coeff.c_str());
    }
    return terms;
}
wu088::Contract contract(slong precision) {
    wu088::Contract c; c.precision=precision; c.max_precision=wu088::MAX_PRECISION_BITS;
    c.max_calls=1; return c;
}
unsigned long number(const std::string &s,unsigned long maximum) {
    if (s.empty() || s.size()>10 || s.find_first_not_of("0123456789")!=std::string::npos)
        throw std::invalid_argument("bounded unsigned decimal option required");
    unsigned long value=0;
    for (char ch:s) {
        const auto digit=static_cast<unsigned long>(ch-'0');
        if (value>(maximum-digit)/10 || digit>maximum)
            throw std::invalid_argument("option exceeds cap");
        value=value*10+digit;
        if (value>maximum) throw std::invalid_argument("option exceeds cap");
    }
    return value;
}
struct Options { std::string output,id="point107"; unsigned long repeat=1; slong precision=128; };
Options options(int argc,char **argv) {
    Options opt; std::set<std::string> seen;
    for (int i=1;i<argc;i+=2) {
        require(i+1<argc,"option value is missing");
        const std::string key(argv[i]),value(argv[i+1]);
        require(seen.insert(key).second,"duplicate CLI option");
        if (key=="--output") opt.output=value;
        else if (key=="--case") opt.id=value;
        else if (key=="--repeat") opt.repeat=number(value,100);
        else if (key=="--precision") opt.precision=static_cast<slong>(number(value,4096));
        else throw std::invalid_argument("unknown CLI option");
    }
    require(!opt.output.empty() && opt.output[0]=='/' && opt.output.size()<=4096,"absolute --output path required");
    require(opt.repeat>=1 && opt.precision>=32,"repeat/precision below supported lower bound");
    require(opt.id=="point107" || opt.id=="complex_point107" || opt.id=="complex_box107" || opt.id=="errors","unknown synthetic case");
    require(opt.id!="errors" || opt.repeat==1,"errors case requires --repeat 1");
    return opt;
}
void write_new(const std::string &path,const std::string &payload) {
    require(payload.size()<=1024*1024,"synthetic payload exceeds cap");
    const int fd=open(path.c_str(),O_WRONLY|O_CREAT|O_EXCL,0600);
    if (fd<0) throw std::runtime_error("cannot create new output file");
    std::size_t offset=0;
    while (offset<payload.size()) {
        const ssize_t n=write(fd,payload.data()+offset,payload.size()-offset);
        if (n<0 && errno==EINTR) continue;
        if (n<=0) { close(fd); throw std::runtime_error("payload write failed"); }
        offset+=static_cast<std::size_t>(n);
    }
    if (close(fd)!=0) throw std::runtime_error("payload close failed");
}
struct Timing {
    double baseline_seconds=0,cached_seconds=0;
    unsigned long comparisons=0,baseline_density_count_model=0,baseline_spatial_count_model=0;
    unsigned long density_evaluations=0,spatial_evaluations=0,density_hits=0,spatial_hits=0;
};
std::string scientific_case(const Options &opt,Timing &timing) {
    const wu088::Parameters p=parameters();
    const auto terms=terms107();
    Value t,u,baseline,cached;
    set_box(t.v,u.v,opt.id,opt.precision);
    std::ostringstream records;
    bool first=true;
    for (int orbital=0;orbital<3;++orbital) for (int field=0;field<3;++field) {
        Value first_value;
        for (unsigned long rep=0;rep<opt.repeat;++rep) {
            auto cb=contract(opt.precision),cc=contract(opt.precision);
            wu088::CacheStats stats;
            int rb=1,rc=1;
            auto run_baseline=[&]() {
                const auto begin=std::chrono::steady_clock::now();
                rb=wu088::polynomial_field(baseline.v,terms,static_cast<wu088::Orbital>(orbital),
                    static_cast<wu088::Field>(field),t.v,u.v,p,cb);
                timing.baseline_seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
            };
            auto run_cached=[&]() {
                const auto begin=std::chrono::steady_clock::now();
                rc=wu088::polynomial_field_cached(cached.v,terms,static_cast<wu088::Orbital>(orbital),
                    static_cast<wu088::Field>(field),t.v,u.v,p,cc,stats);
                timing.cached_seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();
            };
            if (rep%2) { run_cached(); run_baseline(); }
            else { run_baseline(); run_cached(); }
            require(rb==0 && rc==0,"valid synthetic callback refused: "+cb.last_error+" / "+cc.last_error);
            same(baseline.v,cached.v,true); same_contract(cb,cc);
            if (rep==0) acb_set(first_value.v,cached.v);
            else same(first_value.v,cached.v,true);
            require(stats.terms_started==107 && stats.terms_completed==107,"term count changed");
            require(stats.left_requests==107 && stats.right_requests==107 && stats.spatial_requests==107,"term request count changed");
            require(stats.left_evaluations==9 && stats.right_evaluations==9 && stats.spatial_evaluations==9,"per-invocation cache count mismatch");
            require(stats.left_hits==98 && stats.right_hits==98 && stats.spatial_hits==98,"cache reuse count mismatch");
            ++timing.comparisons;
            timing.baseline_density_count_model+=214; timing.baseline_spatial_count_model+=107;
            timing.density_evaluations+=stats.left_evaluations+stats.right_evaluations;
            timing.spatial_evaluations+=stats.spatial_evaluations;
            timing.density_hits+=stats.left_hits+stats.right_hits; timing.spatial_hits+=stats.spatial_hits;
        }
        if (!first) records << ',';
        first=false;
        records << "{\"orbital\":" << orbital << ",\"field\":" << field << ",\"value\":" << dump(cached.v) << '}';
    }
    return "{\"parameters\":{\"a\":\"3/2\",\"b\":\"5/4\",\"mu\":\"7/5\",\"q1\":\"1/3\",\"q2\":\"-2/5\","
        "\"d1\":[\"1/4\",\"-1/5\",\"1/3\"],\"d2\":[\"-1/3\",\"1/7\",\"-1/4\"]},"
        "\"term_recipe\":\"n=0..106;i=n%9;j=(n/9)%9;k=(5*n+3)%9;c=(-1)^n*(n%7+1)/(n%5+2)\","
        "\"t\":"+dump(t.v)+",\"u\":"+dump(u.v)+",\"balls\":["+records.str()+"]}";
}
std::string error_case(const Options &opt,Timing &timing) {
    Value t,u,baseline,cached;
    set_box(t.v,u.v,"point107",opt.precision);
    std::ostringstream records;
    bool first=true;
    const std::vector<std::string> cases={"empty_terms","too_many_terms","bad_i","bad_j","bad_k","mu_zero", "a_zero",
        "bad_orbital","bad_field","whole_box_crosses_zero","precision_low","precision_over_cap","budget_zero"};
    for (const auto &id:cases) {
        auto p=parameters(); auto terms=terms107();
        auto cb=contract(opt.precision),cc=contract(opt.precision);
        auto orbital=wu088::Orbital::PZ; auto field=wu088::Field::G1;
        set_box(t.v,u.v,"point107",opt.precision);
        if (id=="empty_terms") terms.clear();
        if (id=="too_many_terms") terms.resize(108);
        if (id=="bad_i") terms[0].i=9;
        if (id=="bad_j") terms[0].j=9;
        if (id=="bad_k") terms[0].k=9;
        if (id=="mu_zero") p.mu.set("0");
        if (id=="a_zero") p.a.set("0");
        if (id=="bad_orbital") orbital=static_cast<wu088::Orbital>(9);
        if (id=="bad_field") field=static_cast<wu088::Field>(9);
        if (id=="whole_box_crosses_zero") arb_add_error_2exp_si(acb_realref(t.v),2);
        if (id=="precision_low") cb.precision=cc.precision=16;
        if (id=="precision_over_cap") cb.max_precision=cc.max_precision=4097;
        if (id=="budget_zero") cb.max_calls=cc.max_calls=0;
        wu088::CacheStats stats;
        const int rb=wu088::polynomial_field(baseline.v,terms,orbital,field,t.v,u.v,p,cb);
        const int rc=wu088::polynomial_field_cached(cached.v,terms,orbital,field,t.v,u.v,p,cc,stats);
        require(rb!=0 && rc==rb,"error status differs"); same(baseline.v,cached.v,false); same_contract(cb,cc);
        require(stats.terms_completed==0,"failed first term completed unexpectedly");
        if (cb.calls==0) require(stats.left_requests+stats.right_requests+stats.spatial_requests==0,"budget/precision refusal did work");
        if (!first) records << ',';
        first=false;
        records << "{\"case\":" << quoted(id) << ",\"result\":" << dump(cached.v) << '}';
        ++timing.comparisons;
    }
    // Whole-box adapter, precision mismatch, unsupported coefficient slots and
    // exhausted second call. One-term data keeps these boundary tests cheap.
    auto p=parameters(); auto terms=terms107(); terms.resize(1);
    set_box(t.v,u.v,"complex_box107",opt.precision);
    for (slong order: {slong(0),slong(1),slong(2)}) {
        for (bool mismatch: {false,true}) {
            auto cb=contract(opt.precision),cc=contract(opt.precision);
            wu088::CacheStats stats;
            wu088::Slice bs{&p,&terms,&cb,u.v,wu088::Orbital::PZ,wu088::Field::G2};
            wu088::CachedSlice cs{{&p,&terms,&cc,u.v,wu088::Orbital::PZ,wu088::Field::G2},&stats};
            acb_struct bo[2],co[2];
            acb_init(bo); acb_init(bo+1); acb_init(co); acb_init(co+1);
            const slong precision=opt.precision+(mismatch ? 1 : 0);
            wu088::slice_callback(bo,t.v,&bs,order,precision);
            wu088::cached_slice_callback(co,t.v,&cs,order,precision);
            same(bo,co,order<=1 && !mismatch); same_contract(cb,cc);
            if (order==2) same(bo+1,co+1,false);
            acb_clear(bo); acb_clear(bo+1); acb_clear(co); acb_clear(co+1);
            ++timing.comparisons;
        }
    }
    auto cb=contract(opt.precision),cc=contract(opt.precision);
    wu088::CacheStats stats;
    for (unsigned attempt=0;attempt<2;++attempt) {
        const int rb=wu088::polynomial_field(baseline.v,terms,wu088::Orbital::S,wu088::Field::O,t.v,u.v,p,cb);
        const int rc=wu088::polynomial_field_cached(cached.v,terms,wu088::Orbital::S,wu088::Field::O,t.v,u.v,p,cc,stats);
        require(rb==rc && (attempt==0 ? rb==0 : rb!=0),"second call budget behavior changed");
        same(baseline.v,cached.v,attempt==0); same_contract(cb,cc);
        if (attempt==1) require(stats.terms_started==0 && stats.spatial_evaluations==0,"cache survived budget refusal");
        ++timing.comparisons;
    }
    acb_struct invalid_baseline[2],invalid_cached[2];
    acb_init(invalid_baseline); acb_init(invalid_baseline+1);
    acb_init(invalid_cached); acb_init(invalid_cached+1);
    wu088::slice_callback(invalid_baseline,t.v,nullptr,2,opt.precision);
    wu088::cached_slice_callback(invalid_cached,t.v,nullptr,2,opt.precision);
    same(invalid_baseline,invalid_cached,false);
    same(invalid_baseline+1,invalid_cached+1,false);
    acb_clear(invalid_baseline); acb_clear(invalid_baseline+1);
    acb_clear(invalid_cached); acb_clear(invalid_cached+1);
    ++timing.comparisons;
    return "{\"error_results\":["+records.str()+"],\"slice_and_budget_checks\":\"EXACT_DUMP_AND_CONTRACT_EQUAL\"}";
}
}
int main(int argc,char **argv) {
    try {
        const Options opt=options(argc,argv);
        flint_set_num_threads(1);
        require(flint_get_num_threads()==1,"one FLINT thread per worker required");
        acb_calc_func_t typed=&wu088::cached_slice_callback;
        require(typed!=nullptr,"callback signature mismatch");
        Timing timing;
        const std::string result=(opt.id=="errors" ? error_case(opt,timing) : scientific_case(opt,timing));
        const std::string payload="{\"schema\":\"WU088_CACHE_SYNTHETIC_PAYLOAD_V1\",\"scope\":\"SYNTHETIC_ONLY\",\"case\":"+
            quoted(opt.id)+",\"precision\":"+std::to_string(opt.precision)+
            ",\"equality\":\"EXACT_BALL_AND_COMPONENT_DUMP\",\"actual_HH_runs\":0,\"result\":"+result+"}\n";
        write_new(opt.output,payload);
        std::cout << std::setprecision(17)
            << "{\"scope\":\"SYNTHETIC_ONLY\",\"exact_equality_passed\":true,\"case\":" << quoted(opt.id)
            << ",\"repeat\":" << opt.repeat << ",\"precision\":" << opt.precision
            << ",\"timing_order\":\"PAIRED_ALTERNATING\""
            << ",\"comparisons\":" << timing.comparisons << ",\"baseline_seconds\":" << timing.baseline_seconds
            << ",\"cached_seconds\":" << timing.cached_seconds
            << ",\"baseline_density_count_model\":" << timing.baseline_density_count_model
            << ",\"baseline_spatial_count_model\":" << timing.baseline_spatial_count_model
            << ",\"observed_density_evaluations\":" << timing.density_evaluations
            << ",\"observed_spatial_evaluations\":" << timing.spatial_evaluations
            << ",\"observed_density_hits\":" << timing.density_hits
            << ",\"observed_spatial_hits\":" << timing.spatial_hits << ",\"actual_HH_runs\":0}\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "{\"status\":\"REFUSED_OR_EQUALITY_FAILED\",\"reason\":" << quoted(error.what()) << "}\n";
        return 2;
    }
}
