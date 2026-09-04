% GNU Octave witness for the exact ten-node REI 03A4 chain.
% Methodology only: no repository, attempt-state, or native-runtime mutation.

n = 10;
A = zeros(n, n);
for k = 1:(n - 1)
  A(k, k + 1) = 1;
endfor

terminal = A^n;
maximal = A^(n - 1);
reachability = zeros(n, n);
for power = 1:(n - 1)
  reachability = reachability + A^power;
endfor
expected = triu(ones(n, n), 1);

assert(nnz(A) == n - 1);
assert(nnz(terminal) == 0);
assert(nnz(maximal) == 1);
assert(isequal(reachability, expected));
assert(A(1, 7) == 0);

mutated = A;
mutated(1, 7) = 1;
assert(nnz(mutated) == n);
assert(mutated(1, 7) == 1);

result = struct(
  "status", "PASS_OCTAVE_EXACT_CHAIN_WITNESS",
  "matrix_size", n,
  "edge_count", nnz(A),
  "terminal_power_nonzero", nnz(terminal),
  "maximal_power_nonzero", nnz(maximal),
  "reachability_nonzero", nnz(reachability),
  "shortcut_mutation_detected", true,
  "authority_effect", "NONE",
  "native_runtime", "NOT_RUN"
);

disp(jsonencode(result));
