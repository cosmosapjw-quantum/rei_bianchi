// FD1 sidecar only. Numerical callback TUs and original worker are unchanged.
#include "cached_callback.hpp"
#include "assembly.hpp"
#include "frozen107_generated.hpp"
#include "build_identity.hpp"
#include "log_map.hpp"
#include "queries_generated.hpp"
#include "diagnostic_identity.hpp"
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <functional>
#if __FLINT_RELEASE != 30400
#error "Pinned FLINT 3.4.0 required"
#endif
using wu088::petras::Ball;
static std::string text(const std::string &s) {
 if(s.size()>8192)throw std::runtime_error("bounded diagnostic string exceeded");
 std::ostringstream out;out<<'"';
 for(unsigned char ch:s){if(ch=='"'||ch=='\\')out<<'\\'<<ch;else if(ch<32){const char*hex="0123456789abcdef";out<<"\\u00"<<hex[ch>>4]<<hex[ch&15];}else out<<ch;}
 out<<'"';return out.str();
}
static std::string dump(const arb_t x){char*p=arb_dump_str(x);if(!p)throw std::bad_alloc();std::string s(p);flint_free(p);return text(s);}
static std::string ball(const acb_t x){return "{\"real\":"+dump(acb_realref(x))+",\"imag\":"+dump(acb_imagref(x))+"}";}
static std::string rational(const wu088::Rational &x){char*p=fmpq_get_str(nullptr,10,x.value);if(!p)throw std::bad_alloc();std::string s(p);flint_free(p);return text(s);}
static std::string stats(const wu088::CacheStats&s){std::ostringstream o;o<<"{";
#define FD1_STAT(name) o<<"\""#name"\":"<<s.name
 FD1_STAT(terms_started);o<<",";FD1_STAT(terms_completed);o<<",";FD1_STAT(left_requests);o<<",";FD1_STAT(right_requests);o<<",";FD1_STAT(spatial_requests);o<<",";FD1_STAT(left_evaluations);o<<",";FD1_STAT(right_evaluations);o<<",";FD1_STAT(spatial_evaluations);o<<",";FD1_STAT(left_hits);o<<",";FD1_STAT(right_hits);o<<",";FD1_STAT(spatial_hits);o<<"}";
#undef FD1_STAT
 return o.str();}
