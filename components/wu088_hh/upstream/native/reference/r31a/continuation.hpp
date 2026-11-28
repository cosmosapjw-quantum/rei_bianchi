// Isolated research candidate; include after original hypergeom_wide.
// Existing source files remain untouched.
static int continuation_seed(R a,R b,Z z,Z& out){
 Z term(1,0),sum(1,0),correction(0,0);const R eps=std::numeric_limits<R>::epsilon();
 for(int k=1;k<=1024;k++){
  term*=z*((a+k-1)/((b+k-1)*k));Z y=term-correction,updated=sum+y;correction=(updated-sum)-y;sum=updated;
  if(k+a>0){R q=std::abs(z)/(k+1)*fmaxl(1,(k+a)/(k+b));if(q<1&&std::abs(term)*q/(1-q)<=eps*std::abs(sum)/4){out=sum;return k;}}
 }return -1;
}
static int boys_continue(R n,Z x,Z& out){
 Z at(x.real(),copysignl(2,x.imag())),f,raw;
 int status;
 if(at.real()<0){status=continuation_seed(n+.5L,n+1.5L,-at,raw);f=raw/(2*n+1);}
 else{status=continuation_seed(1,n+1.5L,at,raw);f=std::exp(-at)*raw/(2*n+1);}
 if(status<0)return -1;
 const R eps=std::numeric_limits<R>::epsilon();int terms=0,steps=0;
 while(at.imag()!=x.imag()){
  R remaining=x.imag()-at.imag(),step=copysignl(fminl(fabsl(remaining),fminl(2.L,.35L*std::abs(at))),remaining);Z h(0,step),ratio=h/(R(2)*at);
  Z term=f,forcing=std::exp(-at),sum=f,c=0;R recent[4]={1,1,1,1};bool converged=false;
  for(int k=0;k<192;k++){
   term=ratio*(forcing-(2*R(k)+2*n+1)*term)/R(k+1);
   Z y=term-c,updated=sum+y;c=(updated-sum)-y;sum=updated;terms++;
   forcing*=(-h)/R(k+1);recent[k%4]=std::abs(term);
   if(k>8&&recent[0]+recent[1]+recent[2]+recent[3]<eps*std::abs(sum)/64){converged=true;break;}
  }
  if(!converged)return -2;f=sum;
  if(fabsl(step)==fabsl(remaining))at=x;else at+=h;
  if(++steps>128)return -3;
 }
 out=f;return terms;
}
static int hypergeom_cont(R a,R b,Z z,Z& out){
 if(fabsl(z.imag())<=2)return continuation_seed(a,b,z,out);
 if(a==1){Z f;int rc=boys_continue(b-1.5L,z,f);out=(2*b-2)*f/std::exp(-z);return rc;}
 if(a==b-1){Z f;int rc=boys_continue(b-1.5L,-z,f);out=(2*b-2)*f;return rc;}
 Z at(z.real(),copysignl(2,z.imag())),f,fp;
 int it=continuation_seed(a,b,at,f);if(it<0)return -1;
 Z derivative;if(continuation_seed(a+1,b+1,at,derivative)<0)return -1;fp=(a/b)*derivative;
 const R eps=std::numeric_limits<R>::epsilon();int terms=0,steps=0;
 while(at.imag()!=z.imag()){
  R remaining=z.imag()-at.imag();R step=copysignl(fminl(fabsl(remaining),fminl(2.L,.35L*std::abs(at))),remaining);Z h(0,step);
  Z alpha=h*h/at,beta=h/at,t0=f,t1=fp*h;
  Z sum=f,sc=0,der=0,dc=0;
  auto add=[](Z term,Z& sum,Z& c){Z y=term-c,updated=sum+y;c=(updated-sum)-y;sum=updated;};
  add(t1,sum,sc);add(t1,der,dc);bool converged=false;R recent[4]={1,1,1,1};
  for(int n=0;n<192;n++){
   Z next=((n+a)*alpha*t0-R(n+1)*(R(n)+b-at)*beta*t1)/(R(n+1)*(n+2));
   add(next,sum,sc);add(R(n+2)*next,der,dc);terms++;
   recent[n%4]=std::abs(next)*(n+2);
   if(n>8&&recent[0]+recent[1]+recent[2]+recent[3]<eps*fmaxl(std::abs(sum),std::abs(der))/64){converged=true;break;}
   t0=t1;t1=next;
  }
  if(!converged)return -2;
  f=sum;fp=der/h;
  if(fabsl(step)==fabsl(remaining))at=z;else at+=h;
  if(++steps>128)return -3;
 }
 out=f;return terms;
}
