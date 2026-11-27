import sympy as s,json
from pathlib import Path
# Independent stoichiometric variables, physical binding energies kept symbolic.
P=s.symbols('P0:3');C=s.symbols('C0:3');R=s.symbols('R0:3');D,Y=s.symbols('D Y',positive=True);I=s.symbols('I0:3');H,Tcmb,Krr,Kdr,Kce,Kff=s.symbols('H Tcmb Krr Kdr Kce Kff')
h=P[0]+C[0]-R[0];he1=P[1]+C[1]-R[1]-D;he2=P[2]+C[2]-R[2]
dspecies=s.Matrix([-h,h,-he1,he1-he2,he2,h+he1+he2])
charge=s.expand(dspecies[1]+dspecies[3]+2*dspecies[4]-dspecies[5])
dbind=I[0]*h+I[1]*he1+I[2]*he2
capture=sum(i*r for i,r in zip(I,R))+I[1]*D
thermal=H-sum(i*c for i,c in zip(I,C))-Krr-Kdr-Kce-Kff+Tcmb
escape=capture+Krr+Kdr+Kce+Kff
photo=sum(i*p for i,p in zip(I,P))+H
checks={'hydrogen_nuclei':s.simplify(dspecies[0]+dspecies[1]),'helium_nuclei':s.simplify(sum(dspecies[2:5])),'charge':charge,'energy':s.expand(thermal+dbind+escape-Tcmb-photo)}
assert all(x==0 for x in checks.values())
p=Path('/root/HE23_NCP_DENSITY_20261016/SYMBOLIC.json');p.write_text(json.dumps({'engine':'SymPy '+s.__version__,'checks':{k:str(v) for k,v in checks.items()},'scope':'stoichiometric/rate energy identities, not continuum numerical accuracy'},indent=2))
print(p.read_text())
