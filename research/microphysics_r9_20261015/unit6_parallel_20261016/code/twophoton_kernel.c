#include <math.h>
#include <stddef.h>

/* Frozen literature fit; f is one selected photon, q=2f counts both. */
static double beta_fn(double a, double b) {
    return exp(lgamma(a)+lgamma(b)-lgamma(a+b));
}
double tp_normalizer(void) {
    return beta_fn(2,2)-pow(4,.8)*beta_fn(2.8,2.8)
        +.88*pow(4,.8)*beta_fn(3.33,3.33);
}
double tp_f(double y) {
    if (y<=0 || y>=1) return 0;
    double w=y*(1-y);
    return (w*(1-pow(4*w,.8))+.88*pow(4,.8)*pow(w,2.33))/tp_normalizer();
}
double tp_rate(double delta, double delta_h, int z) {
    return 8.229352*pow((double)z,6)*delta/(z*z*delta_h);
}
void tp_reservoir(double p, double a, double t, double *r, double *d) {
    *r=p*exp(-a*t); *d=p*(-expm1(-a*t));
}
/* Unknown above Emax is NaN: it must never be interpreted as zero. */
double tp_sigma(double e) {
    if (e<5.392) return 0;
    if (e>64.39) return NAN;
    double x=e/3.107, y=fabs(x);
    return 1e-22*62.45*(x-1)*(x-1)*pow(y,4.895/2-5.5)
        *pow(1+sqrt(y/15.01),-4.895);
}
/* kind: 0 photons, 1 energy/eV, 2 area, 3 heating J m2, 4 absorbed J m2.
 * This integrates the source per injected precursor, with no flux inference. */
static double integrand(double e,double delta,double p,int kind) {
    double s=2*p*tp_f(e/delta)/delta;
    if (kind==0) return s;
    if (kind==1) return e*s;
    s*=tp_sigma(e);
    if (kind==2) return s;
    return s*1.602176634e-19*(kind==3 ? e-5.392:e);
}
double tp_integrate(double lo,double hi,double delta,double p,int kind,int n) {
    if (hi<=lo) return 0;
    if (kind>=2 && (lo<5.392 || hi>64.39)) return NAN;
    const double pi=3.141592653589793238462643383279502884;
    static double nodes[3][128],weights[3][128];
    static int ready[3]={0,0,0};
    int slot=n==64?0:n==128?1:n==256?2:-1;
    if(slot<0) return NAN;
    double sum=0, mid=(lo+hi)/2, half=(hi-lo)/2;
    for(int i=0;i<(n+1)/2;i++) {
        double z=nodes[slot][i],weight=weights[slot][i];
        if(!ready[slot]) {
        z=cos(pi*(i+.75)/(n+.5)); double derivative=0;
        for(int it=0;it<100;it++) {
            double p1=1,p2=0;
            for(int j=1;j<=n;j++){double p3=p2;p2=p1;p1=((2*j-1)*z*p2-(j-1)*p3)/j;}
            derivative=n*(z*p1-p2)/(z*z-1);
            double next=z-p1/derivative;
            if(fabs(next-z)<2e-15){z=next;break;} z=next;
        }
        /* Re-evaluate derivative at the accepted root. */
        double p1=1,p2=0;
        for(int j=1;j<=n;j++){double p3=p2;p2=p1;p1=((2*j-1)*z*p2-(j-1)*p3)/j;}
        derivative=n*(z*p1-p2)/(z*z-1);
        weight=2/((1-z*z)*derivative*derivative);
        nodes[slot][i]=z; weights[slot][i]=weight;
        }
        sum+=weight*(integrand(mid-half*z,delta,p,kind)+integrand(mid+half*z,delta,p,kind));
    }
    ready[slot]=1;
    return half*sum;
}
