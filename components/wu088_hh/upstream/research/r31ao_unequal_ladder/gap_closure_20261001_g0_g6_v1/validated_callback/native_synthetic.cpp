#include "callback.hpp"
#include "assembly.hpp"
#include <cassert>
#include <iostream>
#include <exception>
#include <flint/acb_hypgeom.h>
#include <flint/acb_calc.h>
#ifdef NDEBUG
#error "Synthetic assertions must remain enabled"
#endif

// SYNTHETIC ONLY. This executable loads no project source arrays or HH inputs.
int main() {
    acb_calc_func_t typed_callback=&wu088::slice_callback;
    assert(typed_callback!=nullptr);
    wu088::Contract c;
    c.precision=192;
    acb_t sigma,s,value,t,u,reference,point;
    acb_init(sigma); acb_init(s); acb_init(value); acb_init(t);
    acb_init(u); acb_init(reference); acb_init(point);
    acb_one(sigma); acb_set_si(s,2);
    const slong exact[5][3]={{1,0,0},{5,1,0},{39,14,2},{407,201,54},{5281,3236,1236}};
    for (unsigned h=0;h<5;++h) for (unsigned r=0;r<3;++r) {
        assert(wu088::radial(value,2*h,r,sigma,s,c)==0);
        assert(acb_contains_fmpq(value,wu088::Rational(std::to_string(exact[h][r]).c_str()).value));
    }
    // A synthetic complex box: whole-box evaluation contains narrow sample balls.
    acb_set_si_si(sigma,1,1); acb_set_si_si(s,2,-1);
    assert(wu088::radial(point,3,1,sigma,s,c)==0);
    arb_add_error_2exp_si(acb_realref(sigma),-5);
    arb_add_error_2exp_si(acb_imagref(sigma),-5);
    arb_add_error_2exp_si(acb_realref(s),-5);
    arb_add_error_2exp_si(acb_imagref(s),-5);
    assert(wu088::radial(value,3,1,sigma,s,c)==0);
    assert(acb_contains(value,point));
    // This box crosses the forbidden real boundary despite its positive midpoint.
    acb_one(sigma); arb_add_error_2exp_si(acb_realref(sigma),1);
    assert(wu088::radial(value,0,0,sigma,s,c)!=0);
    assert(!acb_is_finite(value));
    wu088::Parameters p;
    p.a.set("1"); p.b.set("1"); p.mu.set("1");
    acb_one(t); acb_one(u);
    assert(wu088::primitive(reference,0,wu088::Orbital::S,wu088::Field::O,t,u,p,c)==0);
    assert(wu088::primitive(value,0,wu088::Orbital::S,wu088::Field::G1,t,u,p,c)==0);
    assert(acb_contains_zero(value));
    assert(wu088::primitive(value,0,wu088::Orbital::PZ,wu088::Field::G1,t,u,p,c)==0);
    acb_mul_2exp_si(value,value,1);
    // Independent Gaussian identity: pz G1 = base/2 at these synthetic parameters.
    assert(acb_overlaps(value,reference));
    assert(wu088::primitive(value,0,wu088::Orbital::PX,wu088::Field::G1,t,u,p,c)==0);
    assert(acb_contains_zero(value));
    std::vector<wu088::Term> terms(1);
    terms[0].coefficient.set("1");
    wu088::Slice slice{&p,&terms,&c,u,wu088::Orbital::S,wu088::Field::O};
    assert(wu088::slice_callback(value,t,&slice,1,c.precision)==0);
    assert(acb_is_finite(value));
    acb_struct coefficients[2];
    acb_init(coefficients); acb_init(coefficients+1);
    assert(wu088::slice_callback(coefficients,t,&slice,2,c.precision)==0);
    assert(!acb_is_finite(coefficients) && !acb_is_finite(coefficients+1));
    assert(wu088::slice_callback(coefficients,t,nullptr,2,c.precision)==0);
    assert(!acb_is_finite(coefficients) && !acb_is_finite(coefficients+1));
    acb_clear(coefficients); acb_clear(coefficients+1);
    bool oversized_rejected=false;
    try { wu088::Rational oversized(std::string(wu088::MAX_RATIONAL_TEXT+1,'9').c_str()); (void)oversized; }
    catch (const std::exception &) { oversized_rejected=true; }
    assert(oversized_rejected);
    wu088::Rational preserved("3/7"),expected_preserved("3/7");
    bool invalid_rejected=false;
    try { preserved.set("1/0"); } catch (const std::exception &) { invalid_rejected=true; }
    assert(invalid_rejected && fmpq_equal(preserved.value,expected_preserved.value));
    c.max_calls=c.calls;
    assert(wu088::primitive(value,0,wu088::Orbital::S,wu088::Field::O,t,u,p,c)!=0);
    assert(!acb_is_finite(value));
    // Post-integral assembly on artificial ball data; no callback is invoked here.
    std::string assembly_error;
    wu088::Rational na("4"),nb("9"),npref("7");
    assert(wu088::normalization_factor(reference,na,nb,npref,wu088::Orbital::S,192,assembly_error)==0);
    assert(wu088::normalization_factor(value,na,nb,npref,wu088::Orbital::PZ,192,assembly_error)==0);
    acb_mul_2exp_si(reference,reference,2);
    assert(acb_overlaps(value,reference));
    wu088::AssemblyInputs input;
    for (auto &a:input.exponents) a.set("1");
    input.pref.set("1"); input.v.set("2"); input.z.set("3/4");
    input.s_C[0].set("1"); input.donor_C[0].set("1");
    const auto terms_from_bits=wu088::stored_donor_terms(input);
    assert(terms_from_bits.size()==1 && terms_from_bits[0].i==0 && terms_from_bits[0].k==0);
    const auto geo=wu088::canonical_parameters(input,0,0,1);
    assert(fmpq_equal(geo.q1.value,input.v.value) && fmpq_sgn(geo.q2.value)==0);
    wu088::RealDomainPrimitiveIntegrals integrated;
    acb_one(integrated.unnormalized_real_domain_integrals[wu088::primitive_index(0,0,0,0,0)].value);
    acb_set_si(integrated.unnormalized_real_domain_integrals[wu088::primitive_index(1,0,0,0,0)].value,2);
    acb_set_si_si(integrated.unnormalized_real_domain_integrals[wu088::primitive_index(0,1,0,0,0)].value,2,3);
    acb_set_si_si(integrated.unnormalized_real_domain_integrals[wu088::primitive_index(0,2,0,0,0)].value,-1,4);
    wu088::FinalAssembly assembled;
    assert(wu088::assemble_real_domain(assembled,integrated,input,192,assembly_error)==0);
    acb_mul_2exp_si(reference,assembled.O[0].value,1);
    assert(acb_overlaps(reference,assembled.O[1].value));
    acb_conj(reference,assembled.O[0].value);
    assert(acb_overlaps(reference,assembled.O_row[0].value));
    acb_add(reference,assembled.components_OG[94].value,assembled.components_OG[188].value,192);
    acb_mul_onei(point,assembled.O[0].value); acb_mul_2exp_si(point,point,1);
    acb_add(reference,reference,point,192);
    assert(acb_overlaps(reference,assembled.D_col[0].value));
    input.v.set("0");
    assert(wu088::assemble_real_domain(assembled,integrated,input,192,assembly_error)!=0);
    assert(!acb_is_finite(assembled.D_col[0].value));
    acb_clear(sigma); acb_clear(s); acb_clear(value); acb_clear(t);
    acb_clear(u); acb_clear(reference); acb_clear(point);
    std::cout << "{\"scope\":\"SYNTHETIC_ONLY\",\"native_synthetic_passed\":true}\n";
}
