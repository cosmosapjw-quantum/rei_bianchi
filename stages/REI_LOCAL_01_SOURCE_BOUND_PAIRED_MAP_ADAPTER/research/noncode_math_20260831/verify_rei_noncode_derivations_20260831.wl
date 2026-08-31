(* rei_bianchi non-coding derivation verification, 2026-08-31 *)
ClearAll["Global`*"];

residuals = <||>;

(* Public helium map *)
phi = {1 - x, (1 - x) (1 - r), (1 - x) r};
vars = {x, r};
jac = D[phi, {vars}];
phi0 = phi /. {x -> x0, r -> r0};
jac0 = jac /. {x -> x0, r -> r0};
rem = FullSimplify[Expand[(phi /. {x -> x0 + dx, r -> r0 + dr}) - phi0 - jac0 . {dx, dr}]];
residuals["public_exact_remainder"] = FullSimplify[rem - {0, dx dr, -dx dr}];
residuals["public_helium_sum"] = FullSimplify[x + phi[[2]] + phi[[3]] - 1];

(* Difference-first product identities *)
qb = (qh + qf)/2; rb = (rh + rf)/2; dq = qh - qf; dr2 = rh - rf;
residuals["heiii_product_difference"] = FullSimplify[qh rh - qf rf - (qb dr2 + rb dq)];
residuals["heii_product_difference"] = FullSimplify[qh (1-rh) - qf (1-rf) - ((1-rb) dq - qb dr2)];

(* OTS/source branch identity *)
ell = 57/40; mm = 737/1000; ww = (ell-mm) + mm yy;
aH = vv ww + (1-vv) ff zz;
aHe = vv mm (1-yy) + (1-vv) ff (1-zz);
residuals["source_photon_identity"] = FullSimplify[Expand[aH + aHe + vv (2-ell) + (1-vv) (1-ff) - (1+vv)]];

(* Normalized measure *)
hv = {h1,h2,h3}; ss = Total[hv]; qv = hv/ss;
residuals["normalized_sum"] = FullSimplify[Total[qv]-1];
residuals["normalized_jacobian_sum"] = FullSimplify[Total[D[qv,{hv}]]];

(* MPRK 3x3 column conservation and dominance *)
pmat = {{0,p12,p13},{p21,0,p23},{p31,p32,0}}; den = {d1,d2,d3};
gmat = Table[If[i != j, pmat[[i,j]]/den[[j]], -Sum[If[k != j, pmat[[k,j]]/den[[j]],0],{k,3}]],{i,3},{j,3}];
amat = IdentityMatrix[3] - hh gmat;
residuals["mprk_generator_column_sums"] = FullSimplify[Total[gmat]];
residuals["mprk_matrix_column_sums"] = FullSimplify[Total[amat]-{1,1,1}];
residuals["mprk_dominance_margins"] = FullSimplify[Table[amat[[j,j]] - hh Sum[pmat[[i,j]]/den[[j]],{i,DeleteCases[Range[3],j]}] - 1,{j,3}]];

(* Scalar implicit sensitivity identities *)
zsol[t_,u_] := bfun[t,u]/afun[t,u];
residuals["implicit_first"] = FullSimplify[afun[t,u] D[zsol[t,u],t] - (D[bfun[t,u],t] - D[afun[t,u],t] zsol[t,u])];
residuals["implicit_second_mixed"] = FullSimplify[afun[t,u] D[zsol[t,u],t,u] - (D[bfun[t,u],t,u] - D[afun[t,u],t,u] zsol[t,u] - D[afun[t,u],t] D[zsol[t,u],u] - D[afun[t,u],u] D[zsol[t,u],t])];

(* Whole thermal derivative *)
temp = Exp[xt]; npart = nfun[pp];
ueng = (3/2) kb npart temp;
qrhs = hfun[pp,xt,eta] - lfun[pp,xt,eta] - 3 hub kb npart temp;
ftherm = ueng - un - step (cc + weight qrhs);
thermalCandidate = ueng - step weight (D[hfun[pp,xt,eta],xt] - D[lfun[pp,xt,eta],xt] - 3 hub kb npart temp);
residuals["whole_thermal_derivative"] = FullSimplify[D[ftherm,xt] - thermalCandidate];

(* Hui-Gnedin template *)
lam = c0 Exp[-xx]; uu = (lam/b0)^c0p;
krate = a0 Exp[m0 xx] lam^ap/(1+uu)^dp;
s1 = m0-ap+dp c0p uu/(1+uu);
s1p = -dp c0p^2 uu/(1+uu)^2;
residuals["hg_first"] = FullSimplify[D[krate,xx]-krate s1];
residuals["hg_second"] = FullSimplify[D[krate,{xx,2}]-krate (s1^2+s1p)];

(* Excitation/ionization template *)
tt = Exp[xxx]; qq = Sqrt[tt/t0]; kex = aa tt^pow Exp[-ee/tt]/(1+qq);
sex = pow+ee/tt-(1/2) qq/(1+qq);
sexp = -ee/tt-(1/4) qq/(1+qq)^2;
residuals["exc_first"] = FullSimplify[D[kex,xxx]-kex sex];
residuals["exc_second"] = FullSimplify[D[kex,{xxx,2}]-kex (sex^2+sexp)];

(* Alexander SDIRK2 order condition *)
gamma = 1 - 1/Sqrt[2];
residuals["sdirk_order2"] = FullSimplify[(1-gamma) gamma + gamma - 1/2];

zeroQ[expr_] := TrueQ[FullSimplify[expr] === 0] || TrueQ[FullSimplify[expr] === {0,0}] || TrueQ[FullSimplify[expr] === {0,0,0}];
status = Map[zeroQ, residuals];
Print[ExportString[<|"schema"->"rei-noncode-math-verification/v1","status"->status,"all_pass"->And@@Values[status]|>,"RawJSON"]];
If[And@@Values[status], Exit[0], Exit[1]];
