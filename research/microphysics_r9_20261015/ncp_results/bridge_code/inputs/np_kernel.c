#include "np_kernel.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define PI 3.141592653589793238462643383279502884
/* SI exact h,c,k_B,e; alpha frozen to inherited R6 (SciPy CODATA2022).
   hbar*c in MeV fm is retained at the inherited 10-place value. */
static const double C=299792458., KB=1.380649e-23, HBAR=1.0545718176461565e-34;
static const double MEV=1.602176634e-13, ALPHA=7.2973525643e-3;
static const double HC=197.3269804, M=938.92, Q=2.224575;

double np_sv(double E, double L) {
    if (!isfinite(E)||E<0||E>1||!isfinite(L)) return NAN;
    double m=M/HC, g=sqrt(M*Q)/HC, x=M*E/(HC*HC);
    double b=1./(-23.714), r=2.73, rho=1.764, kap=2.35294;
    double mlo=kap*kap*pow(g,4)*pow(b-g,2)/((b*b+x)*pow(g*g+x,2));
    double corr=1+g*rho-r*(g*b+x)*x/((b*b+x)*(b-g));
    corr-=L*m*(g*g+x)/(kap*2*PI*(b-g));
    double pc=6.53+2*(-5.91)+(20./3)*.57;
    double e1=x*m*m*pow(g,4)/pow(g*g+x,4)*(1+g*rho+pow(g*rho,2)+pow(g*rho,3)+m*g/(6*PI)*(g*g/3+x)*pc);
    double factor=4*PI*ALPHA*pow(g*g+x,3)/(pow(g,3)*pow(m,4))*1e-30*(2*C*HC/M);
    return factor*(mlo*corr+e1);
}
double np_sigma(double E,double L) {
    if(E<=0) return NAN;
    return np_sv(E,L)/(2*C*sqrt(E/M));
}
double np_fit_L(double mb) {
    if(!isfinite(mb)||mb<=0) return NAN;
    double E=M/4*pow(2200./C,2), f0=np_sv(E,0), f1=np_sv(E,1);
    return (mb*1e-31*2200.-f0)/(f1-f0);
}
/* Quadrature has smooth y=sqrt(E/kT) endpoint, rather than a sqrt cusp. */
static int legendre(int n,double *x,double *w,double a,double b) {
    if(n<8||n>1024) return 0;
    for(int i=0;i<(n+1)/2;i++) {
        double z=cos(PI*(i+.75)/(n+.5)), z0, p=0, dp=0;
        int j=0;
        do {
            double p1=1,p2=0;
            for(int k=1;k<=n;k++){double p3=p2;p2=p1;p1=((2*k-1)*z*p2-(k-1)*p3)/k;}
            p=p1; dp=n*(z*p-p2)/(z*z-1); z0=z; z=z0-p/dp;
        } while(fabs(z-z0)>4e-16 && ++j<100);
        double mid=(a+b)/2,rad=(b-a)/2;
        x[i]=mid-rad*z; x[n-1-i]=mid+rad*z;
        w[i]=w[n-1-i]=2*rad/((1-z*z)*dp*dp);
    }
    return 1;
}
static int valid(double T,int n){return isfinite(T)&&T>=1e-3&&T<=1e8&&n>=8&&n<=1024;}
double np_maxwell(double T,double L,int n) {
    if(!valid(T,n)) return NAN;
    double x[1024],w[1024],theta=KB*T/MEV,sum=0;
    legendre(n,x,w,0,sqrt(80.));
    for(int i=0;i<n;i++){double y=x[i];sum+=w[i]*4/sqrt(PI)*y*y*exp(-y*y)*np_sv(theta*y*y,L);}
    return sum;
}
double np_activation(double T,int exact_rest) {
    if(!isfinite(T)||T<=0)return NAN;
    double Md=2*M-Q,th=exact_rest?Q+Q*Q/(2*Md):Q;
    return th/(KB*T/MEV);
}
double np_photo_xsec(double E,double L,int exact_rest) {
    if(!isfinite(E)||E<=0||E>1)return NAN;
    double Md=2*M-Q,W=2*M+E,eps=Q+E,ratio;
    if(exact_rest){eps=(Q+E)*(W+Md)/(2*Md);double pg=eps*Md/W;ratio=(2./3)*E*(4*M+E)/4/(pg*pg);}
    else ratio=(2./3)*M*E/(eps*eps);
    return ratio*np_sigma(E,L);
}
double np_photo_logpref(double T,double L,int n,int exact_rest) {
    if(!valid(T,n))return NAN;
    double ys[1024],ws[1024],theta=KB*T/MEV,activation=np_activation(T,exact_rest),sum=0;
    double Md=2*M-Q;
    legendre(n,ys,ws,0,sqrt(80.));
    for(int i=0;i<n;i++){
        double y=ys[i],delta=theta*y*y,E=delta,W=2*M+E;
        if(exact_rest){/* E=W−2M without catastrophic cancellation. */
            E=2*Md*delta/(sqrt(4*M*M+2*Md*delta)+2*M); W=2*M+E;
        }
        /* eps² sigma_photo = (2/3)*sigma_capture*p²*(W/Md)².
           In zero-recoil convention this is (2/3)*sigma_capture*M*E. */
        double factor=(2./3)*np_sv(E,L)/(2*C)*sqrt(M*E)*(M+(exact_rest?E/4:0));
        if(exact_rest)factor*=pow(W/Md,2);
        double bose=-expm1(-activation-y*y);
        sum+=ws[i]*factor*2*theta*y*exp(-y*y)/bose;
    }
    double pref=C/PI/PI*pow(MEV/(HBAR*C),3);
    return log(pref*sum);
}
double np_saha_logpref(double T,double capture) {
    if(T<=0||capture<=0)return NAN;
    double mu=M*MEV/(2*C*C);
    return log(4./3)+1.5*log(mu*KB*T/(2*PI*HBAR*HBAR))+log(capture);
}
/* K_nu(z) = sqrt(pi/(2z))*exp(-z)*S_nu(z); all uses z>=1e5.
   Six asymptotic terms. Independent scipy scaled-Bessel check provided. */
