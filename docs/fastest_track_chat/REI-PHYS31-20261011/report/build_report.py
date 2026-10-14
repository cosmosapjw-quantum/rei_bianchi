#!/usr/bin/env python3
"""Assemble the PHYS31 report from completed evidence; no scientific execution."""
from pathlib import Path
from hashlib import sha256
from decimal import Decimal
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "contributions/numerics/QUARTIC_PROFILE_FIRST.json"
RAW = json.loads(RAW_PATH.read_text())
REPLAY = json.loads((ROOT / "portability/REPLAY_RECEIPT.json").read_text())
FIRST_EXEC = json.loads((ROOT / "execution/first/EXECUTION.json").read_text())
REPLAY_EXEC = json.loads((ROOT / "execution/replay/EXECUTION.json").read_text())
THEORY = json.loads((ROOT / "contributions/theory/THEORY_CLAIMS.json").read_text())
KERNEL = json.loads((ROOT / "contributions/kernel_scope/KERNEL_PROFILE_CLAIMS.json").read_text())
CONTRACT = json.loads((ROOT / "PHYSICS_CONTRACT.json").read_text())


def ident(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": sha256(data).hexdigest()}


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


FRONT = r"""# PHYS31 — 같은 분산 모멘트의 스펙트럼을 구별하는 사차 문턱 이동

**REI-PHYS31-20261011 · EQUAL_SECOND_MOMENT_QUARTIC_PROFILE_SPLITTING**

같은 이차 모멘트를 가진 고정 대칭 프로파일은 문턱 전개에서 **삼차까지 일치한다**. 현재 고정 물리 커널은 연구 구간에서 해석적이므로 사차 전개가 가능하고, 프로파일 차이는 사차 모멘트와 네 번째 커널 도함수의 가중평균으로 정해진다. 선택한 양의 절대연속 프로파일 쌍에서 저장점의 사차 차이 계수는 두 문턱 모두 음수로 계산되었다.

이 보고서는 직접 증명, 실제 고정 입력 계산, 재현 근거와 남은 한계를 함께 담는다. 전체 증명은 부록 A, 고정 물리 식의 정칙성·프로파일 구성은 부록 B에 포함했다. 생성과 분리된 최종 판정의 권위는 동봉된 [판정서](../independent/DECISION_REVIEW_KO.md)와 [기계 판독 판정](../independent/DECISION_REVIEW.json)에 있다. 부록의 역할·시점 설명은 작성 당시 기록을 보존한다.

## 1. 이번에 해결한 질문

PHYS30은 이차 문턱계수가 프로파일의 \(\mu_2\)에만 의존한다는 결과를 남겼다. 이번 질문은 **같은 \(\mu_2\)를 가지되 더 높은 모멘트가 다른 프로파일이 그다음 어느 차수에서 구별되는가**였다.

답은 정칙성에 따라 나뉜다.

| 전제 | 이번 직접 증명 | 판정 범위 |
|---|---|---|
| \(k\in C^3\), 같은 \(\mu_2\), 대칭 | \(\Delta W=o(\delta^3)\), 삼차까지 공통 | \(O(\delta^4)\)는 따라오지 않음 |
| 추가 \(k\in C^4\) | \(\Delta W=D_4\delta^4+o(\delta^4)\) | \(D_4\ne0\)일 때 실제 첫 비영 차수는 4 |
| \(D_4=0\) | 사차 차이 소거 | 다음 차수가 반드시 6인 것은 아님 |
| 현재 고정 source-real 커널 | 구간의 열린 근방에서 \(C^\omega\) | C4 적용 가능; 수치 오차 인증과 별개 |

C3 한계는 추측으로 남기지 않았다. 같은 양의 밀도 쌍에 대해 임의의 \(3<p<4\)에서 \(\Delta W\sim C_p\delta^p\), \(C_p\ne0\)인 허용 커널을 구성했다. 사차가 소거된 뒤에는 비영 \(\delta^5\) 항이 먼저 나타날 수 있는 매끄러운 예도 제시했다.

## 2. 정의와 보호한 물리 의미

\[
a=13.61,\quad b=24.58,\quad m=18,\quad
L=m-a=4.39,\quad H=b-m=6.58\quad(\mathrm{eV}).
\]

폭 \(\delta\ge0\)는 바깥 반폭이고, 중심 \(Y\)의 공통 구간은 \([a+\delta,b-\delta]\)다. 광자 에너지는 \(E=Y+\delta Z\), 프로파일 \(\nu\)는 \([-1,1]\) 위의 고정 대칭 확률측도다. 프로파일은 폭·중심·실제 분산·분지와 독립이다.

\[
\mu_2=\mathbb E Z^2,\qquad
W=\operatorname{Var}(E),\qquad
V=\operatorname{Var}(Y)=W-\mu_2\delta^2.
\]

따라서 실제 실현가능 구간은

\[
\mu_2\delta^2\le W\le
(L-\delta)(H-\delta)+\mu_2\delta^2,\qquad
0\le\delta<\min(L,H).
\]

같은 \(\mu_2\)에서는 이 구간, 중심 위치, 확률, 응답의 분모가 두 프로파일에 정확히 공통이다. 물리 편미분에서는 실제 \(W\)를 고정한다. 중심분산 \(V\)를 고정한 계산으로 바꾸지 않았다.

\(k(E)\)는 초기 HeIII의 \(\epsilon^2t^4\) 응답 커널이고 단위는 \(\mathrm{s}^{-4}\)다. 기존 전체 정규화, proper time, eV, metric \((-,+,+,+)\), 열 변수 eV/H, \([\epsilon^2]=\tfrac12\partial_\epsilon^2|_0\)를 유지한다. \(c_{\rm light},\hbar,k_B\)를 새로 1로 놓지 않았다.

상속한 \(k''>0,k'''<0\)의 극값 해석은 **고정 공통 프로파일을 사용하는 중심 혼합족**에 한정한다. 임의 광자 분포 전체의 유한폭 극값이라는 의미를 추가하지 않았다.

## 3. 왜 사차 모멘트가 처음 남는가

프로파일 평균은 \(f_{\delta,\nu}(y)=\int k(y+\delta z)\,d\nu(z)\)다. 두 프로파일은 질량·일차·이차·삼차 모멘트가 같으므로, C4 Taylor 전개의 차이에서 처음 남을 수 있는 항은

\[
f_{\delta,\nu}(y)-f_{\delta,\widetilde\nu}(y)
=\frac{\Delta\mu_4}{24}\,k^{(4)}(y)\delta^4+o(\delta^4)
\]

다. 부록 A는 허용되는 모든 중심에서 나머지가 균일함을 직접 증명한다. 일반 측도와 원자를 허용하며 프로파일 밀도를 미분하지 않는다.

분지 \(j\)의 영폭 끝점과 내부 중심을 \(e_j,x_j\), 해당 확률을 \(p_j,q_j\)라 쓰자. 응답을 \(F_{j,\nu}\), 공통 수준을 \(A_j\), 기준점을 \(w_j\)라 하면

\[
F_{j,\nu}(0,w_j)=A_j,\qquad
C_j=F_{j,W}(0,w_j)>0,
\]

\[
\mathcal H_{4,j}=p_jk^{(4)}(e_j)+q_jk^{(4)}(x_j).
\]

두 근 사이의 평균값정리와 양의 \(F_W\) 하한을 사용하면

\[
\boxed{
W_{j,\nu}(\delta)-W_{j,\widetilde\nu}(\delta)
=-\frac{\Delta\mu_4\mathcal H_{4,j}}{24C_j}
\delta^4+o(\delta^4).
}
\]

이는 실제 물리 한쪽 \(\delta\downarrow0\)의 결과다. 부록은 근의 오른쪽 C3/C4 정칙성과 Taylor 전개 자체를 증명하며 형식적 급수만 전제하지 않는다. 개별 문턱의 삼차계수가 0이라는 주장은 아니다. 움직이는 중심 때문에 개별 홀수 차수 항은 남지만 같은 \(\mu_2\)의 두 프로파일에서 그 항이 공통이다.

단위는 \([\mathcal H_4]=\mathrm{s}^{-4}\mathrm{eV}^{-4}\), \([C]=\mathrm{s}^{-4}\mathrm{eV}^{-2}\), \([D_4]=\mathrm{eV}^{-2}\)다. 따라서 \(D_4\delta^4\)는 분산의 단위 eV²를 갖는다. \(D_4\)는 ordinary 사차 계수이며 네 번째 도함수 자체가 아니다.

## 4. 실제 비교한 두 양의 밀도

\[
h_u(z)=\frac12,\qquad
h_p(z)=\frac{35z^4-30z^2+11}{16}
=\frac{35}{16}\left(z^2-\frac37\right)^2+\frac27.
\]

두 밀도는 \([-1,1]\) 전체에서 양수이고 대칭·정규화·지원이 같다. 구간 안에서 연속이며 0으로 연장하면 끝점에 점프가 생긴다. 절대연속 확률측도라는 성질에는 문제가 없다.

| 양 | 균일 \(h_u\) | 다항식 \(h_p\) |
|---|---:|---:|
| 총질량 | 1 | 1 |
| 평균·삼차 모멘트 | 0 | 0 |
| \(\mu_2\) | \(1/3\) | \(1/3\) |
| \(\mu_4\) | \(1/5\) | \(71/315\) |
| 밀도 하한 | \(1/2\) | \(2/7\) |

\[
\Delta\mu_4=\frac8{315},\qquad
\boxed{D_{4,j}^{p-u}=-\frac{\mathcal H_{4,j}}{945C_j}.}
\]

![동일 이차 모멘트의 프로파일과 저장점의 사차 문턱 차이 계수](figures/PHYS31_QUARTIC_PROFILE_SPLITTING.png)

그림의 프로파일 곡선은 정의된 다항식의 표시용 표본이고, 막대는 이미 계산한 계수다. 유한폭 근이나 스펙트럼 적분을 추가로 평가한 그림이 아니다.

## 5. 고정 물리 커널의 계산 결과

새로운 근이나 에너지 지점을 만들지 않고, 기존 네 에너지 문자열에서 \(k^{(4)}\)만 계산했다. 아래 수치는 원시 JSON의 log-energy 경로를 표시용으로 반올림한 것이다.

| 노드 | 보존 에너지 (eV, 표시값) | \(k^{(4)}\;(\mathrm{s}^{-4}\mathrm{eV}^{-4})\) |
|---|---:|---:|
@@NODE_ROWS@@

두 도함수 조립 경로는 모두 각 노드에서 같은 부호를 반환했다. 이것은 해당 유한 산술점의 관측이며 구간 전체의 엄밀한 사차 도함수 부호 인증은 아니다.

| 양 | 상단 문턱 \(W_*\) | 하단 문턱 \(W_0\) |
|---|---:|---:|
| 보존 기준 분산 \(\widehat w\), eV² | 16.339944654589707… | 23.420218992353393… |
| 보존 \(C\), \(\mathrm{s}^{-4}\mathrm{eV}^{-2}\) | @@CSTAR@@ | @@CZERO@@ |
| 새 \(\mathcal H_4\), \(\mathrm{s}^{-4}\mathrm{eV}^{-4}\) | @@HSTAR@@ | @@HZERO@@ |
| \(D_4^{p-u}\), \(\mathrm{eV}^{-2}\) | **@@DSTAR@@** | **@@DZERO@@** |

저장점의 같은 \(A_j\) 수준에서

\[
W_{*,p}-W_{*,u}\sim
-0.00110495859229183348\,\delta^4,
\]
\[
W_{0,p}-W_{0,u}\sim
-0.000619616589313442784\,\delta^4.
\]

표시한 계수의 단위는 eV⁻²이고 \(\delta\)는 eV다. 간격 \(\Gamma=W_0-W_*\)의 사차계수 변화는 원시 결과에서

\[
\boxed{D_{4,\Gamma}^{p-u}
=@@DGAP@@\ \mathrm{eV}^{-2}}
\]

였다. 두 문턱의 계산된 사차 계수가 모두 음수이고 상단의 변화량이 더 커서 간격의 사차계수 변화는 양수다. **양의 유한 폭에서 실제 문턱이나 간격을 계산하거나 그 부호를 인증한 것은 아니다.** 사차 근사에 수치적으로 보장된 유효 폭은 아직 없다.

## 6. 작은 비영 잔차를 보존한 이유

보존 기준점의 응답은

\[
A_*=-2.2748589\times10^{-137},\qquad
A_0=-3.2582515\times10^{-137}\quad(\mathrm{s}^{-4})
\]

다. 이를 0으로 바꾸거나 기준근을 보정하지 않았다. 같은 \(\mu_2\)에서는 공통 분모 \(Q\)를 쓰므로

\[
F_\nu=N_\nu/Q,\quad N_\nu-AQ=0,\quad
Q=R^2+w\quad(\delta=0),
\]
\[
N_W=k(e)+sRk'(x),\qquad N_W-A=QC.
\]

두 번째 수치 경로는 보존된 \(k(e),k'(x)\)로 \(N_W\)를 직접 만들고

\[
D_{4,N}
=-\frac{\Delta\mu_4[\,w k^{(4)}(e)+R^2k^{(4)}(x)\,]}
{24(N_W-A)}
\]

를 계산했다. 분모를 \(QC+A\)에서 역으로 만들어 같은 식을 확인하는 데 그치지 않았다. 그 결과는 확률로 가중한 첫 quotient와 사전 허용치 안에서 일치했다. 하위 도함수·분산·확률·J의 입력 계보를 공유한다는 한계는 유지한다.

정확 영점에 대한 정리와 저장 숫자에서의 유한 산술 평가는 구별해야 한다. 원 J의 오차, 저장근의 정확 영점과의 거리, 반올림된 내부 에너지 문자열과 이상적 중심의 미소 차이는 이번에 enclosure하지 않았다.

## 7. 두 도함수 구현과 정확한 오류 검출

원 식은

\[
\phi(E)=\sigma(E)[J_x+J_w(E-\chi)],\qquad
k=K(D^2+3D)\phi,\quad D=E\partial_E
\]

다. 현재 fit은 H I cutoff와 He I cutoff 사이의 같은 해석적 분기다. 고정된 source binary64 리터럴을 정확한 실수 상수로 해석하고, 직렬화된 J를 고정한다. native floating point 반환 사상의 미분가능성이라는 뜻은 아니다.

Log-energy 경로는 \(\phi(Ee^t)\)의 여섯 번째까지의 Taylor 계수와

\[
k^{(4)}=\frac K{E^4}
(D^6-3D^5-7D^4+27D^3-18D^2)\phi
\]

를 쓴다. Ordinary energy 경로는 독립적인 generalized-binomial 곱으로 \(a_n=[u^n]\phi(E+u)\)를 조립하여

\[
k^{(4)}=K(720E^2a_6+1440Ea_5+672a_4)
\]

를 쓴다. 두 구현은 같은 원 입력·fit·Decimal의 scalar log/exp를 공유한다. 독립 물리 데이터로 세지 않았다.

정확한 Fraction 산술에서는 프로파일 모멘트 10개와 \(\phi=E^n,\ n=0,\ldots,6\)의 도함수 관계를 확인했다. 이어 같은 비영 A를 사용하는 cubic/quartic toy의 문턱을 사차까지 직접 형식 전개했다.

| toy, 분지 | 정확한 \(A\) | 정확한 \(C\) | \(D_4^{p-u}\) |
|---|---:|---:|---:|
| cubic, 상단 | \(43/20\) | \(11/10\) | 0 |
| cubic, 하단 | \(37/20\) | \(9/10\) | 0 |
| quartic, 상단 | \(873/400\) | \(451/400\) | \(-32/142065\) |
| quartic, 하단 | \(753/400\) | \(371/400\) | \(-32/116865\) |

모든 toy에서 삼차까지의 프로파일 차이는 정확히 0이었다. Quartic 응답 차이는 정확히 \((2/7875)\delta^4\)였고, normalized 식과 \(N-AQ\) 식의 근 잔차는 0–4차에서 모두 0이었다. \(1/24\)를 빠뜨린 식과 분모의 A를 빠뜨린 식은 각각 두 quartic 분지에서 오답으로 검출했다. Cubic의 모든 허용 폭에서의 동일성은 유한차수 관측의 외삽이 아니라 다항식 평균의 직접 항등식으로 증명했다.

## 8. 실제 실행과 재현

| 항목 | 첫 실행 | 새 경로 재현 |
|---|---:|---:|
| 새 프로그램 main | 1 | 1 |
| 고정 검사 | 79/79 PASS | 79/79 PASS |
| 새 물리 \(k^{(4)}\) 평가 | 8 | 8 |
| 사용한 기존 에너지 노드 | 4 | 동일한 4 |
| 새 물리 에너지 노드·근 | 0 | 0 |
| 원 프로그램 import/main/suite | 0 | 0 |
| 실제 종료 코드 | 0 | 0 |
| 실제 wall time | @@FIRST_WALL@@ s | @@REPLAY_WALL@@ s |

79개에는 이론·수치 비교 @@SCI_CHECKS@@개와 입력·산술환경·회계 검사 @@META_CHECKS@@개가 포함된다. 두 실행은 같은 79개를 수행했으며 별개의 158개 과학 검증이라고 세지 않는다.

계약대로 Decimal80 / ROUND_HALF_EVEN과 고정 정규화 허용치 \(10^{-60}\)를 사용했다. 실제 최대 오차는

\[
\max|\mathrm{difference}|/\mathrm{fixed\ scale}
=4.6819296\times10^{-74}.
\]

이는 두 수치 표현의 차이이며 물리 오차의 상한이 아니다. 결과를 본 뒤 허용치·precision을 바꾸지 않았다. precision sweep이나 구간 연산을 했다는 주장도 하지 않는다.

최소 runtime 10파일과 manifest를 ZIP에서 새 디렉터리로 복원했다. 파일의 SHA256·크기·mode를 확인한 뒤 같은 프로그램을 한 번 실행했고, 첫 결과와 재현 결과의 **69,411 bytes 전체 및 JSON 내용이 동일**했다. SHA256은 @@RAW_SHA@@다. 같은 호스트와 Python @@PYTHON@@을 사용했으므로 독립 물리 증거의 credit은 0이다. 원격 저장소에서 전체 ZIP을 다시 내려받아 복원했다는 뜻은 아니다.

실제 기록은 [첫 실행](../execution/first/EXECUTION.json), [재현 실행](../execution/replay/EXECUTION.json), [복원·비교 receipt](../portability/REPLAY_RECEIPT.json)에 있다. [고정 프로토콜](../contributions/numerics/PROTOCOL.json)과 [실행 코드](../contributions/numerics/quartic_profile_split.py)는 입력 경로·허용치·79개 ID·횟수를 보존한다. 이번 루프의 first/replay 예산은 모두 사용했다.

## 9. 실패·정정과 근거의 수준

과학 main·물리 평가·toy 실행에서는 실패나 재시도가 없었다. 첫 실행 전에 직접 유도한 A·C·D4 oracle을 기존 검사에 추가하고 gap 표시 필드를 보강했으며, 이전 대기 버전도 보존했다. 이론 기여의 최초 ZIP member 선택에서는 경로 suffix가 중복되어 metadata assertion이 실패했다. 정확한 archive member 경로로 수정했으며 과학 실행 0인 상태의 원 실패·수정 기록을 남겼다. 숫자나 허용치를 바꾸는 수정은 아니었다.

| 근거 수준 | 해당 결과 |
|---|---|
| derived | 공통 삼차, C4 사차 전달, C3 한계 반례, 퇴화 때 5차 항 가능성, 비영 A 식 |
| derived from fixed source | 현재 커널의 해석성, 두 도함수 표현, 정확 프로파일 쌍 |
| numerically checked | 네 저장점의 사차 도함수와 두 문턱의 사차 차이 계수 |
| implementation-verified | 고정 입력·79개 검사·8+8회 호출·분리 경로 raw 재현 |
| unresolved | J·정확근의 오차 enclosure, 수치 나머지 상계, 유효 폭, 전역 순서 |

정확한 주장별 근거는 [주장 목록](../evidence/CLAIM_LEDGER.json)과 최종 판정에 연결했다. 해시와 재현 일치는 증명·물리 모델 타당성·승인 권위를 대신하지 않는다.

## 10. 다음에 풀 문제와 유지 상태

이번 결과는 사차 차이의 방향과 크기를 제공한다. 다음 물리 질문은 **이 국소 계수를 실제 유한 폭의 정량적 비교로 옮길 수 있는가**다. [PHYS32 인수문](../next/PHYS32_NEXT_HANDOFF_KO.md)은 커널의 연속성 모듈러스 또는 고차 도함수 상계, 근의 양의 기울기 하한을 연결하여 나머지와 충분조건을 구하는 제한된 과제를 제안한다. PHYS32의 새로운 정리·수치 실행은 아직 수행하지 않았다.

물리 admission은 **HOLD**다. 원래 [160,161] FAIL, tick 160, auxiliary escape FAIL, HH/RCT/CR OFF, precision atomic PARKED를 유지한다. production source·default·runtime 변경은 0이다. 이번 문턱 국소 결과로 기체 이력·우주론 재이온화·원자 데이터 정확도를 승격하지 않는다.

## 11. 출처와 고정 상태

현재 입력 commit은 **5ac0bceaac2629682f777bc8223fbba07be810b9**, 실제 tree는 **22216f47b19bdb481e8cc16722222272d64edf34**다. 현재 완전 tree와 보존 source를 대조하여 pinned 7파일이 일치함을 확인했다. Source subtree는 **cb69b4736dd046e4675557577eb8e0ead037d1f3**이며 [SOURCE_MANIFEST.json](../SOURCE_MANIFEST.json)에 식별자를 남겼다. 새 문서 게시의 실제 commit과 PR 상태는 완료 후 생성되는 별도 publication receipt로 확인한다.

적용한 연구·코딩 하네스는 명시적으로 호출된 physmath-research-loop의 GPT-6 Astra v4.0.0이다. 신뢰 가능한 현재 모델 표시는 GPT-6 Astra Pro이며 모델 전환·성능 비교를 수행하지 않았다. 하네스 구조 검사나 파일 읽기를 물리 검증으로 세지 않았다.

원 photoionization fit의 일차 출처는 [Verner et al. (1996), ApJ 465, 487](https://arxiv.org/abs/astro-ph/9601009v2) 및 [저자 자료 페이지](https://www.pa.uky.edu/~verner/photo.html)다. 이번에는 초록·서지·저자 페이지를 직접 확인했고 논문 전체를 읽었다고 표시하지 않는다. 실제 계산을 통제하는 식은 고정 Rust source와 보존 PHYS29 수학적 커널 정의다. 이번 모멘트·문턱 정리는 직접 유도이며 해당 논문이 증명한 결과로 귀속하지 않는다. 문헌 전체에 대한 신규성 검색이나 fit 정확도 재인증은 수행하지 않았다.

---

"""

branches = RAW["physical_quartic_profile_difference"]
star, zero = branches["upper_root"], branches["lower_root"]
node_rows = []
for key, label in [("a", "a"), ("v_star", "v_*"), ("u_zero", "u_0"), ("b", "b")]:
    item = RAW["new_fourth_derivative_outputs"]["log"][key]
    node_rows.append("| " + label + " | " + format(Decimal(item["retained_energy_eV"]), ".15f") + " | " + format(Decimal(item["k4_s-4_eV-4"]), ".15E") + " |")
scientific_prefixes = ("PROFILE.", "OPERATOR.", "PHYSICAL.", "TOY.")
science_checks = sum(row["id"].startswith(scientific_prefixes) for row in RAW["checks"])
replacements = {
    "@@NODE_ROWS@@": "\n".join(node_rows),
    "@@CSTAR@@": format(Decimal(star["retained_C_s-4_eV-2"]), ".15E"),
    "@@CZERO@@": format(Decimal(zero["retained_C_s-4_eV-2"]), ".15E"),
    "@@HSTAR@@": format(Decimal(star["paths"]["log"]["H4_s-4_eV-4"]), ".15E"),
    "@@HZERO@@": format(Decimal(zero["paths"]["log"]["H4_s-4_eV-4"]), ".15E"),
    "@@DSTAR@@": format(Decimal(star["paths"]["log"]["D4_eV-2"]), ".18f"),
    "@@DZERO@@": format(Decimal(zero["paths"]["log"]["D4_eV-2"]), ".18f"),
    "@@DGAP@@": format(Decimal(RAW["descriptive_gap_quartic_difference"]["paths"]["log"]), ".21f"),
    "@@FIRST_WALL@@": format(FIRST_EXEC["wall_seconds"], ".6f"),
    "@@REPLAY_WALL@@": format(REPLAY_EXEC["wall_seconds"], ".6f"),
    "@@SCI_CHECKS@@": str(science_checks),
    "@@META_CHECKS@@": str(len(RAW["checks"]) - science_checks),
    "@@RAW_SHA@@": ident(RAW_PATH)["sha256"],
    "@@PYTHON@@": RAW["python_version"],
}
front = FRONT
for key, value in replacements.items():
    front = front.replace(key, value)
if "@@" in front:
    raise ValueError("Unresolved report substitution")
# The appendix proof content is preserved; only internal link targets are remapped.
proof_path = ROOT / "contributions/theory/DERIVATION_KO.md"
proof = proof_path.read_text().replace("](../../", "](../")
for name in ["THEORY_CLAIMS.json", "PROVENANCE.json", "PRE_FREEZE_EVENTS.json"]:
    proof = proof.replace("](" + name + ")", "](../contributions/theory/" + name + ")")
kernel_path = ROOT / "contributions/kernel_scope/KERNEL_REGULARITY_AND_PROFILES_KO.md"
kernel = kernel_path.read_text()
report = front + "# 부록 A. 전체 한쪽 전개·근 전달·반례 증명\n\n" + proof + "\n\n# 부록 B. 실제 고정 커널의 정칙성과 프로파일 구성\n\n" + kernel
report_path = ROOT / "report/PHYS31_REPORT_KO.md"
report_path.write_text(report)

items = []
for group, origin in [(THEORY, "contributions/theory/THEORY_CLAIMS.json"), (KERNEL, "contributions/kernel_scope/KERNEL_PROFILE_CLAIMS.json")]:
    for claim in group["claims"]:
        items.append({"id": claim["id"], "evidence_status": claim["evidence_status"], "origin": origin, "claim": claim["claim"], "source_claim": claim})
items.extend([
    {"id": "NC31-01", "evidence_status": "numerically checked", "claim": "Both separately assembled k4 expressions at four retained nodes agree under frozen Decimal80/fixed-scale tolerance1e-60; all four finite outputs are positive, without rigorous sign or atomic/J uncertainty certification.", "evidence": ["contributions/numerics/QUARTIC_PROFILE_FIRST.json:new_fourth_derivative_outputs", "contributions/numerics/PROTOCOL.json"], "limitations": ["Fixed serialized inputs and shared Decimal scalar primitives", "No interval or whole-support sign certificate"]},
    {"id": "NC31-02", "evidence_status": "numerically checked", "claim": "For the P4-minus-uniform pair, the retained-point same-A quartic differences are the two negative D4 values in the actual raw result; normalized and independent cached-lower-value numerator quotients agree.", "values": branches, "evidence": ["contributions/numerics/QUARTIC_PROFILE_FIRST.json:physical_quartic_profile_difference"], "limitations": ["No exact-zero root or J enclosure", "No valid positive-width interval"]},
    {"id": "NC31-03", "evidence_status": "numerically checked", "claim": "The cached algebraic gap coefficient D4_lower-D4_upper is positive for both numerical paths; this is a descriptive local coefficient rather than a new finite-width calculation or sign certificate.", "value": RAW["descriptive_gap_quartic_difference"], "evidence": ["contributions/numerics/QUARTIC_PROFILE_FIRST.json:descriptive_gap_quartic_difference"]},
    {"id": "NC31-04", "evidence_status": "numerically checked", "claim": "Exact Fraction profile moments, seven polynomial operator cases, cubic equality and quartic same-A formal root differences pass; both deliberately missing24 and droppedA formulas are rejected.", "evidence": ["contributions/numerics/QUARTIC_PROFILE_FIRST.json:exact_profile_moments", "contributions/numerics/QUARTIC_PROFILE_FIRST.json:exact_operator_checks", "contributions/numerics/QUARTIC_PROFILE_FIRST.json:exact_polynomial_toys"], "limitations": ["Toy constants and variables are dimensionless; not physical root runs"]},
    {"id": "IC31-01", "evidence_status": "implementation-verified", "claim": "Exactly one first process and one new-path replay each pass all79 frozen checks and preserve ten runtime files; scientific raw bytes and JSON are identical.", "evidence": ["execution/first/EXECUTION.json", "execution/replay/EXECUTION.json", "portability/REPLAY_RECEIPT.json"], "limitations": ["Same host/Python/input lineage", "Independent physical-data credit0"]},
    {"id": "IC31-02", "evidence_status": "implementation-verified", "claim": "The complete allowed execution budget is spent: two new mains and16 physical k4 calls at four retained nodes, zero new nodes/roots/lower-order physical outputs/old-module imports or old-suite runs.", "evidence": ["portability/REPLAY_RECEIPT.json:all_event_totals_excluding_unique_nodes"], "limitations": ["Auxiliary phi series are counted separately", "No additional science execution authorized in this closed work unit"]},
    {"id": "NEXT31-01", "evidence_status": "conjectural", "claim": "PHYS32 is proposed to turn local quartic splitting into a quantitative finite-width remainder/conditioning statement under explicit assumptions; no PHYS32 theorem or numerical execution is claimed.", "evidence": ["next/PHYS32_NEXT_HANDOFF_KO.md"], "status": "PROPOSED_NOT_RUN"}
])
ledger = {"task": "REI-PHYS31-20261011", "role": "Owner candidate claim integration; distinct final decision separate", "claim_count": len(items), "claims": items, "physical_admission": "HOLD", "proof_sources": ["contributions/theory/DERIVATION_KO.md", "contributions/kernel_scope/KERNEL_REGULARITY_AND_PROFILES_KO.md"], "no_final_decision_preclaim": True}
write_json(ROOT / "evidence/CLAIM_LEDGER.json", ledger)
summary = {
    "task": "REI-PHYS31-20261011",
    "scientific_results": "Equal mu2 implies common cubic jet; C4 first-possible quartic coefficient difference; fixed-source analytic kernel and finite-point nonzero quartic coefficients",
    "decision_authority": "independent/DECISION_REVIEW.json (separate actual reviewer record)",
    "physical_admission": "HOLD",
    "contract": ident(ROOT / "PHYSICS_CONTRACT.json"),
    "input_commit": CONTRACT["input_commit"],
    "input_tree": CONTRACT["input_tree"],
    "profiles": RAW["exact_profile_moments"],
    "formula": "D4=-Delta_mu4*H4/(24*C)=-H4/(945*C) for P4-minus-uniform; Wp-Wu=D4*delta^4+o(delta^4)",
    "units_D4": "eV^-2",
    "new_k4": RAW["new_fourth_derivative_outputs"],
    "branch_coefficients": branches,
    "gap": RAW["descriptive_gap_quartic_difference"],
    "first_summary": RAW["summary"],
    "check_breakdown": {"math_physics_comparisons": science_checks, "input_arithmetic_environment_ledger": len(RAW["checks"]) - science_checks, "same_set_replayed": True},
    "replay": {"status": REPLAY["status"], "raw_byte_equal": True, "raw": REPLAY["replay_raw"], "runtime_payloads": 10, "same_host_same_python": True, "independent_physical_data_credit": 0},
    "execution_counts": REPLAY["all_event_totals_excluding_unique_nodes"],
    "unique_retained_physical_nodes_across_runs": 4,
    "limitations": CONTRACT["exclusions"],
    "protected": CONTRACT["protected"],
    "next": {"task": "PHYS32", "status": "PROPOSED_NOT_RUN", "path": "next/PHYS32_NEXT_HANDOFF_KO.md"},
}
write_json(ROOT / "report/PHYS31_RESULTS_SUMMARY.json", summary)
assembly = {
    "task": "REI-PHYS31-20261011", "created_utc": datetime.now(timezone.utc).isoformat(),
    "report": ident(report_path), "first_raw": ident(RAW_PATH), "theory_source": ident(proof_path),
    "kernel_source": ident(kernel_path), "script": ident(Path(__file__)),
    "appendix_changes": "Only internal theory link target remapping; no proof formulas or claims changed. Source contribution authorship/time status preserved.",
    "source_result_handling": "Exact raw strings preserved in summary JSON; decimal formatting only for display. No scientific module import/evaluation, integration, roots or check reruns.",
    "claim_count": len(items), "new_scientific_executions": 0,
}
write_json(ROOT / "evidence/REPORT_ASSEMBLY.json", assembly)
print(json.dumps({"report": str(report_path), **ident(report_path), "claim_count": len(items), "science_comparisons": science_checks, "metadata_checks": len(RAW["checks"]) - science_checks, "new_science_executions": 0}, ensure_ascii=False))
