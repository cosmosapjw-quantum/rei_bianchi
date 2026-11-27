# HE31 검증용 기존 FLRW donor 선택 복구

**기존 R15/HG97-B FLRW history 1개를 원본 그대로 복구했다.** 새 이력 적분이나 광자 수송은 실행하지 않았다. 이 복구는 12:39 UTC 이후의 새로운 donor 발견과 구별되는 별도 요청이다.

## 실제 복구한 입력

기준 경로는 `recovered/research/broad_history_20261010/evidence/RUN002/flrw_n16384/`다.

| 파일 | bytes | SHA256 |
|---|---:|---|
| history.npz | 1,179,779 | 93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4 |
| COMPLETE.json | 1,312 | bffd7f8fbe5612f2bed99a2ea0b8c3503c53495d85609e85409d22db20d95fa7 |
| STARTED.json | 694 | 14755e5c82407914e93165222bd7d328c68e8a3a9dc4d8dfe93353193404789f |

로컬 investigation/repos의 비제외 파일 목록에서 동일 이름·크기 archive와 대상 history가 없음을 먼저 확인했다. 지정 Dropbox `id:BSpOijBcT10AAAAAAD3yhw`의 `REI_ACCEL01_C02B_FINAL_20261010.zip`을 실제 GET했다. 30,729,916 bytes와 archive SHA256 `3d114d3bea604035e2873b804e965605ea8ff9dc06caebe82e5dadfa735e2857`, Dropbox block content hash가 일치했다.

220개 ZIP member 중 위 3개만 추출했다. 각 파일은 원 RESTORE_MANIFEST의 크기/SHA와 일치하고 history SHA는 COMPLETE의 data_sha256와도 일치했다. manifest scientific commit은 `7530e0239a4d30e99bfeba68d4b4ddc0b78a2c18`, base는 `8d9526a75e85202764e845c7d5d79d7f903e7c55`다. 기존 B1 source note의 최종 delivery receipt pin은 `f66929c23ea3fa6e39dd4808e5b27d136c568a03`이다. 이 세 SHA의 역할을 혼동하지 않는다.

원 model.py, background.py, EXTERNAL_SOURCE_CONTRACT.json의 SHA가 COMPLETE의 identity 및 현재 HE31 worktree의 B1 입력과 모두 일치했다. 원 COMPLETE 상태 `COMPUTED_SCOPED_NOT_YET_REVIEWED`도 그대로 보존했다. 이 선택 복구는 기존 과학 심사를 다시 실행하거나 새로운 수렴 판정을 내린 것이 아니다.

## 구간과 물리적 의미

원 config는 z_i=20, z_f=4, FLRW r=0, T=20000 K, clumping=3, fesc=0.2, 초기 Q=0, h=.6774, Omega_m=.309, Omega_b h²=.0223, Y=.2453이다. 16,384개 셀의 16,385개 edge history다.

Q는 HII filling factor다. 원 closure는 R15 유효 방출률과 HG97 Case-B를 사용하며, HII 영역 안에서 HII+HeII, 바깥에서는 중성 기체를 가정한다. 따라서 명시적으로 다음과 같이 받아들일 수 있다.

- xHII=Q, xHeII=Q, xHeIII=0.
- n_e=(n_H+n_He)*Q.
- nHe/nH=Y/[4(1-Y)].
- HeIII, 잔류전자, 열진화, ionizing spectrum을 별도로 계산한 이력이 아니다.

ne_cm3와 nH_cm3는 proper cm^-3이다. SI-facing adapter는 m^-3로 변환할 때 1e6을 한 번 적용해야 한다. t_s는 원 배경의 초기점에서 센 proper/normal seconds이고 H_s는 s^-1이다.

제한된 endpoint readback 결과는 다음과 같다.

| 값 | z=20 | z=4 |
|---|---:|---:|
| Q | 0 | 1 |
| nH_cm3 | 0.0017503056440672947 | 2.362468475417468e-5 |
| ne_cm3 | 0 | 2.5544366472141768e-5 |
| H_s | 1.1745060465360033e-16 | 1.3765098082529282e-17 |
| t_s | 0 | 4.3041834359854584e16 |

**초기 ne=0은 이 원본 closure의 실제 값이다.** C14의 기존 strictly-positive xe guard를 그대로 재사용하면 이 합법적인 endpoint를 거부한다. 새로운 adapter는 비음수 밀도를 지원하고, 검사를 통과시키기 위해 임의 epsilon을 더하거나 초기점을 삭제해서는 안 된다.

이 입력은 z=4까지만 덮는다. z=2까지 coverage가 필요한 호출에서는 명시적으로 domain 부족을 표시해야 한다. 기존 optical-depth cell measure를 사용하는 경로와 순간 ne 보간 경로도 구별한다. 이 작업은 ne 준비의 실제 입력을 제공하며, z=2까지 donor 동역학이 완료됐다는 뜻이 아니다.

## 근거 파일

`DONOR_RECOVERY.json`에 원 archive identity, 선택 추출 hash, 원 config, 배열 schema, endpoint와 source match를 저장했다. 공개 산출물에 임시 download URL이나 private transcript를 포함하지 않았다.

