#include "../src/finite_m.hpp"
#include <iostream>
#include <string>
int main(){
 if(std::string(flint_version)!="3.4.0")return 3;
 flint_set_num_threads(1);unsigned failed=0,total=0;
 for(int q=0;q<2;++q){acb_t z,out;acb_init(z);acb_init(out);
  const char* re=q==0?"2a4125e1 -19 468f295 -15":"2a4125e1 -1a 468f295 -16";
  const char* im=q==0?"244abe51 -1f 3c8ef465 -1f":"244abe51 -20 3c8ef465 -20";
  if(arb_load_str(acb_realref(z),re)||arb_load_str(acb_imagref(z),im))return 4;
  for(unsigned r=0;r<3;++r){++total;wu088_fd2::family_m(out,1,r,z,128);
   bool ok=acb_is_finite(out);failed+=!ok;
   std::cout<<(ok?"PASS ":"FAIL ")<<(q==0?"Q272":"Q000")<<"_k1_r"<<r<<"_finite_whole_box\n";
  }acb_clear(z);acb_clear(out);
 }
 std::cout<<"TOTAL "<<total<<" FAILED "<<failed<<'\n';return failed?1:0;
}
