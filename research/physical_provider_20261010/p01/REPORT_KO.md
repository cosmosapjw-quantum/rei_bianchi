# P01 — production conditional consumer

`PASS_SCOPED`: production `SourceBoundConditional`은 source hash preflight 뒤에만 실행되며, 2904-node warm H/He interval을 17 epochs에 걸쳐 실제 production Rust RHS로 적분했다. `PhysicalHistory`는 변경하지 않았고 계속 `PhysicalExecutionNotImplemented` 경계를 유지한다.

최종 실행은 257 RHS 호출에서 frozen reference와 최대 scaled state 차이 `1.0471941498209426e-15`를 보였다. local photon/energy ledger 최대값은 각각 `7.000969126733937e-15`, `1.7556755934167118e-16`이며, 모두 `1e-9` 계약 한계 안이다. source, opacity, gas 상태는 같은 stage state를 소비한다. `N_rel=a_rel^3 n`, `E=qR`, `R^-3` source Jacobian, SI boundary, thermal/binding 분리, shear work, recombination escape ENERGY-only 의미를 유지한다.

독립 review는 BLOCKER/MAJOR/MINOR 없이 scoped PASS를 승인했다. 이 결과는 frozen warm primary-only Case-A escape model의 production consumer integration만 승인한다. REC cold IC, diffuse/OTS, secondary/Compton, 50 keV 위, long history, continuum/global EoR, F04/F08 및 관측 claim은 여전히 HOLD다.

다음 최소 work unit은 목표에 따라 갈린다: cold REC→REI가 필요하면 P02의 source-pinned REC IC와 low-temperature provider, full photon history가 필요하면 P03의 diffuse/OTS·secondary/Compton·high-energy boundary/error contract를 먼저 선택해야 한다.
