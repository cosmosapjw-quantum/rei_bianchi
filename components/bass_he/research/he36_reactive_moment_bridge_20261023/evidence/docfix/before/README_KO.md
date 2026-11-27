# HE36 supplied event tensor / finite-source / source-lift bridge

이 패키지는 **공급된 입력을 연결하는 국소 어댑터**다. 실제 핵반응률, 딸핵의 운동량 분포, 열화율, 생성 전자의 분포를 새로 제공하지 않는다. 연구 단원의 `workflow1.0.0 / approval0.2`를 유지하며, 기존 IVP·기존 donor 검사를 재실행하지 않았다.

## 1. 변경하지 않고 재사용한 계산

REI의 `ResolvedEvent.evaluate(Y, n_B)`가 반응률·화학량론·전하에서 추론한 자유전자 수·에너지 원장을 계속 계산한다. 다음 파일은 바이트 단위로 동일하다.

| 파일 | SHA256 |
|---|---|
| `vendor/rei_resolved_local.py` | `d0998261323609901f0cf9636d71282e7848bac6c00c1e5f7240ed7fc540e88a` |
| `reactive_moments.py` | `49104bb9244af92f707f83b489f217a0573566b2d9f3e5154366b7d35eaaab89` |
| `maxwellian_moments.py` | `644260261b82d6a528fd049b2bb20702e4c66de087406c7868a395a41ec99c2c` |

REI pin은 `9620e1fcc4bdda76e0311206f614234926600381`, 원래 경로는 `research/rei_coupled_isotope_sandbox_20261022/code/local.py`다. 함께 저장한 `vendor/REI_EXECUTION_CONTRACT.md`의 3절은 아홉 에너지 항 모두의 단위를 **J/event**로 명시한다. (Y_i=n_i/n_B)이며 donor 행의 반응률은 events/(baryon·s)다. 정확한 파일 정보와 계약 해시는 `DONOR_PROVENANCE.json`에 있다.

## 2. 하나의 완결된 net tensor와 하나의 에너지 소유자

`attach_event_tensor`는 사용자가 완전히 공급한 사건당 중심 운동학적 2차 모멘트 (C_{m event},[{m J/event}])를 받는다. 입력에는 해당 사건의 입사 입자 제거와 열적 생성 입자의 기여가 모두 들어가야 한다. 두 기여를 따로 계산했다면 먼저 부호를 유지하여 합해야 한다.

\[
S=n_Br\,C_{\rm event},\qquad
Q=\tfrac12\operatorname{tr}S=n_Br\,dE_{\rm th},\qquad
J=S-\tfrac23 QI.
\]

(S,J)의 단위는 Pa/s이고, (Q)는 W/m³다. π는 압력 텐서의 STF 부분이며 (J)는 같은 공통 벌크 중심계에서의 반응 기여다. 원장의 `dEth`와 반환된 `Q`는 **같은 열원**이다. 두 값을 더하면 열을 중복 계산한다. 입사 입자 제거에 해당하는 음의 (Q)만으로 반응 전체의 냉각을 정할 수 없다.

반응별 tensor가 없으면 `Unresolved`를 발생시킨다. 상태에서 반응률이 우연히 0이더라도 미상 생성 tensor를 등방적이라고 간주하지 않는다. 원장 단위, tensor 범위, 중심계 및 provenance를 명시해야 한다. 사건당 trace/2와 원장 `dEth`를 먼저 대조하고, 부피당 변환 후 다시 대조한다. 에너지 일치 허용치는 정규화된 128 epsilon이다.

```python
from components.event_bridge import (
    attach_event_tensor, NET_TENSOR_SCOPE, CENTRAL_FRAME,
    ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS,
)

result = attach_event_tensor(
    event, Y, n_B,
    per_event_tensor_J=complete_supplied_net_tensor,
    energy_unit="J/event",
    tensor_scope=NET_TENSOR_SCOPE,
    central_frame=CENTRAL_FRAME,
    tensor_provenance="explicit provenance for this supplied tensor",
    thermal_inventory_scope=ALL_RETAINED_THERMAL,
    charge_census_scope=NEUTRAL_21_STATE_CENSUS,
)
```

### 열적 입자 수의 적용 범위

이 어댑터의 21상태 census는 전하 중성이며 양전자·음이온을 포함하지 않는다. 자유전자 수는 (q\cdot\nu)로 추론한다. 다음 식이 **열적** 입자 수가 되려면 보유한 모든 핵과 자유전자가 열적이어야 한다.

\[
R_{\rm part}=n_B\,r\,(1+q)\cdot\nu
             =R_{\rm nuclei}+R_{e}.
\]

이를 명시하는 `ALL_RETAINED_THERMAL`을 필수로 받으며, 이 범위에서 비영 `dEfast`가 있으면 미해결로 거부한다. 별도 fast population이 있으면 그 입자 수 source를 열적 census에서 빼야 한다. `dEfast`만으로 그 수를 정할 수 없다. fast-particle 수·열화 provider를 이 패키지가 만들어내지 않는다.

## 3. finite evaluation의 범위 보존

`from_finite_evaluation(prepared, evaluation, index, ...)`는 선택한 행을 `FiniteMomentRecord`로 옮긴다. 그 안의 `raw_moments`는 불변 `RawMoments`이며, original evaluation/prepared type, source identity, 행 번호, 원래 T, energy mapping, energy mass, finite-support 범위를 함께 보존한다. 원래 T를 교체하는 인자를 받지 않는다.

두 사용 경로를 명시적으로 구분한다.

