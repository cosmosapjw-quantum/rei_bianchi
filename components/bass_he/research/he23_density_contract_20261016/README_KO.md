# HE23: TOTAL_HYDROGEN_DENSITY_AND_PER_H_CONTRACT_RECOVERY

HE22 실패 보존 커밋 f103fdc48b8c6c3f032fdbe3face6c6fd078768d에서 파생한 독립 패키지다. HE21/HE22와 PR69는 변경하지 않는다. 원본 microphysics는 rei_bianchi f7830e2f55e7a1938bc3c98f61b60651f8dae474이다.

`he21_photo.py`는 역사적 photo-only 참조를 바이트 그대로 보존한다. 그 N_H_Z20은 C19 frozen neutral HI 값이므로 native total density로 사용하지 않는다. `he22_native_client.py`의 HISTORICAL_FROZEN_HI_Z20_CM3가 그 출처를 명시하며, native 실행은 NativeDensityProvider의 실제 Rust Driver 총 수소·헬륨핵 밀도를 사용한다. --density a는 화학 RHS 호출 없이 원본 Driver::baseline의 n_h0/a^3,n_he0/a^3를 반환한다. 모든 밀도 조회에 source commit, binary SHA, 정확한 float.hex(a)를 기록하며 rounded cache는 없다. 빌드 manifest가 실제 소스와 binary를 별도로 결속한다.

per-H는 총 수소핵 하나당이다. Y=nHe,total/nH,total이고 neutral=(1-xHII,Y(1-xHeII-xHeIII),Y*xHeII)이다. optical depth c*nH,total*neutral*sigma*dt, 체적 사건률 nH,total*events_per_H/dt, Gamma=events_per_H/(neutral*dt), heat=EV_ERG*heat_per_H/(neutral*dt)가 동일한 밀도에서 계산된다. 초기 분율 (1e-5,1e-5,0)은 그대로이며 0.9998에서 역추론하지 않는다. source_count=3.45955703510212632e-6는 동일한 조건부 prescribed photons/total-H 예산으로 명시한다. 실제 MD14 시간 방출률 복원이나 과거 frozen gas와의 동일 상태 가정은 하지 않는다.

외부 gas work와 photon redshift/shear work는 HE21 source-age 구조가 소유한다. 원본 RHS h=0; CI/RR/DR, cooling, Case-A escape 및 CMB는 원본 Rust가 소유한다. Grackle 3.4.1 선택 반응률의 Rust 포트이며 upstream 라이브러리 직접 실행 동등성이 아니다. 추가 n=8 정제에서 발견한 조기 Newton 종료는 기존 잔차 기준과 기존 에너지 gate를 **동시에** 만족할 때만 종료하도록 교정했다. 어떤 tolerance도 늘리지 않았다. 실패 원본은 evidence에 보존한다.

실행: `HE22_WORK_ROOT=/root/HE23_NCP_DENSITY_20261016 bash ncp/NCP_BOOTSTRAP_AND_TEST.sh`. 이 스크립트의 HE22_* 변수명은 전달 인터페이스 호환용이다. 새 빈 작업 경로만 사용하며 이미 실패/성공한 출력은 덮어쓰지 않는다. 테스트: `HE23_NATIVE_BIN=/absolute/path/he22_owner_point OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python -m pytest -q -p no:cacheprovider tests`. 기존 24개 테스트는 수정 없이 유지하고 5개 밀도/수지 회귀를 추가했다. Native tests는 실행 바이너리를 명시하지 않으면 SKIP이며 PASS로 해석하지 않는다.

source-age, fit cuts와 binding, per-total-H 및 원래 수치 허용치를 보존한다. 실제 결과 판정은 results/REPORT_KO.md와 기계가 읽는 evidence를 따른다. 전체 EoR, upstream Grackle 동등성, Bianchi 관측, CMB 광학깊이는 HOLD다.
