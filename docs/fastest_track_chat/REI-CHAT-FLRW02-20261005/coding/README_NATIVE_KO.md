# FLRW 세 방정식 native 연결 검증

원본 `rei_bianchi` commit `9455c2a3cbf2ce5ebaba28e9bfb1dfe79aed0efa`의 24-file `rust/rei_microphysics` crate에 `flrw_three_equations` 모듈, 시험, probe를 추가했다. 기존 F03 `hhe_rhs`와 microstep 구현은 바꾸지 않았다. 실제 저장소 이식 대상은 `coding/rei_crate`의 소스이며 `target/`은 게시·백업하지 않는다.

## 실제 연결 경로와 범위

`connected_cell`은 `AtomicProvider::raw_coefficient(K2[,K1])`와 Verner `cross_section(HI)`로 원자율·단면적을 얻고, pure-H `HHeModel`/`HHeState`를 구성하여 **기존 `hhe_rhs`**를 호출한다. 같은 광자와 proper 밀도를 **기존 `homogeneous_photo_rates`**에 전달하여 cMpc³ 변환을 포함한 photo event count를 대조한다. 따라서 별도로 쓰인 analytic 식만 검증하는 함수가 아니다.

모형은 prescribed gas T, pure H `n_e=n_H*x`, primary photon, 공통 FLRW 배경이다. Case A primary-only 또는 Case B local OTS를 명시적으로 선택한다. Case B에서는 tracked recombination photon을 추가하지 않는다. 기존 `hhe_rhs`의 `du`와 `escaped_energy_rate`는 소비하지 않으며 Case-B 열·광자 에너지 폐쇄를 주장하지 않는다. 유한 소스값의 연결 검증은 외부 원자 자료의 physical admission과 다르다.

광자 ledger는 고정된 proper 에너지 경계에서 `F_edge=a^3 H E_edge n_E(edge)`를 직접 계산한다. `n_E` 단위는 proper cm^-3 eV^-1, `E`는 eV다. 각 bin은 `dN_g/dt=a^3(S_g-A_g)+F_(g+1)-F_g`를 쓰며 내부 경계 flux는 합에서 소거된다. 상단 유입은 실제 입력에 따라 남긴다. photon bin 평균만으로 경계 spectrum을 추정하지 않는다. 이 모듈의 `N=a^3 n_gamma`는 reference comoving cm³당 수이며 기존 `cMpc^-3`와 혼동하지 않는다. proper derivative만 `-3H n_gamma`를 갖는다.

`ensemble`은 동일한 `a,H`, 고정 comoving-volume 가중치, 밀도 대비의 고정, matter boundary flux 없음, peculiar advection/compression 및 셀 사이 물질 수송이 없는 co-expanding 셀이라는 가정 아래에서 `X_V=<x>`, `X_M=<n_H*x>/<n_H>`, `eta=<n_gamma>/<n_H>`와 그 순간 source derivative를 계산한다. **일반적인 `X_V`는 기하학적 filling factor `Q_V`가 아니다.** `filling_defect`의 `Q_V`, `dot Q_V`는 외부 geometry가 제공한 입력이며 함수는 정확한 inventory 항등식과 생략항을 계산할 뿐 front geometry를 추론하지 않는다.

`sharp_filling_rhs`는 외부에서 fully-ionized/neutral sharp phase를 선언하고 `X_M=Q_V Delta_I`를 맞춘 경우에만 `(dot X_M-Q_V dot Delta_I)/Delta_I`를 반환한다. `0<Q_V<1`, `Delta_I>0`, `Q_V Delta_I<=1`을 요구한다. `Q=0,1` endpoint의 one-sided closure는 별도 문제다. `Delta_I=1`, `dot Delta_I=0`, photon storage/경계손실이 0, Case B와 적절한 recombination average가 주어지면 standard filling equation을 조건부로 복원한다. 이 연결은 production moving-front consumer의 구현을 뜻하지 않는다.

## 실행

Rust 1.94.1으로 검증했으며 edition 2021, 외부 dependency 없음이다. 저장소 root에서는:

