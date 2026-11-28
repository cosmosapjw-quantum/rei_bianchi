# HE32 시작 전 최신 upstream 조사

관측 종료: 2026-10-21 23:47 KST (14:47 UTC). 기존 HE31 완료본 PR84 `88e415c45d8607c85cd3ab36aabeaed4378820ce` 이후 델타와 이번 H/He/Li isotope 요청에 맞춘 실제 source를 확인했다. 외부 repo 수정·게시, 새 과학 적분, benchmark는 각각 0회다.

## 구현을 결정하는 결론

조사한 최신 결과에서 **실제 모든 H/He/Li 핵종·이온의 z20→2 donor**는 발견하지 못했다. 기존 full-interval 그림은 collisionless 물질/복사 부문이고, 원자화학 donor는 다른 상태·시간 구간을 가진다. 따라서 HE32가 새 원자·동위원소 모델을 만들면 source/초기조건/반응 범위를 새 identity로 고정하고 끝까지 실제 실행하는 것이 적절하다.

재사용 가능한 실물은 충분하다. HE31 prepared-FV moment + electron receiver, REI PR211의 Li6/7 전자계수와 13-state isotope ledger, 공식 자료를 연결하는 PR151 Li photo/Milne/total-RR 코드, 본문 19반응 원문 계약을 확보했다. 이들은 별도 물리 입력이므로 한 묶음의 완료된 coupled network라고 부르지 않는다.

## 실제 조사 범위

GitHub owner catalog 51개를 읽고 관련 여섯 repo의 **1,060개 전체 advertised branch head**를 `git ls-remote --heads`로 SHA와 함께 저장했다. Connector의 branch-name pagination도 REI/BASS/CR/HH/HE에 대해 빈 terminal page까지 완료했다. 각 30개씩 REI, BASS, CR, HH, HE, VigilODE PR, REC15개를 더해 recent PR metadata195개와 atomic PR150/151/175를 추가로 읽었다. PR210/211/199/217 등 관련 changed-file lists를 확인하고 원문25개를 회수했다. **25/25 Git blob SHA와 로컬 바이트가 일치한다.**

| repo | head 수 | 최신 관련 항목 |
|---|---:|---|
| rei_bianchi | 258 | PR217 ACCEL03, PR199 D9, PR211 RUN19 atomic |
| bass | 264 | PR179 ACCEL03 |
| bass_cr | 172 | PR95/94 offgrid4 sandbox/NCP |
| WU088_HH | 141 | PR132 PHYS77, PR130 z20→2 1231 |
| BASS_HE | 89 | PR84 HE31 그대로 |
| rec_bianchi | 136 | PR118 tangent 준비, PR117 z20→2 reuse |

브랜치 이름/head 전수와 모든 브랜치의 파일 본문 전수는 다르다. PR150 changed-file API는 3,000개 제한에 닿았으므로 그 tree 전체 조회로 기록하지 않는다. 대화·백업은 다른 조사자가 맡으며 여기서 그 접근 범위를 주장하지 않는다. 공개 Git 접속은 기본 sandbox proxy 연결 실패 후 승인된 읽기 전용 network escalation으로 성공했다.

## HE31 이후 실제 델타

| 출처 | 고정 head | 실제 내용 | HE32 채택 |
|---|---|---|---|
| HE84 | 88e415c45d8607c85cd3ab36aabeaed4378820ce | HE31 현재 동일 | 기존 receiver/prepared kernel |
| REI217 | de73c5d6c7bd3498571e9226298040d8259e1acf | ACCEL03 portable aggregation, NCP5 수용, 729 endpoint 재사용 | 재사용/그림 provenance 패턴, 새 full EoR donor 아님 |
| BASS179 | d14652646c1da77b6513e7f97725ff5dd5c1db4e | ACCEL03 동시 게시 | 동일 연구 중복계수 방지 |
| REI199 | cce008b3fc32c298185b30550b2cd909d74fcd87 | eb8042 이후 4커밋/111파일: D8 reconciliation, D9 성분 shear budget | 175 저장 궤적 해석; 새 화학 적분 없음 |
| CR95 | Git 실제 ref 8dc5031b3323d4be42a7444843294200aa8887f2; PR metadata e7729092… | z20→4 opposing-stress4 sandbox + 같은4 NCP 반환 수용 | 고유129, 같은 입력 두 호스트 중복합산 금지 |
| HH132 | d43cf2df2c4864ae05049f44301c5b389b80a49c | 유한-owner whole-cell enclosure 및 runner | 준비·수학 근거, full isotope EoR 아님 |
| REC118 | 99f5f4fb57358a0347286f8299977125a2724774 | full40 JVP/VJP,160-state tangent; tiny2회 | fullz2 sensitivity3개 READY_NOT_SUBMITTED |

