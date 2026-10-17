# BASS-INTAKE-01: 실제 donor의 시간가변 기하 접점과 셀 전체 팽창 검사

2026-10-18 KST. 다음 미완료 항목으로 source-bound BASS geometry intake를 선택했다. 내부/외부 오차제어를 다시 구현하거나 자동으로 새 열 단계 연구 루프를 수행한 것이 아니다. **현재 상태: PARTIAL_NATIVE_INTEGRATION_BLOCKED.** 새 Rust는 작성했지만 컴파일/테스트/receiver 연결은0회다. 실제 실행은 Wolfram 대수/원본3행/2셀 수치검산이다.

## 1. source identity와 서로 다른 S10 산출물

이 대화의 직접 선행 S10 ZIP SHA256은 `4bc9f8df911568d44cf3dfdf05066eaa92c41c4039b0a00a842ae328ac57218b`,1349692bytes,78sourcefiles,`budget_native.rs`다. 이 파일의 이전169Rust/4Python 결과는 선행 증거이며 이번 재실행 결과가 아니다. 새로 발견한 원격 PR192 HEAD `14837d300d7845bbe50bc7068f058e1591c581e6`는 `nested_budget.rs`,79sourcefiles,5085358bytes,ZIPsha256 `32addab0ba299ba288db07a163a6a6ea23949e6d5fbbe73a00cb1e4dc920e530`의 다른 산출물이다. 같은 filename이라고 동일 버전으로 대체하거나169와170tests를 합산하지 않는다. 둘의 전체 코드동치 검사는 수행하지 않았다.

이 새 Git branch는 공통 고정 PR191 HEAD `09814115c793bf304654a2ee0066a4772ce51ffd`에 독립 add-only로 저장한다. 선행 local S10 전체코드가 이 commit에 들어 있다고 주장하지 않는다. 그 정확한 선행 ZIP은 별도 고유 이름으로 Drive/Dropbox에 저장했다. PR191/192, original production owner PR150 `da4bd0b9d112cadb2ec78c49d7dc3e7ab4761ea7` 및 사용자 runtime/checkpoint는 변경하지 않는다.

## 2. 실제 donor 읽기

REI PR159 HEAD `64a6dc33873e8be494f78e580a577c8083064eb1`의 `rust/rei_microphysics/src/axbi_bass_background.rs`(blob `7ccff1ce901d24d68fce669933a9f7ba23e1828a`)를 읽었다. 기존 provider는 이미 logH와 b의 cubic Hermite 보간, `s=H db/dx`, GL8의 dt=dx/H 적분 및 시간 역함수를 가진다. 원 provider를 교체하지 않았다.

같은 ref의 `research/bass_dynamic_20261016/source_grids/matched_n121_241_481_retry/n0121/PRODUCER_RECEIPT.json` blob `ccf058240903ea308259db95d2f21430f8ef50ca`와 CSV blob `f9f0bfd3149d566e2009f2a19fdb20ad0bd5bb25`를 읽었다. CSV849–851행의 SIGNED_MINUS3행을 원문 그대로 이 directory에 보존했다. Header는 producer manifest의22개 columns에서 재구성했으므로 이 excerpt는 전체CSV와 byte-identical 파일이 아니다.

Producer가 제시한 전체CSV SHA256은 `5a7844834b50fbc046995678a6aaf936252a81e49de1593604eee30641274133`,8cases*121=968rows다. **이번에는 전체CSV를 내려받아 재해시하거나968행을 검증하지 않았다.** 원 manifest의 source는 BASS PR163 FD96mass/isotropicOmega_r이고 gamma/nu anisotropic hierarchy와 HHe source를 포함하지 않는다. 기존 H/He donor의 source-only backreaction 범위를 새 H/He/D solver의 self-consistent closure로 승격하지 않는다.

## 3. 컨벤션과 직접 유도

