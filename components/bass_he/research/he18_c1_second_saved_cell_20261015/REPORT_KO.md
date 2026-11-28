# HE18 코딩 루프 C1: warm P01 두 번째 저장 셀의 실제 로컬 기준계산 및 AXBI 부분이력 parity 분석

**수행 범위:** 2026-10-14~15 KST. `physmath-research-loop` 새 coding lane **C1** (목표·baseline 및 stage-local 실행). 이전 HE17 R1–R10의 첫 셀 결과는 변경하지 않는다. 현재 C1 작업은 **기존 archived FT03/HM12/R4 evaluator**를 실제 실행하여 다음 셀의 입력·RHS·baseline과 검증조건을 고정하며, 독립적인 AXBI 부분이력 진단을 병렬 수행한다. C2–C10 또는 전체 source IVP를 완료했다고 표시하지 않는다.

## 1. 선택한 실제 두 번째 셀

- `warm P01 FT03/HM12 Case-A`, non-tilted prescribed LRS Bianchi I, `(-,+,+,+)`, `x^0=ct`, proper seconds. CR/RCT/HH=OFF.
- 원 state: `P01_STATE.npz`, SHA256 `3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be`. 실제 shape `(2913,17)` = gas4+photons2904+ledger5. 동일 source에서 archived R4 `pilot.py` checksum을 변경 없이 사용했다.
- Target cell = `[6,250,000,000,12,500,000,000]s` (저장 node1→node2), left state는 HE17 첫 셀 오른쪽 저장 상태와 같다. `src.rhs(t1,y1).astype(float)`의 **2908개 성분이 HE17 R4 frozen Hermite 오른쪽 기울기와 bitwise 일치**했다. 이전 첫 셀 끝의 gas4+photon2904 오차는 `ENDPOINT_MEMORY_R7.json`에서 읽어 **nonzero incoming**으로 보존했다. 이 incoming error는 현재 수치 진단에서 실제로 bounds propagate 한 것이 아니다.

### 실행한 물리 계산 (exploratory only)

원 archived RHS를 새 셀에서 endpoint 2회, 내부 7개 노드에서 PL/Hermite 각 1회씩, **총 16회 실제 평가**했다. 모든 원자상수, electron census `χ_e=x_HII+(3/38)(x_HeII+2x_HeIII)`, 가스 thermal coordinate `w[eV/H]`, photon reference-volume stock, 원 emissivity 표를 고정했다. 수치표는 `results/C1_SECOND_CELL_PILOT_FINAL.json`.

| 저장 상태 기반 pilot | PL | Cubic Hermite |
|---|---:|---:|
| 7개 표본의 scaled gas RHS 잔차 최댓값 [1/s] | 9.371644209570914e-22 | 2.678172307847861e-26 |
| 7개 표본의 photon normalized L1 잔차 최댓값 [1/s] | 2.0522618642339406e-22 | 2.2814612619939704e-26 |

이 표본 정의에서 Hermite가 gas 약 **3.4993×10⁴**, photon 약 **8.9954×10³**배 작은 표본 최댓값을 제공했다. 하지만 **표본 최댓값은 whole-cell supremum이 아니며, 실제 IVP 오차·정밀도·수렴의 인증이 아니다**. 모든 2908변수의 cubic Bernstein 네 control point를 exact binary64→Fraction으로 검사해 photon nonnegative, gas simplex 및 30000–110000K thermal domain이 첫/끝을 포함한 **셀 전체**에서 유효함을 확인했다. Temperature endpoints 49999.986066984224,49999.9721340126K.

### 발견하고 수정한 단위 오류 (실제 RED→GREEN)

archived R4 Source의 `C=29979245800`은 **cm/s**이고 `n_H`는 **cm^-3**이다. 처음의 새 C1 pilot에서 column으로 `C×10^6∫n_e dt`를 사용하여 결과가 100배 과대평가되는 오류를 발견했다. 다음 항등식이 올바르다:

\[
\mathcal C_{\rm m^{-2}}=c_{\rm(cm/s)}10^4\int n_e^{\rm(cm^{-3})}\,dt
=c_{\rm(m/s)}10^6\int n_e^{\rm(cm^{-3})}\,dt.
\]

새 테스트 `test_unit_conversion_and_column_order`는 실제 전 계산에서 `τ≈7.999916026373407174×10^-7`이어서 **FAIL**했고, 단위를 `10^4`로 수정한 같은 테스트가 **PASS**했다. 원 archived physics implementation/parameters와 외부 rei_bianchi repo는 변경하지 않았다. 원 실패/수정 로그를 함께 보존했다.

수정 후 **새 Hermite reconstruction 진단**은 GL24 column `1.2025502721633432743×10^20 m^-2`, `τ_center≈7.9999160263734071745×10^-9`. GL12/24 column 차이 **3960 m^-2**는 서로 다른 부동소수점 quadrature 간 진단일 뿐 유효한 적분 오차상계는 아니다. Endpoint proper-ne PL 재구성과의 차이는 `-1.400032×10^7 m^-2`이며 이것 역시 *reconstruction definition bias*다. 두 번째 셀 참해 column/tau interval은 **null**.

