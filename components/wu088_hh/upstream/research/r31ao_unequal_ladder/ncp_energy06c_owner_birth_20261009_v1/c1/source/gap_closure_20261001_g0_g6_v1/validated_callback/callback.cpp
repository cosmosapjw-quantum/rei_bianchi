#include "callback.hpp"
#include "finite_m.hpp"
#include <flint/acb_hypgeom.h>
#include <stdexcept>
#include <utility>

#if __FLINT_VERSION != 3 || __FLINT_VERSION_MINOR != 4 || __FLINT_VERSION_PATCHLEVEL != 0
#error "This draft requires the pinned FLINT 3.4.0 headers"
#endif

namespace wu088 {
Rational::Rational() { fmpq_init(value); }
Rational::Rational(const char *v):Rational() { set(v); }
Rational::Rational(const Rational &v):Rational() { fmpq_set(value,v.value); }
Rational &Rational::operator=(const Rational &v) { fmpq_set(value,v.value); return *this; }
Rational::~Rational() { fmpq_clear(value); }
void Rational::set(const char *v) {
    if (!v) throw std::invalid_argument("null rational text");
    std::size_t size=0;
    while (size<=MAX_RATIONAL_TEXT && v[size]) ++size;
    if (size>MAX_RATIONAL_TEXT) throw std::invalid_argument("rational text exceeds bounded input size");
    Rational candidate;
    if (fmpq_set_str(candidate.value,v,10)!=0 || fmpz_is_zero(fmpq_denref(candidate.value)))
        throw std::invalid_argument("invalid exact rational");
    fmpq_canonicalise(candidate.value);
    require_bounded_rational(candidate);
    fmpq_swap(value,candidate.value); // invalid input preserves the previous object
}
void require_bounded_rational(const Rational &q) {
    if (fmpz_sgn(fmpq_denref(q.value))<=0 ||
        fmpz_bits(fmpq_numref(q.value))>MAX_RATIONAL_BITS ||
        fmpz_bits(fmpq_denref(q.value))>MAX_RATIONAL_BITS || !fmpq_is_canonical(q.value))
        throw std::domain_error("rational numerator/denominator exceeds bounded input contract");
}
namespace {
struct Ball {
    acb_t v;
    slong p;
    explicit Ball(slong precision):p(precision) { acb_init(v); }
    Ball(slong precision,slong n):Ball(precision) { acb_set_si(v,n); }
    Ball(slong precision,const Rational &q):Ball(precision) { require_bounded_rational(q); acb_set_fmpq(v,q.value,p); }
    Ball(slong precision,acb_srcptr x,bool):Ball(precision) { acb_set(v,x); }
    Ball(const Ball &x):Ball(x.p) { acb_set(v,x.v); }
    Ball(Ball &&x) noexcept:Ball(x.p) { acb_swap(v,x.v); }
    Ball &operator=(const Ball &x) { p=x.p; acb_set(v,x.v); return *this; }
    ~Ball() { acb_clear(v); }
};
Ball operator+(const Ball &a,const Ball &b) { Ball c(a.p); acb_add(c.v,a.v,b.v,a.p); return c; }
Ball operator-(const Ball &a,const Ball &b) { Ball c(a.p); acb_sub(c.v,a.v,b.v,a.p); return c; }
Ball operator-(const Ball &a) { Ball c(a.p); acb_neg(c.v,a.v); return c; }
Ball operator*(const Ball &a,const Ball &b) { Ball c(a.p); acb_mul(c.v,a.v,b.v,a.p); return c; }
Ball operator/(const Ball &a,const Ball &b) { Ball c(a.p); acb_div(c.v,a.v,b.v,a.p); return c; }
Ball half(slong p,slong numerator) { Ball c(p,numerator); acb_mul_2exp_si(c.v,c.v,-1); return c; }
Ball power(const Ball &x,const Ball &n) { Ball c(x.p); acb_pow(c.v,x.v,n.v,x.p); return c; }
Ball pow_ui(const Ball &x,unsigned n) { Ball c(x.p); acb_pow_ui(c.v,x.v,n,x.p); return c; }
Ball exponential(const Ball &x) { Ball c(x.p); acb_exp(c.v,x.v,x.p); return c; }
Ball gamma(const Ball &x) { Ball c(x.p); acb_hypgeom_gamma(c.v,x.v,x.p); return c; }
Ball imaginary(const Ball &x) { Ball c(x.p); acb_mul_onei(c.v,x.v); return c; }
void positive(const Ball &x,const Rational &margin) {
    require_bounded_rational(margin);
    arb_t delta,m;
    arb_init(delta); arb_init(m);
    arb_set_fmpq(m,margin.value,x.p);
    arb_sub(delta,acb_realref(x.v),m,x.p);
    bool valid=acb_is_finite(x.v) && arb_is_positive(delta);
    arb_clear(delta); arb_clear(m);
    if (!valid) throw std::domain_error("whole-box positive real margin not proved");
}
void check(Contract &c) {
    if (c.precision<32 || c.max_precision<32 || c.precision>c.max_precision || c.max_precision>MAX_PRECISION_BITS)
        throw std::domain_error("precision outside declared cap");
    if (fmpq_sgn(c.margin.value)<=0)
        throw std::domain_error("positive exact domain margin required");
    require_bounded_rational(c.margin);
    if (c.calls>=c.max_calls) throw std::runtime_error("callback budget exhausted");
    ++c.calls;
}
void finite(const Ball &v) {
    if (!acb_is_finite(v.v)) throw std::runtime_error("backend returned nonfinite enclosure");
}
Ball moment(unsigned k,unsigned r,const Ball &sigma,const Ball &s,const Rational &margin) {
    if (k>8 || r>2) throw std::domain_error("radial degree or derivative outside contract");
    positive(sigma,margin); finite(s);
    slong p=sigma.p;
    if ((k%2)==0 && r>k/2) return Ball(p,0);
    Ball two_sigma=Ball(p,2)*sigma;
    Ball a=half(p,-static_cast<slong>(k)+2*static_cast<slong>(r));
    Ball b=half(p,3+2*static_cast<slong>(r));
    Ball z=-s/two_sigma, out(p), factor(p,1);
    // Exact half-integer parameters; deliberately unregularized 1F1.
    wu088_fd2::family_m(out.v, k, r, z.v, p);
    for (unsigned j=0;j<r;++j)
        factor=factor*half(p,-static_cast<slong>(k)+2*static_cast<slong>(j))
            /half(p,3+2*static_cast<slong>(j))*(-Ball(p,1)/two_sigma);
    Ball pref=power(two_sigma,half(p,static_cast<slong>(k)))
        *gamma(half(p,static_cast<slong>(k)+3))/gamma(half(p,3));
    out=out*pref*factor; finite(out); return out;
}
struct Geometry {
    Ball A,base;
    std::array<Ball,3> m,n;
    explicit Geometry(slong p):A(p),base(p),m{Ball(p),Ball(p),Ball(p)},n{Ball(p),Ball(p),Ball(p)} {}
};
Geometry geometry(const Rational &aq,const Ball &t,const std::array<Rational,3> &dq,
                  const Rational &qq,const Rational &margin) {
    slong p=t.p;
    Ball a(p,aq),q(p,qq),one(p,1),pi(p),d2(p,0);
    if (fmpq_sgn(aq.value)<=0) throw std::domain_error("a,b must be positive exact rationals");
    acb_const_pi(pi.v,p);
    Geometry g(p); g.A=a+t; positive(t,margin); positive(g.A,margin);
    for (unsigned j=0;j<3;++j) {
        Ball d(p,dq[j]); d2=d2+d*d;
        g.m[j]=a*d/g.A;
        if (j==2) g.m[j]=g.m[j]+imaginary(q/(Ball(p,2)*g.A));
        g.n[j]=g.m[j]-d;
    }
    Ball exponent=-a*t*d2/g.A-q*q/(Ball(p,4)*g.A)
        +imaginary(q*a*Ball(p,dq[2])/g.A);
    // pi/A remains in the right half-plane because Re(A)>0.
    g.base=power(pi/g.A,half(p,3))*exponential(exponent);
    finite(g.base); return g;
}
Ball spatial(unsigned k,Orbital ell,Field field,const Ball &t,const Ball &u,
             const Parameters &par,const Rational &margin) {
    if (static_cast<int>(ell)<0 || static_cast<int>(ell)>2 ||
        static_cast<int>(field)<0 || static_cast<int>(field)>2)
        throw std::domain_error("unsupported field or orbital");
    slong p=t.p;
    Geometry g1=geometry(par.a,t,par.d1,par.q1,margin);
    Geometry g2=geometry(par.b,u,par.d2,par.q2,margin);
    Ball one(p,1),two(p,2),a(p,par.a),b(p,par.b);
    Ball sigma=half(p,1)*(one/g1.A+one/g2.A),s(p,0);
    std::array<Ball,3> delta{g1.m[0]-g2.m[0],g1.m[1]-g2.m[1],g1.m[2]-g2.m[2]};
    for (unsigned j=0;j<3;++j) s=s+delta[j]*delta[j]; // bilinear square
    Ball M=moment(k,0,sigma,s,margin),F=moment(k,1,sigma,s,margin),F2=moment(k,2,sigma,s,margin);
    unsigned axis=(ell==Orbital::PX ? 0 : 2);
    Ball E=M;
    if (ell!=Orbital::S) E=g1.n[axis]*M+delta[axis]/g1.A*F;
    Ball value=g1.base*g2.base*E;
    if (field!=Field::O) {
        bool first=field==Field::G1;
        Ball h=first ? a/g1.A : b/g2.A;
        Ball sp=(first ? two*h*delta[2] : -two*h*delta[2]);
        Ball logp=first ? two*a*g1.n[2] : two*b*g2.n[2];
        Ball derivative=sp*F;
        if (ell!=Orbital::S) {
            derivative=g1.n[axis]*sp*F+delta[axis]/g1.A*sp*F2;
            if (axis==2) {
                if (first) derivative=derivative+(h-one)*M+h/g1.A*F;
                else derivative=derivative-h/g1.A*F;
            }
        }
        value=-g1.base*g2.base*(logp*E+derivative);
    }
    finite(value); return value;
}
unsigned long factorial(unsigned n) {
    unsigned long value=1;
    for (unsigned j=2;j<=n;++j) value*=j;
    return value;
}
Ball density(unsigned i,const Ball &t,const Rational &muq,const Rational &margin) {
    if (i>8 || fmpq_sgn(muq.value)<=0)
        throw std::domain_error("density requires i<=8, exact mu>0");
    positive(t,margin);
    slong p=t.p;
    Ball mu(p,muq),pi(p),sum(p,0);
    acb_const_pi(pi.v,p);
    unsigned n=i+1;
    for (unsigned r=0;r<=n/2;++r) {
        // n<=9: all integer products below are below 2^31.
        Rational coef;
        fmpq_set_si(coef.value,static_cast<slong>(factorial(n)),
                    (1UL<<n)*factorial(r)*factorial(n-2*r));
        if (r%2) fmpq_neg(coef.value,coef.value);
        sum=sum+Ball(p,coef)*pow_ui(mu,n-2*r)
            *power(t,half(p,-static_cast<slong>(2*i+3-2*r)));
    }
    Ball value=exponential(-mu*mu/(Ball(p,4)*t))*sum/power(pi,half(p,1));
    finite(value); return value;
}
int fail(acb_t out,Contract &c,const char *message) noexcept {
    acb_indeterminate(out); ++c.failures;
    try { c.last_error=message; } catch (...) {}
    return 1;
}
void invalidate_requested_coefficients(acb_ptr out,slong order) {
    // acb_calc requires the caller to allocate max(order,1) valid output slots.
    const slong slots=(order>0 ? order : 1);
    for (slong j=0;j<slots;++j) acb_indeterminate(out+j);
}
}
int radial(acb_t out,unsigned k,unsigned r,const acb_t sigma,const acb_t s,Contract &c) noexcept {
    try { check(c); Ball v=moment(k,r,Ball(c.precision,sigma,true),Ball(c.precision,s,true),c.margin); acb_set(out,v.v); return 0; }
    catch (const std::exception &e) { return fail(out,c,e.what()); }
    catch (...) { return fail(out,c,"unknown callback exception"); }
}
int primitive(acb_t out,unsigned k,Orbital ell,Field field,const acb_t t,const acb_t u,
              const Parameters &par,Contract &c) noexcept {
    try { check(c); Ball v=spatial(k,ell,field,Ball(c.precision,t,true),Ball(c.precision,u,true),par,c.margin); acb_set(out,v.v); return 0; }
    catch (const std::exception &e) { return fail(out,c,e.what()); }
    catch (...) { return fail(out,c,"unknown callback exception"); }
}
int polynomial_field(acb_t out,const std::vector<Term> &terms,Orbital ell,Field field,
                     const acb_t t,const acb_t u,const Parameters &par,Contract &c) noexcept {
    try {
        check(c);
        if (terms.empty() || terms.size()>107) throw std::domain_error("nonempty finite polynomial <=107 terms required");
        Ball bt(c.precision,t,true),bu(c.precision,u,true),sum(c.precision,0);
        for (const auto &term:terms) {
            Ball value=Ball(c.precision,term.coefficient)
                *density(term.i,bt,par.mu,c.margin)*density(term.j,bu,par.mu,c.margin)
                *spatial(term.k,ell,field,bt,bu,par,c.margin);
            sum=sum+value;
        }
        finite(sum); acb_set(out,sum.v); return 0;
    } catch (const std::exception &e) { return fail(out,c,e.what()); }
    catch (...) { return fail(out,c,"unknown callback exception"); }
}
int slice_callback(acb_ptr out,const acb_t inner,void *param,slong order,slong prec) {
    Slice *slice=static_cast<Slice *>(param);
    if (!slice || !slice->parameters || !slice->terms || !slice->contract || !slice->outer_box) {
        invalidate_requested_coefficients(out,order); return 0;
    }
    Contract &c=*slice->contract;
    if (order != 0 && order != 1) {
        fail(out,c,"unsupported acb_calc order; order is not a radial derivative");
        invalidate_requested_coefficients(out,order); return 0;
    }
    if (prec!=c.precision) {
        fail(out,c,"integration precision must equal declared callback precision"); return 0;
    }
    polynomial_field(out,*slice->terms,slice->orbital,slice->field,
                     inner,slice->outer_box,*slice->parameters,c);
    return 0; // acb_calc reserves return code; nonfinite output carries failure.
}
}
