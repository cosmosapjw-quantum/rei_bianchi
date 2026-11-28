"""Bounded independent r_min, r_max and mesh sensitivity of isotope BO ΔE/k_B."""
import argparse,csv
from pathlib import Path
from .native_pes import NativePES,build
from .rovib import RadialGrid, MU_HD,MU_H2,K_PER_EH,energy_levels
GRID=[(.5,.015,16),(.5,.01,16),(.5,.0075,16),(.5,.005,16),(.5,.00375,16),(.4,.005,16),(.6,.005,16),(.5,.005,12),(.5,.005,20),(.7,.005,16)]
def main(out):
 p=NativePES(build());data=[]
 for lo,dr,hi in GRID:
  g=RadialGrid(r_min=lo,r_max=hi,step=dr)
  Ehd=energy_levels(p,MU_HD,range(1),1,g)[(0,0)];Eh2=energy_levels(p,MU_H2,range(1),1,g)[(0,0)]
  data.append({'r_min_a0':lo,'r_max_a0':hi,'step_a0':dr,'HD_Eh':Ehd,'H2_Eh':Eh2,'endothermic_threshold_K':(Eh2-Ehd)*K_PER_EH})
 with Path(out).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),lineterminator='\n');w.writeheader();w.writerows(data)
 print(f'Grid sensitivity rows={len(data)}; baseline rmin0.5/dr0.005={(data[3]["endothermic_threshold_K"]):.9f} K; rmin0.7/dr0.005={(data[-1]["endothermic_threshold_K"]):.9f} K')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);q=a.parse_args();main(q.out)
