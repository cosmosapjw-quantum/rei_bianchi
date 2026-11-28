#pragma once
// Candidate scalar representation only. Original source and accepted results remain unchanged.
#include <flint/acb.h>
#include <flint/acb_hypgeom.h>
#if __FLINT_RELEASE != 30400
#error "FD2 candidate is pinned to FLINT 3.4.0"
#endif
namespace wu088_fd2 {
inline constexpr unsigned terms=256;
inline constexpr ulong tail_numerator=26471,tail_denominator=19815;
struct Temp {acb_t x;Temp(){acb_init(x);}~Temp(){acb_clear(x);}Temp(const Temp&)=delete;Temp&operator=(const Temp&)=delete;};
struct Mag {mag_t x;Mag(){mag_init(x);}~Mag(){mag_clear(x);}Mag(const Mag&)=delete;Mag&operator=(const Mag&)=delete;};
inline bool parameters_valid(unsigned k,unsigned r,slong p){return k<=8&&r<=2&&p>=32&&p<=4096;}
inline bool bounded_box(const acb_t z){
    if(!acb_is_finite(z))return false;
    arf_t re,im,upper;arf_init(re);arf_init(im);arf_init(upper);
    arb_get_abs_ubound_arf(re,acb_realref(z),128);
    arb_get_abs_ubound_arf(im,acb_imagref(z),128);
    arf_add(upper,re,im,128,ARF_RND_CEIL);
    const bool ok=arf_cmp_2exp_si(upper,6)<=0; // L1 upper bound implies |z|<=64.
    arf_clear(re);arf_clear(im);arf_clear(upper);return ok;
}
// Uniform absolutely convergent series for a=r-k/2,b=r+3/2, k<=8,r<=2.
// Sum n=0..255 and add |T_256|/(1-q), q=6656/26471 <1.
// Each operation uses the supplied precision; all rounding is outward by Acb/Mag.
inline bool bounded_series(acb_t out,unsigned k,unsigned r,const acb_t z,slong p){
    if(!parameters_valid(k,r,p)||!bounded_box(z)){acb_indeterminate(out);return false;}
    Temp term,sum;acb_one(term.x);acb_zero(sum.x);
    for(unsigned n=0;n<terms;++n){
        acb_add(sum.x,sum.x,term.x,p);
        acb_mul(term.x,term.x,z,p);
        const slong numerator=2*static_cast<slong>(n)+2*static_cast<slong>(r)-static_cast<slong>(k);
        const ulong denominator=(2*static_cast<ulong>(n)+3+2*r)*(static_cast<ulong>(n)+1);
        acb_mul_si(term.x,term.x,numerator,p);
        acb_div_ui(term.x,term.x,denominator,p);
        if(acb_is_zero(term.x)){acb_set(out,sum.x);return true;}
    }
    Mag error;acb_get_mag(error.x,term.x);
    mag_mul_ui(error.x,error.x,tail_numerator);
    mag_div_ui(error.x,error.x,tail_denominator);
    arb_add_error_mag(acb_realref(sum.x),error.x);
    arb_add_error_mag(acb_imagref(sum.x),error.x);
    acb_set(out,sum.x);
    return acb_is_finite(out)!=0;
}
inline bool selected(unsigned k,unsigned r,const acb_t z,slong p){
    return parameters_valid(k,r,p)&&(k%2==1)&&acb_contains_zero(z)&&bounded_box(z);
}
inline void family_m(acb_t out,unsigned k,unsigned r,const acb_t z,slong p){
    if(!parameters_valid(k,r,p)){acb_indeterminate(out);return;}
    if(selected(k,r,z,p)){(void)bounded_series(out,k,r,z,p);return;}
    // Untargeted inputs use the unchanged, pinned original automatic evaluator.
    Temp a,b;
    acb_set_si(a.x,2*static_cast<slong>(r)-static_cast<slong>(k));acb_mul_2exp_si(a.x,a.x,-1);
    acb_set_si(b.x,3+2*static_cast<slong>(r));acb_mul_2exp_si(b.x,b.x,-1);
    acb_hypgeom_m(out,a.x,b.x,z,0,p);
}
}
