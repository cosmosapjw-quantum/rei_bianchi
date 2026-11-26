"""Cold-plasma vacuum validity diagnostic on actual accepted history."""
from pathlib import Path
import numpy as np,json,hashlib
D=Path(__file__).resolve().parent
P=D.parent/'r118c3i_event_ledger/native/history.csv'
E=1.602176634e-19;EPS=8.8541878128e-12;ME=9.1093837139e-31;HBAR=1.054571817e-34;KB=1.380649e-23
def cutoff(ne,T):
 return HBAR*np.sqrt(ne*1e6*E**2/(EPS*ME))/(KB*T)
def dos(x,xp):
 x=np.asarray(x,float)
 if np.any(x<=0):raise ValueError('positive frequency')
 return np.sqrt(np.maximum(0,1-(xp/x)**2))
def run():
 r=np.genfromtxt(P,names=True,delimiter=',');x=cutoff(r['ne'],2.7255/r['a'])
 o=dict(source_sha=hashlib.sha256(P.read_bytes()).hexdigest(),rows=len(r),ne_range_cm3=[float(r['ne'].min()),float(r['ne'].max())],xp_range=[float(x.min()),float(x.max())],frequency_Hz_range=[float((x*KB*(2.7255/r['a'])/(2*np.pi*HBAR)).min()),float((x*KB*(2.7255/r['a'])/(2*np.pi*HBAR)).max())],vacuum_dos_ratio_at_2xp=float(dos(2.,1.)),vacuum_dos_ratio_at_10xp=float(dos(10.,1.)),removed_RJ_number_fraction_max=float(x.max()**2/(4*1.202056903159594)),removed_RJ_energy_fraction_max=float(5*x.max()**3/np.pi**4),scope='cold transverse dispersion cutoff; RJ vacuum asymptotic inventory below xp; no dispersive collision operator or propagation claim')
 (D/'PLASMA.json').write_text(json.dumps(o,indent=2)+'\n');print(o)
if __name__=='__main__':run()
