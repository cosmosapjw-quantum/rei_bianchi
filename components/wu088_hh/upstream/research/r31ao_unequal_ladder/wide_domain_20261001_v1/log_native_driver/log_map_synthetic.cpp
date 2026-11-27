#include "log_map.hpp"
#include <iostream>
#include <stdexcept>

using namespace wu088;
using namespace wu088::petras;
namespace {
struct Observation { unsigned calls=0; bool outer_nonexact=false; int mode=0; };
int physical(acb_ptr out,const acb_t t,const acb_t u,void *opaque,slong order,slong precision) {
    auto &o=*static_cast<Observation *>(opaque);++o.calls;
    if (!acb_is_exact(u)) o.outer_nonexact=true;
    if (order>1 || !arb_is_positive(acb_realref(t)) || !arb_is_positive(acb_realref(u))) {
        acb_indeterminate(out);return 0;
    }
    if (o.mode==0) { // f(t,u)=t+2u; asymmetric polynomial oracle.
        acb_mul_ui(out,u,2,precision);acb_add(out,out,t,precision);
    } else { acb_mul(out,t,u,precision);acb_inv(out,out,precision); }
    return 0;
}
void require(bool value,const char *message) { if(!value) throw std::runtime_error(message); }
NestedPlan plan() {
    NestedPlan p;
    for (auto *q:{&p.outer,&p.point_inner,&p.uniform_inner}) {
        q->precision=128;q->max_precision=128;q->relative_goal=64;
        q->per_call_eval_limit=20000;q->degree_limit=64;q->queued_panel_limit=64;
    }
    p.outer.absolute_tolerance_exp=-64;p.outer.accepted_component_radius_exp=-48;
    p.point_inner.absolute_tolerance_exp=-80;p.point_inner.accepted_component_radius_exp=-64;
    p.uniform_inner.absolute_tolerance_exp=20;p.uniform_inner.accepted_component_radius_exp=20;
    return p;
}
GlobalLimits limits() {
    GlobalLimits l;l.max_dispatched_evaluations=20000;l.max_integration_calls=1024;
    l.max_nested_integrations=2;l.cooperative_wall_seconds=10;return l;
}
}
int main() {
    try {
        flint_set_num_threads(1);
        Observation obs;
        Bivariate b{physical,&obs,true,true,"synthetic right-half-plane polynomial/inverse product"};
        log2map::Context context(b,128);
        Bivariate transformed{log2map::callback,&context,true,true,"exact exponential substitution"};
        Ball x0,x1,y0,y1,result,expected;
        log2map::exact_log_endpoint("1/4",x0.value);log2map::exact_log_endpoint("4",x1.value);
        log2map::exact_log_endpoint("1/2",y0.value);log2map::exact_log_endpoint("8",y1.value);
        require(acb_equal_si(x0.value,-2) && acb_equal_si(x1.value,2) &&
                acb_equal_si(y0.value,-1) && acb_equal_si(y1.value,3),"integer endpoint map");
        unsigned invalid=0;
        for (const char *bad:{"3/4","3","2/2","0","-1","1.0"}) {
            try {log2map::exact_log_endpoint(bad,result.value);}
            catch(const std::invalid_argument &) {++invalid;}
        }
        require(invalid==6,"invalid/nonpower endpoint rejection");
        auto p=plan();auto l=limits();SharedBudget budget(l);
        auto report=integrate_nested_2d(result.value,transformed,x0.value,x1.value,y0.value,y1.value,p,budget);
        // ((4^2-(1/4)^2)/2)*(8-1/2) + (4-1/4)*(8^2-(1/2)^2) = 19125/64.
        Rational oracle("19125/64");acb_set_fmpq(expected.value,oracle.value,128);
        require(report.status==Status::RADIUS_MET && acb_contains(result.value,expected.value),"asymmetric polynomial Jacobian integral");
        const auto polynomial_evals=budget.dispatched_evaluations;
        // The wider inverse fixture exhausted its fixed 20k budget in retained
        // attempts 1/2. This compact oracle is a separate bounded test, not a
        // retry with relaxed tolerances or evidence of broad-box convergence.
        obs.mode=1;SharedBudget budget2(l);
        acb_zero(x0.value);acb_one(x1.value);acb_zero(y0.value);acb_one(y1.value);
        report=integrate_nested_2d(result.value,transformed,x0.value,x1.value,y0.value,y1.value,p,budget2);
        // integral over [1,2]^2 dtdu/(tu)=log(2)^2, evaluated independently.
        acb_mul(expected.value,context.log_two.value,context.log_two.value,128);
        if (report.status!=Status::RADIUS_MET || !acb_overlaps(result.value,expected.value)) {
            std::cerr<<"inverse status="<<status_name(report.status)<<" reason="<<report.reason
                     <<" evaluations="<<budget2.dispatched_evaluations<<" calls="<<budget2.integration_calls<<"\n";
            acb_printd(result.value,30);flint_printf("\n");acb_printd(expected.value,30);flint_printf("\n");
        }
        require(report.status==Status::RADIUS_MET && acb_overlaps(result.value,expected.value),"inverse product logarithmic oracle");
        const auto inverse_evals=budget2.dispatched_evaluations;
        // Deliberately nonzero outer radius: the underlying callback must see it.
        acb_zero(x0.value);acb_zero(y0.value);arb_add_error_2exp_si(acb_realref(y0.value),-4);
        obs.outer_nonexact=false;
        log2map::callback(result.value,x0.value,y0.value,&context,1,128);
        require(obs.outer_nonexact && acb_is_finite(result.value),"whole outer parameter image");
        acb_zero(y0.value);arb_set_si(acb_imagref(y0.value),4);
        log2map::callback(result.value,x0.value,y0.value,&context,1,128);
        require(!acb_is_finite(result.value),"high imaginary input conservatively refused");
        // Resource exhaustion is fatal and is never reset by the map adapter.
        acb_zero(x0.value);acb_one(x1.value);acb_zero(y0.value);acb_one(y1.value);
        l.max_dispatched_evaluations=1;SharedBudget exhausted(l);
        report=integrate_nested_2d(result.value,transformed,x0.value,x1.value,y0.value,y1.value,p,exhausted);
        require(exhausted.stopped && report.status==Status::RESOURCE_LIMIT && !acb_is_finite(result.value),"fatal shared resource contract");
        std::cout<<"{\"status\":\"PASS\",\"checks\":7,\"physical_hh_evaluations\":0,\"polynomial_dispatched_evaluations\":"
                 <<polynomial_evals<<",\"inverse_dispatched_evaluations\":"<<inverse_evals
                 <<",\"precision_bits\":128,\"scientific_admission\":false}\n";
        return 0;
    } catch(const std::exception &e) {std::cerr<<e.what()<<'\n';return 2;}
}
