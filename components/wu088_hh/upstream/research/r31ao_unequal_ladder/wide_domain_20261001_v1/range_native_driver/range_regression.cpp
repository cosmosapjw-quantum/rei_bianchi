#if WU088_RANGE_HOST
#include "range_petras.hpp"
#include "diagnostics.hpp"
#else
#include "../../gap_closure_20261001_g0_g6_v1/interior_pilot/petras_host.hpp"
#include "../diagnostic_native_driver/diagnostics.hpp"
#endif
#include <iostream>
#include <stdexcept>
using namespace wu088::petras;
namespace {
void require(bool condition,const char *label) {if(!condition)throw std::runtime_error(label);}
int polynomial(acb_ptr out,const acb_t x,const acb_t y,void *,slong,slong precision) {
    acb_mul(out,x,y,precision);acb_mul_2exp_si(out,out,40);return 0;
}
int uncertain(acb_ptr out,const acb_t,void *,slong,slong) {
    acb_one(out);arb_add_error_2exp_si(acb_realref(out),-10);return 0;
}
[[maybe_unused]] int nonfinite(acb_ptr out,const acb_t,void *,slong,slong) {acb_indeterminate(out);return 0;}
NestedPlan make_plan() {
    NestedPlan p;
    for(auto *q:{&p.outer,&p.point_inner,&p.uniform_inner}) {
        q->precision=128;q->max_precision=128;q->relative_goal=128;
        q->per_call_eval_limit=20000;q->degree_limit=64;q->queued_panel_limit=64;
    }
    p.outer.absolute_tolerance_exp=-68;p.outer.accepted_component_radius_exp=-52;
    p.point_inner.absolute_tolerance_exp=-84;p.point_inner.accepted_component_radius_exp=-68;
    p.uniform_inner.absolute_tolerance_exp=20;p.uniform_inner.accepted_component_radius_exp=20;
    return p;
}
GlobalLimits caps() {
    GlobalLimits l;l.max_dispatched_evaluations=20000;l.max_integration_calls=1024;
    l.max_nested_integrations=2;l.cooperative_wall_seconds=10;return l;
}
}
int main() {
    try {
        flint_set_num_threads(1);Ball a,b,out,oracle;acb_one(a.value);acb_set_si(b.value,2);
        Bivariate f{polynomial,nullptr,true,true,"entire polynomial 2^40*x*y"};
        // For this 2^40-scale polynomial, goal 64 permits a relative tolerance
        // much wider than the independently required final radius. Both old
        // and corrected hosts use goal 128 in this focused mechanism test.
        // Production driver defaults and the real HH experiment stay unchanged.
        auto plan=make_plan();SharedBudget budget(caps());
        auto report=integrate_nested_2d(out.value,f,a.value,b.value,a.value,b.value,plan,budget);
        acb_set_si(oracle.value,9);acb_mul_2exp_si(oracle.value,oracle.value,38);
        const auto initial_status=report.status;const auto calls=budget.integration_calls;
        const auto evaluations=budget.dispatched_evaluations;
        const auto analytic=diagnostic::counters.outer_order1_calls;
        const auto wide=diagnostic::counters.inner_radius_too_wide;
#if WU088_RANGE_HOST
        const auto available=diagnostic::counters.inner_enclosure_available;
        if(report.status!=Status::RADIUS_MET || !acb_contains(out.value,oracle.value)) {
            std::cerr<<"status="<<status_name(report.status)<<" reason="<<report.reason<<" eval="<<evaluations
                     <<" calls="<<calls<<" analytic="<<analytic<<" available="<<available<<'\n';
            diagnostic::write(std::cerr);std::cerr<<'\n';
        }
        require(report.status==Status::RADIUS_MET && report.achieved_radius_accepted &&
                acb_contains(out.value,oracle.value),"corrected final radius and independent exact oracle");
        require(analytic>0 && available>0,"finite uniform enclosures enable outer analytic quadrature");
#else
        require(report.status==Status::INTEGRATOR_NO_CONVERGENCE && analytic==0 && wide>0,
                "old intermediate gate reproduces heap starvation");
        const unsigned available=0;
#endif
        // An uncertain POINT result must still fail its tight achieved radius.
        auto p=plan.point_inner;p.absolute_tolerance_exp=20;
        SharedBudget point(caps());report=integrate_1d(out.value,uncertain,nullptr,a.value,b.value,p,point);
        require(report.status==Status::RADIUS_TOO_WIDE && !report.achieved_radius_accepted && !acb_is_finite(out.value),
                "point-inner width remains rejected");
#if WU088_RANGE_HOST
        SharedBudget range(caps());report=integrate_1d(out.value,uncertain,nullptr,a.value,b.value,p,range,true,true);
        require(report.status==Status::ENCLOSURE_AVAILABLE && !report.achieved_radius_accepted && acb_is_finite(out.value),
                "uniform enclosure has distinct non-accuracy status");
        SharedBudget invalid(caps());report=integrate_1d(out.value,nonfinite,nullptr,a.value,b.value,p,invalid,true,true);
        require(report.status!=Status::ENCLOSURE_AVAILABLE && !acb_is_finite(out.value),"nonfinite cannot become enclosure available");
        p.per_call_eval_limit=1;SharedBudget failed(caps());
        report=integrate_1d(out.value,uncertain,nullptr,a.value,b.value,p,failed,true,true);
        require(report.status==Status::INTEGRATOR_NO_CONVERGENCE && !acb_is_finite(out.value),"FLINT failure cannot become enclosure available");
#endif
        std::cout<<"{\"status\":\"PASS\",\"range_host\":"<<(WU088_RANGE_HOST?"true":"false")
                 <<",\"initial_status\":\""<<status_name(initial_status)<<"\",\"dispatched_evaluations\":"<<evaluations
                 <<",\"integration_calls\":"<<calls<<",\"outer_analytic_calls\":"<<analytic
                 <<",\"inner_radius_too_wide\":"<<wide<<",\"inner_enclosure_available\":"<<available
                 <<",\"fixture_relative_goal\":128,\"precision_bits\":128,\"new_hh_evaluations\":0,\"scientific_admission\":false}\n";
        return 0;
    } catch(const std::exception &e) {std::cerr<<e.what()<<'\n';return 2;}
}
