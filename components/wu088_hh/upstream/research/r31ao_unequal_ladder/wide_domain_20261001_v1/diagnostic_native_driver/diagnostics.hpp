#pragma once
#include <cstddef>
#include <ostream>
#include <array>
#include <string>
#include <vector>
#include <flint/arb.h>
namespace wu088::petras::diagnostic {
// One process, one worker, one FLINT thread. Counters are observational only.
struct Counters {
    std::size_t preflight_calls=0,preflight_nonfinite=0;
    std::size_t nonfinite_order1=0,nonfinite_order0_range=0,nonfinite_order0_exact=0;
    std::size_t selected_point_inner=0,selected_uniform_inner=0;
    std::size_t inner_radius_met=0,inner_radius_too_wide=0,inner_no_convergence=0;
    std::size_t inner_nonfinite=0,inner_resource_limit=0,inner_invalid_contract=0;
    std::size_t outer_order1_calls=0,outer_order0_range_calls=0,outer_order0_exact_calls=0;
    std::size_t outer_order1_failures=0,outer_order0_range_failures=0,outer_order0_exact_failures=0;
    std::size_t outer_refinable_failures=0,outer_fatal_failures=0;
    std::size_t peak_active_integrations=0;
};
inline Counters counters;
// Categories: outer order0 exact, order0 nonexact, order1; point/uniform;
// inner RADIUS_MET, RADIUS_TOO_WIDE, NO_CONVERGENCE, NONFINITE, RESOURCE, INVALID.
inline std::array<std::array<std::array<std::size_t,6>,2>,3> inner_outcomes{};
struct Snapshot {
    bool observed=false,finite=false,truncated=false;
    int flint_status=-1;
    std::string real,imag,real_radius,imag_radius;
};
inline Snapshot last_inner;
inline std::string bounded(char *raw,bool &truncated) {
    std::string s(raw);flint_free(raw);
    if(s.size()>2048) {s.resize(2048);truncated=true;}
    return s;
}
inline void observe_inner_return(const acb_t out,int code) {
    last_inner=Snapshot{};last_inner.observed=true;last_inner.flint_status=code;
    last_inner.finite=acb_is_finite(out);
    if(last_inner.finite) {
        last_inner.real=bounded(arb_dump_str(acb_realref(out)),last_inner.truncated);
        last_inner.imag=bounded(arb_dump_str(acb_imagref(out)),last_inner.truncated);
        last_inner.real_radius=bounded(mag_dump_str(arb_radref(acb_realref(out))),last_inner.truncated);
        last_inner.imag_radius=bounded(mag_dump_str(arb_radref(acb_imagref(out))),last_inner.truncated);
    }
}
struct FailureSample {
    slong outer_order,precision,absolute_tolerance_exp,accepted_component_radius_exp,relative_goal;
    bool outer_exact,uniform_inner,truncated=false;
    std::string status,reason,outer_real,outer_imag;
    int flint_status;
    Snapshot inner;
};
inline std::vector<FailureSample> failures;
inline void record_failure(const acb_t outer,slong order,const Limits &selected,bool uniform,const Report &report) {
    FailureSample s{order,selected.precision,selected.absolute_tolerance_exp,selected.accepted_component_radius_exp,
        selected.relative_goal,static_cast<bool>(acb_is_exact(outer)),uniform,false,status_name(report.status),report.reason,"","",report.flint_status,last_inner};
    s.outer_real=bounded(arb_dump_str(acb_realref(outer)),s.truncated);
    s.outer_imag=bounded(arb_dump_str(acb_imagref(outer)),s.truncated);
    // Keep the first seven failures and the latest failure, at most eight.
    if(failures.size()<8)failures.push_back(s);else failures[7]=s;
}
inline void quoted(std::ostream &out,const std::string &s) {
    out<<'"';for(char c:s) {if(c=='"'||c=='\\')out<<'\\';if(c=='\n')out<<"\\n";else out<<c;}out<<'"';
}
inline void write(std::ostream &out) {
    out<<"{\"counters\":{";
#define WU088_DIAG_FIELD(name) out<<"\"" #name "\":"<<counters.name<<",";
    WU088_DIAG_FIELD(preflight_calls)
    WU088_DIAG_FIELD(preflight_nonfinite)
    WU088_DIAG_FIELD(nonfinite_order1)
    WU088_DIAG_FIELD(nonfinite_order0_range)
    WU088_DIAG_FIELD(nonfinite_order0_exact)
    WU088_DIAG_FIELD(selected_point_inner)
    WU088_DIAG_FIELD(selected_uniform_inner)
    WU088_DIAG_FIELD(inner_radius_met)
    WU088_DIAG_FIELD(inner_radius_too_wide)
    WU088_DIAG_FIELD(inner_no_convergence)
    WU088_DIAG_FIELD(inner_nonfinite)
    WU088_DIAG_FIELD(inner_resource_limit)
    WU088_DIAG_FIELD(inner_invalid_contract)
    WU088_DIAG_FIELD(outer_order1_calls)
    WU088_DIAG_FIELD(outer_order0_range_calls)
    WU088_DIAG_FIELD(outer_order0_exact_calls)
    WU088_DIAG_FIELD(outer_order1_failures)
    WU088_DIAG_FIELD(outer_order0_range_failures)
    WU088_DIAG_FIELD(outer_order0_exact_failures)
    WU088_DIAG_FIELD(outer_refinable_failures)
    WU088_DIAG_FIELD(outer_fatal_failures)
#undef WU088_DIAG_FIELD
    out<<"\"peak_active_integrations\":"<<counters.peak_active_integrations<<"},\"inner_outcomes\":[";
    for(unsigned a=0;a<3;++a) {if(a)out<<',';out<<'[';
        for(unsigned b=0;b<2;++b) {if(b)out<<',';out<<'[';
            for(unsigned c=0;c<6;++c) {if(c)out<<',';out<<inner_outcomes[a][b][c];}out<<']';}out<<']';}
    out<<"],\"failure_samples\":[";
    for(std::size_t i=0;i<failures.size();++i) {
        if(i)out<<',';
        const auto &s=failures[i];
        out<<"{\"outer_order\":"<<s.outer_order<<",\"precision_bits\":"<<s.precision
           <<",\"absolute_tolerance_exp\":"<<s.absolute_tolerance_exp
           <<",\"accepted_component_radius_exp\":"<<s.accepted_component_radius_exp<<",\"relative_goal\":"<<s.relative_goal
           <<",\"outer_exact\":"<<(s.outer_exact?"true":"false")<<",\"uniform_inner\":"<<(s.uniform_inner?"true":"false")
           <<",\"truncated\":"<<(s.truncated?"true":"false")<<",\"status\":";quoted(out,s.status);
        out<<",\"reason\":";quoted(out,s.reason);out<<",\"outer_real\":";quoted(out,s.outer_real);
        out<<",\"outer_imag\":";quoted(out,s.outer_imag);out<<",\"flint_status\":"<<s.flint_status;
        const auto &r=s.inner;
        out<<",\"inner_return\":{\"observed\":"<<(r.observed?"true":"false")<<",\"finite\":"<<(r.finite?"true":"false")
           <<",\"truncated\":"<<(r.truncated?"true":"false")<<",\"flint_status\":"<<r.flint_status<<",\"real\":";quoted(out,r.real);
        out<<",\"imag\":";quoted(out,r.imag);out<<",\"real_radius\":";quoted(out,r.real_radius);
        out<<",\"imag_radius\":";quoted(out,r.imag_radius);out<<"}}";
    }
    out<<"]}";
}
}
