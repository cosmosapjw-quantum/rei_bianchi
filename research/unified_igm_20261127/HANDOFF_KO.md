# 기존 스레드별 인계

공통 작업 브랜치는 `cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127`이다. 각 블록은 해당 스레드에서 독립적으로 복사해 사용할 수 있다.

## REI · 원 AXBI/AX11

```text
cosmosapjw-quantum/rei_bianchi의 research/rei-unified-microphysics-20261127에서 research/unified_igm_20261127/DAG.json과 results/SECOND_INTEGRATION.json을 읽어라. 원본 시나리오의 완료 수는 10/17 및 28/88, AX11은 부분 완료다. E16/mu8 T1의 기존 전구간과 T2의 실제 공유 체크포인트를 인수하고 같은 IC의 ZERO/PLUS T2를 남은 구간에서 재개하라. 출력 여유공간과 compact checkpoint를 먼저 산정하라. 고정 a·동일 고유시간의 HII/T 및 중수소 응답에 대해 독립 시간·각도·주파수 오차를 보고하라. 각 턴 시작에 대상 관측량, 끝에 수치 변화·오차·다음 물리 판별을 기록하라.
```

## BASS · R118 기하와 복사

```text
이제 소유 저장소는 cosmosapjw-quantum/rei_bianchi, 브랜치는 research/rei-unified-microphysics-20261127이다. components/bass_rec/bass와 research/r118c3t_cell_moments/NEXT.md에서 C3U를 진행하라. 수락된 상태에서 변하는 coframe과 광자 출생을 적용하고 scalar-mean 소유권 및 rollback을 검증한 뒤 32 ray 이상, 주파수와 시간 독립 정련으로 H/He와 REC가 소비하는 방향장 차이를 측정하라. 같은 z에서의 DII 대비와 같은 고유시간 대비를 별도로 보존하라.
```

## REC · 재결합

```text
cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127의 components/bass_rec/rec에서 작업하라. HMLA z=20 초기상태의 조성·단위·clock과 z=1100 matched REC 출력을 보존하라. R118-C3U에서 REI와 동일한 방향 광자 분포를 실제로 소비하게 하고, donor 경계와 scalar mean의 일치 및 수락/기각 후 상태를 측정하라. 결과를 중앙 DAG의 native-owner 및 C3U에 연결하라.
```

## WU088_HH · H/D

```text
cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127의 components/wu088_hh와 rei_bianchi.microphysics.hh가 H/D 작업 위치다. 원래 다섯 AXBI 곡선의 +0.01 대 ZERO 동일 고유시간 최대 차이는 +1.72114e-5이며 한 점 건너 표본화 오차는 피크의 17%다. 다음 AX11 native 출력으로 그 오차를 줄여라. 유한 D/H에는 보존되는 x+ηy와 양성 경계를 적용하고 D 광이온화·재결합을 추가할 때 입력·소유권을 명시하라. 기준 tracer와 능동 gas feedback을 별도 결과로 기록하라.
```

## BASS_HE · 헬륨 광자

```text
cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127의 components/bass_he와 rei_bianchi.microphysics.he에서 진행하라. 기존 F05 92,160행의 한 광자 공동제약과 실제 수락된 H/He 광자에서 종별 결합열 장부를 인수하라. F05 공급자가 이미 지불한 사건은 다시 적분하지 마라. 이동하는 선광자가 필요한 다음 실험에서는 방출·탈출·다음 흡수의 사건 ID와 proper-time을 맞추고, 껐을 때 회복되는 host 관측량을 제출하라.
```

## bass_cr · 비열적 전자

```text
cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127의 components/bass_cr와 rei_bianchi.microphysics.cr가 공급자다. z=7.992469의 실제 gas 수신기에 전달된 1e10 s window의 fast 전자 스펙트럼을 사용하라. 수신기 조성과 맞는 열화·이차 이온화·가열 커널을 구한 뒤 별도 초기조건의 CR-ON 이력을 적분하고 원 조건의 OFF와 비교하라. PHYS02의 100 K 표를 다른 조성의 gas에 곧바로 넣지 마라. binding·fast·threshold offset·열화를 서로 대조하라.
```

## VigilODE · 수치진단

```text
IGM 연결은 cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127에서 담당한다. 원 AX11 PR189 연결은 측정된 제어기 비교의 범위로 유지하라. 기존 WU/HE 진단의 a21d5739 핀과 별도의 최신 M2 계열을 구별하라. 실제 paired HII/T/DII 오차 또는 같은 허용오차에서 T2 완주 비용이 바뀌는 경우만 원 DAG로 되돌려라.
```

## htt_base · 공동 검증 기록

```text
공동 검증의 현재 실행 소유자는 cosmosapjw-quantum/rei_bianchi:research/rei-unified-microphysics-20261127이다. htt_base의 R118-C2K는 시점이 고정된 중간 근거다. CENSUS.json과 DAG.json을 읽고 R118-C3T, 단일 checkout의 matched-time 결과와 열려 있는 C3U/AX11을 반영하라. 과학 DAG 계수는 중앙 REI에만 기록하라.
```
