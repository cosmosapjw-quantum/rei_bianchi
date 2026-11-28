cpuStart=TimeUsed[]; wallStart=AbsoluteTime[];
mu=m/(m+1); nu=(m+1)/(m+2); aa=mu; bb=1/(m+1); tt=m+2;
xA=xx+nu rr; xB=xx-rr/tt+aa ss; xN=xx-rr/tt-bb ss;
pA=pp/tt+qq; pB=pp/tt-bb qq+kk; pN=m pp/tt-aa qq-kk;
qi=nu pp; delta=qi-qq;
phi=Exp[-mu r];
rho2=67/200; c0=9 Sqrt[2]/20;
residuals=<|
"relative_r"->Together[xB-xN-ss],
"relative_R"->Together[xA-(xB+m xN)/(m+1)-rr],
"COM"->Together[(xA+xB+m xN)/tt-xx],
"coordinate_determinant"->Together[Det[Table[D[v,w],{v,{xA,xB,xN}},{w,{xx,rr,ss}}]]-1],
"total_momentum"->Together[pA+pB+pN-pp],
"kinetic_separation"->Together[pA^2/2+pB^2/2+pN^2/(2m)-pp^2/(2tt)-qq^2/(2nu)-kk^2/(2mu)],
"projectile_electron_separation"->Together[xA-xB-(rr-aa ss)],
"projectile_nuclear_separation"->Together[xA-xN-(rr+bb ss)],
"phase_coefficients_sum"->Together[aa+bb-1],
"finite_mass_1s_eigenvalue"->FullSimplify[-(D[phi,{r,2}]+2D[phi,r]/r)/(2mu phi)-1/r+mu/2,Assumptions->m>0&&r>0],
"matching_orthogonality"->Together[mu-(mu/kk)kk],
"lab_relative_transfer"->Together[delta-(pp-pA)],
"relative_incident_flux"->Together[qi/nu-pp],
"relative_incident_energy"->Together[qi^2/(2nu)-nu pp^2/2],
"lab_threshold"->Together[mu/(2nu)-m(m+2)/(2(m+1)^2)],
"box_volume_prefactor"->Together[(2Pi)*(2Pi)^3*(4Pi)^2/(2Pi)^6-4],
"invariant_delta_prefactor"->Together[(2Pi)^4/(qi/nu)*(4Pi/(dd^2*(2Pi)^3))^2-4nu/(qi*dd^4)],
"Jacobi_density_prefactor"->Together[(2Pi)^4*nu/qi*(4Pi/(dd^2*(2Pi)^3))^2*mu kk*nu qq-4mu nu^2 qq kk/(qi dd^4)],
"fold_change_of_variable"->Together[D[Sqrt[hh^2+cc^2-rh^2]/cc,hh]/(al hh)-1/(al cc Sqrt[hh^2+cc^2-rh^2])],
"fold_fixture_radius"->Together[1-1/4-(Sqrt[2]/10)^2/2-(9Sqrt[2]/10)^2/4-rho2],
"fold_fixture_positive_gap"->Together[c0^2-rho2-7/100],
"transverse_mass_coefficient"->Together[aa^2-bb^2-(m-1)/(m+1)],
"infinite_mass_density_coefficient"->(Limit[mu nu^2,m->Infinity]-1)
|>;
checks=Map[FullSimplify[#==0,Assumptions->m>0&&r>0&&kk>0&&pp>0&&dd>0&&al>0&&cc>rh>0&&hh>0]&,residuals];
ExportString[<|"checks"->checks,"residuals"->residuals,"count"->Length[checks],"all_true"->And@@Values[checks],"body_CPU_s"->(TimeUsed[]-cpuStart),"body_wall_s"->(AbsoluteTime[]-wallStart),"scope"->"Finite-mass channel algebra and coefficient bookkeeping only; no empirical/physical-provider admission"|>,"RawJSON"]
