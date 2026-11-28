ClearAll[w, mc2, ma2, mb2, gm, b, z, t, kb, ma, mb, v, g, s, mu, sig0, e, n, ndot, tdot, theta, qth, sn];
eg=(w^2-mc2^2)/(2 w); ec=(w^2+mc2^2)/(2 w);
ph=gm eg (1+b z); tc=gm (ec-b eg z)-mc2;
tin=gm w-ma2-mb2; q=ma2+mb2-mc2;
rEvent=Factor[ph+tc-tin-q];
rShell=Factor[ec^2-eg^2-mc2^2];
va=v+mb/(ma+mb) g; vb=v-ma/(ma+mb) g;
rPair=Factor[(ma va^2+mb vb^2)/2-((ma+mb) v^2+ma mb/(ma+mb) g^2)/2];
ass={t>0,kb>0,mu>0,sig0>0,s>-2};
i1=Integrate[sig0 e^(s+1) Exp[-e/(kb t)],{e,0,Infinity},Assumptions->ass];
i2=Integrate[sig0 e^(s+2) Exp[-e/(kb t)],{e,0,Infinity},Assumptions->ass];
rate=Sqrt[8/(Pi mu)] (kb t)^(-3/2) i1;
rMoment=FullSimplify[i2/i1-(s+2) kb t,Assumptions->ass];
rDerivative=FullSimplify[i2/i1-kb t (3/2+t D[rate,t]/rate),Assumptions->ass];
uth=3 n kb t/2; p=n kb t;
energyEq=3 kb (n tdot+t ndot)/2+theta (uth+p)-qth;
tempEq=3 n kb tdot/2-qth+3 kb t sn/2+n kb t theta;
rEOS=Factor[(energyEq/.ndot->sn-theta n)-tempEq];
ExportString[<|"residuals"-><|"same_normal_frame_event"->rEvent,"product_mass_shell"->rShell,"equal_temperature_pair_factorization"->rPair,"powerlaw_event_mean"->rMoment,"rate_derivative_event_mean"->rDerivative,"temperature_number_source"->rEOS|>,"powerlaw_rate"->ToString[InputForm[FullSimplify[rate,Assumptions->ass]]],"assumptions"->"positive t,kB,mu,sigma0; s>-2; scalar pair factorization applies componentwise; exact two-body event energies w>mc2>0"|>,"JSON"]