```sh
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --offline --locked --test flrw_three_equations
cargo test --manifest-path rust/rei_microphysics/Cargo.toml --offline --locked
cargo build --manifest-path rust/rei_microphysics/Cargo.toml --offline --locked --example flrw_three_probe
```

CSV probe binary는 `rust/rei_microphysics/target/debug/examples/flrw_three_probe`다. stdin의 한 줄당 한 점을 처리하고 stdout을 매 줄 flush하므로 persistent subprocess로 사용할 수 있다. 빈 줄과 `#` 주석은 무시한다. 입력 header는 넣지 않는다. 출력 첫 줄에는 열 이름이 있다. 잘못된 입력은 exit 2와 stderr로 반환한다.

| 모드 | 인자와 CSV 입력 |
|---|---|
| `photon` | 19 fields: `a,H,N0,N1,N2,Eedge0..3,nE0..3,Sproper0..2,Absproper0..2` |
| `cell A 0` | Case A·collision off. 25 fields: `a,H,T,nH,x,Nproper0..2,Sproper0..2,OtherAbsproper0..2,Ecenter0..2,Eedge0..3,nE0..3` |
| `cell B 1` | 같은 입력; Case B·collision on을 명시적으로 선택 |
| `ensemble A 0 Q Qdot invTref` | 각 행에 `weight` + 위 25-field cell 입력. EOF에서 전체 ensemble과 exact filling defect를 출력 |

photon 출력: `dN0..2,dn0..2,F0..3,boundary_net,source_comoving,absorption_comoving,residual`.
cell 출력: `alpha,ci,sigma0..2,gamma,ne,photo,recombination,collision,dx,photo_bridge_residual,dN0..2,dn0..2,boundary_net,source_comoving,other_absorption_proper,photon_total_proper`.
ensemble 출력에는 `XV,XM,eta`, 각 derivative, per-H source/sink, covariance, `Xi`, filling defect의 storage/boundary/other/collision/geometry/sink 항이 있다.

## 실제 검증

사전에 `NATIVE_CONTRACT.json`에서 범위·단위·tolerance·negative control을 고정했다. 원본 crate에 새 seam import를 요청하면 E0432·exit 101이 발생하여 missing implementation을 확인했다. 초기 추가 19개를 포함한 전체 82개 시험(기존 63 + 추가 19)이 실제 통과했다. 독립 검토에서 발견한 public Ensemble의 NaN 우회 가능성을 닫은 후, 추가된 부정 입력 시험을 포함한 최종 20개 targeted tests가 실제 통과했다. 기존 63개 시험은 이 국소 입력검증 변경 뒤 다시 실행하지 않았다. 최종 targeted 실행에는 warning이 없다. 로그는 `BASELINE_GAP_LOG.txt`, `TARGETED_TEST_LOG.txt`, `FULL_CRATE_TEST_LOG.txt`다.

시험은 fraction/comoving 변수에 `-3H` 중복, threshold flux 생략, energy center로 edge를 대체, recombination product-of-means, `X_M=X_V` 오인, photon storage 생략, 잘못된 sharp mass closure와 endpoint 사용을 검출한다. thermal closure, uniform interval error, 일반 Bianchi RT, 실제 EoR history는 이 시험으로 승격하지 않는다. 외부 독립 Decimal/시간적분 검증은 루트 연구 패킷의 별도 evidence를 따른다.

독립 검토의 같은 public-input 경계 문제를 `CellResult`에도 확장해 닫았다. 각 셀의 유한값·양의 핵 밀도·분율·비음수 source/sink를 가중합 전에 검사하므로 음의 개별 밀도가 양의 ensemble 평균에 숨을 수 없다. 이 국소 수정 후 최종 21개 targeted tests가 exit 0으로 통과했고 probe를 재빌드했다. 원래 producer의 시험 횟수 기록은 변경하지 않고 `REVIEW_FIX_RECORDS.json`과 `TARGETED_REVIEW_FIX_LOG.txt`에 후속 증거를 추가했다.
