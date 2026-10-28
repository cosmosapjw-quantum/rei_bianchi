"""Reference arithmetic; imports no production helper or old producer."""
from fractions import Fraction
from itertools import product

def corners(level,literal,h,W):
    output=[]
    for signs in product((-1,1),repeat=8):
        amplitudes=[Fraction(1)+Fraction(s,2) for s in signs]
        losses=sum((-h*x*r for x,r in zip(level,amplitudes)),Fraction(0));photons=sum((h*x*r for x,r in zip(literal,amplitudes)),Fraction(0))
        output.append({'signs':list(signs),'amplitudes':amplitudes,'integrated_residual':W*(losses+photons)})
    return output

def cr_vertices(labels,vertices):
    out=[]
    for vertex in vertices:
        value=Fraction(0);marginal=[Fraction(0),Fraction(0)];pairs=Fraction(0)
        for label,mass in zip(labels,vertex):
            if label[0]=='single':value+=Fraction(2459,100)*mass;marginal[label[1]]+=mass
            elif label[0]=='pair':value+=Fraction(7901,100)*mass;pairs+=mass;marginal[label[1]]+=mass;marginal[label[2]]+=mass
            else:raise ValueError('UNKNOWN_EVENT')
        out.append({'value_eV_m3':value,'marginals':marginal,'d':pairs})
    return out

def daughter_variances(v):
    return {'total':v+v+2*(-v),'imbalance':v+v-2*(-v),'independent_total':v+v,'independent_imbalance':v+v}

def scalar_oracle():
    return {'linear':Fraction(2)*Fraction(1,10),'quadratic':Fraction(3)*Fraction(1,5)**2,'mismatch':Fraction(1,2)*Fraction(1,5),'other':Fraction(1,100),'epsilon':Fraction(43,100),'projected':Fraction(86,100),'omitted_mismatch':Fraction(33,100)}
