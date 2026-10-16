#ifndef NP_KERNEL_H
#define NP_KERNEL_H
/* C11, SI rates, MeV energies. Historical Chen--Savage 1999 model only. */
double np_fit_L(double anchor_mb);
double np_sv(double E_MeV, double L_fm2);
double np_sigma(double E_MeV, double L_fm2);
double np_maxwell(double T_K, double L_fm2, int n);
double np_photo_logpref(double T_K, double L_fm2, int n, int exact_rest);
double np_activation(double T_K, int exact_rest);
double np_photo_xsec(double E_MeV, double L_fm2, int exact_rest);
double np_saha_logpref(double T_K, double capture_m3_s);
double np_bessel_S(int nu, double z);
double np_maxwell_juttner(double T_K,double L_fm2,int n);
double np_photo_thermal_MB_logpref(double T_K,double L_fm2,int n);
#endif
