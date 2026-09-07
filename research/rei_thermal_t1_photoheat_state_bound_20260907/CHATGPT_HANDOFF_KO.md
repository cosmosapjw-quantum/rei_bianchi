# REI thermal_t1_final photoheating 부분 경계 — source-bound derivation

STATUS: **RESOLVED_PHOTOHEAT_STATE_PARTIAL_DERIVED / THERMAL_INVERSE_OPEN**

PR #80의 실제 G2b endpoint scalar 결과를 수용했다. `D_lo>0`, G01--G06 6/6 PASS,
exit 0, timeout 없음은 기존 실행 결과이며 여기서 재실행하지 않았다.

이번에는 PR #80의 source-site를 보존했다. 그 endpoint는 second-half
`thermal_t1_final` corrected population에 연결되므로 predictor/gamma/corrector
F0/F1 population site에 곧바로 이식하지 않았다.

`physical_trial.py`에서 resolved thermal photoheat는

```text
photo.heating_i = EV_ERG * sum node_current[species,group,i] * excess_eV[species,group]
```

이고 이것만 `thermal.solve(... photoheat=photo.heating ...)`에 들어간다.
unresolved subgrid energy는 별도 reservoir다.

첫 forcing cell의 resolved support와 고정 heating moment는

```text
G1   resolved 없음
G2a  HeI only,  E = 5.058090825749249 eV
G2b  HI + HeI,  max E = 31.261852675211813 eV
G3   J = 0 on this cell for fixed-forcing state partial
```

이다.

`U_H=||delta(N_HI/H_H)||_1`, `U_He=||delta(N_HeI/H_He)||_1`,
`U_plus=U_H+U_He`로 두고 기존 상수

```text
L_G2a < 5.7e52
L_G2b < 1.914e52
```

를 재사용하면

```text
||delta Q_res||_1
 <= EV_ERG * [E_HeI,G2a L_G2a U_He + E_HI,G2b L_G2b U_plus]
 < 1.421e42 * U_plus  erg/s.
```

여기서 `Q_res`는 resolved per-node photoheating rate vector다. local fraction norm,
unnormalized count norm, unresolved subgrid output norm이 아니다. node weight나 volume을
다시 곱하지 않았다.

또 `thermal_backends.py`의 balance가

```text
energy - parent_energy - dt*(photoheat - cooling - expansion)
```

이므로, population/T/forcing을 고정한 photoheat channel만 보면

```text
delta balance_photo = -dt * delta Q_res,
||delta balance_photo||_1 <= dt * 1.421e42 * U_plus.
```

이것은 **thermal numerator/residual channel**의 부분 경계다. thermal root 출력 자체의
Lipschitz 상수가 아니다. `delta logT`, `delta T`, `delta energy`까지 가려면 저장
endpoint 위에서 `partial balance/partial logT`의 양의 균일 하한이 추가로 필요하다.
Cooling/expansion의 population-mediated 변화도 별도 항이다.

고정 결과와 전체 증명은 [PROOF_AND_SCOPE.md](PROOF_AND_SCOPE.md)에 있다.
이번 새 node는 source/수식 정적 유도이며 새 project/CAS 실행은 NOT_RUN이다.
같은 assistant의 PHYS-MATH -> PHYS-MATH-CODE 순차 검토이며 독립 인증이 아니다.

NEXT: `REI_THERMAL_T1_PHOTOHEAT_ROOT_INVERSE_BOUND`.
기존 endpoint와 second-half forcing만 읽어 thermal balance의 logT slope를 inclusion
arithmetic으로 하한내라. 양수면 이번 numerator bound와 결합해 photoheat-mediated
thermal output component를 닫고, 0을 포함하면 exact obstruction을 반환한다.
producer/old suite/canonical interval/다른 source site를 재실행하거나 합치지 않는다.

FULL source tube, F0/F1 population owner bound, OTS/atomic 전체 미분, cooling feedback,
thermal total inverse, rho, production/native/first interval/provider는 계속 미완료다.
