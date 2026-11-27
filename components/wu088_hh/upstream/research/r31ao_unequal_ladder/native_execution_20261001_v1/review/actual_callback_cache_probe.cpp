// Independent equality/throughput probe of pre-existing immutable cache.
// Actual Frozen107 inputs; callback values only, zero HH quadrature integrals.
#include "../../ncp64_acceleration_20261001_v1/native_cache/cached_callback.hpp"
#include "../../gap_closure_20261001_g0_g6_v1/validated_callback/assembly.hpp"
#include "frozen107_generated.hpp"
#include <algorithm>
#include <array>
#include <chrono>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#if __FLINT_RELEASE != 30400
#error "The comparison requires pinned FLINT 3.4.0"
#endif

namespace {
struct Value {
    acb_t v;
    Value() { acb_init(v); }
    ~Value() { acb_clear(v); }
    Value(const Value &) = delete;
};
void require(bool value, const char *message) {
    if (!value) throw std::runtime_error(message);
}
std::string quoted(const std::string &value) {
    std::string out="\"";
    for (unsigned char c:value) {
        if (c=='"' || c=='\\') out+='\\';
        if (c<32) throw std::runtime_error("unexpected nonprintable diagnostic");
        out+=static_cast<char>(c);
    }
    return out+'"';
}
std::string dump(const arb_t value) {
    char *raw=arb_dump_str(value);
    if (!raw) throw std::bad_alloc();
    const std::string out(raw); flint_free(raw); return out;
}
void set_dyadic(arb_ptr value, long mantissa, slong exponent) {
    arb_set_si(value,mantissa);
    arb_mul_2exp_si(value,value,exponent);
}
void set_box(acb_t t,acb_t u,bool complex) {
    acb_zero(t); acb_zero(u);
    set_dyadic(acb_realref(t),5,-2);
    set_dyadic(acb_realref(u),3,-1);
    if (complex) {
        set_dyadic(acb_imagref(t),1,-7);
        set_dyadic(acb_imagref(u),-1,-8);
        for (auto part:{acb_realref(t),acb_imagref(t),acb_realref(u),acb_imagref(u)})
            arb_add_error_2exp_si(part,-16);
    }
}
wu088::Contract contract(slong precision) {
    wu088::Contract c;
    c.precision=precision; c.max_precision=precision; c.max_calls=1;
    return c;
}
template<class Function> long long measure(Function function) {
    const auto begin=std::chrono::steady_clock::now();
    function();
    return std::chrono::duration_cast<std::chrono::nanoseconds>(
        std::chrono::steady_clock::now()-begin).count();
}
std::string array(const std::vector<long long> &v) {
    std::ostringstream out; out << '[';
    for (std::size_t i=0;i<v.size();++i) { if(i) out << ','; out << v[i]; }
    out << ']'; return out.str();
}
long long median(std::vector<long long> values) {
    std::sort(values.begin(),values.end()); return values.at(values.size()/2);
}
}

