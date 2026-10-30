from decimal import Decimal as D
import csv
from pathlib import Path
root=Path(__file__).parent
rs=list(csv.DictReader((root/'drake1969_tableII_LiII_21.csv').open()))
expected=[0,379,1110,1810,2420,2940,3380,3740,4060,4320,4540,4730,4880,5020,5130,5220,5290,5350,5380,5410,5420]
assert len(rs)==21 and [int(r['A_per_y_s_minus_1']) for r in rs]==expected
area=sum((D(expected[i])+D(expected[i+1]))*D('0.025')/2 for i in range(20))
assert area==D('1945.475'), area
b=list(csv.DictReader((root/'ferrett1987_n2_raw.csv').open()))
p=next(x for x in b if x['photon_energy_eV']=='77.5')
R=D(p['R_3S_over_rest_n2']);P=D(p['R_1P_over_3S'])
assert abs((1-R*(1+P)/(1+R))-D('0.3228947368421053'))<D('1e-15')
print('PASS 21/21 source, PL integral, measured local branch bound; full astrophysics NOT_RUN')
