# BASS_HE T3B2 봉인 산출물 게시·백업 복구

2026-10-03 KST. 사용자가 GitHub/Drive/Dropbox 백업을 우선 재시도하도록 명시적으로 승인했다. 이번 기록은 원 산출물의 전송 복구이며 새 물리 계산이나 독립심사가 아니다.

## 과학적 원본

- 파일: BASS_HE_EOR_T3B2_DUAL_RESIDUAL_20261003_v1.zip
- 크기: 2147568 bytes
- SHA256: fe5f90b6896bcd94246fbcfe30704105e34c0facc091fc12405d1c7ae0d77c94
- ZIP entries 60, manifest payloads 59.
- 이번에 CRC와 모든 payload의 크기/SHA256을 실제로 확인했다. 원본은 수정하지 않았다. 과거 67개 시험과 native 재현은 봉인된 과거 evidence이며 이번 백업에서 반복 실행하지 않았다.
- 과학적 부모 T4: SHA256 6898716a560c9426fe4e592215f882131dae06baf0251e5166ff930d8b3c6c4a.

## 원 연구 결과의 범위

원 T3B2A는 전체 unitary moving-Coulomb propagator를 유지한 forward/backward dual-residual identity를 유도한다. A1b의 H1s 입사 및 He1s+n2의 유한 B5 출사 채널, 직선 상수속도 경로, 명시한 domain/regularity 조건 아래 두 residual의 시간순서 적분이 O(b^-2) 진폭 및 O(b^-4) 포획확률 envelope를 준다. 실제 atomic orbital로 residual 상수를 계산한다. 전체 all-bound 합, continuum, 곡선/양자 핵 운동 또는 실제 source accuracy의 인증은 아니다.

원 reference code에는 projected-residual pairing, 시간순서 이중합의 O(N) evaluator, analytic residual/tail bound, phase/error ownership 검사와 Fortran ordered batch kernel이 있다. 봉인 evidence는 67개 관련 시험, 5개 제조계 항등식, strict binary64 native parity, OpenMP1/2 thread bitwise 일치를 보고한다. 그것을 새로운 물리 단면적 표로 사용하지 않는다.

## 원자 데이터 공급 범위

Bianchi physics는 rei_bianchi가 소유한다. BASS_HE는 atomic cross sections/rates, state/channel definitions, collision energy/isotope convention, energy moments, applicability and uncertainty/provenance를 공급한다. 기존 T4 receiver adapter는 reference로 동결하고 새 Bianchi dynamics/transport를 구현하지 않는다.

C0 physical_ready=false, EOR_THEORY_GATE=NOT_SATISFIED, independent_review=NOT_RUN, scientific_PROMOTE=HOLD, continuum_certificate=false, full_H_gap_certificate=false, full_C2_closed=false, atomic_correlation_established=false, Eq55=NOT_RUN, production_default_change=NOT_AUTHORIZED를 유지한다.

## 전송 복구

Drive 새 업로드 성공 후 metadata size=2147568을 확인했다. Dropbox의 원래 동명 경로에는2154106-byte 파일이 존재하여 업로드가 ALREADY_EXISTS로 거부됐다. 그 기존 객체는 덮어쓰거나 삭제하지 않는다. 현재 봉인본을 구분하기 위해 같은 승인 폴더의 BASS_HE_EOR_T3B2_DUAL_RESIDUAL_20261003_sha_fe5f90b6896b.zip 경로로 별도 저장 요청했다. 두 파일의 이름만으로 byte identity를 추정하지 않는다. 최종 provider ACK/object/size와 이 commit/tree는 detached BACKUP_RETRY_RECEIPT가 소유한다. 이 문서만으로 아직 반환되지 않은 action의 성공을 주장하지 않는다.

공개 Git의 범위는 이 복구/과학범위/archive identity 기록이다. 전체 실행코드와 부모자료는 SHA-bound private ZIP에 있다. 원자료 PDF/private source bytes를 공개 Git에 새로 게시하지 않는다. public source subset과 private complete archive를 구분한다. UPLOAD acknowledgement/metadata 검증과 실제 download/restore 검증은 다르다.

## 다음 단일 작업

EOR_C0A_ATOMIC_SOURCE_RECOVERY_AND_COVERAGE_LOCK: Liu2024의 원 공개 수치자료를 실제 회수해 원자종, H1s/H2s, 출사 채널, native energy/per-u, cross-section unit, uncertainty, license 및 moment availability를 고정한다. raw data, 추출, fit, digitization, interpolation을 구분한다. 저에너지 radiative CX와 ionization secondary/recoil moments는 별도 결손이다. 이 자료 확보는 production gate를 자동으로 열지 않는다.
