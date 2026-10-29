# REI↔BASS source-qualified physical-charge binding preflight | 2026-10-29

**권고 상태:** `PASS_SCOPED_SOURCE_INVENTORY_OBSTRUCTION_AND_PHOTO_ONLY_LUMP` / `PHYSICAL_BIND=BLOCKED_SOURCE_MISMATCH` / independent R6,C9 `NOT_RUN`. 새로운 IVP 없음. 원 REI working **33/88**, central **28/88**, physical delta **0**, F4 PARTIAL, L4 false. 이번 단위 이론·코딩 **18/20 scoped**만 별도 계수한다.

## 실제 조사 범위

REI PR264 HEAD `7067a0e73743ce9fb3a07c81bc4207188129985a`와 부모 PR263/262, BASS PR234, BASS PR247, BASS_HE PR108, CR PR121, REC PR156, WU R22 PR160, VigilODE PR109, HTT PR564를 최신 관련 PR 메타데이터/HEAD 수준에서 대조했다. 관련 repo의 모든 branch/PR 원문을 전부 읽은 전수조사는 아니다. 대화 검색은 최신 handoff와 일치했고 더 새로운 REI 물리 입력이 확인되지는 않았다. 다른 저장소 결과는 동일 source/clock/chemical state를 제공하지 않아 물리적 import하지 않는다.

이번에는 단순 PR 설명 재사용을 넘어 **BASS PR234 원본 ZIP(222443 bytes)과 REI PR262 원본 ZIP(162333 bytes)을 Google Drive에서 실제 재다운로드**하고 SHA-256 및 CRC를 확인했다. BASS의 `atomic_model.json`, `atomic_network.py`, `coupled.py`, `compact_system.py`, REI의 실제 7×17 ON_refined 선택 상태를 전부 원문 byte SHA로 확인했다. 재포장된 자료의 CRC는 원본 ZIP 전체의 물리 정확도를 증명하지 않는다.

## 물리·수학 결과 1: source-pinned mismatch

BASS full62는 T⁰/T⁺를 포함하지만 BASS pilot `T/H1=0`이며 compact33/reduced30은 nonzero T initial을 `NEED_FULL62`로 거절한다. REI 7개 ON_refined 상태는 모두 T⁰/T⁺가 양수이므로, 동일한 초기 구성에서 이 둘을 곧바로 잇는 물리 동일성은 없다. 특히 BASS 고정 He4/H1=0.08112582781456953, REI 저장 He4/H1=0.08193182602307137~0.08197162942407441. 비율은 공통 양의 밀도정규화로 바뀌지 않는다.

임의 `ρ>0`로 H1과 He4 inventory를 동시에 맞추려 할 때의 정확한 상대 minimax:

`A=N_H1^REI/N_H1^BASS, B=N_He4^REI/N_He4^BASS`,

`ρ*=2/(A+B)`, `δ*=min_{ρ>0} max(|Aρ−1|,|Bρ−1|)=|A−B|/(A+B)`.

7개 저장 상태의 `δ*`는 **0.00494302591465216 ~ 0.00518586631468634 (0.494303%–0.518587%)**다. 최적 `ρ*`는 0.813053396832~0.776763873973이나 물리적으로 확인된 `nHref/n_b`가 아니다. T_B=0 versus T_REI>0 문제는 이 유한 상대 minimax에 합쳐 계산하지 않는다.

이 결과는 **두 특정 조건부 pilot source/보존 isotope inventory의 불일치**이고, 우주의 실제 동위원소비에 대한 관측 판정도, 일반 Bianchi 모델에 대한 보편적인 no-go도 아니다. 서로 다른 pilot의 값이 다른 것은 수치 오류의 증거가 아니다.

## 물리·수학 결과 2: 성립하는 positive source-only closure

동일한 H1/D/T `Γ_H`, He3/He4 공통 `Γ_I`, `Γ_II`, 7개 광이온화 사건, source-only로 보존되는 각 동위원소 총량을 명시하면 다음 aggregate 4-state RHS는 정확하다:

`ḣ=Γ_H (N_H−h),  ṗ=Γ_I(N_He−p−d)−Γ_II p,  ḋ=Γ_II p,  ṫ=Γ_H(N_T−t)`.

