// Standalone C++20 alternate arithmetic for saved seven isotope-inventory inputs.
// This is NOT a chemistry IVP, physical-source or full-repo validation.
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
int main(int argc,char** argv){
 if(argc!=2){std::cerr<<"USAGE input.tsv\n";return 2;}
 std::ifstream in(argv[1]);if(!in){std::cerr<<"NO_FILE\n";return 3;}
 long double maxrel=0;int count=0;std::string line;
 std::cout<<std::setprecision(20);
 while(std::getline(in,line)){
  if(line.empty()||line[0]=='#')continue;
  std::istringstream ss(line);
  long double z,REI_H,REI_He,BASS_H,BASS_He,ref;
  if(!(ss>>z>>REI_H>>REI_He>>BASS_H>>BASS_He>>ref)){std::cerr<<"BAD_TSV\n";return 4;}
  if(!(REI_H>0 && REI_He>0 && BASS_H>0 && BASS_He>0)){std::cerr<<"BAD_DOMAIN\n";return 5;}
  const long double a=REI_H/BASS_H,b=REI_He/BASS_He;
  const long double rho=2/(a+b);
  const long double d=std::fabs(a-b)/(a+b);
  const long double achieved=std::fmax(std::fabs(rho*a-1),std::fabs(rho*b-1));
  const long double rel=std::fabs(d-ref)/ref;
  const long double att=std::fabs(achieved-d);
  if(rel>3e-15L || att>3e-18L){std::cerr<<"MISMATCH "<<rel<<" "<<att<<"\n";return 6;}
  if(rel>maxrel)maxrel=rel;
  std::cout<<z<<'\t'<<rho<<'\t'<<d<<'\t'<<rel<<'\n';count++;
 }
 if(count!=7){std::cerr<<"WRONG_ROWS\n";return 7;}
 std::cerr<<"CPP_PASS rows="<<count<<" max_relative="<<std::setprecision(20)<<maxrel<<"\n";
 return 0;
}
