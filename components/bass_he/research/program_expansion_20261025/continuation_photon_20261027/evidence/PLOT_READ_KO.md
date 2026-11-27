# PHOTON05 생성 그림의 root 판독

Root는 2026-10-27 실행의 실제 `evidence/plot/PHOTON05_NATIVE_RECOIL.png`를 이미지 도구로 열어 읽었다. PNG SHA256 `fdb59dffa0b8f74a003ab439c47d0e48ab925739b983636b050f1bf81ba009d3`, SVG `840b6c288881415b826f05b0bb9f75ea9e8a29fa6466b929babd873471d77840`이다. `PLOT_DATA.json`은 검증의 `SAVED_PLOT_DATA.json`과 원바이트가 같으며 SHA256은 `923c9349019d7061a4d6e71343ef6930b9db6b95b82f16085f725f18b618d755`다.

왼쪽 패널은 EXFOR의 213/258/330 MeV, CM 46/61/73/87도에서 계산한 두 deuteron의 lab 운동에너지다. 같은 입사 에너지에서 + 딸핵의 운동에너지는 각도가 커지며 내려가고 − 딸핵은 올라가며, 90도에 가까워질수록 두 값이 접근한다. 이는 boost 항이 cos(theta)에 비례한다는 유도와 맞는다. 두 딸핵의 +/−는 수학적 label이다. 서로 다른 입사 에너지 곡선의 교차는 사건 확률이나 rate의 비교가 아니다.

오른쪽 패널은 같은 상대론적 운동량에 비상대론적 에너지식을 사용했을 때의 상대 초과 `(K_NR-K)/K`다. 저장 자료에서 약 1.9–5.2%의 양수이며, 새 비상대론적 solver 실행 결과가 아니다. 축, 범례, 마커 및 두 패널의 읽기에 가려진 항목은 발견하지 않았다. 곡선의 선은 native 좌표를 잇는 시각적 안내이며 DCS 보간이나 측정된 각분포가 아니다. phi=0은 명시적인 대표 평면이다. 질량 covariance나 source physical error band는 표시하지 않았다.

**그림 실행 판정은 FAIL이다.** child exit0, wall4.406950156 s와 과학 함수 호출0이지만, child+runner CPU4.40726504 s가 4 s 한도를 넘었다. 이 시각 판독은 그림 내용에 대한 관측이며 실패를 PASS로 바꾸지 않는다. 원본 START/FINISH/stdout/stderr와 생성 파일을 보존하고 새 실행을 하지 않았다. Matplotlib의 쓰기 불가능한 기본 설정 폴더와 임시 캐시 경고는 실제 관측되었지만, 그 경고가 초과의 확정 원인이라는 인과적 측정은 없다. 재실행·profiling·budget transfer는 수행하지 않는다.

24-method 수치 검증은 별도의 4 CPU s /15 wall s allocation에서 PASS했다. 이 결과의 조건부 과학적 사용과 plot resource gate 실패를 분리한다. Native 저장 출력에 포함된 adapter flux0은 호출자가 넣은 예시 입력이며 실제 물리 사건률0의 추론이 아니다. 전체 작업의 clean completion이나 physical production을 승인하지 않는다.
