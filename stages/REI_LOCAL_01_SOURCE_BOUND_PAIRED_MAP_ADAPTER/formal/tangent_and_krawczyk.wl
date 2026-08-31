(* Exact rational cross-check; no numerical physics claim. *)
ClearAll[assert, a, r, x1, x2];
assert[condition_, label_] := If[TrueQ[condition], Null,
  Print["FAIL: " <> label]; Exit[1]];

A[t_] := {{2 + t, 1}, {1, 3 - t}};
b[t_] := {1 + t, 2 - t};
z0 = LinearSolve[A[0], b[0]];
dz = LinearSolve[A[0], (D[b[t], t] /. t -> 0) -
    (D[A[t], t] /. t -> 0).z0];
wrong = LinearSolve[A[0], D[b[t], t] /. t -> 0];
assert[z0 == {1/5, 3/5}, "locked solution"];
assert[dz == {14/25, -8/25}, "full tangent"];
assert[wrong == {4/5, -3/5} && wrong =!= dz, "delta-A counterexample"];

fullRhs = {-7, 3};
terms = {{1, 2}, {11, 7}, {8, 5}};
bvf = {13, 17};
assert[bvf - Total[terms] == fullRhs, "mixed RHS all products"];
assert[LinearSolve[{{2, -1}, {-1, 1}}, fullRhs] == {-4, -1},
  "mixed solution"];
assert[LinearSolve[{{2, -1}, {-1, 1}}, fullRhs + terms[[1]]] == {-1, 4},
  "omit Avf mutation"];
assert[LinearSolve[{{2, -1}, {-1, 1}}, fullRhs + terms[[2]]] == {14, 24},
  "omit Av mutation"];
assert[LinearSolve[{{2, -1}, {-1, 1}}, fullRhs + terms[[3]]] == {9, 17},
  "omit Af mutation"];

C2 = 1/3 {{2, 1}, {1, 2}};
w = {-3/4, -3/8};
xbox = {{-9/4, 3/4}, {-9/8, 3/8}};
corners = Tuples[{{3/2, 5/2}, {-3/2, -3/4},
    xbox[[1]], xbox[[2]]}];
kvals = Function[q,
    aa = {{q[[1]], -1}, {-1, 2}};
    bb = {q[[2]], 0}; xx = {q[[3]], q[[4]]};
    w - C2.(aa.w - bb) + (IdentityMatrix[2] - C2.aa).(xx - w)
  ] /@ corners;
khull = Transpose[{Min /@ Transpose[kvals], Max /@ Transpose[kvals]}];
assert[khull == {{-7/4, 1/4}, {-7/8, 1/8}}, "2x2 Krawczyk hull"];
assert[{khull[[1, 1]] - xbox[[1, 1]], xbox[[1, 2]] - khull[[1, 2]],
        khull[[2, 1]] - xbox[[2, 1]], xbox[[2, 2]] - khull[[2, 2]]} ==
       {1/2, 1/2, 1/4, 1/4}, "2x2 strict margins"];

x3 = {{-9/8, -1/8}, {-1/2, 0}, {-1/4, 0}};
k3 = {{-245/256, -75/256}, {-49/128, -15/128},
      {-49/256, -15/256}};
assert[And @@ Flatten[MapThread[{#1[[1]] < #2[[1]], #2[[2]] < #1[[2]]} &,
    {x3, k3}]], "3x3 strict inclusion"];
assert[{k3[[1, 1]] - x3[[1, 1]], x3[[1, 2]] - k3[[1, 2]],
        k3[[2, 1]] - x3[[2, 1]], x3[[2, 2]] - k3[[2, 2]],
        k3[[3, 1]] - x3[[3, 1]], x3[[3, 2]] - k3[[3, 2]]} ==
       {43/256, 43/256, 15/128, 15/128, 15/256, 15/256},
  "3x3 strict margins"];
Print["PASS exact tangent/mixed/Krawczyk arithmetic"];
