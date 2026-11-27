# KINEMATIC08 Wolfram 잔여식의 직접 통분 — 독립 검토 pass1

이 검토는 Wolfram을 다시 호출하거나 Python/CAS 과학 계산을 실행하지 않았다. 실행 스크립트 `SYMBOLIC_CHECK.wl`와 root가 전달한 기존 한 번의 Wolfram 응답을 읽었다. 원 tool 응답 객체는 이 continuation 검토자에게 제공되지 않았으므로 응답 수치는 root의 보존 전사에 귀속한다.

보고된 잔차15개 가운데 tool이 명시적으로0을 반환한 것은12개다. 나머지3개는 서로 같은 mass-shell 유리식2개와 topology 유리식1개다. 아래는 추가 수치 실험이 아니라 각 식의 직접 통분이다.

## Mass-shell 잔차 두 개

\(H=a^2+2ae-4m^2\), \(d=a+2e\)라 놓는다. 두 잔차 각각은

\[
u^2\left[a^2+2ae-4m^2-
\frac{a^3+4a^2e+4ae^2-4am^2-8em^2}{a+2e}\right].
\]

분자는

\[
a(a+2e)^2-4m^2(a+2e)
=(a+2e)\bigl[a(a+2e)-4m^2\bigr]
=dH.
\]

따라서 잔차는 \(u^2(H-dH/d)=0\)이다. 계약상 \(a>0,e>0\)이므로 \(d>0\)이고 분모를 지우는 조작이 적법하다. 같은 식이 두 번 나타났으므로 두 mass-shell 잔차 모두 정확히0이다.

## Topology 잔차 한 개

\[
e^2-\frac{ae^2}{a+2e}-\frac{2e^3}{a+2e}
=\frac{e^2[(a+2e)-a-2e]}{a+2e}=0.
\]

여기에도 같은 양의 분모 조건이 적용된다.

## 결과 표현

정확한 표현은 **Wolfram 출력의 명시적0:12개, 직접 통분으로0을 확인한 미정리 유리식:3개**다. `15개 모두 tool이 literal0을 반환했다`고 쓰면 안 된다. 보고된11개 surd sign 비교는 모두 일치하고, 실제 원격 CPU는 `null`로 유지한다. 사용된 Wolfram 호출 수는 기존1회를 그대로 보존한다.

이 보조 검산만으로 구현 테스트, 자원 한도, empirical 정규화나 physical completion을 인증하지 않는다. 최종 과학 채택은 같은 pass의 실제 repaired-source 테스트·자원·저장 plot 검토를 기다린다.
