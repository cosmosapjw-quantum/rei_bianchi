#include <flint/acb.h>
#include <iostream>

#if __FLINT_RELEASE != 30400
#error "Pinned FLINT 3.4.0 required"
#endif

// Pure interval geometry diagnostic. No HH callback and no integral runs.
int main() {
    flint_set_num_threads(1);
    std::cout << "{\"schema\":\"WU088_LOG_IMAGE_GEOMETRY_PROBE_V1\",\"rows\":[";
    bool first=true, all_endpoints=true;
    for (slong prec: {128L,256L}) {
        for (auto bounds: {std::pair<slong,slong>{0,1},{-4,8},{-8,24},{-8,56},{-8,192}}) {
            acb_t a,b,path,l2,mapped,endpoint;
            acb_init(a);acb_init(b);acb_init(path);acb_init(l2);acb_init(mapped);acb_init(endpoint);
            acb_set_si(a,bounds.first);acb_set_si(b,bounds.second);
            acb_union(path,a,b,prec);
            arb_const_log2(acb_realref(l2),prec);
            acb_mul(mapped,path,l2,prec);acb_exp(mapped,mapped,prec);
            acb_one(endpoint);acb_mul_2exp_si(endpoint,endpoint,bounds.first);
            bool lower=acb_contains(mapped,endpoint);
            acb_one(endpoint);acb_mul_2exp_si(endpoint,endpoint,bounds.second);
            bool upper=acb_contains(mapped,endpoint);
            bool positive=arb_is_positive(acb_realref(mapped));
            all_endpoints=all_endpoints&&lower&&upper;
            if(!first)std::cout<<",";first=false;
            std::cout<<"{\"precision_bits\":"<<prec<<",\"lower_log2\":"<<bounds.first
                     <<",\"upper_log2\":"<<bounds.second<<",\"both_exact_endpoints_contained\":"
                     <<(lower&&upper?"true":"false")<<",\"whole_image_proves_positive_real\":"
                     <<(positive?"true":"false")<<"}";
            acb_clear(a);acb_clear(b);acb_clear(path);acb_clear(l2);acb_clear(mapped);acb_clear(endpoint);
        }
    }
    std::cout<<"],\"all_endpoint_enclosures_valid\":"<<(all_endpoints?"true":"false")
             <<",\"hh_callback_calls\":0,\"native_integral_runs\":0,\"production_admission\":false}\n";
    return all_endpoints?0:1;
}
