# H/He/Li 최신 source intake

관측 시각: 2026-10-21 15:00:43 UTC. 4개 repo의 branch refs **798개**를 끝까지 pagination했고, 관련 5개 tree는 truncation 없이 조회했다. 모든 historical branch 파일을 전부 읽었다는 뜻은 아니다. 실제 회수한 source **38개**는 Git blob SHA1이 모두 일치한다. 세부 pin·SHA256은 `SOURCE_BINDINGS_VERIFIED.json`, 판정은 `REMOTE_HHELI_INTAKE.json`에 있다.

## 실제 새 결과

- PR198 HEAD `8bd35af5f11c7ea5945b656be1c013d1c1933498`, PR199 HEAD `cce008b3fc32c298185b30550b2cd909d74fcd87`: 보존. AGE HOLD와 production NOT_ISSUED 유지.
- REI217 `de73c5d6c7bd3498571e9226298040d8259e1acf` / BASS179 `d14652646c1da77b6513e7f97725ff5dd5c1db4e`: ACCEL03 warm 5-case/729-endpoint 분석. fullEoR 새 계산이 아니다.
- HE31 `88e415c45d8607c85cd3ab36aabeaed4378820ce`: H/He prescribed-electron on/off와 reference의 z20→4 결과 summary를 회수. donor support는 z4까지만이다.
- **진행 중 HE32 branch가 갱신됨**: 첫 snapshot의88e415에서 `e8bb035d31f59e34734947b9082bdbd60128b799`로 전진했다. 새 compact transport와 independent review가 실제 존재한다. **HHeLi chemistry는 아직 pending**이다.

## 즉시 재사용할 코드

`HE32_source/`는 source의 디렉터리 구조를 보존한 import-ready 사본이다. `src/compact_transport.py`, `evidence/BASELINE_MANIFEST.json`, vendor5개를 포함한다. 별도 실행이나 benchmark는 하지 않았다.

L8 finite hierarchy의 정확한 reflection-even 부분공간으로 원40-state에서23-state가 된다. Photon/neutrino energy/number 4towers를 유지하고 closure 차수를 바꾸지 않는다. 원격 independent record는 z20→2의 weak constant-ne와 strong collisionless 두 original/compact pair를 PASS_SCOPED_COMPACT_OPTIMIZATION으로 기록한다. review JSON의 source hash는 `0fa826025836a0126fac580de98e3b45c9dcc750e1e243afe933c249ae8e4b6c`이며 회수한 source와 일치한다. finite parity를 전구간 truncation theorem으로 승격하지 않는다.

질량분포는 mass/Tref30, fraction0.1의 **비바리온성 warm massive component**다. 새 H/He/Li 원자 chemistry와 동일한 입자집단이라고 해석하지 않는다. 바리온 전자밀도만 Thomson collision argument로 연결할 경우 그 한 방향 결합을 명시한다.

## 저온 Li의 실제 source

`R9_verner_photo.dat`와 `verner_ferland_rr_table1.dat`에 HI/HeI/HeII/LiI/LiII/LiIII의 실제 fit rows가 있다. Verner–Ferland 공식 저자 페이지 https://www.pa.uky.edu/~verner/rec.html 를 열어 RR fit의3K~1e9K 범위를 확인했다. 따라서 root가 고른100~10^4K는 범위 내다.

Root의 유한 UV5~60eV는 LiI PH2 fit의64.39eV 상한 이내다. LiII/III 문턱은75.64/122.5eV이므로 해당 광이온화0은 선언한 광원 cutoff의 결과다. RR는3개 모두 유지한다. RR 표의 라벨은 **생성물**: LiI행은 LiII→LiI, LiII행은 LiIII→LiII, LiIII행은 LiIV→LiIII다. HeI b는 기존 rrfit 선택과 일치한다. TotalRR에 groundMilneRR를 다시 더하지 않는다.

RUN19는 기존 PR150의 Li6/Li7 CI/RR/DR number-only 코드를 그대로 보존한다. 하지만 CI 포함 공통 온도 하한은 약58,022K이고, 실제검증도 제조한밀도에서 coefficient/number contribution scan뿐이다. trajectory0, whole gas/radiation0이다. 이 번들을 IGM 저온에 그대로 투입하지 않는다.

## 미완료 범위를 보존

`isotope_state.rs`는 n/H/D/T/He3/He4 13species bookkeeping일 뿐 rate가 없고 Li도 없다. `RUN19_full_network.rs`는 H/He/D finite initial photon pool의 split step으로, expansion/birth/Li가 없다. `RUN19_target_network.json`의 광핵반응·beta·Li핵반응들은 unresolved native coupling이다. 21상태 원자 photo+totalRR pilot을19핵반응 전체 완료로 부르지 않는다. R5 BBN donor도 z≈4.26×10^6 bare-Be7 source여서 z20조성으로 직접 사용하지 않는다.

## 다음 DAG와 게시

이 intake는 read-only이다. 다음 노드는 root의21species 원자모형 physical contract와 독립검토이며, 구현자는 HE32 source를 재사용한다. root가 새 독립 REI branch에 additive publication/백업을 수행한다. prior lane 검증·계산은 반복하지 않았다.
