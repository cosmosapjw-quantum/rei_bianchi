ClearAll[nu,z,w,chi,theta,H,R,n,r,x,C,Q,cv,B,h,dnu,dz,dw,dchi,dtheta,dH,dn,dr,dR,dC,dQ,dB,dx];
fa=nu*(w/theta-z)/chi;
qa=nu*w;
ja=nu*z;
checks=<|"assimilation_caloric_energy"->FullSimplify[theta*(chi*fa+ja)-qa],"assimilation_number"->FullSimplify[-ja+ja],"assimilation_total_energy"->FullSimplify[-qa+theta*(chi*fa+ja)],"assimilation_directional_derivative"->FullSimplify[(D[(nu+h*dnu)*((w+h*dw)/(theta*Exp[h*dtheta])-(z+h*dz))/(chi+h*dchi),h]/.h->0)-((dnu*(w/theta-z)+nu*(dw/theta-w*dtheta/theta-dz))/chi-fa*dchi/chi)],"compton_regular_quotient_derivative"->FullSimplify[(D[(x+h*dx)*(B+h*dB)/((H+h*dH)*(chi+h*dchi)),h]/.h->0)-((B*dx+x*dB)/(H*chi)-x*B/(H*chi)*(dH/H+dchi/chi))],"reference_expansion_cancellation"->FullSimplify[cv*((R-3*H*r)*chi*theta+r*((C-chi*R)/r)*theta+r*chi*theta*(-2*H+(Q/(cv*theta)-C)/(r*chi)))+3*H*(cv*r*chi*theta+(2/3)*cv*r*chi*theta)-Q]|>;
checks