## 2. 별도 Codex/AXBI 실행의 실제 읽기 전용 분석

원 repo source는 cold `Plancklike_MD14_BB50K` IGM/Grackle, `YHe=.2454`, `nHe/nH=1227/15092`, 가스 초기 약8.1K, thermal erg/H다. Stellar 50000K는 gas 온도가 아니다. Warm HE18의 FT03/HM12/eV/H 숫자를 해당 모델에 삽입하지 않았다.

실제 원격 repo HEAD `e65e11895fd8e5cfe647edf440592c90359a0923` (2026-10-14 23:46 KST), tracked clean을 읽었다. 당시 AX07 fullZERO 지정 범위 완료, AX08 signed in progress, AX11/12 prepared-not-run, AX13 scoped partial figure/report 완료. 진행 중인 PLUS recovery observer 및 Half+/- 연속 실행/중단 영수증을 재생성하거나 작업을 중단하지 않았다. 실제 source/queue/STATE에 대한 mutation은 0.

원 `report/signed_terminal_partial_32d11e733155`의 5개 source-specific display CSV(각 4003행)를 Dropbox에서 실제 materialize하고 `SAMPLE_MANIFEST`의 SHA256과 **5/5 바이트 일치**를 확인했다. 원 CSV는 private full ZIP으로만 보존하고 공개 Git에 게시하지 않는다. 원 종점의 scale `a=0.08873654701704167`은 다섯 경우에 정확히 같지만, proper elapsed time은 3가지이므로 **고정-a 비교이지 고정시간 비교가 아니다**.

\[
E(q)=\frac{O(+q)+O(-q)}2-O(0),\quad
O_{\rm odd}(q)=\frac{O(+q)-O(-q)}2.
\]

| `a`가 같은 표시값 종점의 observable | E(0.01)/E(0.005) | odd(0.01) |
|---|---:|---:|
| x_HII | 3.9999259842 | 9×10^-17 |
| x_HeII | 3.9999241263 | 9.5×10^-16 |
| electron per baryon | 3.9999258378 | 1.25×10^-16 |
| gas temperature [K] | 3.9999555998 | 5.83×10^-11 |

이는 **저장된 유한 partial 이력에 대해 even response가 q² scaling과 호환되는 진단**이다. q 부호에 따른 odd는 작은 저장값 차이에 불과하고, 실제 rounding/numerical convergence·adaptive solver 오류 상계가 없으므로 odd=0의 엄밀한 물리 정리나 shear signal detection을 주장하지 않는다. `electron` 필드는 per-baryon이고 H/H, He/He 분율과의 관계를 같은 source `Y_He`로 검사했다. 실제 원자료 전체가 아닌 기존 display sample의 같은 종점만 소비했다.

모든 재사용 도구는 read-only. 새 `rei_supplier/signed_parity.py`는 선택된 Source manifest identity, 같은 scale, accepted-row=200000, electron baryon normalization을 확인하고 숫자를 exact Decimal로 계산한다. 현행 Codex 생성 plot 결과는 재사용하며 중복 재실행하지 않았다.

## 3. 이번 C1 완료 조건과 다음 코딩 단계

- 실제 local code execution: `python src/second_cell_pilot.py --out results/C1_SECOND_CELL_PILOT_FINAL.json`; `python rei_supplier/signed_parity.py --samples rei_supplier/source --out results/C1_REI_SIGNED_PARITY.json`; 각 0 exit.
- Fresh main tests: `python -m unittest discover -s tests -p 'test_*.py' -v`, **8/8 PASS**. 원 단위 테스트의 실패와 같은 검사 수정 뒤 통과를 분리 기록.
- 실제 Wolfram Language15.0.1 Hermite endpoint/clock/column 단위·전자 census 등 scalar **7개 0**, xAct/xTensor1.3.0 covariance/projection **4개 0** (공식 archive/file SHA pin 확인). 처음 메시지의 symbol 경고는 미정의 패키지 동작의 실패가 아니며 출력 0을 직접 검사했다.
- No source ODE/full production history/native/HPC run. Single-author analysis+CAS; external independent review/subagent NOT_RUN.

**C1 status: COMPLETE_SCOPED_EXECUTABLE_BASELINE. 다음 C2에서는 실제 새 셀의 source gas/photon derivative·thermal and photon feedback, `A/B/C`, provider and geometry error terms를 소유한 함수/데이터에 매핑하고, `ENDPOINT_MEMORY_R7`의 원 4gas+2904 photon error를 모델 이식 없이 소비하도록 결박한다.** C2가 끝나기 전까지 새 두 번째 셀의 high-accuracy/whole-cell certificate를 생성하지 않으며, 별도 AXBI의 AX08 signed/history·AX11 convergence 목표에 HE warm optical을 선행조건으로 넣지 않는다.

참고 방법: SciSpace 및 Exa에서 조회한 residual-based a posteriori error 및 Bernstein convex-hull 방법은 일반론이며, 특정 warm source 상계는 본문 직접 계산 및 보존된 R5/R7 자료만 쓴다.
