// Candidate native assembly/export driver. Compile/run acceptance is separate.
#include "assembly.hpp"
#include "frozen107_generated.hpp"
#include "build_identity.hpp"
#include "primitive_rectangles_generated.hpp"
#include <flint/arf.h>
#include <array>
#include <cstdlib>
#include <iostream>
#include <regex>
#include <stdexcept>
#include <string>
#if __FLINT_RELEASE != 30400
#error "Pinned FLINT 3.4.0 required"
#endif
namespace {
struct Int { fmpz_t v; Int(){fmpz_init(v);} ~Int(){fmpz_clear(v);} };
struct Float { arf_t v; Float(){arf_init(v);} ~Float(){arf_clear(v);} };
std::string decimal(const fmpz_t x) {
    char* p=fmpz_get_str(nullptr,10,x); if(!p) throw std::bad_alloc();
    std::string s(p); flint_free(p); return s;
}
std::string interval(const arb_t x) {
    if(!arb_is_finite(x)) throw std::runtime_error("nonfinite final interval");
    Int mid,me,rad,re,lo,hi,exp; Float r;
    arf_get_fmpz_2exp(mid.v,me.v,arb_midref(x));
    arf_set_mag(r.v,arb_radref(x)); arf_get_fmpz_2exp(rad.v,re.v,r.v);
    if(!fmpz_fits_si(me.v)||!fmpz_fits_si(re.v)||
       fmpz_cmp_si(me.v,-4096)<0||fmpz_cmp_si(me.v,4096)>0||
       fmpz_cmp_si(re.v,-4096)<0||fmpz_cmp_si(re.v,4096)>0||
       fmpz_bits(mid.v)>4096||fmpz_bits(rad.v)>4096||
       (!fmpz_is_zero(mid.v)&&!fmpz_is_zero(rad.v)&&std::labs(fmpz_get_si(me.v)-fmpz_get_si(re.v))>4096))
        throw std::runtime_error("final interval serialization work cap");
    arb_get_interval_fmpz_2exp(lo.v,hi.v,exp.v,x);
    if(fmpz_bits(lo.v)>8192||fmpz_bits(hi.v)>8192||!fmpz_fits_si(exp.v)||
       fmpz_cmp_si(exp.v,-4096)<0||fmpz_cmp_si(exp.v,4096)>0)
        throw std::runtime_error("final interval serialization cap");
    return "{\"lower_mantissa\":\""+decimal(lo.v)+"\",\"upper_mantissa\":\""+decimal(hi.v)+
        "\",\"exponent2\":\""+decimal(exp.v)+"\"}";
}
std::string rectangle(const wu088::ComplexBall& x) {
    return "{\"real\":"+interval(acb_realref(x.value))+",\"imag\":"+interval(acb_imagref(x.value))+"}";
}
std::string matrix(const std::array<wu088::ComplexBall,94>& x,unsigned rows,unsigned cols) {
    std::string s="[";
    for(unsigned i=0;i<rows;++i){if(i)s+=",";s+="[";
        for(unsigned j=0;j<cols;++j){if(j)s+=",";s+=rectangle(x[i*cols+j]);}s+="]";}
    return s+"]";
}
}
int main(int argc,char** argv) {
    try {
        if(argc!=2||!std::regex_match(argv[1],std::regex("[1-9][0-9]{1,3}")))
            throw std::invalid_argument("one precision argument required");
        const slong p=std::stol(argv[1]); if(p<32||p>4096)throw std::invalid_argument("precision 32..4096 required");
        if(std::string(flint_version)!="3.4.0")throw std::runtime_error("runtime FLINT mismatch");
        if(std::string(WU088_ARCHIVE_SHA256)!=WU088_PRIMITIVE_ARCHIVE_SHA256 ||
           std::string(WU088_RECORD_SHA256)!=WU088_PRIMITIVE_RECORD_SHA256)
            throw std::runtime_error("assembly input/primitive identity mismatch");
        flint_set_num_threads(1);
        wu088::AssemblyInputs inputs;load_frozen107_rational_record(inputs);
        wu088::RealDomainPrimitiveIntegrals raw;load_real_domain_primitives(raw,p);
        wu088::FinalAssembly out;std::string error;
        if(wu088::assemble_real_domain(out,raw,inputs,p,error))throw std::runtime_error(error);
        // Construct all serialized values before emitting any successful JSON.
        const auto c=matrix(out.D_col,47,2),r=matrix(out.D_row,2,47);
        std::cout<<"{\"schema\":\"WU088_FINAL_D_RECTANGLES_V1\",\"coverage_sha256\":\""
            <<WU088_PRIMITIVE_COVERAGE_SHA256<<"\",\"execution_identity_sha256\":\""<<WU088_PRIMITIVE_EXECUTION_SHA256
            <<"\",\"archive_sha256\":\""<<WU088_PRIMITIVE_ARCHIVE_SHA256
            <<"\",\"input_record_sha256\":\""<<WU088_PRIMITIVE_RECORD_SHA256
            <<"\",\"assembler_source_sha256\":\""<<WU088_ASSEMBLER_SOURCE_SHA256
            <<"\",\"precision_bits\":"<<p<<",\"D_col\":"<<c<<",\"D_row\":"<<r
            <<",\"scientific_admission\":false,\"production_admission\":false}\n";
        return 0;
    } catch(const std::exception& e){std::cerr<<"ASSEMBLY_REJECTED: "<<e.what()<<'\n';return 2;}
}
