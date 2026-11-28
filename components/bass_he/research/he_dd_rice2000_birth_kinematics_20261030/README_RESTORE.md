# BASS_HE PR126: measured-source high-energy D-fast birth kinetic atlas

This is source-qualified Rice 2000 Table I data combined with exact relativistic 2->2 kinematics at the published **effective CM angles** and the two broad *energy supports*. The 12 recorded cross-section values remain original measurements from ONE experimental campaign. Calculated energy boundaries and energy-weighted differential cross section supports are conditional derivations, not new experiments, not a source-target photon spectrum, and not heat deposition.

Prerequisite frozen source: BASS_HE PR125 HEAD b7a3f7e7f3eb2461ff75039797c085296e575acb, parent PR124 HEAD 9696297205c2560bd8bdfc8d72b8b80b86fae8d3. Original author Table I source Git blob 9cdec4449b22bdba2797bbdfb815e98901b85636. Source PDF SHA256 0f5a390dfb31d9aa8c1066d48e5054192aa23c445aaeed1d24675a6b22f304fc (PDF not redistributed). Required Python 3.9+ standard library only.

Reproduce: `bash REPRODUCE.sh` (or `python3 src/build_rice_birth.py --root .` then `python3 -m unittest discover -s tests -v`). See `notes/THEORY_KO.md`, `notes/BLIND_REFEREE_KO.md`, `notes/HANDOFF_NEXT_THREAD_KO.md`, and `STATUS.json`. No live astrophysical rate or heat gate is promoted.