Metric(-,+,+,+), `ds²=-c²dt²+a²e^-2b(dx1²+dx2²)+a²e^4b dx3²`. x=ln(a/a_ref), a_ref=1/21, t[s], H,s[s^-1], b,x무차원. 원 좌표를 쓰는 동안 c를 설정값1로 바꾸지 않는다. photon energy[eV], c p_i를 에너지 차원의 Killing 성분으로 정의한다.

`r=b'(x)=s/H`, `H_perp=H(1-r)`, `H_parallel=H(1+2r)`, `Sigma=sqrt(3)|r|`. 원 BackgroundPoint.sigma의 signed s/H를 사용자의 비음수Sigma로 그대로 전달하면 안 된다. `signed_s_over_h`와 `sigma_magnitude` 필드를 분리했다.

출생값 xb,bb,Eb,mu_b에 대해

    E²/Eb²=exp[-2(x-xb)] [(1-mu_b²) exp(2(b-bb))+mu_b² exp(-4(b-bb))].

두 번째 항의 fraction을 q_parallel∈[0,1]이라 두면

    d ln E/dx=-1+r(1-3q_parallel)
               =-(1-q_parallel)(1-r)-q_parallel(1+2r).

한 셀 전체에서 r_min>−1/2이고 r_max<1이면 모든 광선에서 에너지가 엄격히 감소한다. alpha=min(1-r_max,1+2r_min)>0이면 `E(x2)<=E(x1) exp[-alpha(x2-x1)]`. 따라서 해당 셀의 고정 photo edge는 최대 한번 교차한다. 이 엄격한 guard를 통과한 셀에서만 endpoint sign/bisection을 이용한다. 경계의 영팽창/수축 셀은 '물리적으로 금지'가 아니라 현재 monotone route의 지원 범위 밖으로 반환한다.

Hermite b(u)=c0+c1u+c2u²+c3u³, u∈[0,1], cellwidth L이면 r=(c1+2c2u+3c3u²)/L다. 끝점과 내부 vertex u*=−c2/(3c3)만 검사하면 실수 대수에서 셀 전체 r extrema를 얻는다. Rust의 coefficient arithmetic과 safety cushion은 directed-rounding enclosure가 아니므로 f64의 엄밀한 인증이라고 부르지 않는다.

### 끝점 검사만으로 부족한 반례

제조된 b(u)=−2u²+4u³/3, x=u는 두 끝점에서 r=0이지만 u=1/2에서 r=−1이므로 H_parallel/H=−1이다. 축방향 광선의 ln(E/Eb)=−u−2b(u)와 edge/Eb=exp(−1/50)를 택하면 양끝에서 에너지가 edge보다 높음에도

    u=0.021888452464273960..., 0.287882845629721198...

두 번 교차한다. 이 반례는 **실제 donor에서 발견한 결함이 아니다**. 일반 Hermite 셀에 endpoint-only monotonicity를 가정할 때의 오류를 보여 주는 수학적 대조군이다.

## 4. 실제 source3행/2셀의 CAS 검산

Binary64 source input을 rationalize한 뒤40–45자리 연산으로 보간/적분했다. 더 많은 물리적 유효숫자를 가진 입력으로 바꾼 것이 아니다. H0,Omega_m,Omega_r,Omega_L, f_mass=.1은 기존 donor 검사식과 같으며 재보정하지 않았다.

3node에서 Hamiltonian relative residual max=3.31847774768e-16, Raychaudhuri/dHdx residual max=4.43319241335e-16. Hperp/Hparallel 원 columns와 H−s/H+2s의 상대 차이 max=1.23240124243e-16/5.63670804182e-17. 이는 읽은3node의 대수적 일치이지 전체 보간곡선의 Einstein equation 검증이 아니다.

| 셀 | b' 전체 범위 | alpha | H_mid[s^-1] | Sigma_mid |
|---|---|---|---|---|
|1|[-.009999500037497,-.009820498383790]|.980000999925006|1.172976336347936e-16|.017163922897660|
|2|[-.009820498383790,-.009644697533212]|.980359003232420|1.152074566774859e-16|.016856667374003|

