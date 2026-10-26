# Frozen state reader after donor restoration

The restored `grid044_history.npz` has the pinned SHA256 ae20c278239787c020e45028a6d6804cb9f056b75076a1d5ab045c0a7389733b and supplies eta[201], physical `atomic_abundance_per_Href[21,201]`, labels[21], and temperature_K[201]. `SNAPSHOT_READER_CONTRACT.json` fixes the executable input representation. This addendum supersedes the earlier pending-data statements in `INPUT_BINDING.json` and `SNAPSHOT_NORMALIZATION.md`; actual evaluated snapshot values remain pending the delegated bounded execution.

At eta*=ln(21/3.479), bracket the adjacent saved knots eta_k and eta_{k+1}, set theta=(eta*−eta_k)/(eta_{k+1}−eta_k), and form x*=(1−theta)x_k+theta x_{k+1} and T*=(1−theta)T_k+theta T_{k+1}. An exact saved knot uses its stored column. This explicitly selected finite representation preserves nonnegativity and positive temperature. For every isotope selector row c, c·x*=(1−theta)c·x_k+theta c·x_{k+1}; hence equal endpoint isotope counts remain equal exactly in real arithmetic. No assumption that unequal endpoint totals are equal is used. The main execution records the two totals and the interpolation identity. The continuum interpolation error remains unspecified, so this is a source-qualified saved-donor counterfactual snapshot rather than a newly solved cosmological trajectory.

Read physical per-Href abundances, then permute by labels and normalize with beta=A·x*, n_b=beta r, Y=x*/beta. The preserved r law and original H/b interpolants remain as derived. Interpolating normalized Y columns separately would define a different representation when beta changes; the specified order avoids that ambiguity. Existing donor UV fields and photo rates are context and are not substituted for the selected PW19 source. No source-epoch derivative is supplied by this snapshot.

For arbitrary dimension N and beta>0, differentiation gives D=(I−Y A^T)/beta. Since A^T Y=1, A^T D=0 and D x=0. Let P=beta D=I−Y A^T. Direct multiplication yields P²=I−2Y A^T+Y(A^T Y)A^T=P. Thus D maps every physical perturbation into the tangent plane A·deltaY=0 and removes pure scaling directions in x. This is a normalization property, not a physical gauge identification: the removed scaling still changes n_b and SI rates. Retaining delta n_b=beta delta r+r A·delta x gives

    delta(n_b Y)=(beta delta r+r A·delta x)Y+beta r D delta x
                =x delta r+r delta x.

For fixed reference r the reconstructed physical-density variation is exactly r delta x. This proves the correct full Jacobian pullback without assuming that the perturbation preserves the inventory. A supplied fixed-inventory direction A·delta x=0 is its simpler special case.

Remote Wolfram independently returned zero for the direct normalized Jacobian difference, A·D, D·x, projection idempotence, and reconstructed density JVP in a generic three-component symbolic representative. The dimension-independent proof is above. Its context lookup failed with an internal error; the evaluator emitted an undefined-M warning but returned all requested exact zero arrays. Both raw statuses are preserved in `WOLFRAM_PROJECTIVE_MAP.json`; remote CPU remains UNKNOWN_NOT_ZERO. No local scientific calculation was run by this lane.

The finite reader's positive exit is the actual source-qualified REC callback with bounded state/JVP/energy controls. The original V6 native client, continuous REC-HISTORY reference and L4 feedback/refinement gates remain unchanged; no extra review loop is introduced.
