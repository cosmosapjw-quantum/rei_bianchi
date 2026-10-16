/* Thin exports around the pinned, unchanged literal-C coefficient bodies. */
#define main grackle_literal_original_main
#include "grackle_literal_reference.c"
#undef main

int c16b_reference_coefficients(double T, double *v) {
    if (!isfinite(T) || T < 1.0 || T > 1e6) return 1;
    chemistry_data c = {0,1,1,1};
    double tev=T/11605.0;
    /* Same explicit algebraic RR/DR decomposition as original emit(), not k4-RR subtraction. */
    double rr=3.92e-13/pow(tev,0.6353);
    double dr=tev>0.8 ? 1.54e-9*(1.0+0.3/exp(8.099328789667/tev))/(exp(40.49664394833662/tev)*pow(tev,1.5)) : 0.0;
    double raw_dr=reHeII2_rate(T,1.0,&c);
    double a[17]={k1_rate(T,1.0,&c),k3_rate(T,1.0,&c),k5_rate(T,1.0,&c),
      k2_rate(T,1.0,&c),rr,k6_rate(T,1.0,&c),dr,
      ceHI_rate(T,1.0,&c),ceHeI_rate(T,1.0,&c),ceHeII_rate(T,1.0,&c),
      reHII_rate(T,1.0,&c),reHeII1_rate(T,1.0,&c),reHeIII_rate(T,1.0,&c),
      raw_dr,brem_rate(T,1.0,&c),k4_rate(T,1.0,&c),tev>0.8?raw_dr:0.0};
    for(int i=0;i<17;i++)v[i]=a[i];
    return 0;
}
