# R4 — 세 가지 consumer와 두 판별 사건

원자 좌표를 \(N=(N_g,N_s,N_p,N_c)^T\), coarse 좌표를
\[
P N=(N_g+N_s+N_p,N_c,N_c)^T
\]
로 둔다. 마지막 행은 thermal free electrons다. Fast \(\zeta\)는 별도이며 선택된 source 거래에서 증감 0이다.

## 후보 A: Lyα 수만 HI 생성으로 사용

한 번의 하향 Lyα 사건은 \(\nu_\alpha=(1,0,-1,0)^T\)다. 따라서 \(P\nu_\alpha=0\)이다. 이 사건에서 photon count는 증가하지만 전체 중성 원자는 그대로다. 이는 후보 A를 이번 consumer로 선택하지 않을 직접 판별 예다. 모든 재결합 모델에 대한 strong no-go가 아니다.

## 후보 B: 원자 수만 coarse-grain

\(P\)는 원자와 thermal charge를 보존한다. 그러나 \(2p\to g\)에서 사라지는 들뜸 에너지를 H1I/H1II만으로는 기록하지 못한다. Source의 atomic energy를 그대로 버리거나 gas heat로 보내면 원래 source transaction과 다른 모형이 된다.

## 후보 C: coarse 수와 atomic-storage/convention port

Source atomic energy \(U_B\)와 target ion reference \(\chi_R\)를 SI로 명시하고
\[
U_h=U_B-\chi_R N_c
\]
를 별도 port로 둔다. 이는 상태의 에너지 표현에 대한 구성적 보완이다. Native ground/ion binding과 \(U_h\)의 합이 원래 \(U_B\)다. Source already-J 에너지는 재변환하지 않는다.

한 번의 continuum→2p 사건 \(\nu_{cp}=(0,0,1,-1)^T\)에는
\[
P\nu_{cp}=(1,-1,-1)^T,\qquad
\Delta U_h=\epsilon_{21}^B-\epsilon_I^B+\chi_R.
\]
그 뒤 Lyα 사건의 \(\Delta U_h=-\epsilon_{21}^B\)를 더하면
\[
\Delta U_h^{cp+\alpha}=\chi_R-\epsilon_I^B.
\]
중간 들뜸 에너지가 정확히 소거되고 두 owner의 ion reference 차이가 남는다. 두 에너지 기준까지 같으면 이 완결된 경로의 hidden port는0이다. 두 사건의 photon/thermal energies는 source에서 한 번만 유지한다.

## 선택

후보 C를 구현한다. 입력은 실제 저장된4-state event increments와 five-sector energies다. Photon count, source alternatives, 다른 공급자의 recipient density를 추가 합산하지 않는다. \(V_0=1\,{\rm m^3}\), source right-volume ratio, actual recipient \(b\)와 EOS의 공급 여부를 타입으로 유지한다.

이후 단계 ZIP은 모든 작은 원문을 포함하는 정확한 UTF8 source capsule과 manifest를 담는다. 큰 불변 원문은 같은ZIP의 별도 원문 파일로 포함한다. 각 capsule의files[].text로 원래 상대경로를 복원할 수 있으며, 최종 source ZIP은 실제 개별 파일 전체를 담는다. 기존 R1–R3 ZIP은 다시 만들지 않는다.
