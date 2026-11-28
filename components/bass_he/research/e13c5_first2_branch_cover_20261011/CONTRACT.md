# HE_E13C5_FIRST2_PATH_CONTRACT01

This is a transcription of the Astra frozen contract.  It authorizes only the
immediate 12-path branch-cover experiment; the full first2 target remains
`HOLD_RESOURCE_AUTHORIZATION`.

Base: BASS_HE PR18 `48f648cd905cd8c232ae43abe97745ac6a96dec2`, tree
`b9a0ba328c8b6534849a601318574bd862f6aefe`.  Write only beneath
`research/e13c5_first2_branch_cover_20261011/`.

Sources: E13C4 ZIP
`/home/cosmosapjw/Dropbox/BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_E13C4_LOCAL_REMAINDER_ENCLOSURE_20261010_sha_5498d936ee7d.zip`,
SHA256 `5498d936ee7d25b1322c6c4bb3b15315e6c31e4ec148076fe1682d068dc8fc67`;
recovery SHA256 `fbf8cd26e87cdffe83f236d4bc646b2c6ffab9a4ac408b83b1fef09ec7d72020`.
Within BASE, helper hashes are local_enclosure.py
`fade8983b7db8974c479ac4473424b7d572e8f7a0f09c042669fb3c40c32e370`,
directed_interval.py `ce4a44b11d1c0a3a5c52861033fa817a587bca9a5b852fab48329213b9a732e5`,
SIX_CONTROLS `2f543b128bdb6efe020868475619765d1a08f47c102cf0b9e5f65cb615c146dd`.

Selector: modes OFF/KF/GM; nodes 0/700/1620/2344; keys (1,0),(2,0),(2,1).
There are 36 selected segments: reuse reviewed OFF/700 records, calculate 33
segments across the other 11 paths.  Node meanings are lower source switch,
HeI threshold, HeII threshold, upper source switch respectively.  All selected
captured rows have h>0, L>0, zero outflow.  Reject unexpected L=0, h=0, or
outflow.  Source-off uses captured q=0 and retains incoming stock.

Use unchanged E13C4 interval helpers, N=128, Decimal precision 60, serial.
For first segment I_a=[0,0]; later I_a=previous_Pend-captured_f0, keyed by
(mode,node) across stage seams.  Let S=sup(abs(I_a))+B_r.  Use inherited J_X
and response/remainder formulas exactly as pilot.py: C_X=J_X+g_X I_a+[-R_X,R_X],
with g_P=exp(-Lh), g_A=lambda*j0, g_B=lambda*jE,
g_H=lambda*(jE-chi*j0), g_Z=jE, g_QN=g_QE=0.  Do not add a second incoming
radius.  For L>0: F_N=f0*j0+q*(h-j0)/L and
F_E=f0*jE+E0*q*(J_h(1)-J_h(L+1))/L.

Use P_f=f0 exp(-Lh)+q j0; frozen A=lambda F_N, B=lambda F_E,
H=lambda(F_E-chi F_N), Z=F_E, QN=q h, QE=E0 q J_h(1); Pend=P_f+C_P.
Lift captured erg to eV with binary64-lift epsilon=1.602176634e-12 exactly once.
Every adjacent seam, including anchored=false, has J_anchor=(nextE0-currentE0
exp(-h))*Pend.  Every segment/path prefix, each step and whole path must have
count ledger Pend-Pinitial+sum A-QN and anchored-energy ledger
Eend Pend-Einitial Pinitial+sum B+Z-QE-sum J_anchor containing zero.

Weight every endpoint/moment/source/anchor by exact lifted captured positive
weight.  Aggregates are selected-subset only; never compare full AGGREGATE.csv.
Store separately continuous-minus-frozen, frozen-minus-captured, captured
segment-to-node reduction, weighted reduction, and epsilon*Eend*Pend-u_captured.

Acceptance: A01 exact identities/no duplicate or missing keys; A02 exactly
36=3 reuse+33 new and all transition classes; A03 finite ordered intervals
and inherited domain; A04 chronological carry; A05 all stated ledgers include
zero; A06 representation separations; A07 rational control and invalid branch
rejections; A08 raw accounting; A09 fresh Astra review.  Only inclusion is an
acceptance criterion; no new relative/physical/sharpness threshold. Display
floors retain 1e-25 number and 1e-24 eV.

Exact rational control: two paths, stocks 1,2; weights 1,3; two source-off
constant-opacity segments L=1,h=ln2,T=1/2; anchors 8->4 and 6->3; chi=1.
Expected weighted final stock 7/4, absorbed count 21/4, B=231/8, Z=231/8,
anchor=7; ledgers exact zero.  Omit anchors gives energy residual 7; resetting
second carry gives count residual -7/2; swapping carries/dropping weights fails.

Limits: one new primary invocation, 11 new paths/33 new segments, 180s,
1024MiB, N128/p60/serial; controls aggregate <=60s; native/gas/old continuous/
six-control/full-first2 all zero.  One Astra-approved repair/re-run max, total
new science <=360s.  Preserve first failure; no automatic refinement/substitution.
Scope PASS is only finite enclosures for the 12 selected captured paths under
fixed gas/masks/source branches/anchors.  Physical, production, full first2,
new gas evolution, actual photon/heat/recoil, receiver adoption remain HOLD.
