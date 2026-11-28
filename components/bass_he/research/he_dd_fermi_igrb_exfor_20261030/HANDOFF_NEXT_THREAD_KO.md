# BASS_HE | 관측 Fermi 고에너지 감마선 × EXFOR DD 자료 다음 스레드 인계

```ini
$physmath-research-loop $scispace $exa $wolfram
PROJECT=cosmosapjw-quantum/BASS_HE
CURRENT_PR=116
CURRENT_HEAD=READ_GITHUB_LATEST
PARENT_PR=115
PARENT_HEAD=b271023c9fe6a9c87cd96cc2561c7d1f7bf8e0ed
SIBLING_LOW_E_PR=114
SIBLING_LOW_E_HEAD=0646448a551b4669def04e5176e6b851d870ce03
BRANCH=research/he-dd-fermi-igrb-exfor-observed-photons-20261030
ROOT=research/he_dd_fermi_igrb_exfor_20261030
CENTRAL_DAG=28/88
HE_DAG=14/18
HIGH_E_MEASURED_DATA=2/2_SCOPED
LOW_E_E2_SIBLING=3/4_SCOPED
NEW_GAMMA_SOURCE_DAG=2/4_SCOPED
PHYSICAL_DELTA=0
NEW_STAGE_PUBLICATION=20/20_ACTUAL_GIT
INDEPENDENT_R6_C9=NOT_RUN
NATIVE_SUBAGENT=NOT_RUN
kappa=null
R_event=null
heat_rate=null
physical_activation=false
L4=false
production=HOLD
```

## 확인/복구 우선순위
1. GitHub PR116 및 PR115 현재 Draft/Open HEAD 확인, 원본/부모 commit identity 잠금. 부모 코드 및 원본 데이터는 불변.
2. ROOT의 THEORY_KO.md, REPORT_KO.md, STAGE_LEDGER.json, HANDOFF_NEXT_THREAD_KO.md, data/*, src/build_igrb_exfor.py, tests/test_igrb_exfor.py, results/*를 읽고 비교하라. 모든 핵심 6개 원격 Git blob와 로컬 파일 byte identity는 이전 세션 확인됨.
3. 인계 ZIP에는 본 PR116의 데이터/소스/테스트/결과 및 **이전 PR115 ZIP nested copy** 포함된다. ZIP manifest/CRC, nested PR115 ZIP SHA256 a07c1a8e2e622a58822fee5e17736b1c89cf959886b63dd66e2dbd4cde92529b 확인. Fermi 출판물 원본과 upstream 원본 EXFOR x4 바이트는 이 ZIP 자체에 포함되어 있지 않으며 source provenance/remote 원본은 Git에서 검증해야 한다. 이 패키지를 온전한 upstream raw archive라고 하지 말 것.
4. 새 12개 targeted tests와 새 자료 계산만 재실행: `python -m unittest discover -s tests -v`, `python -m compileall -q src tests`, `python src/build_igrb_exfor.py --root . --out results/IGRB_EXFOR_LOCAL_DIAGNOSTIC.json` + `--mode flat_within_bin` (별도 결과 파일). 201–359 MeV 외삽하지 않음. 기존 IVP/4501-node LP 재실행 금지.
5. 2015 IGRB/EGB 두 bin 데이터는 원 출판 논문의 인간 전사 데이터라 출판물 원본 byte-source-lock이 아니다. IGRB와 EGB를 합산하지 말 것. 실측 적분 flux에서 모델별 intra-bin spectral shape와 six-point EXFOR interpolation를 분리 유지할 것.
6. 다음 물리 연구: (i) Arends 1976 원문 detector efficiency/acceptance/polarization + event vs inclusive 정규화, (ii) He 대상 고유계의 실제 z,t,x 200–400MeV 광자장 공급자 및 K-correction/attenuation/anisotropy, (iii) physical sigma_event with uncertainty, (iv) source-specific D_fast slowing/redistribution/secondary ionization, escape, heat plus real C_V. Fermi observed local scale을 330 MeV gamma cosmological history라 부르지 말 것. 연구 노드 완료 조건 증거 도착 전 original Central 28/88, HE14/18 유지.
7. Drive stage log ID 1h9nlgSQBMR4Gt_BuVRrg-S4vzACMvm4cam-MS9rgVSY 20/20 TEXT readback, Dropbox Paper id:BSpOijBcT10AAAAAAEHV6g 20/20 TEXT readback. Binary full ZIP independent dual-cloud download/readback은 따로 검증해야 하며 이 스레드에서 자동 충족이 아니다. Merge Draft/force-push 없음.
