// BASS source-qualified Li6 charge lift, standalone 7-row numeric cross-check.
// Input columns: saved z, Li7+,Li7++,Li7+++, owner nu6,nu7, Python exact reference.
// This does NOT calculate physical n_e, rates, trajectories, or tau.
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <algorithm>
int main(int argc, char** argv){
  if(argc!=2){std::cerr<<"one input TSV required\n";return 2;}
  std::ifstream in(argv[1]); if(!in){std::cerr<<"cannot read TSV\n";return 3;}
  std::cout<<std::setprecision(22);
  std::string line; unsigned count=0; long double worst=0;
  while(std::getline(in,line)){
    if(line.empty() || line[0]=='#')continue;
    std::istringstream r(line);
    long double z,y1,y2,y3,nu6,nu7,ref;
    if(!(r>>z>>y1>>y2>>y3>>nu6>>nu7>>ref)){std::cerr<<"bad row\n";return 4;}
    if(!(z>=2.4L && z<=4.75L && y1>=0.L && y2>=0.L && y3>=0.L && nu6>0.L && nu7>0.L && ref>=0.L)){
      std::cerr<<"invalid input domain\n";return 5;
    }
    long double calc=(y1+2.L*y2+3.L*y3)*(nu6/nu7);
    long double delta=std::abs(calc-ref);
    long double rel= ref>0.L ? delta/ref : delta;
    worst=std::max(worst,rel);
    if(rel>2e-16L){std::cerr<<"reference mismatch\n";return 6;}
    std::cout<<z<<'\t'<<calc<<'\t'<<ref<<'\t'<<rel<<'\n';++count;
  }
  if(count!=7){std::cerr<<"expected 7 saved rows\n";return 7;}
  std::cerr<<std::setprecision(22)<<"CPP_PASS rows=7 max_relative="<<worst<<"\n";
  return 0;
}
