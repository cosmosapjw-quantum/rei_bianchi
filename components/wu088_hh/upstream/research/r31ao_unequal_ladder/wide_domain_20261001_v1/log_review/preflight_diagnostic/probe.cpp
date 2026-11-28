#include "../../log_native_driver/log_map.hpp"
#include "../../../ncp64_acceleration_20261001_v1/native_cache/cached_callback.hpp"
#include "frozen107_generated.hpp"
#include <iostream>
#include <stdexcept>

namespace {
int bridge(acb_ptr out,const acb_t inner,const acb_t outer,void *opaque,slong order,slong prec) {
    auto slice=*static_cast<wu088::CachedSlice *>(opaque);
    slice.source.outer_box=outer;
    return wu088::cached_slice_callback(out,inner,&slice,order,prec);
}
std::string quote(const std::string &s) {
    std::string out="\"";
    for(char c:s) {
        if(c=='\\'||c=='\"')out+='\\';
        if(c=='\n')out+="\\n";else out+=c;
    }
    return out+'\"';
}
}
int main() {
    try {
        flint_set_num_threads(1);
        wu088::AssemblyInputs inputs;load_frozen107_rational_record(inputs);
        auto parameters=wu088::canonical_parameters(inputs,0,0,0);
        auto terms=wu088::stored_donor_terms(inputs);
        if(terms.size()!=107)throw std::runtime_error("expected all107 signed terms");
        wu088::Contract contract;contract.precision=contract.max_precision=128;contract.max_calls=16;
        // Exact physical W1 margin, identical formula to the frozen worker.
        wu088::Rational lower("1/16"),upper("256"),da,db,ia,ib,sigma_min,margin("1/16");
        fmpq_add(da.value,parameters.a.value,upper.value);fmpq_add(db.value,parameters.b.value,upper.value);
        fmpq_inv(ia.value,da.value);fmpq_inv(ib.value,db.value);
        fmpq_add(sigma_min.value,ia.value,ib.value);fmpq_div_2exp(sigma_min.value,sigma_min.value,1);
        if(fmpq_cmp(sigma_min.value,margin.value)<0)margin=sigma_min;
        fmpq_div_2exp(margin.value,margin.value,20);
        if(fmpq_cmp(margin.value,contract.margin.value)<0)contract.margin=margin;
        wu088::Slice slice;slice.parameters=&parameters;slice.terms=&terms;slice.contract=&contract;
        slice.orbital=wu088::Orbital::S;slice.field=wu088::Field::O;
        wu088::CacheStats stats;wu088::CachedSlice cached{slice,&stats};
        wu088::petras::Bivariate physical{bridge,&cached,true,true,"same fixed physical whole-box callback"};
        wu088::log2map::Context context(physical,128);
        char *margin_text=fmpq_get_str(nullptr,10,contract.margin.value);
        std::cout<<"{\"schema\":\"WU088_ACTUAL_CALLBACK_PREFLIGHT_DIAGNOSTIC_V1\",\"primitive_index\":0,\"precision_bits\":128,\"physical_global_window\":\"[1/16,256]^2\",\"margin\":"<<quote(margin_text)<<",\"rows\":[";
        flint_free(margin_text);bool first=true;unsigned count=0;
        for(slong hi:{8L,-1L,-3L})for(slong outer:{-4L,0L,8L}) {
            wu088::petras::Ball lo,upper_log,inner,y,result;
            acb_set_si(lo.value,-4);acb_set_si(upper_log.value,hi);
            acb_union(inner.value,lo.value,upper_log.value,128);acb_set_si(y.value,outer);
            const auto before=contract.calls,fail_before=contract.failures;
            contract.last_error.clear();
            wu088::log2map::callback(result.value,inner.value,y.value,&context,1,128);++count;
            if(contract.calls!=before+1)throw std::runtime_error("unexpected physical callback count");
            if(!first)std::cout<<",";first=false;
            std::cout<<"{\"inner_log_lower\":-4,\"inner_log_upper\":"<<hi<<",\"outer_log_point\":"<<outer
                     <<",\"order\":1,\"finite\":"<<(acb_is_finite(result.value)?"true":"false")
                     <<",\"contract_last_error\":"<<quote(contract.last_error)
                     <<",\"contract_call_delta\":"<<contract.calls-before<<",\"contract_failure_delta\":"<<contract.failures-fail_before
                     <<",\"terms_completed\":"<<stats.terms_completed<<"}";
        }
        std::cout<<"],\"actual_hh_callback_evaluations\":"<<count<<",\"actual_hh_integrals\":0,\"contract_calls\":"<<contract.calls
                 <<",\"contract_failures\":"<<contract.failures<<",\"max_contract_calls\":16,\"scientific_admission\":false,\"production_admission\":false}\n";
        return count==9?0:2;
    } catch(const std::exception &e){std::cerr<<e.what()<<'\n';return 2;}
}
