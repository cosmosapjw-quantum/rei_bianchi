ClearAll["Global`*"]; kb=1380649/10^29; ev=1602176634/10^28; me=91093837139/10^41; ep=88541878188/10^22; hh=662607015/10^42; cc=299792458;
temp=14994847774798709/10^12; ne=5996197830412253/10^15; ll=20; theta=kb*temp/ev;
gam=4*Pi*ne*(ev^2/(4*Pi*ep))^2*ll/me^2;
b0[en_]:=me*gam/(ev*Sqrt[2*ev*en/me]);
fun[x_]:=Erf[Sqrt[x]]-2*Sqrt[x]*Exp[-x]/Sqrt[Pi];
diff[en_]:=theta*b0[en]*fun[en/theta];
drift[en_]:=b0[en]*(4*Sqrt[en/theta]*Exp[-en/theta]/Sqrt[Pi]-Erf[Sqrt[en/theta]]);
ens={11/1000,theta,136/10,134476/1000};
debye=Sqrt[ep*kb*temp/(ne*ev^2)];
sphere=(3/(4*Pi*ne))^(1/3);lambda=hh/Sqrt[2*Pi*me*kb*temp];
<|"constants"-><|"me_kg"->N[me,18],"eps0"->N[ep,18],"e_C"->N[ev,18]|>,
"EE_coefficients_E_drift_eV_s_diffusion_eV2_s"->N[Table[{en,drift[en],diff[en]},{en,ens}],18],
"Debye_electron_m"->N[debye,18],"Debye_electron_sphere_occupancy"->N[4*Pi*ne*debye^3/3,18],"classical_coupling"->N[ev^2/(4*Pi*ep*sphere*kb*temp),18],"degeneracy"->N[ne*lambda^3,18],"theta_over_mec2"->N[ev*theta/(me*cc^2),18]|>
