# C2g 등록된 전자 기준 계산의 후처리

`analyze_reference.py`는 물리 고유값 계산을 실행하지 않는다. 등록된 두 실행 배치의 성공 영수증, 원래 과제 12개, rank별 소유권, 코드·계약 해시, 실제 NPZ 바이트를 먼저 대조한다. 배치당 독립 고유근 54개가 모두 있어야 분석한다. 한 R·수준에 m=0 여섯 근과 |m|=1 세 근을 묶고, ±m를 각각 복원하여 선택 5열과 guard 7열을 모두 검사한다.

```sh
python code/analyze_reference.py --manifest contract/PHYSICAL_TASKS.json \
  --review review/PHYSICAL_LAUNCH_REVIEW.json \
  --layout numpy_serial_1x1=/absolute/numpy.json \
  --layout native_mpi_2x1=/absolute/native.json \
  --output /absolute/new/ANALYSIS.json
```

각 배치의 여섯 상태 묶음은 모든 원래 FEM 반지름 매듭과 관측량 경계 r=16의 합집합으로 만든 같은 물리 격자에 사상된다. 등록 격자는 반지름·eta·phi 차례로 7·32·5, 검증 격자는 9·40·7이다. 서로 다른 격자의 샘플 벡터를 직접 내적하지 않는다. 대신 각 격자 안에서 계산한 5×5 R간 내적과 r² trace를 비교한다.

선택 프레임 V에는 G=V†WV의 대칭 역제곱근 C를 명시적으로 적용한다. r² trace는 tr(C†V†Wr²VC), 외곽층 지표는 C†V†W1_[16,20]VC의 최대 고유값이다. 두 값은 선택 공간의 기저 변경에 불변이다. 외곽층 지표는 상자 바깥 확률의 오차 상한이 아니다. 원래 Gram 오차와 교정 크기도 그대로 보고한다.

R간 비교, coarse→medium→fine 비교, 두 구현 배치의 같은 과제 비교는 같은 W에서 수행한다. 거의 같은 공간의 projector 거리는 sqrt(1−sigma²)의 상쇄를 피하는 가중 잔차 SVD로 구한다. C2f 검증과 polar transport 호출 결과를 별도로 보존한다. 알려진 guard 충돌 등으로 transport가 거부되더라도 관측된 수치와 거부 이유를 버리지 않는다. 단계별 임계값은 사전등록 파일에서 읽고 변경하지 않으며, 첫 실패와 전체 실패 목록을 함께 남긴다.

임베딩 LRU는 최대 세 묶음을 보관한다. 분석 결과에는 프레임 전체를 넣지 않고 작은 행렬·수치·출처만 기록한다. 결과와 출처 결합 JSON은 생성 전용이며 fsync를 수행한다. 실행별 벽시계 시간과 assembly/eigensolve 시간의 합은 기록하지만 한 번의 numpy 직렬 대 native OpenMPI 측정은 backend와 병렬성의 효과가 섞여 있어 독립적인 backend 가속률이나 NCP64 확장성으로 해석하지 않는다.

모든 결과에서 continuum·무한차원 전체 H·PDE 잔차 인증은 false이고, 전체 C2는 닫지 않으며 scientific_PROMOTE=HOLD와 Eq55=NOT_RUN을 유지한다. 유한 기저 정밀도 탐색의 실패는 구현 검증 결과와 구분한다.
