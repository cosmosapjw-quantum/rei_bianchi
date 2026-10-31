"""Published standalone atomic table + Grackle n=2 benchmark kernel; no cosmic IVP."""
from __future__ import annotations
import math
LOG_T=[3.6,3.8,4.0,4.2,4.4,4.6,4.8,5.0,5.2,5.4]
UP={
'2s':[.1713,.1689,.1661,.1629,.1595,.1553,.1502,.1458,.1432,.1417],
'2p12':[.1141,.1162,.1191,.1229,.1281,.1349,.1445,.1597,.1831,.2118],
'2p32':[.2264,.2311,.2371,.2449,.2555,.2692,.2885,.3190,.3660,.4233],
}
RY=13.605693122994
DELTA={'2s':2.999707*RY,'2p12':2.999702*RY,'2p32':2.999756*RY}
KB=8.617333262145e-5
ERG_PER_EV=1.602176634e-12

def upsilon(T,channel):
    if not(10**3.6<=T<=10**5.4):return float('nan')
    x=math.log10(T)
    if x<=LOG_T[0]:return UP[channel][0]
    for i in range(len(LOG_T)-1):
        if x<=LOG_T[i+1]:
            w=(x-LOG_T[i])/(LOG_T[i+1]-LOG_T[i])
            return (1-w)*UP[channel][i]+w*UP[channel][i+1]
    return UP[channel][-1]

def rate(T,channel):
    u=upsilon(T,channel)
    return 8.629e-6*u/(2*math.sqrt(T))*math.exp(-DELTA[channel]/(KB*T))

def energy_loss_coefficient(T):
    return sum(rate(T,key)*DELTA[key]*ERG_PER_EV for key in UP)

def grackle_ceHeII(T):
    return 5.54e-17*math.exp(-473638.0/T)*T**(-0.3970)/(1+math.sqrt(T/1e5))

def rate_ratio(T):
    return energy_loss_coefficient(T)/grackle_ceHeII(T)

def point_loss(T,ne_cm3,nHeII_cm3,nb_cm3):
    """eV/(original baryon s), only supported native point coefficient."""
    return ne_cm3*nHeII_cm3/nb_cm3 * energy_loss_coefficient(T)/ERG_PER_EV

def demo():
    assert math.isnan(rate(100,'2s'))
    assert math.isclose(rate(12000,'2s'),4.4e-26,rel_tol=.03)
    assert 1.3<rate_ratio(12000)<1.4
    return {k:rate(12000,k) for k in UP}

if __name__=='__main__':
    print(demo())
