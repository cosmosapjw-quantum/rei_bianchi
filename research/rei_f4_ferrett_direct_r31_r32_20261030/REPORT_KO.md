# Ferrett (1987) 실측 직접 비율 × BASS193 분기 및 초기 광전자 구간

## 정식 연구 단위

`REI_F4_FERRETT1987_DIRECT_R31_R32_BASS193_SOURCE_INJECTION_20261030`. 원본 제공 파일 LBL-22068 PDF 34–37쪽 Table I–IV 이미지를 직접 확인하고, Table II의 R31과 Table III의 R32만 이용했다. 1987 저자 가정이 들어간 Rc 및 93–99 eV Table IV 분기율에 대한 의존을 제거했다. 193 원본 epoch ×2 Li 동위원소 ×3 원본 photo bin = **1,158 물리 데이터 행**.

## 수치 결과

`results/RESULT.json`과 `FERRETT_DIRECT_R31_R32_BASS_EVENT_1158.csv`가 수치적 SSOT다. 원본 `source/PR289_full_source.zip` byte-locked. `PDF 7fbabb1fe8c77a2f...`도 exact source lock. 사용된 photon energies (eV): 81.8523384828,86.7088205644,91.8534485762.

- 원본 구간 전체 K-shell 사건: **7.881829561377594e-12 / baryon**.
- 직접 관측 R31/R32를 이용한 명목 triplet 사이트: **4.067416707685623e-12 / baryon**, 표시 통계 rectangle **[4.002730623452220e-12,4.131596091519242e-12]**.
- n2의 비Triplet 잔류 채널: **2.488514276163851e-12 / baryon**; 알 수 없는 순수 singlet 가능한 최대 (box) **2.5443741801578483e-12**; 하한 **0**.
- n3 위성: **1.3258985775280962e-12**.
- 가능한 출사 1차 광전자 운동에너지 구간 (변동 ratio & Ferrett Table I 잔류 에너지): **[1.4869412379997572e-10,1.5440924486905871e-10] eV / baryon**. *Deposited heat는 아님.*
- 완전 진공 M1 decay를 **가정할 경우** triplet 방출 가능 광자 에너지 명목값 **2.400618775678986e-10 eV / baryon**. 완전 진공 2E1를 **가정할 경우** 가능한 singlet 2E1 에너지 **[0,1.5500978724748324e-10] eV / baryon**. 두 값은 source production의 조건부 가능치이며 실제 photon emission/transport 아님.
- PR289 parent Table IV-assisted triplet strict-window **4.062999075216019e-12**. 새 direct-R31/R32 값과 차이가 작더라도 원전 가정의 종류는 다르다. 새 순수 singlet 상한이 더 느슨해지는 것은 불확실한 Rp 가정을 제거한 결과다.

## 검증 수준과 보존

Wolfram analytic derivatives and exact normalization residual 0; Python 21 targeted checks PASS (including two original-source negative controls), original 193 saved epochs & 21-ion source unchanged. No new IVP/production. ZIP+manifest clean-restore reproduction, source/master cloud readback and Git SHA see `delivery/FINAL_ACK.json` (먼저 해당 파일의 실제 승인 결과를 조회하고 인용할 것). Stage R1–R10/C1–C10은 같은 과학 루프의 업무별 retrospective 기록이며 별도 20번 독립 연구 수행의 주장이 아니다. Distinct-author R6/C9 NOT_RUN.

원본 canonical DAG: Working **33/88**, Central **28/88**, F4 fast **4/7**; scientific auxiliary **1/1 scoped**; canonical physical delta **0**. F4 PARTIAL, L4_ready=false, thermal port UNBOUND, production HOLD.
