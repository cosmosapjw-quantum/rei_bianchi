# 단일 endpoint gas residual와 허용 trial

독립 판정 `PASS_GAS_RESIDUAL_VALUE_AND_ADMISSIBLE_TRIAL_SCOPED`. 저장된 incident photon node와 endpoint 기하를 고정하고, 매 gas trial의 동일한 흡수값을 실제 CELL RHS에 전달했다. 원자물리 모델이나 source를 바꾸지 않았다.

29개 검사 PASS. Energy residual identity의 최대 오차는1.855586124080583e-16. 첫 theta=1 trial의 residual norm은2.3805513472150953e-7, 계약 상한은0.0003649467431164878이고 온도는19.990268129326424K이다. 이것은 admissible decreasing trial이며 수렴한 gas 해나 채택된 timestep이 아니다. radiation work는 gas energy ledger에 다시 더하지 않았다.

Native2, SIGMA4/384energies, CELL5, positive map8, trial1을 사용했다. 실제 fixture는 r=0이고 nonzero shear history validation이 아니다. 다음 노드는 같은 endpoint의 제한된 nonlinear correction이며 global scientific admission은 HOLD이다.