struct Recorder {
 wu088::Contract& contract;wu088::CacheStats& cache;bool used=false;
 Recorder(wu088::Contract& c, wu088::CacheStats& s): contract(c), cache(s) {}
 unsigned long before_calls=0,before_failures=0;std::string before_error,after_error,output;unsigned long after_calls=0,after_failures=0;wu088::CacheStats before_cache{},after_cache{};int returncode=-1;bool finite=false;
 int invoke(acb_ptr out,const std::function<int()>&fn){
  if(used)throw std::runtime_error("duplicate diagnostic callback refused");
  if(contract.calls||contract.failures||!contract.last_error.empty()||stats(cache)!=stats(wu088::CacheStats{}))throw std::runtime_error("stale Contract.last_error/counters/CacheStats refused");
  before_calls=contract.calls;before_failures=contract.failures;before_error=contract.last_error;before_cache=cache;used=true;
  returncode=fn();after_calls=contract.calls;after_failures=contract.failures;after_error=contract.last_error;after_cache=cache;finite=acb_is_finite(out);output=ball(out);
  if(after_calls<before_calls||after_failures<before_failures||(!after_error.empty()&&after_failures==before_failures))throw std::runtime_error("stale or uncharged last_error refused");
  return returncode;
 }
 std::string json()const{std::ostringstream o;o<<"{\"before\":{\"calls\":"<<before_calls<<",\"failures\":"<<before_failures<<",\"last_error\":"<<text(before_error)<<",\"cache\":"<<stats(before_cache)<<"},\"after\":{\"calls\":"<<after_calls<<",\"failures\":"<<after_failures<<",\"last_error\":"<<text(after_error)<<",\"cache\":"<<stats(after_cache)<<"},\"fresh_failure\":"<<(after_failures>before_failures?"true":"false")<<",\"physical_callback_return\":"<<returncode<<",\"physical_output_finite\":"<<(finite?"true":"false")<<",\"physical_output_dump\":"<<output<<",\"callback_invocations\":"<<(used?1:0)<<"}";return o.str();}
};
static void first_box(acb_t wide,const acb_t a,const acb_t b){
 // Exact constructor from pinned FLINT3.4.0 quad_simple, with no f/integral.
 Ball mid,delta;mag_t tmpm;mag_init(tmpm);
 acb_sub(delta.value,b,a,128);acb_mul_2exp_si(delta.value,delta.value,-1);
 acb_add(mid.value,a,b,128);acb_mul_2exp_si(mid.value,mid.value,-1);
 acb_set(wide,mid.value);
 arb_get_mag(tmpm,acb_realref(delta.value));arb_add_error_mag(acb_realref(wide),tmpm);
 arb_get_mag(tmpm,acb_imagref(delta.value));arb_add_error_mag(acb_imagref(wide),tmpm);mag_clear(tmpm);
}
static const QuerySpec& query(const std::string&id){for(const auto&q:QUERY_SPECS)if(id==q.id)return q;throw std::invalid_argument("outside fixed diagnostic query");}
struct Capture {std::string t,u;unsigned calls=0;};
static int capture_geometry(acb_ptr out,const acb_t t,const acb_t u,void*ptr,slong order,slong prec){
 if(order!=0||prec!=128)throw std::invalid_argument("fixed order0/128 required");
 auto&c=*static_cast<Capture*>(ptr);if(c.calls++)throw std::runtime_error("duplicate geometry capture");c.t=ball(t);c.u=ball(u);acb_zero(out);return 0;
}
struct Physical {wu088::Slice slice;wu088::CacheStats*cache;Recorder*recorder;bool cached;Capture capture;};
static int recorded_physical(acb_ptr out,const acb_t t,const acb_t u,void*ptr,slong order,slong prec){
 if(order!=0||prec!=128)throw std::invalid_argument("fixed order0/128 required");
 auto&s=*static_cast<Physical*>(ptr);s.capture.t=ball(t);s.capture.u=ball(u);++s.capture.calls;
 // The original worker's adapter copies Slice and preserves the whole box.
 auto slice=s.slice;slice.outer_box=u;
 return s.recorder->invoke(out,[&](){if(s.cached){wu088::CachedSlice cached{slice,s.cache};return wu088::cached_slice_callback(out,t,&cached,order,prec);}return wu088::slice_callback(out,t,&slice,order,prec);});
}
static int synthetic(const std::string&mode){
 // No frozen inputs, Parameters or field callbacks are loaded on this path.
 wu088::Contract c;wu088::CacheStats cache;Recorder record{c,cache};Ball out;unsigned calls=0;
 if(mode=="stale")c.last_error="STALE_SYNTHETIC_ERROR";
 auto fn=[&](){++calls;++c.calls;if(mode=="failure"){++c.failures;c.last_error="FRESH_SYNTHETIC_REFUSAL";cache.terms_started=1;acb_indeterminate(out.value);return 0;}if(mode=="uncharged"){c.last_error="UNCHARGED_SYNTHETIC_ERROR";acb_one(out.value);return 0;}acb_one(out.value);return 0;};
 if(mode!="finite"&&mode!="failure"&&mode!="stale"&&mode!="duplicate"&&mode!="uncharged")throw std::invalid_argument("unknown synthetic fixture");
 record.invoke(out.value,fn);if(mode=="duplicate")record.invoke(out.value,fn);
 std::cout<<"{\"schema\":\"WU088_FD1_SYNTHETIC_RECORDER_V1\",\"mode\":"<<text(mode)<<",\"synthetic_callback_calls\":"<<calls<<",\"HH_evaluations\":0,\"integrations\":0,\"record\":"<<record.json()<<"}\n";return 0;
}
static int execute_query(const std::string&id,bool hh,const std::string&mode){
 const auto&q=query(id);if(mode!="cached"&&mode!="reference")throw std::invalid_argument("outside cached/reference implementations");
 wu088::AssemblyInputs inputs;load_frozen107_rational_record(inputs);
 auto parameters=wu088::canonical_parameters(inputs,0,0,0);auto terms=wu088::stored_donor_terms(inputs);
 if(terms.size()!=107)throw std::runtime_error("signed ordered107 term count changed");
 wu088::Contract contract;contract.precision=128;contract.max_precision=128;contract.max_calls=200000;
 Ball lt,Tt,lu,Tu,inner,outer,out;
 auto l_t=wu088::log2map::exact_log_endpoint(q.endpoints[0],lt.value),T_t=wu088::log2map::exact_log_endpoint(q.endpoints[1],Tt.value);
 auto l_u=wu088::log2map::exact_log_endpoint(q.endpoints[2],lu.value),T_u=wu088::log2map::exact_log_endpoint(q.endpoints[3],Tu.value);
#include "original_margin.inc"
 first_box(inner.value,lt.value,Tt.value);
 if(arb_load_str(acb_realref(outer.value),"-f -1 30000001 -1d")||arb_load_str(acb_imagref(outer.value),"0 0 0 0"))throw std::runtime_error("exact outer dump parsing failed");
 wu088::CacheStats cache;Recorder recorder{contract,cache};wu088::Slice slice;slice.parameters=&parameters;slice.terms=&terms;slice.contract=&contract;slice.orbital=wu088::Orbital::S;slice.field=wu088::Field::O;
 Physical physical{slice,&cache,&recorder,mode=="cached",{}};Capture geometry;
 wu088::petras::Bivariate b;b.callback=hh?recorded_physical:capture_geometry;b.param=hh?static_cast<void*>(&physical):static_cast<void*>(&geometry);b.uniform_whole_parameter_box=true;b.joint_holomorphy_proved=true;
 wu088::log2map::Context context(b,128);
 int map_return=wu088::log2map::callback(out.value,inner.value,outer.value,&context,0,128);
 const Capture&images=hh?physical.capture:geometry;
 if(images.calls!=1)throw std::runtime_error("exactly one physical/capture entry required");
 std::ostringstream ts;ts<<"[";bool first=true;for(const auto&t:terms){if(!first)ts<<",";first=false;ts<<"["<<t.i<<","<<t.j<<","<<t.k<<","<<rational(t.coefficient)<<"]";}ts<<"]";
 std::cout<<"{\"schema\":\"WU088_FD1_FIRST_BOX_OBSERVATION_V1\",\"kind\":"<<text(hh?"HH_SINGLE_CALLBACK_OBSERVATION":"GEOMETRY_ONLY_NO_FIELD_CALLBACK")<<",\"query_id\":"<<text(id)<<",\"implementation\":"<<text(mode)<<",\"cell_id\":"<<q.cell<<",\"parent_raw_sha256\":"<<text(q.parent_raw_sha)<<",\"query_scope_sha256\":\""<<FD1_QUERY_SCOPE_SHA256<<"\",\"archive_sha256\":\""<<WU088_ARCHIVE_SHA256<<"\",\"input_record_sha256\":\""<<WU088_RECORD_SHA256<<"\",\"original_build_source_sha256\":\""<<WU088_BUILD_SOURCE_SHA256<<"\",\"diagnostic_source_sha256\":\""<<FD1_DIAGNOSTIC_SOURCE_SHA256<<"\",\"primitive_index\":0,\"precision_bits\":128,\"order\":0,\"field\":\"O\",\"orbital\":\"S\",\"ia\":0,\"ib\":0,\"coefficient_semantics\":\"ORIGINAL_SIGNED_ORDERED107\",\"inner_log_box\":"<<ball(inner.value)<<",\"outer_log_box\":"<<ball(outer.value)<<",\"physical_t\":"<<images.t<<",\"physical_u\":"<<images.u<<",\"margin\":"<<rational(contract.margin)<<",\"a\":"<<rational(parameters.a)<<",\"b\":"<<rational(parameters.b)<<",\"ordered_terms\":"<<ts.str()<<",\"HH_evaluations\":"<<(hh?1:0)<<",\"integrations\":0,\"log_map_return\":"<<map_return<<",\"mapped_output_finite\":"<<(hh?(acb_is_finite(out.value)?"true":"false"):"null")<<",\"mapped_output_dump\":"<<(hh?ball(out.value):"null")<<",\"record\":"<<(hh?recorder.json():"null")<<",\"scientific_admission\":false,\"production_admission\":false}\n";
 return 0; // Nonfinite HH output is an observation, never an enclosure admission.
}
int main(int argc,char**argv){try{
 if(std::string(flint_version)!="3.4.0")throw std::runtime_error("runtime FLINT pin changed");
 flint_set_num_threads(1);
 if(argc==3&&std::string(argv[1])=="--synthetic")return synthetic(argv[2]);
 if(argc==3&&std::string(argv[1])=="--geometry")return execute_query(argv[2],false,"cached");
 // This branch is not invoked in preparation. Future exact-authorized adapter only.
 if(argc==5&&std::string(argv[1])=="--hh-single"){
  if(std::string(argv[4])!=FD1_QUERY_SCOPE_SHA256)throw std::invalid_argument("query scope hash mismatch");
  return execute_query(argv[2],true,argv[3]);}
 throw std::invalid_argument("bounded diagnostic interface required");
 }catch(const std::exception&e){std::cerr<<"FD1_REJECTED: "<<e.what()<<"\n";return 64;}}
