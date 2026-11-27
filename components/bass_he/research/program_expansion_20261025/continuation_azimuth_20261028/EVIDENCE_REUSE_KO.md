# R2/C2 — 근거 재사용과 다음 연결

## 최신 조사와 원전

`preflight/SYNTHESIS_KO.md` 및 `SURVEY_SUMMARY.json`은 2026-10-28 05:32:27–05:33:03 KST의 관련 6repo 1,194 branch/14 terminal pages를 기록한다. 보충 조사 `SUPPLEMENT_SYNTHESIS_KO.md`는 05:38:36–05:39:42 KST에 owner의 접근 가능한 51repo metadata와 추가 VigilODE 220branch/3pages를 읽었다. 해당 cutoff 이후 push metadata가 있던 관련 7repo의 합은 **1,414branch/17pages**다. 시점이 다른 비원자적 합이며 51repo 전체 branch/history 전수 열람 수가 아니다.

`preflight/BACKUP_CONTEXT_SURVEY_KO.md`는 Library 최근 69 metadata/1 terminal page, Dropbox 선택 5폴더 4,651고유ID/10terminal pages와 Drive 범위를 기록한다. Drive dossier cap1,000/continuation 미노출과 선택 본문, Personal Context unavailable을 보존한다. 과거 archive body GET·재생성은0. 공개 요약에 private repository 이름이나 raw 계정정보를 복사하지 않았다.

새 REI ZIP 준비, WU R8, CR parent-event partial native25, BASS endpoint/KM2A/KM2B 및 VigilODE corridor 결과는 각각 현재 명시된 정의역으로 읽었다. KM2B의 두 archive identity, BASS main20/20와 추가 consolidation HOLD, CR C10 preimage와 실제 Git·backup 존재, WU 원 reference FAIL을 구분한다. 이 자료에서 HE의 세 물리 입력을 새로 닫는 payload는 확인되지 않았다. 결과는 읽은 source 범위에 관한 관측이다.

문헌 검색은 Exa1query/6results, SciSpace1question/10results, Exa primary fetch2URL을 실제 수행했다. [Arends et al., Phys. Lett. B62(1976)411–412](https://doi.org/10.1016/0370-2693(76)90671-7)는 bibliographic metadata만 확인했고 원 normalization 본문을 확보하지 못했다. [Rice et al., Phys. Rev. C61(2000)064612](https://journals.aps.org/prc/abstract/10.1103/PhysRevC.61.064612)의 APS 초록은 150–250MeV, 두 입자 coincidence, 여섯 각도의 다른 실험을 설명한다. 본문은 authorization-required였으며 이 초록에서 원 M0475002 정규화나 detector shape를 추론하지 않는다. SciSpace의 abstract는 검색 근거이며 새 운동학 정리의 증명으로 쓰지 않는다.

이전 pinned [IAEA-NDS M0475.x4](https://github.com/IAEA-NDS/exfor_master/blob/939a14d7bba1ddce51975cb5e8711ce96b3b0871/exforall/M04/M0475.x4)와 `../continuation_photon_20261027/sources/PHOTON05_SOURCE_OBSERVATIONS.json`, `../continuation_kinematic_20261028/SCIENTIFIC_INTAKE_KO.md`의 실제 읽은 BIB·단위·12행 provenance를 재사용한다. `DA/CM`, NB/SR, 통계 ERR-S만으로 full-sphere/identical-particle convention, polarization, finite-phi response가 고정되지 않는다. NIST rest-energy 예제는 native mass 값과 source hash를 유지하며 각밀도는 제조값으로 명시한다.

## 실제 재사용 의존성

| 대상 | 유지한 근거 | 이번 변화 |
|---|---|---|
| PhysicalAngularMap | KINEMATIC08 tested Local S05R d004212d560907eb4058d9539eec8e9b262ec406, remote391f1e4c356082c0b5cc693d49fb2aef873a0f2a; source SHA2567bec25c47c23cabd20a985aad8e194dcd2754814d3f38e0db5f580282b0e4bd9 | 입력A,M,e, exactsurds, fold/endpoint 처리 불변; 새 φ mask와 합성 |
| SetBounds/BernsteinDensity | APERTURE07 source SHA2561ac8ab886623178283c62910f132a364827763b8a08b417f55702fa416516b0c, 당시32/32PASS | 정확 intervalunion/intersection/적분 불변; strip 길이로 가중 |
| 5δ polar bound | KINEMATIC08 THEORY_KO.md와14/14검증 | N창·두label의 공통 불확실 집합에서10Nδ로 유도 |
| Pair energy | E±=(G±e√Rμ)/2 및 label교환 | 2D 사건C의 교환대칭을 새로 증명하여GY/GY2사용 |
| Runtime wrapper | KINEMATIC08의 percommand Git환경수정·wholeprocess측정 | 새unit별 sourcepin·12/40 validation·8/20 plot계약, 이전budget불변 |

## 다음 단위 선택

후보는 (1) exact input uncertainty boxes, (2) finite-azimuth shared-pair geometry, (3) 실제 encounter/nonthermal flux 결속이었다. (2)를 선택했다. 이미 검증된 polar map과 사건 측도에서 z-boost의 transverse antipode를 직접 이용할 수 있고, 원형 telescopes/실제 φ-law를 가정하지 않은 상태에서도 정확 선언한 기하에 대해 새 계산을 완결한다. (1)은 추가 interval-parameter topology 의무가 있고, (3)은 새 물리 provider payload가 필요하다. 새 선택은 이전 plot 실패의 repair가 아니다.

## 정책 적용과 실패의 경계

첨부 Adaptive CMB Development/Executor의 contract→physics→code→plot 감사는 이번 방정식과 observables에 맞춰 적용한다. CMB gauge/LoS 등은 이 핵분해 각도 참조의 의존성이 아니므로 새 gate를 만들지 않는다. 단순 단계 번호로 미완료 predecessor 전체를 봉쇄하는 해석은 현재 skill1.0.0의 dependency-matched reuse로 대체한다. KINEMATIC08의 과학 코드14/14는 유효 의존성이고 plot CPU FAIL은 과거 workflow partial로 보존한다.

기존 재시도·그림 예산을 새 label로 초기화하지 않는다. 새 AZIMUTH09 cap은 구현 전에 CONTRACT_KO.md에서 고정됐다. 원료 tool/metadata 비용과 science 비용은 별도이며, 준비 과정의 응답 지연·디스크 오류를 scientific repair로 세지 않는다. 정적 F01은 원주 atan2 oracle의 seam 표현을 기존 places12에서 교정한 실행 전 finding이다. 실제 suite repair reserve는 아직 미소비다.

Binding owner·thermal ports·global state는 CONTRACT_KO.md를 따른다. 새 strong no-go/문헌 신규성 주장은 없다. NG1–NG7은 해당 종류의 성과 채택에 적용되며, 이번 포함 정리와 국소 diagnostic witness를 no-go로 재명명하지 않는다.
