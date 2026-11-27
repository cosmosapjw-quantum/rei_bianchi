#include "assembly.hpp"
#include <stdexcept>

// S01 od_run.assemble and S02 H0Fused.h0, ideal exact-lift target.
// Conjugation is confined to this post-real-domain-integration translation unit.
#if __FLINT_VERSION != 3 || __FLINT_VERSION_MINOR != 4 || __FLINT_VERSION_PATCHLEVEL != 0
#error "Pinned FLINT 3.4.0 required"
#endif
namespace wu088 {
ComplexBall::ComplexBall() { acb_init(value); }
ComplexBall::ComplexBall(const ComplexBall &other):ComplexBall() { acb_set(value,other.value); }
ComplexBall::ComplexBall(ComplexBall &&other) noexcept:ComplexBall() { acb_swap(value,other.value); }
ComplexBall &ComplexBall::operator=(const ComplexBall &other) { acb_set(value,other.value); return *this; }
ComplexBall::~ComplexBall() { acb_clear(value); }
namespace {
ComplexBall exact(const Rational &q,slong p) { require_bounded_rational(q); ComplexBall x; acb_set_fmpq(x.value,q.value,p); return x; }
ComplexBall integer(slong n) { ComplexBall x; acb_set_si(x.value,n); return x; }
ComplexBall add(const ComplexBall &a,const ComplexBall &b,slong p) { ComplexBall x; acb_add(x.value,a.value,b.value,p); return x; }
ComplexBall sub(const ComplexBall &a,const ComplexBall &b,slong p) { ComplexBall x; acb_sub(x.value,a.value,b.value,p); return x; }
ComplexBall mul(const ComplexBall &a,const ComplexBall &b,slong p) { ComplexBall x; acb_mul(x.value,a.value,b.value,p); return x; }
ComplexBall div(const ComplexBall &a,const ComplexBall &b,slong p) { ComplexBall x; acb_div(x.value,a.value,b.value,p); return x; }
ComplexBall neg(const ComplexBall &a) { ComplexBall x; acb_neg(x.value,a.value); return x; }
ComplexBall conjugate_after_integral(const ComplexBall &a) { ComplexBall x; acb_conj(x.value,a.value); return x; }
ComplexBall times_i(const ComplexBall &a) { ComplexBall x; acb_mul_onei(x.value,a.value); return x; }
void finite(const ComplexBall &a) {
    if (!acb_is_finite(a.value)) throw std::domain_error("nonfinite input or output integral ball");
}
void precision_check(slong p) {
    if (p<32 || p>MAX_PRECISION_BITS) throw std::domain_error("assembly precision outside 32..4096 draft cap");
}
void validate_inputs(const AssemblyInputs &input) {
    require_bounded_rational(input.v); require_bounded_rational(input.z);
    if (fmpq_sgn(input.v.value)==0) throw std::domain_error("stored v must be nonzero");
    Rational z_target("3/4");
    if (!fmpq_equal(input.z.value,z_target.value)) throw std::domain_error("target geometry must remain exact z=3/4");
    for (const auto &a:input.exponents) {
        require_bounded_rational(a);
        if (fmpq_sgn(a.value)<=0) throw std::domain_error("stored exponents must be positive");
    }
}
ComplexBall normalization(const Rational &aq,const Rational &bq,const Rational &prefq,Orbital ell,slong p) {
    precision_check(p);
    if (fmpq_sgn(aq.value)<=0 || fmpq_sgn(bq.value)<=0 ||
        static_cast<int>(ell)<0 || static_cast<int>(ell)>2)
        throw std::domain_error("invalid normalization exponent or orbital");
    auto a=exact(aq,p),b=exact(bq,p),pref=exact(prefq,p),two=integer(2);
    ComplexBall pi,sqrt_two,three_quarters,pa,pb;
    acb_const_pi(pi.value,p); acb_sqrt(sqrt_two.value,two.value,p);
    acb_set_si(three_quarters.value,3); acb_mul_2exp_si(three_quarters.value,three_quarters.value,-2);
    auto xa=div(mul(two,a,p),pi,p),xb=div(mul(two,b,p),pi,p);
    acb_pow(pa.value,xa.value,three_quarters.value,p);
    acb_pow(pb.value,xb.value,three_quarters.value,p);
    auto n=mul(mul(sqrt_two,pref,p),mul(pa,pb,p),p);
    if (ell!=Orbital::S) {
        ComplexBall sqrt_a; acb_sqrt(sqrt_a.value,a.value,p);
        n=mul(n,mul(two,sqrt_a,p),p);
    }
    finite(n); return n;
}
void invalidate(FinalAssembly &out) {
    for (auto &x:out.components_OG) acb_indeterminate(x.value);
    for (auto &x:out.O) acb_indeterminate(x.value);
    for (auto &x:out.O_row) acb_indeterminate(x.value);
    for (auto &x:out.D_col) acb_indeterminate(x.value);
    for (auto &x:out.D_row) acb_indeterminate(x.value);
}
}
std::size_t primitive_index(unsigned active,unsigned field,unsigned orbital,unsigned ia,unsigned ib) {
    if (active>1 || field>2 || orbital>2 || ia>11 || ib>11)
        throw std::out_of_range("canonical primitive index");
    return ((((active*3+field)*3+orbital)*12+ia)*12+ib);
}
Parameters canonical_parameters(const AssemblyInputs &input,unsigned ia,unsigned ib,unsigned active) {
    validate_inputs(input);
    if (ia>11 || ib>11 || active>1) throw std::out_of_range("canonical geometry index");
    Parameters par;
    par.a=input.exponents[ia]; par.b=input.exponents[ib]; par.mu.set("1");
    if (active) {
        par.d1[0].set("-2"); fmpq_neg(par.d1[2].value,input.z.value);
        par.q1=input.v;
    } else {
        par.d2[0].set("-2"); fmpq_neg(par.d2[2].value,input.z.value);
        par.q2=input.v;
    }
    return par;
}
std::vector<Term> stored_donor_terms(const AssemblyInputs &input) {
    std::vector<Term> terms;
    for (unsigned i=0;i<9;++i) for (unsigned j=0;j<9;++j) for (unsigned k=0;k<9;++k) {
        const auto &coefficient=input.donor_C[(i*9+j)*9+k];
        require_bounded_rational(coefficient);
        if (fmpq_sgn(coefficient.value)!=0) {
            Term term; term.i=i; term.j=j; term.k=k; term.coefficient=coefficient;
            terms.push_back(term);
        }
    }
    if (terms.empty() || terms.size()>107) throw std::domain_error("stored donor must have 1..107 nonzero terms");
    return terms;
}
int normalization_factor(acb_t out,const Rational &a,const Rational &b,const Rational &pref,
                         Orbital ell,slong p,std::string &error) noexcept {
    try { auto n=normalization(a,b,pref,ell,p); acb_set(out,n.value); return 0; }
    catch (const std::exception &e) { acb_indeterminate(out); try {error=e.what();} catch (...) {} return 1; }
    catch (...) { acb_indeterminate(out); return 1; }
}
int assemble_real_domain(FinalAssembly &out,const RealDomainPrimitiveIntegrals &raw,
                         const AssemblyInputs &input,slong p,std::string &error) noexcept {
    try {
        precision_check(p); validate_inputs(input);
        for (const auto &x:raw.unnormalized_real_domain_integrals) finite(x);
        std::array<ComplexBall,432> norms;
        for (unsigned ell=0;ell<3;++ell) for (unsigned ia=0;ia<12;++ia) for (unsigned ib=0;ib<12;++ib)
            norms[(ell*12+ia)*12+ib]=normalization(input.exponents[ia],input.exponents[ib],input.pref,static_cast<Orbital>(ell),p);
        const auto v=exact(input.v,p),z=exact(input.z,p),two=integer(2);
        const auto half_v=div(v,two,p),half_z=div(z,two,p),tau=div(z,v,p);
        for (unsigned ch=0;ch<47;++ch) {
            const unsigned active=(ch<24 ? 0 : 1),j=(ch<24 ? ch : ch-23);
            const unsigned ell=j/8,column=j%8;
            const auto &orbital_coefficients=(ell==0 ? input.s_C : input.p_C);
            const auto en=exact(input.phase_E[ch],p);
            for (unsigned cusp=0;cusp<2;++cusp) {
                const unsigned act=active ^ cusp;
                const auto kc=(cusp ? neg(half_v) : half_v),cz=(cusp ? neg(half_z) : half_z);
                const auto ei=exact(input.phase_E[47+cusp],p);
                const auto argument=add(mul(mul(two,kc,p),cz,p),mul(sub(en,ei,p),tau,p),p);
                const auto exponent=times_i(argument);
                ComplexBall phase; acb_exp(phase.value,exponent.value,p);
                for (unsigned field=0;field<3;++field) {
                    auto sum=integer(0);
                    for (unsigned ia=0;ia<12;++ia) for (unsigned ib=0;ib<12;++ib) {
                        // Source coeff=C_neutral[ia,j%8]*C_ground[ib,0].
                        const auto coefficient=mul(exact(orbital_coefficients[ia*12+column],p),exact(input.s_C[ib*12],p),p);
                        const auto &integral=raw.unnormalized_real_domain_integrals[primitive_index(act,field,ell,ia,ib)];
                        const auto term=mul(mul(integral,norms[(ell*12+ia)*12+ib],p),coefficient,p);
                        sum=add(sum,term,p);
                    }
                    const int parity=(cusp && ell ? -1 : 1)*(cusp && field ? -1 : 1);
                    auto result=mul(phase,sum,p);
                    if (parity<0) result=neg(result);
                    finite(result); out.components_OG[(field*47+ch)*2+cusp]=result;
                }
                const auto &O=out.components_OG[ch*2+cusp];
                const auto &G1=out.components_OG[(47+ch)*2+cusp];
                const auto &G2=out.components_OG[(94+ch)*2+cusp];
                const auto ka=(active ? neg(half_v) : half_v),kb=neg(ka);
                const auto omega=sub(mul(kc,sub(sub(mul(two,kc,p),ka,p),kb,p),p),ei,p);
                auto dc=add(mul(kc,add(G1,G2,p),p),mul(times_i(omega),O,p),p);
                auto dr=sub(sub(neg(mul(ka,conjugate_after_integral(G1),p)),
                                mul(kb,conjugate_after_integral(G2),p),p),
                            mul(times_i(en),conjugate_after_integral(O),p),p);
                finite(dc); finite(dr);
                out.O[ch*2+cusp]=O;
                out.O_row[cusp*47+ch]=conjugate_after_integral(O);
                out.D_col[ch*2+cusp]=dc; out.D_row[cusp*47+ch]=dr;
            }
        }
        return 0;
    } catch (const std::exception &e) {
        invalidate(out); try {error=e.what();} catch (...) {} return 1;
    } catch (...) { invalidate(out); return 1; }
}
}
