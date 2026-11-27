# BASS_HE | M0826 event-consistency 후속 인계

```
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
PARENT_PR=121
IMMUTABLE_PARENT_HEAD=ea1e7968636aae6200c26a0377159736d009cee0
NEXT_NODE=SOURCE_OWNED_RICE_1998_ABSOLUTE_DD_COINCIDENCE_TABLES
AUTO_NEXT_NODE=false
NO_MERGE=true
NO_FORCE_PUSH=true
PRODUCTION=HOLD
CENTRAL_DAG=28/88
HE_PHYSICAL_DAG=14/18
```

1. 현재 PR과 HEAD는 GitHub에서 live read first. 새 child는 PR121에서 분기된 source-exact M0826 본문을 포함한다.
2. 원본 IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871 M0826 original Git blob `95010842754215e98eea8d99eff5f3de0799c666` / M0011 `20804471fb7584e07ab979ecad6a3e96cba0c6a2`.
3. Direct physical consistency: 9 measured angular DA rows integral 5.430601681837213 μb; half-event 2.7153008409186064 μb; mean original SIG 30–50 comparison 2.705 μb; ratio 2.007616148553498. Source-defined CURVE/TABLE and statistical vs systematic uncertainty kept separate; covariance, energy weighting and detector calibration UNKNOWN.
4. New physical evidence is source-derived 1 normalization consistency witness, no new original experiments, no rate/heat, no source-exact reciprocal capture event rate admission. Central 28/88, HE 14/18, physical delta=0, scoped 2/2.
5. Next actual physics: Rice 1998 doctoral thesis direct absolute six-angle two-energy photon disintegration tables and coincidence efficiencies (full PDF scan may be visually readable; first locate original tables), Rice 1995 master's quantitative tables, Arkatov 1972 event-counting definitions and independent detector normalization. Alternatively compare primary measured M0011 high-quality SIG overlap without assuming calibration independence.
6. Need actual He-rest gamma occupation/phase-space, D_fast stopping and energy deposition, gas heat capacity before `R_event` or `heat_rate` becomes populated. New scripts must leave those null until scientifically qualified.
7. Restore ZIP, verify SHA256 and manifest then run 12 unit tests. Independent native R6 and C9 remain NOT_RUN. No prior IVP/LP repeat.
```