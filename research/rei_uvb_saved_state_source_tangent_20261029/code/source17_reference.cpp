// Standalone independent direct-event C++ reference for seven saved REI rows.
// Inputs: z, y[17], moments[6] (PR261 already-scaled); no IVP or native solver.
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

int main() {
    constexpr std::array<int,7> src{1,3,5,7,8,10,11};
    constexpr std::array<int,7> dst{2,4,6,8,9,11,12};
    constexpr std::array<int,7> moment{0,0,0,2,4,2,4};
    constexpr std::array<int,7> heat{1,1,1,3,5,3,5};
    const double ln10=std::log(10.0);
    std::cout << std::setprecision(17);
    std::string line;
    while (std::getline(std::cin,line)) {
        if (line.empty()) continue;
        std::istringstream in(line);
        double z{}; std::array<double,17> y{}; std::array<double,6> r{};
        if (!(in>>z)) return 2;
        for (double& v:y) if (!(in>>v)) return 3;
        for (double& v:r) if (!(in>>v)) return 4;
        std::array<double,17> f{};
        double electrons=0.0, photoheat=0.0;
        for (std::size_t k=0;k<src.size();++k) {
            const double ev=y[src[k]]*r[moment[k]];
            f[src[k]]-=ev; f[dst[k]]+=ev;
            electrons+=ev;
            photoheat+=y[src[k]]*r[heat[k]];
        }
        std::cout<<z<<' '<<electrons<<' '<<photoheat<<' '
                 <<ln10*electrons<<' '<<ln10*electrons*(z-3.6);
        for (double v:f) std::cout<<' '<<v;
        std::cout<<'\n';
    }
}