REI217의 NCP5는 a=.1999→.2, 각2step이고 원래 gates40개를 통과했다. 전체 z20→2 진화가 아니다. 기존 729case와 47,385행 raw의 lineage도 유지한다. REI199 D9는 175 nominal grid×153저장 epoch에서 0 IVP/0 moment recomputation으로 성분 적분인자 budget을 계산했다. 이 delta에는 새로운 z2 H/He/Li chemistry source가 없다.

HH130 `535d24dbccf4fab40fd11f36330a63c4e288e24c`의 1231 z20→2 결과는 REI198 collisionless finite-owner closure다. 초기 signed half norm S∈[-.004,.004], Pm∈[-.0004,.0004], Pr∈[-.001,.001]이고 Frobenius는 sqrt2배다. HE31/HE32 Frobenius축과 half축을 수치 그대로 혼합하지 않는다. REC117 `77b71c7d…`는 기존175의 저장 trajectory 축 response 재사용이며 새 ODE0이다.

## 원자·핵종 소스와 빠진 의존성

### PR211 RUN19: 실제 Li source와 isotope ledger

현재 head `c9deb933761a8d2593d1176aee028cd423bdbc05`, 과학 source `e540256ecf77df1c88fccb57b81d5d60110f367c`. `metals/upstream/rei_bianchi/rust/rei_microphysics/src/lithium_rates.rs`는 PR150 원문 `fd9a21c4d3886a495540b51d780a83b608e72ea2`에서 가져온 SHA256 `10e4db3fa5bd9a4c2dca5c4bfd7fc7fa6a3fa4bbe83862c25b5c4e1a7ba4d629`다. 실제 원문, 3개 parameter rows, README, provenance 및 thermal contract를 회수했다.

Li q=0..3 adjacent chain을 Voronov CI, Badnell RR/DR로 구성한다. stable6Li/7Li는 명시적 elemental-electronic-equality approximation을 선택해야 한다. 이 source는 isotope-resolved atomic coefficient를 공급하지 않으며 Li8/9는 decay daughter closure가 없어서 거절한다. 전체 rates bundle의 공통 Tmin=5eV/kB≈58022K라서 cold IGM에 그 bundle을 그대로 사용하면 domain 오류다. 각 RR channel은 별도 저온 domain을 갖는다. Source-bound 저온 대안을 선택하거나 추가 유도 없이 이 guard를 지우지 않는다.

원 isotope_state.rs는 n, H1I/II, DI/II, TI/II, He3I/II/III, He4I/II/III의13상태, proper SI density, baryon/charge/free-electron count를 구현한다. 원 Li 두 isotope의8상태를 합치면21heavy species다. 이 ledger가 특정 nuclear reaction rate나 초기 abundance를 자동 부여하지는 않는다. Li source contribution에는 thermal energy 및 photo source가 없고, global electron source는 caller에서 한 번만 소유한다.

### 원 그림의 19반응

`metals/network/TARGET_NETWORK_19.json`은 원 네트워크 그림1856861bytes, SHA256 `472ba6be633d2b5fc05fc1e0e88f965ff3c0311b0697e3c35c05bbca1629e6f9`의 오른쪽19반응 목록을 전사했다. 일부 왼쪽 arrow label과 식이 다르므로 오른쪽 식을 authority로 삼았다는 원 기록을 유지했다. 이번 누락 첨부가 바로 이 byte인지 직접 대조한 것은 아니다.