첫 셀 logH 보간의 proper increment=1.0195600729585139e14s, 두 번째=1.0380576677560974e14s. 원 producer의 elapsed-time 차이와 상대 차이는 각각6.06065e-13,6.07751e-13이다. 원 provider가 재적분한 clock과 producer clock을 구분해 보존해야 한다. 이 차이를 자동으로 오류나 허용범위 초과라고 판정하지 않았다.

첫 셀의 Eb=13.605eV,mu_b=.4 ray가 receiver의 제조 Dedge13.602134599702eV를 지나는 위치: x=0.00020954653923285161, 재적분 proper time=1.7707416039508226e12s. 이는 새 photon root probe이며 HHeD chemistry 이력이나 실제 D의 실험 측정 threshold가 아니다. 이 crossing은 기존8e10s 회귀 이력보다 뒤에 있다.

## 5. 작성 코드와 실제 실행의 구분

`bass_cell.rs`는 작은 standalone utility다. 동일 수학적 Hermite 정의를 coefficient form으로 표현하여 기하 snapshot, signed/magnitude 분리, cell expansion, positive GL8 clock increment 및 guard-first monotone photon root를 제공한다. ln-sum-exp energy evaluation, finite/domain checks, no extrapolation, no-progress rejection을 작성했다. 같은 수식이어도 원 provider와 bit identity를 주장하지 않는다.

`bass_cell_tests.rs`: **10개 작성, 실행0개**. donor 수치값은 위 CAS결과를 참조한다. 컴파일/Clippy/native receiver binding/원자 반응0회다. runtime 초기명령과 echo diagnostic,Python initialization이 모두 실행 전에ServerError였다. Native subagent NOT_RUN_UNAVAILABLE. 물리 원식을 대체하거나 user-local/NCP/Codex로 우회하지 않았다.

Wolfram 첫 actual-row 호출에 Python e-16 표기를 넣어 비수치 e기호가 발생했다. 원인을 scientific-notation syntax로 분리하고 *^-16로 고친 호출을 새로 실행했다. 잘못된 결과는 채택하지 않았고 실패 기록을 EVIDENCE.json에 보존했다.

## 6. 재개와 claim gate

    rustc --edition=2021 --test bass_cell_tests.rs -o bass_cell_tests
    ./bass_cell_tests

그다음 고정 sourceCSV/manifest 전체 bytes를 확인하고 모든 채택 셀을 검사한다. 원 BassBackground로 absolute proper clock을 정한 뒤 receiver의 constant-axisymmetric 구체 타입 의존성을 geometry interface로 분리하고, 새 root route를 선택적으로 연결한다. 먼저 source-only photon/clock parity, 이후 실제 H/He/D 짧은 이력 순서로 검증한다. 현재3행만으로 full121/241/481 refinement/물리IC/feedback/tilt/polarization을 승인하지 않는다.

BASS-INTAKE-01: SOURCE_BOUND_KINEMATICS_CAS_CHECKED, NATIVE_INTEGRATION_BLOCKED. 전체P4 PARTIAL, SA01/02/FLRW-CONV/BI-SIGNED/FULL_EOR HOLD. 첨부 S10의 기존 local PASS와 원격 sibling PR192는 모두 역사적 별개 결과로 보존한다.

문헌: Fleury,Pitrou,Uzan,PRD91,043511(2015),DOI10.1103/PhysRevD.91.043511,arXiv1410.8473v3는 Killing/redshift 구성의 근거다. Exa와SciSpace journal metadata를 확인했고SciSpace의2022 repository-index date는 출판연도로 쓰지 않았다. 공식 CVODE rootfinding 문서는 일반 sign-change search의 한계를 설명하지만 이번새guard/코드를 검증하지 않는다. 셀 전체 조건과 반례는 직접 유도/CAS계산이다.
