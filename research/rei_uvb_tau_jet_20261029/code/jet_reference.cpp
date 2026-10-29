// Independent C++20 numeric oracle for the parameter-response jet determinant.
// This is algebra on saved scalar forcing, not an IVP or a tau calculation.
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

int main(int argc, char **argv) {
  if (argc != 2) { std::cerr << "expected one TSV path\n"; return 2; }
  std::ifstream f(argv[1]);
  if (!f) { std::cerr << "input missing\n"; return 3; }
  std::string line;
  std::size_t count=0;
  long double max_relative=0;
  std::cout << std::setprecision(19);
  while (std::getline(f,line)) {
    if (line.empty() || line[0]=='#') continue;
    std::istringstream iss(line);
    long double z,g,ref;
    if (!(iss>>z>>g>>ref)) { std::cerr << "bad row\n";return 4; }
    if (z<2.4L || z>4.75L || !(g>0)) { std::cerr << "bad domain\n";return 5; }
    const long double d=z-3.6L;
    const long double zp=-(1+z);
    // Deliberately arbitrary third-derivative nuisance: should cancel exactly.
    const long double u=g*(7.0L+0.125L*z);
    const long double det=std::fma(g,d*u+g*zp,-d*g*u);
    const long double expected=g*g*zp;
    const long double rel=std::abs((det-expected)/expected);
    const long double relref=std::abs((det-ref)/ref);
    max_relative=std::max(max_relative,std::max(rel,relref));
    if (rel>2e-15L || relref>2e-15L) { std::cerr << "mismatch\n";return 6; }
    ++count;
    std::cout << z << '\t' << det << '\t' << expected << '\t' << rel << '\n';
  }
  if (count!=7) { std::cerr << "expected 7 rows, got " << count << '\n';return 7; }
  std::cerr << "CPP_PASS rows=" << count << " max_relative=" << max_relative << '\n';
  return 0;
}