광원천만의 Jacobian 고유값은 `−Γ_H`(2중), `−Γ_I`, `−Γ_II`이고 simplex에 대해 positivity-preserving이다. `ρ(x)`가 변하면 반드시 `(ρ_x/ρ)` 항을 포함한다. 이 부분은 Puchwein 7-source 이벤트의 algebraic reduction이고, 실제 BASS의 `G0=UV*_Gphoto`, recombination `Gne`, decay `D` 및 전자 feedback과 동일한 forward model은 아니다.

BASS original `atomic_network.py`는 실제 전체 21-state Jacobian **operator expression** `J_B=G0+D+n_e Gne+n_b(GneY)q_B^T`를 갖는다. 이 항등식은 전자 feedback을 분명히 보존하지만, 본 ZIP에는 donor native rate coefficient tables와 `lrs_boltzmann` authority가 없어 실제 수치 `J_B(t)`를 재구성하지 않았다. REI full chemical Jacobian도 별도로 미결이다.

## 코드/검증과 실패 복구

- Python 현재 세션 **32/32 PASS**, 그중 200개 exact Fraction minimax witness, 200개 random source-only photo lumping, 7 saved raw source identities, time-dependent density-ratio chain rule, invalid negative domains, T-branch and Li6/fast missingness 검사 포함.
- C++20 독립 long-double 7/7 PASS, 최대 상대 차 `5.8194815209046552188e−18` (stored Decimal65 reference 대비), 새 IVP 없음.
- Wolfram 1차 Module symbol warning이 있었으나 수정된 독립 입력에서 minimax/He closure exact residual `{0,0,0}`를 반환했다.
- 첫 Python 28개 검사에서 byte-tamper negative test가 target filename을 SHA key로 쓰는 결함을 포착했다 (`KeyError: tampered.json`). source-role key로 고쳐 28/28 통과한 뒤 4개 명시적 폐쇄·고유값·simplex 검사를 추가, 32/32로 종료했다. 입력·허용오차를 바꾸지 않았다.
- GitHub 초회 공개원본은 파일읽기 종료 개행 1바이트가 유실되어 Git blob mismatch. 이 결함을 실제로 감지하고 exact trailing LF로 수정·재검증했다. 역사적 오류와 수리 이력은 유지한다.
- 완성한 두 개의 7-point save-only 플롯을 직접 읽었다. 점마다 비교 증거이고 연속 우주론적 경로가 아니다.

## 현재 claim gate

`BASS_REI_PHYSICAL_CHARGE_BIND`는 **현재 두 pilot 동일 source에는 REFUSED/INPUT_CONFLICT**. 이전 PR264 전하 관측 대수항등식은 변함없이 유효하나 생산 BASS reduced30의 source-qualified forward 동역학으로 승격되지 않는다. Li6의 REI 숨김 charge state, T/fast reservoir, 동일 정규화·initial inventory, 완전 `J_y`, nHref/nb,H,K, Bianchi directional redshift는 여전히 미결이다. BASS photo rates와 Puchwein rate를 동일하다고 해석하지 않는다.

**최소 다음 물리 조치:** 서로 다른 pilot source를 교체하지 말고, 실제 REI/BASS owner가 합의한 **동일 초기 isotope inventory·공통 rate/electron-pool 정의**를 source로 제공하는 정적 source-scope 계약을 먼저 구성하고, 이를 통해 21→17→6 event/charge commutator를 실제 행렬로 검사하라. `NO_MORE_IVPs=true` 조건에서 전체 물리적 `D_a τ` 적분이나 CMB observable, native solver run은 하지 않는다.

## 백업/게시

원본 BASS/REI SOURCE ZIP들은 과거 Drive 객체에서 이번 세션 실제 raw readback+SHA+CRC를 확보했다. 새 산출물은 독립 GitHub Draft PR로 게시하고 단계별 20개 stage checkpoint를 유지한다. 새로운 master ZIP은 ChatGPT Library와 로컬에 저장하며, 새 Drive/Dropbox 전체 ZIP 업로드는 각각 실제 반환이 확인된 경우에만 완료로 기록한다. 인지되지 않은 준비·호스트·네트워크 비용은 `UNKNOWN_NOT_ZERO`이고 기존 closed 예산은 재할당하지 않는다.