double np_bessel_S(int nu,double z) {
    if((nu!=1&&nu!=2)||!isfinite(z)||z<1e5)return NAN;
    double sum=1,term=1;
    for(int k=1;k<=6;k++){term*=(4.*nu*nu-(2.*k-1)*(2.*k-1))/(8*k*z);sum+=term;}
    return sum;
}
double np_maxwell_juttner(double T,double L,int n) {
    if(!valid(T,n))return NAN;
    double x[1024],w[1024],theta=KB*T/MEV,sum=0,S2=np_bessel_S(2,M/theta);
    legendre(n,x,w,0,sqrt(80.));
    for(int i=0;i<n;i++){
        double y=x[i],E=theta*y*y,W=2*M+E;
        double correction=(1+E/(4*M))*pow(W/(2*M),1.5)*np_bessel_S(1,W/theta)/(S2*S2);
        sum+=w[i]*4/sqrt(PI)*y*y*exp(-y*y)*np_sv(E,L)*correction;
    }
    return sum;
}
double np_photo_thermal_MB_logpref(double T,double L,int n) {
    if(!valid(T,n))return NAN;
    double theta=KB*T/MEV,Md=2*M-Q,K=np_maxwell_juttner(T,L,n);
    double mstar=(M*M/Md)*MEV/(C*C);
    return log(K)+log(4./3)+1.5*log(mstar*KB*T/(2*PI*HBAR*HBAR))
      +2*log(np_bessel_S(2,M/theta))-log(np_bessel_S(2,Md/theta));
}
#ifndef NP_NO_MAIN
int main(void){
    double ts[]={1e-3,1e-2,1,2.7255,6.109701377331961,100,1e4,1e6,1e7,1e8};
    double L=np_fit_L(334.2);
    puts("T_K,capture_m3_s,capture_quad_rel,NR_logpref_s_inv,NR_activation,NR_log10_lambda_s_inv,rest_logpref_s_inv,rest_activation,rest_log10_lambda_s_inv,Saha_logpref_residual,rest_quad_logpref_diff");
    for(unsigned i=0;i<sizeof(ts)/sizeof(ts[0]);i++){
        double T=ts[i],k=np_maxwell(T,L,128),k64=np_maxwell(T,L,64);
        double ln=np_photo_logpref(T,L,128,0),an=np_activation(T,0);
        double lr=np_photo_logpref(T,L,128,1),ar=np_activation(T,1),lr64=np_photo_logpref(T,L,64,1);
        printf("%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",T,k,k64/k-1,ln,an,(ln-an)/log(10.),lr,ar,(lr-ar)/log(10.),ln-np_saha_logpref(T,k),lr-lr64);
    }
    return 0;
}
#endif
