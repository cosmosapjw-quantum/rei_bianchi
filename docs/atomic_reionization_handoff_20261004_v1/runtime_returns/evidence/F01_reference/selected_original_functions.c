/* Isolated research harness. Original Grackle function bodies follow unchanged.
Copyright (c) 2013-, Enzo/Grackle development team. License in inputs/LICENSE.
The struct below is a minimal local stub, NOT the library public ABI. */
#include <math.h>
#define tiny 1.0e-20
#define tevk 1.1605e4
#define dhuge 1.0e30
#define kboltz 1.3806504e-16
typedef struct { int CaseBRecombination; int collisional_excitation_rates;
 int collisional_ionisation_rates; int recombination_cooling_rates;
 int bremsstrahlung_cooling_rates; } chemistry_data;
double k1_rate(double T, double units, chemistry_data *my_chemistry)
{
    double T_ev = T / 11605.0;
    double logT_ev = log(T_ev);

    double k1 = exp( -32.71396786375
                        + 13.53655609057*logT_ev
                        - 5.739328757388*pow(logT_ev, 2)
                        + 1.563154982022*pow(logT_ev, 3)
                        - 0.2877056004391*pow(logT_ev, 4)
                        + 0.03482559773736999*pow(logT_ev, 5)
                        - 0.00263197617559*pow(logT_ev, 6)
                        + 0.0001119543953861*pow(logT_ev, 7)
                        - 2.039149852002e-6*pow(logT_ev, 8)) / units;
    if (T_ev <= 0.8){
        k1 = fmax(tiny, k1); 
    }
    return k1;
}

double k3_rate(double T, double units, chemistry_data *my_chemistry)
{
    double T_ev = T / 11605.0;
    double logT_ev = log(T_ev);

    if (T_ev > 0.8){
        return exp( -44.09864886561001
                + 23.91596563469*logT_ev
                - 10.75323019821*pow(logT_ev, 2)
                + 3.058038757198*pow(logT_ev, 3)
                - 0.5685118909884001*pow(logT_ev, 4)
                + 0.06795391233790001*pow(logT_ev, 5)
                - 0.005009056101857001*pow(logT_ev, 6)
                + 0.0002067236157507*pow(logT_ev, 7)
                - 3.649161410833e-6*pow(logT_ev, 8)) / units;
    } else {
        return tiny;
    }
}

double k4_rate(double T, double units, chemistry_data *my_chemistry)
{
    double T_ev = T / 11605.0;

    //If case B recombination on.
    if (my_chemistry->CaseBRecombination == 1){
        return 1.26e-14 * pow(5.7067e5/T, 0.75) / units;
    }

    //If case B recombination off.
    if (T_ev > 0.8){
        return (1.54e-9*(1.0 + 0.3 / exp(8.099328789667/T_ev))
             / (exp(40.49664394833662/T_ev)*pow(T_ev, 1.5))
             + 3.92e-13/pow(T_ev, 0.6353)) / units;
    } else {
        return 3.92e-13/pow(T_ev, 0.6353) / units;
    }
}

double k2_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->CaseBRecombination == 1) {
        if (T < 1.0e9) {
            return 4.881357e-6*pow(T, -1.5) \
                * pow((1.0 + 1.14813e2*pow(T, -0.407)), -2.242) / units;
        } else {
            return tiny;
        }  
    } else {
        if (T > 5500) {
            //Convert temperature to appropriate form.
            double T_ev = T / tevk;
            double logT_ev = log(T_ev);

            return exp( -28.61303380689232 \
                - 0.7241125657826851*logT_ev \
                - 0.02026044731984691*pow(logT_ev, 2) \
                - 0.002380861877349834*pow(logT_ev, 3) \
                - 0.0003212605213188796*pow(logT_ev, 4) \
                - 0.00001421502914054107*pow(logT_ev, 5) \
                + 4.989108920299513e-6*pow(logT_ev, 6) \
                + 5.755614137575758e-7*pow(logT_ev, 7) \
                - 1.856767039775261e-8*pow(logT_ev, 8) \
                - 3.071135243196595e-9*pow(logT_ev, 9)) / units;
        } else {
            return k4_rate(T, units, my_chemistry);
        }
    }
}

double k5_rate(double T, double units, chemistry_data *my_chemistry)
{
    double T_ev = T / 11605.0;
    double logT_ev = log(T_ev);

    double k5;
    if (T_ev > 0.8){
        k5 = exp(-68.71040990212001
                + 43.93347632635*logT_ev
                - 18.48066993568*pow(logT_ev, 2)
                + 4.701626486759002*pow(logT_ev, 3)
                - 0.7692466334492*pow(logT_ev, 4)
                + 0.08113042097303*pow(logT_ev, 5)
                - 0.005324020628287001*pow(logT_ev, 6)
                + 0.0001975705312221*pow(logT_ev, 7)
                - 3.165581065665e-6*pow(logT_ev, 8)) / units;
    } else {
        k5 = tiny;
    }
    return k5;
}

double k6_rate(double T, double units, chemistry_data *my_chemistry)
{
    double k6;
    //Has case B recombination setting.
    if (my_chemistry->CaseBRecombination == 1) {
        if (T < 1.0e9) {
            k6 = 7.8155e-5*pow(T, -1.5)
                * pow((1.0 + 2.0189e2*pow(T, -0.407)), -2.242) / units;
        } else {
            k6 = tiny;
        }
    } else {
        k6 = 3.36e-10/sqrt(T)/pow(T/1.0e3, 0.2)
             / (1.0 + pow(T/1.0e6, 0.7)) / units;
    }
    return k6;
}

