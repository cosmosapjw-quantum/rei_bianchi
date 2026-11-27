#include "../../gap_closure_20261001_g0_g6_v1/interior_pilot/petras_host.hpp"
#include "../../gap_closure_20261001_g0_g6_v1/validated_callback/assembly.hpp"
#include "frozen107_generated.hpp"
#include "build_identity.hpp"
#include "log_map.hpp"
#ifndef WU088_USE_CACHED
#define WU088_USE_CACHED 0
#endif
#if WU088_USE_CACHED
#include "../../ncp64_acceleration_20261001_v1/native_cache/cached_callback.hpp"
#endif
#include <flint/arf.h>
#include <flint/arb.h>
#include <array>
#include <cstdlib>
#include <iostream>
#include <regex>
#include <stdexcept>
#include <string>

#if __FLINT_RELEASE != 30400
#error "Pinned FLINT 3.4.0 required"
#endif

namespace {
#if WU088_USE_CACHED
int cached_field_bivariate(acb_ptr out,const acb_t inner,const acb_t outer_box,
                           void *opaque,slong analytic_order,slong precision) {
    if (!opaque) {
        for (slong k=0;k<(analytic_order>0?analytic_order:1);++k) acb_indeterminate(out+k);
        return 0;
    }
    // Copy only the adapter; the exact parameters/terms/contract remain owned
    // by main. Preserve the entire complex outer box, never its midpoint.
    auto slice=*static_cast<wu088::CachedSlice *>(opaque);
    slice.source.outer_box=outer_box;
    return wu088::cached_slice_callback(out,inner,&slice,analytic_order,precision);
}
#endif
struct Integer {
    fmpz_t v;
    Integer() { fmpz_init(v); }
    ~Integer() { fmpz_clear(v); }
    Integer(const Integer &) = delete;
};
struct Float {
    arf_t v;
    Float() { arf_init(v); }
    ~Float() { arf_clear(v); }
};
long integer(const char *s, long lo, long hi) {
    const std::string token(s);
    if (token.size()>12 || !std::regex_match(token,std::regex("0|-?[1-9][0-9]*")))
        throw std::invalid_argument("noncanonical integer argument");
    const long value=std::stol(token);
    if (value<lo || value>hi) throw std::invalid_argument("integer argument out of range");
    return value;
}
void hash(const char *s) {
    if (!std::regex_match(s,std::regex("[0-9a-f]{64}")))
        throw std::invalid_argument("lowercase SHA256 required");
}
std::string decimal(const fmpz_t x) {
    char *p=fmpz_get_str(nullptr,10,x);
    if (!p) throw std::bad_alloc();
    const std::string value(p); flint_free(p); return value;
}
std::string interval(const arb_t x) {
    if (!arb_is_finite(x)) throw std::runtime_error("nonfinite serialization refused");
    // The FLINT routine can allocate enormous mantissas when midpoint and
    // radius exponents are far apart. Check both before requesting endpoints.
    Integer mid,me,rad,re,lower,upper,exp;
    Float radius;
    arf_get_fmpz_2exp(mid.v,me.v,arb_midref(x));
    arf_set_mag(radius.v,arb_radref(x));
    arf_get_fmpz_2exp(rad.v,re.v,radius.v);
    if (!fmpz_fits_si(me.v) || !fmpz_fits_si(re.v) ||
        fmpz_cmp_si(me.v,-8192)<0 || fmpz_cmp_si(me.v,8192)>0 ||
        fmpz_cmp_si(re.v,-8192)<0 || fmpz_cmp_si(re.v,8192)>0 ||
        fmpz_bits(mid.v)>4096 || fmpz_bits(rad.v)>4096 ||
        (!fmpz_is_zero(mid.v) && !fmpz_is_zero(rad.v) &&
         std::labs(fmpz_get_si(me.v)-fmpz_get_si(re.v))>4096))
        throw std::runtime_error("endpoint serialization resource cap");
    arb_get_interval_fmpz_2exp(lower.v,upper.v,exp.v,x);
    if (fmpz_bits(lower.v)>8192 || fmpz_bits(upper.v)>8192 ||
        !fmpz_fits_si(exp.v) || fmpz_cmp_si(exp.v,-8192)<0 || fmpz_cmp_si(exp.v,8192)>0)
        throw std::runtime_error("serialized interval resource cap");
    return "{\"lower_mantissa\":\""+decimal(lower.v)+"\",\"upper_mantissa\":\""+
        decimal(upper.v)+"\",\"exponent2\":\""+decimal(exp.v)+"\"}";
}
}

