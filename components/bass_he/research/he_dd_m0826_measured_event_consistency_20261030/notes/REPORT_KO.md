# BASS_HE | 측정 M0826 총단면적–각도분포 사건 계수 정합성

- 2026-10-30 pinned PR121 HEAD: `ea1e7968636aae6200c26a0377159736d009cee0`.
- 원본 EXFOR M0826 angular 9 measured bins (`CURVE`) + SIG 4 reported total bins (`TABLE`); M0011 old 14 source totals. 원본 신규 측정 행 0, source-derived comparative result 1.
- 적분 원자료 `I_DA=5.430601681837213 μb`; daughter-counting 가정의 단일 사건 `I_DA/2=2.7153008409186064 μb`; 원본 30–40/40–50 SIG 폭 가중평균 `2.705 μb`; 비율 `2.007616148553498`; 사건 기준 상대 차 `0.3808074%`.
- source ERR-S 독립 **가정**일 때 event angular SD `0.351295329671934 μb`, SIG 평균 SD `0.456097577279248 μb`; actual joint covariance UNKNOWN. Arbitrary correlation upper 0.968326 and 0.645 μb respectively. Photon intensity systematic ≤5% (M0826001).
- Born/event-rate/heating not inferred. Photon flux history, detector acceptance, original event definition, Rice full numeric data unresolved; Whitton 1993 explicitly states its cross-section angular dependence only, not absolute.
- Targeted Python 12/12 tests PASS; compileall PASS; independent Wolfram summation numerical match. Distinct-author native R6/C9 NOT_RUN; no old IVPs or 4501-node LP reruns.
- DAG Central 28/88, HE Physical 14/18, new scoped 2/2; `physical_delta=0`, `R_event=null`, `heat_rate=null`, `kappa=null`, `L4=false`, `production=HOLD`.

Original science sources: M0826 (Arkatov et al. 1972, YF16,12; SNP16,6), M0011 (Arkatov et al. 1978, UFZ23,918), Whitton et al. PRC48 2355 (1993), Rice et al. PRC61 064612 (2000). Git input: IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871.