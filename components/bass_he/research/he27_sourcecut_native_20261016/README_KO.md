# HE27 opt-in source-cut native 연구

실제 결과와 한계는 [REPORT_KO.md](REPORT_KO.md), 단계별 판정은 [DAG_STATUS.json](DAG_STATUS.json)에 기록했다.

24개 native 완결,17/17 후속 matrix,6개 실패/미완료 원본 보존. 동일 입력 Radau/DOP853 차이7.11e-14K, source-cut A/B ΔT=+9.42695e-9K. 시간 정제만 scoped VERIFIED; 연속 spectral convergence와 EoR/CMB 관측은 HOLD. 기존 HE25/HE23와 원본 Rust는 불변이다.

analysis/run_native_fast.py는 신규 디렉터리에서만 실행한다. 원본 C5 manifest와 각 case ID, raw native streams, measured commands/resources, source/binary SHA 및 backup 영수증을 함께 사용한다. 전체 cohort arrays는 byte manifest와 복원 아카이브에 포함한다.
