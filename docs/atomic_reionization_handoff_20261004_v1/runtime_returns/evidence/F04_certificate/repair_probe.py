import importlib.util,json
from pathlib import Path
P=Path('.cuh/fastest-track/REI-F04-CERT')
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
old=load('original',P/'pre-repair/checker.py');new=load('repaired',P/'checker.py')
mf=json.loads(Path('runs/rei_fastest_v1/map_certificate/parent_manifest.json').read_text());cs=json.loads((P/'model_constants.json').read_text());a=old.Model(mf,cs);b=new.Model(mf,cs);R=old.R
dc=R(float(1.923))*R(float(.470))-R(float(1.923)*float(.470));rows=[];checks=0
for site in json.loads((P/'candidate.json').read_text())['sites']:
    point=[R(float(v)) for v in site['center']];prior=a.rhs(point);fixed=b.rhs(point);y=[old.J(v,index=i) for i,v in enumerate(point)];t=a.temperature(y);ne=a.nh*y[0]+a.nhe*(y[1]+2*y[2]);up=[a.nh*y[0],a.nhe*y[1],a.nhe*y[2]];correction=old.J(0)
    for k in [0,2]:
        l=R(float([315614,570670,1263030][k]))/t;u=(l/R(float(.522))).power(.470);alpha=R(float(2 if k==2 else 1))*R(float(1.269e-13))*l.power(1.503)/(1+u).power(1.923)
        correction=correction-up[k]*ne*a.kb*t*alpha*dc*u/(1+u)/(a.nh*a.ev)
    expected=prior[3]+correction
    pairs=[(fixed[3].v,expected.v)]+[(fixed[3].g[i],expected.g[i]) for i in range(7)]+[(fixed[3].h[i,j],expected.h[i,j]) for i in range(7) for j in range(7)]
    for got,want in pairs:
        assert got.lower()<=want.upper() and want.lower()<=got.upper(),(str(got),str(want));checks+=1
    assert prior[3].v.upper()<fixed[3].v.lower() or fixed[3].v.upper()<prior[3].v.lower()
    rows.append({'id':site['id'],'old_new_rhs_disjoint':True,'analytic_coefficient_correction':str(correction.v)})
print(json.dumps({'status':'PASS','coefficient_correction_overlap_checks':checks,'sites':rows,'scope':'Discriminates old incorrect coefficient from repaired analytic expression; uniform proof remains separate frozen external validator'}))