int main(int argc,char **argv) {
    try {
        // Fixed positional interface is generated only by driver.py.
        if (argc!=16) throw std::invalid_argument("expected 15 bounded positional arguments");
        if (std::string(flint_version)!="3.4.0") throw std::runtime_error("runtime FLINT version mismatch");
        const unsigned index=integer(argv[1],0,2591);
        wu088::petras::Ball lt,Tt,lu,Tu,result;
        auto l_t=wu088::log2map::exact_log_endpoint(argv[2],lt.value),T_t=wu088::log2map::exact_log_endpoint(argv[3],Tt.value);
        auto l_u=wu088::log2map::exact_log_endpoint(argv[4],lu.value),T_u=wu088::log2map::exact_log_endpoint(argv[5],Tu.value);
        if (fmpq_cmp(l_t.value,T_t.value)>=0 || fmpq_cmp(l_u.value,T_u.value)>=0)
            throw std::invalid_argument("unordered compact window");
        const slong precision=integer(argv[6],64,1024);
        const slong radius_exp=integer(argv[7],-1024,0);
        const slong goal=integer(argv[8],16,precision);
        const long evaluations=integer(argv[9],1,1000000);
        const long calls=integer(argv[10],1,100000);
        const long wall=integer(argv[11],1,3600);
        const slong panels=integer(argv[12],1,4096);
        const slong degree=integer(argv[13],1,1024);
        hash(argv[14]); hash(argv[15]);
        unsigned rem=index;
        const unsigned ib=rem%12; rem/=12;
        const unsigned ia=rem%12; rem/=12;
        const unsigned orbital=rem%3; rem/=3;
        const unsigned field=rem%3; rem/=3;
        const unsigned active=rem;
        if (wu088::primitive_index(active,field,orbital,ia,ib)!=index)
            throw std::runtime_error("primitive index mismatch");
        wu088::AssemblyInputs inputs;
        load_frozen107_rational_record(inputs);
        auto parameters=wu088::canonical_parameters(inputs,ia,ib,active);
        auto terms=wu088::stored_donor_terms(inputs);
        wu088::Contract contract;
        contract.precision=precision; contract.max_precision=precision;
        contract.max_calls=static_cast<unsigned long>(evaluations);
        // A smaller exact guard is permitted only to establish positivity;
        // it is not a quadrature-error tolerance or a changed target.
        wu088::Rational margin=l_t;
        if (fmpq_cmp(l_u.value,margin.value)<0) margin=l_u;
        // On the closed real rectangle, sigma is decreasing in each variable:
        // sigma >= (1/(a+T_t)+1/(b+T_u))/2 > 0. The former guard based only
        // on lower endpoints rejected valid large real t,u regardless of precision.
        // This does not admit any complex box: unchanged callback guards still
        // test the whole computed balls before principal powers/special functions.
        wu088::Rational denominator_a,denominator_b,inverse_a,inverse_b,sigma_min;
        fmpq_add(denominator_a.value,parameters.a.value,T_t.value);
        fmpq_add(denominator_b.value,parameters.b.value,T_u.value);
        fmpq_inv(inverse_a.value,denominator_a.value);
        fmpq_inv(inverse_b.value,denominator_b.value);
        fmpq_add(sigma_min.value,inverse_a.value,inverse_b.value);
        fmpq_div_2exp(sigma_min.value,sigma_min.value,1);
        if (fmpq_cmp(sigma_min.value,margin.value)<0) margin=sigma_min;
        fmpq_div_2exp(margin.value,margin.value,20);
        if (fmpq_cmp(margin.value,contract.margin.value)<0) contract.margin=margin;
        wu088::Slice slice;
        slice.parameters=&parameters; slice.terms=&terms; slice.contract=&contract;
        slice.orbital=static_cast<wu088::Orbital>(orbital);
        slice.field=static_cast<wu088::Field>(field);
        wu088::petras::Bivariate callback;
#if WU088_USE_CACHED
        wu088::CacheStats cache_stats;
        wu088::CachedSlice cached_slice{slice,&cache_stats};
        callback.callback=cached_field_bivariate; callback.param=&cached_slice;
#else
        callback.callback=wu088::petras::field_bivariate; callback.param=&slice;
#endif
        callback.uniform_whole_parameter_box=true;
        callback.joint_holomorphy_proved=true;
        callback.proof_reference="T1_COMPLEX_DOMAIN_BOUNDS + callback whole-box positivity guards; conditional source contract";
        wu088::log2map::Context log_context(callback,precision);
        wu088::petras::Bivariate transformed=callback;
        transformed.callback=wu088::log2map::callback;
        transformed.param=&log_context;
        transformed.proof_reference="exact log2 substitution; entire exponential images and Jacobian; physical whole-box guards";
        wu088::petras::NestedPlan plan;
        for (auto *p:{&plan.outer,&plan.point_inner,&plan.uniform_inner}) {
            p->precision=precision; p->max_precision=precision;
            p->relative_goal=goal; p->per_call_eval_limit=evaluations;
            p->queued_panel_limit=panels; p->degree_limit=degree;
        }
        plan.outer.absolute_tolerance_exp=radius_exp-16;
        plan.point_inner.absolute_tolerance_exp=radius_exp-32;
        plan.outer.accepted_component_radius_exp=radius_exp;
        plan.point_inner.accepted_component_radius_exp=radius_exp-16;
        // Whole-parameter balls can be wide. Their exact widths propagate
        // through the outer integrator; only its achieved radius is accepted.
        plan.uniform_inner.absolute_tolerance_exp=20;
        plan.uniform_inner.accepted_component_radius_exp=20;
        wu088::petras::GlobalLimits global;
        global.max_dispatched_evaluations=evaluations;
        global.max_integration_calls=calls;
        global.max_nested_integrations=2;
        global.cooperative_wall_seconds=static_cast<double>(wall);
        flint_set_num_threads(1);
        wu088::petras::SharedBudget budget(global);
        const auto report=wu088::petras::integrate_nested_2d(result.value,transformed,
            lt.value,Tt.value,lu.value,Tu.value,plan,budget);
        const bool accepted=report.status==wu088::petras::Status::RADIUS_MET &&
            report.achieved_radius_accepted && !budget.stopped && acb_is_finite(result.value);
        std::string rect="null";
        if (accepted) rect="{\"real\":"+interval(acb_realref(result.value))+
                           ",\"imag\":"+interval(acb_imagref(result.value))+"}";
        std::cout << "{\"schema\":\"WU088_LOG2_NATIVE_INTERIOR_RESULT_V1\",\"status\":\""
                  << wu088::petras::status_name(report.status) << "\",\"accepted\":"
                  << (accepted?"true":"false") << ",\"index\":" << index
                  << ",\"task_sha256\":\"" << argv[14] << "\",\"plan_sha256\":\"" << argv[15]
                  << "\",\"archive_sha256\":\"" << WU088_ARCHIVE_SHA256
                  << "\",\"input_record_sha256\":\"" << WU088_RECORD_SHA256
                  << "\",\"build_source_sha256\":\"" << WU088_BUILD_SOURCE_SHA256
                  << "\",\"precision_bits\":" << precision
                  << ",\"accepted_component_radius_exp\":" << radius_exp
                  << ",\"coordinate_map\":\"LOG2_EXACT_POWER_ENDPOINTS_V1\""
                  << ",\"rectangle\":" << rect
                  << ",\"dispatched_evaluations\":" << budget.dispatched_evaluations
                  << ",\"integration_calls\":" << budget.integration_calls
                  << ",\"analytic_box_refusals\":" << budget.analytic_box_refusals
                  << ",\"callback_calls\":" << contract.calls
                  << ",\"callback_refusals\":" << contract.failures
                  << ",\"flint_status\":" << report.flint_status
                  << ",\"endpoint_included\":false,\"normalization_applied\":false"
                  << ",\"full_domain_integral\":false,\"scientific_admission\":false"
                  << ",\"production_admission\":false}\n";
        return accepted?0:2;
    } catch (const std::exception &e) {
        std::cerr << "NATIVE_DRIVER_REJECTED: " << e.what() << '\n';
        return 64;
    }
}
