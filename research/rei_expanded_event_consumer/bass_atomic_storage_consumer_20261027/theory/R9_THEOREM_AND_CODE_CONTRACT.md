# R9 — 재사용 가능한 명제와 구현 계약

## Conservative finite atomic representation theorem

Fix one admitted finite effective-H transaction in common left reference volume
\(V_a=V_0\). Let \(N=(N_g,N_s,N_p,N_c)\), \(R=V_b/V_0>0\), and identify
bound H with target H1I and continuum H with target H1II. Continuum electrons
are thermal; no fast-electron channel is included.

For
\[
P=\begin{pmatrix}1&1&1&0\\0&0&0&1\\0&0&0&1\end{pmatrix},
\]
the coarse event is \(Pd\). Its nuclear-count residual is \(\mathbf1^Td\),
its HII-minus-thermal-electron residual is0, and all bound-bound transitions
map to0. The fast coordinate \(\zeta\) is unchanged.

Given source atomic event energy \(A\) already in SI and explicit target
reference \(\chi_R>0\), the application ports
\[
(\chi_Rd_c,\ A-\chi_Rd_c,\ E_{\rm rest},E_{\rm gas},
 E_{\rm ambient},E_{\alpha})
\]
have exactly the source represented total energy. The original atomic sector
is a reference, not a seventh application port. This identity preserves the
source's nonzero saved residual and original energy encoding.

With \(r_N=N_b-N_a-d\),
\[
\frac{PN_b}{Rb_b}-\frac{PN_a}{b_a}
=\frac{Pd}{Rb_b}
+PN_a\left(\frac1{Rb_b}-\frac1{b_a}\right)
+\frac{Pr_N}{Rb_b}.
\]
The full JVP is the five-term expression in R5. Proper density follows by
taking the same algebra without a baryon normalization. These are integrated
finite quantities; no \(1/H\), ddt or ddeta conversion is applied.

Proof: the rows of \(P\), cancellation of \(\chi_Rd_c\), and substitution
\(N_b=N_a+d+r_N\); full derivation R5, independent review R6, eight CAS
identities R7. Scope: exact representation of the stored source with its
inherited physical/numerical uncertainty, not a new physical enclosure.

## Function contract

- \`coarse_mapping\`: four exact Fraction coordinates, explicit fine order and
  H1 native mapping; frozen result with direct neutral sum, complement
  diagnostic and unmodified baryon residual.
- \`energy_lift\`: five exact source energies, continuum delta and declared
  target threshold. Source reference and application ports are distinct.
- \`endpoint_split\`: initial/final/event common-\(V_0\) inventories and positive
  \(R\); actual proper endpoint, event part, dilution and source residual.
- \`conditional_abundance\` and \`conditional_abundance_jvp\`: require both
  positive supplied \(b_a,b_b\), positive \(R\), explicit vector/scale
  directions. These are conditional diagnostics.
- \`consume\`: accepts only the frozen source schema and actual field order,
  reads original decimal strings without binary64 coercion, preserves source
  residual lexemes, volume/work ports and ownership.
- Runner verifies original raw bytes/source SHA256/Git blob before its one
  source parse. New14tests and one actual consume share a bounded process.

Actual recipient \(b\) and EOS/state are unsupplied. Therefore
\`actual_native25=null\`, \`temperature_update=null\`, and
\`full_state_update=false\`. Nonzero source gas energy is not discarded or
renamed. \`physical_radii\` remain null. All88originalIDs/17edges remain.
