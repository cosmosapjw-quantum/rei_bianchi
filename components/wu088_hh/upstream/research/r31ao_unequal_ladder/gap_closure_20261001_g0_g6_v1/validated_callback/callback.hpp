#ifndef WU088_VALIDATED_CALLBACK_HPP
#define WU088_VALIDATED_CALLBACK_HPP
#include <flint/acb.h>
#include <flint/fmpq.h>
#include <array>
#include <cstddef>
#include <string>
#include <vector>

// Source implementation draft. Backend and binary are NOT runtime verified.
namespace wu088 {
constexpr slong MAX_PRECISION_BITS=4096;
constexpr ulong MAX_RATIONAL_BITS=16384;
constexpr std::size_t MAX_RATIONAL_TEXT=8192;
struct Rational {
    fmpq_t value;
    Rational();
    explicit Rational(const char *value);
    Rational(const Rational &other);
    Rational &operator=(const Rational &other);
    ~Rational();
    void set(const char *value); // fmpq decimal INTEGER or INTEGER/INTEGER; no float.
};
void require_bounded_rational(const Rational &);
struct Parameters {
    Rational a,b,q1,q2,mu;
    std::array<Rational,3> d1,d2;
};
struct Contract {
    slong precision=128;
    slong max_precision=512;
    Rational margin{"1/1048576"};
    unsigned long calls=0, failures=0;
    unsigned long max_calls=10000;
    std::string last_error;
};
struct Term {
    unsigned i=0,j=0,k=0;
    Rational coefficient;
};
enum class Field { O=0, G1=1, G2=2 };
enum class Orbital { S=0, PX=1, PZ=2 };
// Nonzero return => out is indeterminate. Inputs/outputs must not alias.
int radial(acb_t out,unsigned k,unsigned derivative,const acb_t sigma,
           const acb_t s,Contract &contract) noexcept;
// Returns the unnormalized spatial primitive I or negative center derivative.
int primitive(acb_t out,unsigned k,Orbital ell,Field field,const acb_t t,
              const acb_t u,const Parameters &,Contract &) noexcept;
// Sum coefficient * U_i(t) U_j(u) * spatial primitive, using signed coefficients.
// No quadrature weights, Jacobians, Gaussian normalization or phase are included.
int polynomial_field(acb_t out,const std::vector<Term> &,Orbital ell,Field field,
                     const acb_t t,const acb_t u,const Parameters &,Contract &) noexcept;
struct Slice {
    const Parameters *parameters=nullptr;
    const std::vector<Term> *terms=nullptr;
    Contract *contract=nullptr;
    acb_srcptr outer_box=nullptr; // whole outer complex box, never its midpoint
    Orbital orbital=Orbital::S;
    Field field=Field::O;
};
// acb_calc_func_t-compatible value callback; order 1 requests holomorphy.
// This is only the inner integrand, NOT a uniform nested-integral implementation.
int slice_callback(acb_ptr out,const acb_t inner,void *param,slong order,slong prec);
}
#endif
