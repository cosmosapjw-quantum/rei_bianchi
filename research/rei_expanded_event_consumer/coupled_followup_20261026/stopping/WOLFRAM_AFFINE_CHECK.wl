ClearAll["Global`*"];
cc=3 nt/2;hh=3 th/2;c=kap th;
ce=cc-kap*(c-hh)*nc+ell;td=(-(c-hh)*jj-i0)/ce;ph=kap*td*nc-jj;ia=i0+ell*td;
iph=kap*z*nc-j0;ih=(cut-e0)*iph+(e1-e0)*(j1-s1*z*t1)+(e2-e1)*(j2-s2*z*t2)+z*(r0*n0+r1*n1+r2*n2);
iv0=-(cut-e0)*j0+(e1-e0)*j1+(e2-e1)*j2;
lv=(cut-e0)*kap*nc-(e1-e0)*s1*t1-(e2-e1)*s2*t2+r0*n0+r1*n1+r2*n2;
checks={Together[cc*td+hh*ph-(c*ph-ia)],Expand[ih-iv0-lv*z],Expand[(cut+del-(e0+del))*iph+(e1+del-e0-del)*(j1-s1*z*t1)+(e2+del-e1-del)*(j2-s2*z*t2)+z*(r0*n0+r1*n1+r2*n2)-ih]};
<|"residuals"->checks,"all_zero"->And@@Thread[checks==0],"affine_fixture_Ceff_thetadot_Phi_Iactual_Ureservoir"->({ce,td,ph,ia,c*ph-ia}/.{th->1,kap->2,nt->10,nc->1,jj->3,i0->4,ell->2})|>