int main() {
    try {
        require(std::string(flint_version)=="3.4.0","FLINT runtime mismatch");
        flint_set_num_threads(1);
        wu088::AssemblyInputs inputs;
        load_frozen107_rational_record(inputs);
        const auto terms=wu088::stored_donor_terms(inputs);
        require(terms.size()==107,"actual Frozen107 term count mismatch");
        std::set<unsigned> is,js,ks;
        unsigned positive=0,negative=0;
        for (const auto &term:terms) {
            is.insert(term.i); js.insert(term.j); ks.insert(term.k);
            const int sign=fmpq_sgn(term.coefficient.value);
            positive+=sign>0; negative+=sign<0;
        }
        require(is.size()==8 && js.size()==8 && ks.size()==9,"actual degree coverage mismatch");
        struct Configuration { slong precision; bool complex; unsigned ia,ib; };
        const std::array<Configuration,4> configurations{{
            {128,false,0,0},{128,true,11,0},
            {256,false,0,11},{256,true,11,11}}};
        std::ostringstream records;
        unsigned case_count=0,comparisons=0,benchmark_cases=0;
        for (const auto &config:configurations)
          for (unsigned active=0;active<2;++active)
            for (unsigned field=0;field<3;++field)
              for (unsigned orbital=0;orbital<3;++orbital) {
                const auto parameters=wu088::canonical_parameters(inputs,config.ia,config.ib,active);
                Value t,u,baseline,cached,first;
                set_box(t.v,u.v,config.complex);
                const bool benchmark=(active==0 && field==0 && orbital==0) ||
                                     (active==1 && field==2 && orbital==2);
                const unsigned repeats=benchmark?3:1;
                benchmark_cases+=benchmark;
                std::vector<long long> baseline_times,cached_times;
                for (unsigned rep=0;rep<repeats;++rep) {
                    auto baseline_contract=contract(config.precision);
                    auto cached_contract=contract(config.precision);
                    wu088::CacheStats stats;
                    int baseline_status=1,cached_status=1;
                    auto run_baseline=[&]() {
                        baseline_times.push_back(measure([&]() {
                            baseline_status=wu088::polynomial_field(baseline.v,terms,
                                static_cast<wu088::Orbital>(orbital),static_cast<wu088::Field>(field),
                                t.v,u.v,parameters,baseline_contract);
                        }));
                    };
                    auto run_cached=[&]() {
                        cached_times.push_back(measure([&]() {
                            cached_status=wu088::polynomial_field_cached(cached.v,terms,
                                static_cast<wu088::Orbital>(orbital),static_cast<wu088::Field>(field),
                                t.v,u.v,parameters,cached_contract,stats);
                        }));
                    };
                    if (rep%2) {run_cached();run_baseline();}
                    else {run_baseline();run_cached();}
                    require(baseline_status==0 && cached_status==0,"actual callback refused");
                    require(acb_is_finite(baseline.v) && acb_is_finite(cached.v),"nonfinite callback");
                    require(acb_equal(baseline.v,cached.v),"baseline/cache exact ball mismatch");
                    require(dump(acb_realref(baseline.v))==dump(acb_realref(cached.v)) &&
                            dump(acb_imagref(baseline.v))==dump(acb_imagref(cached.v)),"ball dump mismatch");
                    require(baseline_contract.calls==cached_contract.calls &&
                            baseline_contract.failures==cached_contract.failures &&
                            baseline_contract.last_error==cached_contract.last_error,"contract mismatch");
                    require(stats.terms_completed==107 && stats.terms_started==107 &&
                            stats.left_requests==107 && stats.right_requests==107 && stats.spatial_requests==107,
                            "signed ordered term coverage mismatch");
                    require(stats.left_evaluations==is.size() && stats.right_evaluations==js.size() &&
                            stats.spatial_evaluations==ks.size(),"cache evaluation count mismatch");
                    if (rep) require(acb_equal(first.v,cached.v),"repeat result mismatch");
                    else acb_set(first.v,cached.v);
                    ++comparisons;
                }
                if (case_count++) records << ',';
                records << "{\"precision_bits\":" << config.precision
                        << ",\"box\":" << quoted(config.complex?"complex_box":"real_point")
                        << ",\"ia\":" << config.ia << ",\"ib\":" << config.ib
                        << ",\"active\":" << active << ",\"field\":" << field << ",\"orbital\":" << orbital
                        << ",\"exact_acb_equal\":true,\"terms\":107,\"helper_evaluations\":[8,8,9]"
                        << ",\"benchmark_repeat\":" << repeats
                        << ",\"baseline_nanoseconds\":" << array(baseline_times)
                        << ",\"cache_nanoseconds\":" << array(cached_times)
                        << ",\"baseline_median_nanoseconds\":" << median(baseline_times)
                        << ",\"cache_median_nanoseconds\":" << median(cached_times)
                        << ",\"real_arb_dump\":" << quoted(dump(acb_realref(first.v)))
                        << ",\"imag_arb_dump\":" << quoted(dump(acb_imagref(first.v))) << '}';
              }
        require(case_count==72 && comparisons==88 && benchmark_cases==8,"probe coverage mismatch");
        std::cout << "{\"schema\":\"WU088_ACTUAL_FROZEN107_CACHE_REVIEW_V1\",\"status\":\"PASS\""
                  << ",\"unique_callback_cases\":" << case_count << ",\"paired_comparisons\":" << comparisons
                  << ",\"benchmark_cases\":" << benchmark_cases
                  << ",\"timing_order\":\"PAIRED_ALTERNATING_THREE_SAMPLES\""
                  << ",\"positive_donor_terms\":" << positive << ",\"negative_donor_terms\":" << negative
                  << ",\"flint_version\":" << quoted(flint_version)
                  << ",\"records\":[" << records.str() << ']' 
                  << ",\"actual_callback_inputs\":true,\"actual_HH_integrals\":0,\"ncp_benchmark\":false"
                  << ",\"historical_abi_admission\":false,\"scientific_admission\":false,\"production_admission\":false}\n";
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "CACHE_PROBE_REJECTED: " << error.what() << '\n';
        return 2;
    }
}