double ceHI_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->collisional_excitation_rates == 1){
        return 7.5e-19*exp( -fmin(log(dhuge), 118348.0 / T) )
                / ( 1.0 + sqrt(T / 1.0e5) ) / units;
    } else {
        return tiny;
    }
}

double ceHeI_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->collisional_excitation_rates == 1){
        return 9.1e-27*exp(-fmin(log(dhuge), 13179.0/T))
                * pow(T, -0.1687) / ( 1.0 + sqrt(T/1.0e5) ) / units;
    } else {
        return tiny;
    }
}

double ceHeII_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->collisional_excitation_rates == 1){
        return 5.54e-17*exp(-fmin(log(dhuge), 473638.0/T))
                * pow(T, -0.3970) / ( 1.0 + sqrt(T/1.0e5) ) / units;
    } else {
        return tiny;
    }
}

double ciHeIS_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->collisional_ionisation_rates == 1){
        return 5.01e-27*pow(T, -0.1687) / ( 1.0 + sqrt(T/1.0e5) )
                * exp(-fmin(log(dhuge), 55338.0/T)) / units;
    } else {
        return tiny;
    }
}

double ciHI_rate(double T, double units, chemistry_data *my_chemistry)
{
    //Collisional ionization. Polynomial fit from Tom Abel.
    if (my_chemistry->collisional_ionisation_rates == 1){
        return 2.18e-11 * k1_rate(T, 1, my_chemistry) / units;
    } else {
        return tiny;
    }
}

double ciHeI_rate(double T, double units, chemistry_data *my_chemistry)
{
    //Collisional ionization. Polynomial fit from Tom Abel.
    if (my_chemistry->collisional_ionisation_rates == 1){
        return 3.94e-11 * k3_rate(T, 1, my_chemistry) / units;
    } else {
        return tiny;
    }
}

double ciHeII_rate(double T, double units, chemistry_data *my_chemistry)
{
    //Collisional ionization. Polynomial fit from Tom Abel.
    if (my_chemistry->collisional_ionisation_rates == 1){
        return 8.72e-11 * k5_rate(T, 1, my_chemistry) / units; 
    } else {
        return tiny;
    }
}

double reHII_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->recombination_cooling_rates == 1){
        //Define parameters used in the calculations.
        double lambdaHI    = 2.0 * 157807.0 / T;

        //These depend on if the user has chosen recombination case A or B.
        if (my_chemistry->CaseBRecombination == 1) {
            return 3.435e-30 * T * pow(lambdaHI, 1.970)
                    / pow( 1.0 + pow(lambdaHI/2.25, 0.376), 3.720)
                    / units;
        } else {
            return 1.778e-29 * T * pow(lambdaHI, 1.965)
                    / pow(1.0 + pow(lambdaHI/0.541, 0.502), 2.697)
                    / units; 
        }
    } else {
        return tiny;
    }
}

double reHeII1_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->recombination_cooling_rates == 1){
        //Define parameters used in the calculations.
        double lambdaHeII  = 2.0 * 285335.0 / T;

        //These depend on if the user has chosen recombination case A or B.
        if (my_chemistry->CaseBRecombination == 1) {
            return 1.26e-14 * kboltz * T * pow(lambdaHeII, 0.75)
                            / units;
        } else {
            return 3e-14 * kboltz * T * pow(lambdaHeII, 0.654)
                    / units;
        }
    } else {
        return tiny;
    }
}

double reHeII2_rate(double T, double units, chemistry_data *my_chemistry)
{
    //Dielectronic recombination (Cen, 1992).
    if (my_chemistry->recombination_cooling_rates == 1){
        return 1.24e-13 * pow(T, -1.5)
                * exp( -fmin(log(dhuge), 470000.0 / T) )
                * ( 1.0 + 0.3 * exp( -fmin(log(dhuge), 94000.0 / T) ) ) 
                / units;
    } else {
        return tiny;
    }
}

double reHeIII_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->recombination_cooling_rates == 1){
        //Define parameters used in the calculations.
        double lambdaHeIII = 2.0 * 631515.0 / T;

        //These depend on if the user has chosen recombination case A or B.
        if (my_chemistry->CaseBRecombination == 1) {
            return 8.0 * 3.435e-30 * T * pow(lambdaHeIII, 1.970)
                    / pow(1.0 + pow(lambdaHeIII / 2.25, 0.376), 3.720) 
                    / units;
        } else {
            return 8.0 * 1.778e-29 * T * pow(lambdaHeIII, 1.965)
                    / pow(1.0 + pow(lambdaHeIII / 0.541, 0.502), 2.697)
                    / units;
        }
    } else {
        return tiny;
    }
}

double brem_rate(double T, double units, chemistry_data *my_chemistry)
{
    if (my_chemistry->bremsstrahlung_cooling_rates == 1){
        return 1.43e-27 * sqrt(T)
                * ( 1.1 + 0.34 * exp( -pow(5.5 - log10(T), 2) / 3.0) )
                / units;
    } else {
        return tiny;
    }
}