원 전사: H/He 3photo/RR, He4 gamma→He3+n/T+p/D+D, He3 gamma→D+p, D gamma→p+n, T beta decay, n beta decay, Li7 gamma→He4+T, pn capture, Dp capture, DDpT, DDnHe3, TDnHe4, He3DpHe4, He3npT, T-alpha gammaLi7. 선택한 RUN19 native lineage에서 핵반응4–19 coupled implementation은 미완료라고 명시한다. Li6은 이19식에 없으므로 새 요청의 isotope coverage를 확장할 때 추가 의무다.

전체 RUN19 보존본: Dropbox `id:BSpOijBcT10AAAAAAD_SVw`, Drive `1pRPhitdAFfEU8HrSC02uXXVXwRI1U8wk`, 25,344,988bytes, SHA256 `6421ead745f3e5d298286e13b9515b7f668dcbb72de11b9f86650021c92b4f62`. 이번 agent는 해당 archive를 다시 다운로드하지 않았다.

### PR150/151/175

PR150 current `fd9a21c4…`의 native root lib.rs와 current AXBI source를 읽었다. AXBI source는 여전히4≤z≤20 guard를 갖는다. Full005의 초기 기록은 z20→4다. 일부 이후 recovery FINAL_STATUS는 completed-binding check 실패를 보존하며, 원 full history completion과 후처리 실패를 구분해야 한다. PR150 파일 목록 cap 때문에 모든 full005 binary history를 다시 회수하지는 않았다.

PR151 current `8a4f5df46f6e3058f5e685b85cc1cf3c20926368`에서 `unit8_remaining_bridges_20261016/code/li_thermal_rates.py`를 회수했다. Verner photo/Milne/totalRR selected ground-channel reference이며6개 ratechannel18quadrature 비교를 보고한다. 기존 Li thermal IVP는 독립 BDF failure로 kinetics HOLD 상태이므로 그것을 검증완료 donor로 채택하지 않는다. `NUCLEAR_PRIOR_RESULT.json`의 실제8nuclide C64 prior샘플은 BBN donor 근거이며 reionization trajectory가 아니다. D/H nominal2.503248144e-5가 기록되어 있다.

PR175 `f75d0cd5c01f9803d8eb0c3bb42d2cd175975b92`는 26-node sandbox-first SSOT와17state nuclear baseline 설계다. 구조 ledger 및 miniature manufactured reference와 물리 fullnetwork execution을 구분한다.

## HE32에 대한 구체적 권고

1. HE31 scientific source를 유지하고, 새21heavy-species+electron 모델의 원자율·초기 abundance·온도·방출 spectrum을 별도 계약으로 연결한다.
2. ne=Σq n_(A,Z,q)로 전자 source 소유권을 통합하고 proper density/seconds를 유지한다. Isotropic collisional gas와 독립 massive-Vlasov anisotropic-stress 부문을 구분한다.
3. z20→2 기존 collisionless175/237/1231은 재적분하지 않고 source/관측량 비교에 재사용한다. 새 chemistry/Thomson identity의 실제 campaign만 실행한다.
4. Fullnorm/halfnorm, signedstress→tensor합→norm, 값0과 plotlogfloor를 계약으로 유지한다. 가시적 범위는 초기 input의 물리양성 허용 범위에서 확보한다.
5. 성능배수는 측정하지 않는다. NumPy prepared arrays, source-rate precomputation, bounded parallel worker와 create-only completed reuse를 구조적 최적화로 기술한다.

근거 파일: `COVERAGE.json`, `GITHUB_SNAPSHOT.json`, `ATOMIC_AND_REC_METADATA.json`, `PR199_DELTA.json`, `*_heads.tsv`, `SOURCE_FILE_HASHES.json`. Parent가 공개 연구 단원으로 옮길 때는 무관한 private repo catalog를 포함한 전체 GITHUB_SNAPSHOT을 그대로 게시할 필요가 없다. 관련 repo 공개 field만 추리면 충분하다.
