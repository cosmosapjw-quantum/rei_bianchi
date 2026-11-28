#include "petras_host.hpp"
#include <cassert>
#include <iostream>
using namespace wu088::petras;
namespace {
int square(acb_ptr out,const acb_t t,void *,slong order,slong prec) {
    if (order<0 || order>1) {
        for (slong k=0;k<(order>0 ? order : 1);++k) acb_indeterminate(out+k);
        return 0;
    }
    acb_mul(out,t,t,prec); return 0;
}
int bivariate_toy(acb_ptr out,const acb_t t,const acb_t u,void *,slong order,slong prec) {
    if (order<0 || order>1) { acb_indeterminate(out); return 0; }
    acb_mul(out,t,t,prec); acb_mul(out,out,u,prec); return 0;
}
int domain_toy(acb_ptr out,const acb_t t,const acb_t u,void *param,slong order,slong prec) {
    if (!arb_is_positive(acb_realref(u))) { acb_indeterminate(out); return 0; }
    return bivariate_toy(out,t,u,param,order,prec);
}
int nonfinite(acb_ptr out,const acb_t,void *,slong,slong) {
    acb_indeterminate(out); return 0;
}
int wide_constant(acb_ptr out,const acb_t,void *,slong,slong) {
    acb_one(out); arb_add_error_2exp_si(acb_realref(out),-1); return 0;
}
void contains_rational(const acb_t out,slong numerator,ulong denominator) {
    fmpq_t exact; fmpq_init(exact); fmpq_set_si(exact,numerator,denominator);
    assert(acb_contains_fmpq(out,exact)); fmpq_clear(exact);
}
}
int main() {
    // Only synthetic polynomial/range/refusal fixtures. No input-file loader.
    flint_set_num_threads(1);
    Ball a,b,out,box;
    acb_zero(a.value); acb_one(b.value);
    Limits one;
    {
        SharedBudget budget;
        Report report=integrate_1d(out.value,square,nullptr,a.value,b.value,one,budget);
        assert(report.status==Status::RADIUS_MET);
        contains_rational(out.value,1, 3);
        assert(budget.active_integrations==0);
        std::cout << "one_dimensional_polynomial=";
        acb_printn(out.value,30,0); std::cout << '\n';
    }
    Bivariate polynomial{bivariate_toy,nullptr,true,true,"SYNTHETIC_ENTIRE_POLYNOMIAL_t_squared_times_u"};
    NestedPlan plan;
    {
        acb_set_si(box.value,3); acb_mul_2exp_si(box.value,box.value,-1);
        arb_add_error_2exp_si(acb_realref(box.value),-1);
        arb_add_error_2exp_si(acb_imagref(box.value),0);
        SharedBudget budget;
        Report report=integrate_uniform_inner(out.value,polynomial,a.value,b.value,box.value,1,plan,budget);
        assert(report.status==Status::RADIUS_MET);
        fmpq_t q; fmpq_init(q); fmpq_set_si(q,1, 3);
        assert(arb_contains_fmpq(acb_realref(out.value),q));
        assert(arb_contains_fmpq(acb_imagref(out.value),q));
        fmpq_set_si(q,2,3); assert(arb_contains_fmpq(acb_realref(out.value),q));
        fmpq_set_si(q,-1,3); assert(arb_contains_fmpq(acb_imagref(out.value),q));
        fmpq_clear(q);
    }
    {
        SharedBudget budget;
        Report report=integrate_nested_2d(out.value,polynomial,a.value,b.value,a.value,b.value,plan,budget);
        assert(report.status==Status::RADIUS_MET);
        contains_rational(out.value,1, 6);
        assert(budget.peak_active_integrations==2);
        assert(budget.active_integrations==0);
        std::cout << "nested_polynomial=";
        acb_printn(out.value,30,0); std::cout << '\n';
    }
    {
        Bivariate midpoint_only=polynomial; midpoint_only.uniform_whole_parameter_box=false;
        SharedBudget budget;
        Report report=integrate_nested_2d(out.value,midpoint_only,a.value,b.value,a.value,b.value,plan,budget);
        assert(report.status==Status::INVALID_CONTRACT && !acb_is_finite(out.value));
        assert(budget.integration_calls==0);
    }
    {
        GlobalLimits limit; limit.max_dispatched_evaluations = 1;
        SharedBudget budget(limit);
        Report report=integrate_1d(out.value,square,nullptr,a.value,b.value,one,budget);
        assert(report.status==Status::RESOURCE_LIMIT && !acb_is_finite(out.value));
        assert(budget.dispatched_evaluations<=1);
    }
    {
        GlobalLimits limit; limit.max_nested_integrations=1;
        SharedBudget budget(limit);
        Report report=integrate_nested_2d(out.value,polynomial,a.value,b.value,a.value,b.value,plan,budget);
        assert(report.status==Status::RESOURCE_LIMIT && !acb_is_finite(out.value));
        assert(budget.active_integrations==0);
    }
    {
        SharedBudget budget;
        Report report=integrate_1d(out.value,nonfinite,nullptr,a.value,b.value,one,budget);
        assert(report.status==Status::NONFINITE_CALLBACK && !acb_is_finite(out.value));
    }
    {
        Limits wide=one; wide.absolute_tolerance_exp=20; wide.accepted_component_radius_exp=-100;
        SharedBudget budget;
        Report report=integrate_1d(out.value,wide_constant,nullptr,a.value,b.value,wide,budget);
        assert(report.status==Status::RADIUS_TOO_WIDE && !acb_is_finite(out.value));
        assert(!report.real_radius_dump.empty() && !report.imag_radius_dump.empty());
    }
    {
        wu088::Slice missing;
        field_bivariate(out.value,a.value,b.value,&missing,0,128);
        assert(!acb_is_finite(out.value));
    }
    {
        // Review P01: outer analytic trial-domain refusal must not poison a
        // later valid trial; this fixture is pending actual native execution.
        Bivariate guarded{domain_toy,nullptr,true,true,"SYNTHETIC_RIGHT_HALF_PLANE_u"};
        SharedBudget budget;
        acb_zero(box.value); arb_add_error_2exp_si(acb_realref(box.value),0);
        Report bad=integrate_uniform_inner(out.value,guarded,a.value,b.value,box.value,1,plan,budget);
        assert(bad.status==Status::NONFINITE_CALLBACK && !budget.stopped);
        assert(!acb_is_finite(out.value));
        acb_one(box.value);
        Report good=integrate_uniform_inner(out.value,guarded,a.value,b.value,box.value,1,plan,budget);
        assert(good.status==Status::RADIUS_MET && !budget.stopped);
        contains_rational(out.value,1,3);
    }
    std::cout << "{\"synthetic_only\":true,\"native_fixture_checks\":10,\"actual_HH_evaluations\":0}\n";
}
