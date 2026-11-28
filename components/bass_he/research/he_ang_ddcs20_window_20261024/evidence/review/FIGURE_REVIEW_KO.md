# Root figure review

2026-10-24 UTC, reviewer /root. 생성된 PNG를 직접 표시하여 확인했다.

판정: PASS_SCOPED. 대상은 figures/ddcs20_window.png와 같은 plot invocation에서
생성한 figure_metadata.json이다. 그림을 다시 생성하지 않았다.

- (a)의 가로축은 검출각 degree, 세로축은 원표 DDCS의 10^-19 cm^2/(sr eV)다.
  3,4,5,6 eV의 곡선, 각 node와 원전의 quoted uncertainty를 구별할 수 있다.
- (b)는 angular-window integral J0(E)이며 전체 입체각 적분으로 표시하지 않았다.
- (c–f)의 검은 점과 주황 점은 linear-mu nominal과 linear-theta comparison이다.
  파란 구간은 선택한 cellwise deterministic box extrema로 명시했다.
- 제목에 E0=20 eV, E=3–6 eV, theta=15–120 degree와 axisymmetric model이 있다.
- Footer는 source 1-sigma와 deterministic ranges를 구분하고 unknown covariance,
  omitted reference-DCS error와 scalar마다 서로 다른 extremizer를 명시한다.
- 확인한 표시에서 label, legend와 footer의 잘림이나 겹침은 없고 단위와 구간을 읽을 수 있다.

이 그림은 지정한 window와 보간의 결과를 나타낸다. 전체 각도, event law,
recoil 또는 X1 empirical angular correction의 그림으로 해석하지 않는다.
