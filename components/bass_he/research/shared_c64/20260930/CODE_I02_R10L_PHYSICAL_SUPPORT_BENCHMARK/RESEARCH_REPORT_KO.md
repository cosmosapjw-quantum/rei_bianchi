# BASS_HE R10L: author reproduction 이후의 물리적 support 검증 설계

R10K는 구현 재현을 닫았지만 물리모델 선택은 닫지 않았다. Author lane A가 Appendix-A를 잘 재현하는 것은 분산된 ARSENY 구현의 REAL support를 복제했기 때문이다. Appendix-A를 REAL 대 EXTENDED 물리 선택의 기준으로 다시 사용하면 순환적이다.

현재 source 상태:
- author code / Appendix-A: REAL support
- CPC Eq.(52): EXTENDED support
- 물리적 우월성: unresolved

Wolfram sensitivity에서 hard cutoff b에 대해 d sigma/db = 2 pi b P(b)다. 따라서 경계에서 전이확률이 0이 아니면 support 선택은 직접 cross section을 바꾼다. 다섯 branch의 EXTENDED/REAL 기하학적 disk-area ratio는 약 2.31--14.44다.

독립 benchmark:
- Stolterfoht et al. PRA81 (2010), DOI 10.1103/PhysRevA.81.052704: Library full PDF, n=1,2,3, 30 eV/u 이상, 0.5와 5 keV/u 모두 포함.
- Liu et al. HSCC PRA67 (2003), DOI 10.1103/PhysRevA.67.052705: n=2, Ecm 10 eV--4 keV. He2+ on H에서는 Ecm=0.8 EkeV/u이므로 두 project energy를 모두 포함.
- Minami et al. JPB41 (2008), DOI 10.1088/0953-4075/41/13/135201: 약 1--1000 keV/u, 5 keV/u cross-check.

다음 비교:
A = locked author REAL+frozen reproduction control.
B = dynamic Delta(rho)+factor2+printed EXTENDED+straight/CPC rotation.
C = B와 동일하지만 support만 REAL.

C는 support-only diagnostic이며 production 후보가 아니다. REAL--EXTENDED 사이 alpha fitting은 금지한다.

Benchmark 수치는 model 값을 보기 전에 provenance, digitization calibration, uncertainty를 고정한다. 허용 verdict:
EXTENDED_SUPPORT_EXTERNALLY_SUPPORTED_IN_SCOPE,
REAL_SUPPORT_EXTERNALLY_SUPPORTED_IN_SCOPE,
PHYSICAL_SUPPORT_UNRESOLVED,
SUPPORT_NOT_DOMINANT_EXTERNAL_DISCREPANCY.

Gates remain CODE_I02_CLOSED=true, full_certificate_fail_closed=true,
scientific_PROMOTE=HOLD, Eq55_next_node_authorized=false, Eq55=NOT_RUN.
