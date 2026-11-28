# HE-DD | Rice 2000 절대 광분해 실측을 통한 원자료 병목 해소

현재 기준: `cosmosapjw-quantum/BASS_HE` PR124 `9696297205c2560bd8bdfc8d72b8b80b86fae8d3`에서 독립 새 브랜치로 생성한 source-qualified 연구. 새 실측은 Rice et al. (2000) **12 source rows**; 같은 논문 Table II의 **8 대안 Legendre fit 모델**과 Rice 1998 학위논문 **6 동일 실험 예비행**을 별도 객체로 보존. EXFOR user ZIP은 **Arkatov M0826**으로 Rice와 관계 없음.

실측: 150–190 MeV의 DA는 각도(44.7,62.7,90.3,107.3,123.5,138.9)°에서 (0.77±0.15,1.26±0.16,2.32±0.20,1.73±0.19,1.50±0.17,1.03±0.15) nb/sr; 190–250 MeV에서는 (45.4,63.6,91.4,108.4,124.4,139.7)°에서 (0.14±0.11,0.59±0.15,1.42±0.17,1.11±0.16,0.68±0.12,0.43±0.13) nb/sr. 통계오차 외 연구자가 제시한 systematic 7.1%, 13%를 typed 별도 속성으로 보존. 논문은 각 bin에서 총단면적을 동일 중수소 계수 `σ_tot=2π A0`로 적분한다.

Legendre model의 총 단면적 중심값 범위: **8.29–9.55 nb** (150–190), **4.20–6.05 nb** (190–250). 이는 8개 독립 총단면적 측정이 아니라 2개 bin에 대한 8개의 대안 적합이다. 하나의 모델 `150–190 unconstrained P2 only`에서 A0/sigma와 systematic source-internal 불일치 발생 (blind-referee note 참조).

변환: PR104 rest masses 고정, photo/capture phase-space factor 정확하게 유도; 동일 비음수 energy weight 가정을 추가할 때만 빈 단면적의 capture-equivalent conditional range를 생성. 원본 Rice 데이터는 **bin averaged**, 170/220 MeV monochromatic 관측이 아니다. `K1+K2 = Eγ - 23.8464782 MeV`의 daughter pair kinetic support 생성, 물질 내 heat deposition 및 event rate 미생성.

이론/코딩 단계별 기록 R01–R10 및 C01–C10, 실제 Git HEAD, SHA, 백업 provider ACK는 `STAGE_LEDGER.json`. independent R06/C09 not run. scoped 3/3, canonical Central 28/88, HE 14/18, physical delta0.
