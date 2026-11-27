u=100;v=1/10^8;mat={{2u-v/3,v/3},{2v/3,-4u-2v/3}};out=MatrixExp[N[mat,100]].{0,1};N[out,60]
