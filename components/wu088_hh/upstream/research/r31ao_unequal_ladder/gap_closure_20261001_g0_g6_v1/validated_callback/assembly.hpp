#ifndef WU088_POST_INTEGRAL_ASSEMBLY_HPP
#define WU088_POST_INTEGRAL_ASSEMBLY_HPP
#include "callback.hpp"
#include <cstddef>

namespace wu088 {
struct ComplexBall {
    acb_t value;
    ComplexBall();
    ComplexBall(const ComplexBall &);
    ComplexBall(ComplexBall &&) noexcept;
    ComplexBall &operator=(const ComplexBall &);
    ~ComplexBall();
};
// Decoder must supply exact represented values in semantic index order.
// This object alone does not prove FROZEN_INPUTS.npz byte identity.
struct AssemblyInputs {
    std::array<Rational,12> exponents;
    std::array<Rational,144> s_C,p_C; // primitive * 12 + orbital column
    std::array<Rational,729> donor_C; // (i*9+j)*9+k; direct stored dyadics
    std::array<Rational,49> phase_E;
    Rational pref,v,z;
};
struct RealDomainPrimitiveIntegrals {
    // Each is integral over ALL real-positive t,u of polynomial_field.
    // Interior and endpoint contributions must already be combined exactly once.
    // No orbital normalization, phase, parity or contraction has been applied.
    std::array<ComplexBall,2592> unnormalized_real_domain_integrals;
};
struct FinalAssembly {
    std::array<ComplexBall,282> components_OG; // (field*47+ch)*2+cusp
    std::array<ComplexBall,94> O,D_col;       // ch*2+cusp
    std::array<ComplexBall,94> O_row,D_row;   // cusp*47+ch
};
std::size_t primitive_index(unsigned active,unsigned field,unsigned orbital,unsigned ia,unsigned ib);
Parameters canonical_parameters(const AssemblyInputs &,unsigned ia,unsigned ib,unsigned active);
std::vector<Term> stored_donor_terms(const AssemblyInputs &);
int normalization_factor(acb_t out,const Rational &a,const Rational &b,const Rational &pref,
                         Orbital orbital,slong precision,std::string &error) noexcept;
// Assembly only: never calls an integrand, quadrature, special-function moment or source producer.
// On any failure, every output is indeterminate. This is not a certificate-admission function.
int assemble_real_domain(FinalAssembly &,const RealDomainPrimitiveIntegrals &,
                         const AssemblyInputs &,slong precision,std::string &error) noexcept;
}
#endif
