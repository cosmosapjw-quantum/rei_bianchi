# Failure log

1. Baseline coarse k12 rejected `3.812277937532397e-309` as nonnormal. Audit proved that this was a positive HI heat term, not incoming stock. The local heat repair resolved it.
2. After k12/24/12 passed, coarse k13 accepted and k14 returned `negative photoheat`, with total counts `[41862,135052,14]`. The isolated k14 cell showed that the shared energy integral had already become subnormal before multiplication by opacity: `B_HI=8.049173728942649e-317`, threshold term `8.124533561902814e-317`.
3. One local repair reassociated only the subnormal/zero `B_i` route so opacity scales the terms before their final subnormal projection. The NORMAL route remains bit-identical. The same k14 then reached `paired readout requires extended material path`, counts `[5,4,1]`.
4. A clean checkpoint copy reproduced the paired-readout failure once, also `[5,4,1]`. No further retry or partial scalar workaround was attempted. The required next change is a coherent paired node N/E representation through weighting, accepted density, observer and checkpoint.

The first negative failure remains in `numeric/repair-coarse-12-48.log`; the paired failures remain in the later logs and copied run failure JSON. Original numeric checkpoints and historical failure JSON files are unchanged.
