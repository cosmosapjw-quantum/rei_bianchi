# rei_bianchi 확장 연구 헌장 — 2026-10-25

rei_bianchi는 선택한 우주론적 시나리오의 source·absorber·environment 조립, 결합 보존식과 관측량, 저장소 간 DAG와 실제 수신 기록을 책임진다. 대상은 동일한 확장 catalog의 모든 선택 원자핵·동위원소·이성질체·이온·음이온·분자·상태이며, 인접 stellar/galactic/IGM/AGN/CMB/CR/핵·약반응 기원의 photon/electron/baryon 공급과 방출·흡수도 포함한다. 전체 장기 범위를 과거 H-only 또는21population에 고정하지 않는다.

공유 species/elementary reaction compiler의 lead는 **WU088_HH**다. 현재 `REI-CHEM-LEDGER-01` 이름과 중앙 staging 위치는 이력이며, 재사용 가능한 compiler의 소유권을 뜻하지 않는다. 이번 중앙 검증 완료 뒤 WU가 같은 검토된 source identity를 import하고 공통 species/isotope/isomer/elementary atomic·molecular·nuclear·weak channel interface를 유지한다. REI는 선택 시나리오에 이 provider를 소비하는 event assembly를 소유한다. 코드 복제나 두 물리 owner를 만들지 않는다.

공동 역할은 다음과 같다.

- WU088_HH: nucleus/species identity, microscopic reaction channels, branching, reaction-energy inputs.
- rec_bianchi: state-resolved atomic/ionic/molecular spectroscopy·populations, recombination과 bb/fb/ff emission/absorption, radiative transport/history.
- BASS_HE: differential collisions와 finite-mass/angular energy-momentum exchange, thermalization와 particle-count/heat-capacity closure.
- bass_cr: 외부 nonthermal photon/electron/baryon injection, distributions, cascade/stopping/secondary production.
- bass: geometry/background, covariant energy-momentum coupling, native receiver/cohort transport와 domain-qualified stress/four-force.
- vigilode: integration/domain/failure/native gateway/error-control evidence.
- rei_bianchi: 시나리오 선택, 실제 provider/환경/흡수자 결속, 통합 보존과 관측량.

현재 확인한 n/H1/D/T/He3/He4/Li6/Li7의21population은 초기 catalog다. 새로운 `(Z,A,isomer)`·molecular composition·signed charge·state·collider·electron pool은 source discovery, 구현, 검증, 수신 admission 상태를 별도로 갖는다. 계산된 한 finite channel의 PASS를 전체catalog 또는 부모목표 완료로 승격하지 않는다. Missing physical input은 UNQUALIFIED이며 실제 supported zero와 다르다.

원40계약·17edge·7authority, L0/nativeHI/stress/strain와 ANGTHERM 완료자료 및 실패·누적비용을 보존한다. 중앙c5050305…의 REI `PROPOSED` 상태는 원계획 snapshot으로 남기고 최신 source-backed 관측을 덧붙인다. PR2218d10231…는 read-only; conditional ANGTHERM02 leaf 완료와 전체 continuum-angular 목표 OPEN을 함께 유지한다. GRID044 opacity의 Library-only18/18reportedPASS는 optional finite provider 관측이며 새 전체 결합 완료가 아니다.

원시 photon moment Γ/P/K는 같은 observer/measure/normalization으로 사용해야 한다. Photon sink−P, stored ionization+χΓ, primary-electron+K를 한 번씩 배정하며 K 전체를 heat로 바꾸지 않는다. 25×23 target/source-template Jacobian은 그 지정 변수의 local derivative이며 전체 photon/thermal/geometry Jacobian을 대체하지 않는다. 실제 source history·birth cohort·density/IC·frame/clock과 소스별 불확실성이 연결되기 전 L4_ready=false다.

새 실행은 해당 단위의 동결된 과학 입력·acceptance·예산이 있을 때만 수행한다. 본 새 REI future nodes의 실행예산은 null이다. 이미 별도로 승인된 compiler30CPU/120wall/512MiB는 해당 단위에만 적용한다. L0 historical overrun, whole debit UNKNOWN_NOT_ZERO, GRID044 main NO_MORE_IVPs와 기존83cohort 재사용을 유지한다. 새 scope를 정했다고 기존 allowance가 재설정되지 않는다.

정규화 명시: 기본 Nref는 comoving volume에 고정된 bookkeeping 수이며 nref=nref0*a^-3이다. 실제 H·동위원소·바리온 수가 주입·핵변환으로 변해도 기준을 같이 바꾸지 않는다. dot(n_s)+3H*n_s=S_s이면 dot(x_s)=S_s/nref다. 물리적으로 변하는 기준을 별도로 택해 dot(nref)+3H*nref=Sref인 경우 dot(x_s)=(S_s−x_s*Sref)/nref와 그 미분을 사용하고 Sref를 명시한다.
