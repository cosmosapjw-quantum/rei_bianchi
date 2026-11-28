Module[{z,r,a,m11,m12,m21,m22,ll,uu,v,d,rr,b,L,U,h,k,fp,zeros,trues},
v[x_]:={1,x,x^2};d={2,2/3,2/5};rr=17/20;b={rr^2,-2rr,1};L=9/25;U=9/16;
h=v[1/4]-(L/U)v[1/10];k=d/4+h/2+v[rr]/3;
fp[x_]:=U(x-1/4)^2-L(x-1/10)^2;
zeros=Flatten[{
Expand[{a*r^2,-2a*r,a}.v[z]-a(z-r)^2],
Expand[uu(r^2-2m11*r+m12)-ll(r^2-2m21*r+m22)-((uu*m12-ll*m22)+(-2uu*m11+2ll*m21)r+(uu-ll)r^2)],
fp[rr],fp[4/5]+999/160000,fp[9/10]-1161/160000,
Expand[D[fp[r],r]-(81r/200-837/4000)],
h-{9/25,93/500,561/10000},h.b,v[rr].b,d.b-427/600,
k-{76/75,543/1000,22133/60000},k.b/(d.b)-1/4,
Expand[D[(z-rr)^2,z]/.z->rr]
}];
trues={0<rr<1,L>0,U>0,fp[4/5]<0,fp[9/10]>0,d.b>0,1/2>=0&&1/3>=0,rr-rr^2>=0,Det[{{1,rr},{rr,rr^2}}]==0,b[[2]]<0,1/10<3602879701896397/36028797018963968,Min[Table[(81r/200-837/4000)/.r->x,{x,{4/5,9/10}}]]>0};
<|"unit"->"HE-EXP-TANGENT-13","zeros"->zeros,"true_controls"->trues,"all_zero"->And@@Thread[zeros==0],"all_true"->And@@trues,"scope"->"generic polynomial and manufactured exact certificate controls; no previous campaign rerun"|>
]
