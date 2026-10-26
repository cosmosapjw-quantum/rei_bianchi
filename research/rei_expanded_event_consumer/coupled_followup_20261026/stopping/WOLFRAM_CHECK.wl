ClearAll["Global`*"];
nd={f0-f1,f1-f2,f2};ph=-f0;
ud={e0,e1,e2}.nd+{v0,v1,v2}.{n0,n1,n2};
ih=(cut-e0)*ph+(e1-e0)*f1+(e2-e1)*f2+{v0,v1,v2}.{n0,n1,n2};
cc=3 nt/2;hh=3 th/2;cut2=kap th;ce=cc-kap*(cut2-hh)*nc;
td=(-(cut2-hh)*jc-ii)/ce;ph2=kap*td*nc-jc;
checks={Expand[Total[nd]+ph],Expand[ud+cut*ph-ih],Together[cc*td+hh*ph2-(cut2*ph2-ii)],Expand[(ww+del)+(en-bn-ww+del)+(bn-del)-(en+del)],Expand[(en+del)-(ww+del)-(en-bn-ww+del)-(bn-del)],Expand[(ue+del*ne)+(ui-del*ni)-(ue+ui)-del*(ne-ni)],Expand[(uep+del*ph)+(uip-del*ph)-(uep+uip)]};
fixture={ud,ih,ph,cut*ph-ih}/.{e0->2,e1->4,e2->7,n0->5,n1->6,n2->7,v0->1/10,v1->1/5,v2->3/10,f0->-2,f1->3,f2->-1,cut->1};
thermal={ce,td,ph2,cut2*ph2-ii}/.{th->1,kap->2,nt->10,nc->1,jc->3,ii->4};
<|"residuals"->checks,"all_zero"->And@@Thread[checks==0],"finite_volume_fixture_Udot_I_Phi_Ureservoir"->fixture,"thermal_fixture_Ceff_thetadot_Phi_Ureservoir"->thermal,"native_tagged_pair"->{30+57/10000,57/10000,30-136057/10000+57/10000,136/10},"singular_example_Ceff"->(ce/.{th->1,kap->2,nt->2/3,nc->1})|>
