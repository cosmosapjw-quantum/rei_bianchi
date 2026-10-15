# R9 NCP microphysics research loop

This additive research package continues the eight-job program against rei_bianchi PR150 commit54dd5352672127e77970eb06f3dda027f2aee275. It contains actual NCP calculations, not merely launch instructions. The full eight-job physical project is not closed.

## Unit1 completed

On NCP hostname s1a0e5abed09 (64 logical CPUs,125GiB RAM), execute all-electron nonrelativistic finite-Gaussian FCI atomic targets, common-basis sudden projections, neutral LiH/LiHe ground-state Born-Oppenheimer curves with counterpoise, and bounded nuclear/cascade/inventory/source calculations. Full raw receipts and CI/RDM arrays are in the archive below.56 solver receipts include53 successful finite-model calculations and3 preserved failures; repairs are running as Unit2. The193 bridge checks and6 microphysics/backend/SCF tests passed on the actual NCP host. These are implementation checks, not complete-basis error bars.

## Physical interpretation

The Li-only contracted common basis gives He-to-Li+ ground survival.4672820372 at aug-DZ and.7167028695 at aug-TZ. This large change diagnoses an inadequate basis; do not use either as a converged physical probability. Balanced parent+daughter basis unions and Li-to-Be+ three-electron projections are Unit2.

At LiHe R=11.5a0, cc-DZ raw attraction changes to CP repulsion+5.5109086e-6Eh. A low-temperature reaction rate cannot be inferred from an unconverged ground-state curve. LiH aug-DZ R=3a0 has V_CP=-.0861078210Eh. Ionic/excited channels, couplings and nuclear scattering remain separate work.

The projected Li dipole response is a finite Gaussian pseudostate calculation, not a physical continuum cross section. BBN-to17 is a conservative inventory and conditional charge map, not an evolved recombination history. Nuclear anchor sensitivity is not a fitted posterior. E1 cascade shell mixtures contain physical line energies but no recombination injection weights or2s two-photon spectrum. Source moments are conditional on the declared50000K blackbody shape and reference photon flux.

## Raw backup

Unit1 archive: REIONIZATION_R9_UNIT1_FCI_BO_BRIDGE_20261015.tar.gz

- Bytes:14974254
- SHA256:3b354154d8f460ecaedaeb6fc506c2f4a70ba4c20e704b606989ecf8366d1dde
- [Google Drive](https://drive.google.com/file/d/1wz1d0fGfqH_UJY4XdOVwnQ7VZpWGESHO/view)
- Dropbox:/BASS_DERIVATION_DOSSIERS_20260912/REIONIZATION_R9_UNIT1_FCI_BO_BRIDGE_20261015.tar.gz

Read the contracts, versioned code, review records and actual per-case receipts before promoting a result. Source versions remain immutable. Unit2 will add balanced-basis/core-correlation calculations, exact two-electron treatment above the64-orbital bitstring limit, dissociation SCF-initializer repairs and128-step projected response.