| `usage` | 허용 범위 |
|---|---|
| `RADIAL_DIAGNOSTIC` | finite-support radial 값의 진단. 실제 CCC의 fixed-target incident-electron convention은 이 경로에 한정한다. |
| `MANUFACTURED_PAIR` | manufactured relative-energy 표만 사용하며, 명시한 두 질량의 μ와 표의 질량을 대조한다. |

어느 경로든 `acknowledge_finite_source_partial=True`가 필수다. α·β·γ 중 하나라도 provider의 underflow flag가 켜지면 양의 미소 값을 물리적 0으로 바꾸지 않고 거부한다. 실제로 모든 표 값이 0인 경우만 **공급된 finite support에서의 선언된 0**으로 보존하며, 전체 물리 반응률이 0이라고 확장하지 않는다.

pair 계산은 `record.binary_loss(...)` 또는 `record.for_pair(ma, mb, T)`를 통해 진행한다. 이 경로는 T와 μ를 다시 검사한다. fixed-target 진단 결과는 유한 질량 pair로 진입할 수 없다. `raw_moments`의 노출 목적은 감사와 radial 진단이며, 해당 필드를 직접 꺼내 범위 검사를 우회하는 사용을 승인하지 않는다. 원래 `RawMoments` primitive는 입력의 수학적 필요조건만 검사하며 물리적 출처를 인증하지 않는다.

**수치적 한계:** value/log identity 검사 때문에, 표현 가능한 subnormal도 `exp` 반올림 오차가 허용치를 넘으면 보수적으로 거부할 수 있다. 이 finite adapter는 모든 subnormal의 수용을 보장하지 않는다. 모든 어댑터는 요구한 비영 곱·변환이 표현되지 않으면 명시적으로 실패하며 clipping 또는 바닥값을 도입하지 않는다. finite-support tail 및 물리적 보간 오차 상한은 여전히 공급되지 않았다.

## 4. source-aware lift 검사

`validate_source_lift`는 고정 선형 lift (L), 축소 상태 (z), 두 source 함수를 받는다. (Y=Lz>0)를 먼저 확인한 뒤 각 함수를 정확히 한 번씩 평가한다.

\[
d=R_{\rm full}(Lz)-LR_{\rm red}(z),\qquad
|d_i|\le a_i+r\max\{|R_{{\rm full},i}|,|(LR_{\rm red})_i|\}.
\]

`atol`, `rtol`, `source_unit`에 기본값을 두지 않는다. 실패하면 `SourceLiftDefect.report`에 source, defect, gate, 실패 성분을 보존한다. 이는 한 양의 상태에서의 검사이며, 전체 영역의 반응망 closure나 시간 진화 오차 정리가 아니다. 이동·비선형 lift에서 필요한 추가 미분 항도 다루지 않는다.

## 5. 실제 신규 검증과 결과

`attempts/attempt_001/RESULT.json`에 2026-10-22 22:39:56–22:39:57 UTC 실제 실행의 명령·환경·코드 해시·자원·결과를 저장했다. **첫 실행 7/7 그룹 통과, exit 0**이다. 그 안에서 세 사건은 다음의 정수 census를 확인했다.

| manufactured 사건 | 핵 수 변화 | 자유전자 수 변화 | 열적 입자 수 변화 |
|---|---:|---:|---:|
| H⁰ → H⁺ | 0 | +1 | +1 |
| D⁺ + p⁺ → ³He²⁺ | −1 | 0 | −1 |
| n → p⁺, β census | 0 | +1 | +1 |

반응률과 모든 에너지 분배는 임의로 선언한 manufactured 값이며, 실제 중성자 수명·핵반응 Q 값·에너지 분배를 주장하지 않는다. 세 경우 모두 정수 baryon census가 보존되었고, 부피당 열원 일치의 최대 정규화 잔차는 (2.220446049250313\times10^{-16})이었다. 별도의 입사 제거와 gain을 부호대로 합한 tensor를 수용했고, tensor 누락·입사 제거만 입력·열원 두 번 입력·단위 오류·fast energy만 제시한 수 census·underflow를 거부했다.

source-lift 사례에서는 동일 비율의 source가 defect 0을 주었다. 두 isotope에 (+10^{-4},-10^{-4})를 더한 source는 합을 보존하면서 lift를 깨뜨렸으며, 두 성분의 약 (10^{-4}) defect가 명시한 약 (10^{-14}) gate를 넘어서 거부되었다. 양수가 아닌 full state도 source 평가 전에 거부되었다.

추가로 `/`에서 격리된 subprocess import를 확인했으므로 이 디렉터리를 통째로 복사하여 패키지로 사용할 수 있다. 기존 6D oracle·donor 검사·HE32·CCC 실제 표 계산을 다시 수행하지 않았다. 이 검사의 새 IVP는 0이다. 독립 검토자는 저장 결과와 코드를 읽고 차단할 과학·구현 결함을 찾지 않았으며, subnormal의 보수적 거부 한계를 문서에 명시하도록 권고했다. 그 문서 보완 때문에 검사를 다시 실행하지 않았다.

## 6. 통합 handoff

상위 연구 단원은 이 디렉터리를 `components/event_bridge`로 복사할 수 있다. 공개 export는 `attach_event_tensor`, `from_finite_evaluation`, `validate_source_lift`이며, dependency 사본은 원본과 동일하다. 다음 작업은 통합 import 확인과 전체 단원 문서·게시·백업이다. 이미 통과한 7개 그룹의 재실행은 다음 작업의 기본 요건이 아니다.

`FILE_MANIFEST.json`은 자기 자신과 재생성 가능한 Python cache를 제외한 최종 패키지 파일의 해시를 기록한다. 실제 물리 source 활성화에는 별도의 생성 tensor·에너지/입자 열화·isotope-aware source provider가 필요하다.
