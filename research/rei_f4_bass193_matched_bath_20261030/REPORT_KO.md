# 물리 자료 생산 결과 · 2026-10-30

**행동:** 새 IVP 대신 원본 BASS21 (193\times21\) 실제 저장상태와 BASS native RR/DR 계수 및 REI가 쓰는 Grackle H/He rate-family를 동일한 온도, 밀도, UV source에서 직접 대조했다. 193 epoch summary, **1,351 event-rate observations**, 각 epoch 5-vector/5x5 Jacobian 3개를 생산했다. Native REI Rust execution and original REI full17 RHS: NOT_RUN. 이는 동일 원자물리 coefficient family의 비교이지 동일 source의 둘 이상의 실제 진화 이력이 아니다.

**물리 데이터:** T=100.000...11999.95565 K; 102 low-T Grackle branch epochs. 원본 BASS 자유전자 중 H1/He4 이외 양전하 핵종이 공급한 분율은 [2.7499293768e-5,3.8715560801e-5]. REI rate-family의 공통 전자 bath에서 (\Delta\dot Y_e\)는 193개 시점 모두 양수, max (5.1864969741e-17\; baryon^{-1}s^{-1}\) at z≈8.91983. 추가 HHe-only pool effect max (2.127042722e-20\;baryon^{-1}s^{-1}\).

**저장 격자에서 사후 Simpson \(\int (q^T\Delta F/H)\,dx\):** rate discrepancy +0.2214155293848522; electron-pool +0.00013401365680309308; sum +0.2215495430416553 per baryon. Seven event-source contributions: HII RR +0.20343152587660007 (91.87771356%), HeII RR +0.015494203818858274, HeIII RR +0.0024896621759863307, CI HI +1.3699030984461167e-7, CI HeI +1.5272196515397332e-10, CI HeII +3.703758006347961e-10, DR HeII +5.757975685808258e-19. Original H/He total F and J identity max residual 1.2325951644e-32 and 6.1629758220e-33 s^-1.

**이론:** 동일 상태에서 (\Delta F=n_e^B\Delta MX-n_o M_RX\); (\Delta J=n_e^B\Delta M+n_b(\Delta MX)q_5^T-n_o M_R\) at fixed bath/other isotopes. Wolfram 5x5 source/J/conservation exact zero. These are chemical RHS partials only; original thermal EOS, UVB photon, species hidden dynamics, rho=nHref/nb and Bianchi clock derivatives not included.

**현재 완료/보류:** Physical-data subtask 1/1 accepted within its exact conditional scope; cumulative auxiliary PR275+this 2/2; research stage R/C 18/20, different-author R6/C9 NOT_RUN. Original REI working33/88, central28/88, F4 fast4/7, physical_delta0. `F4=PARTIAL`, `L4_ready=false`, no new IVPs, production HOLD. Previous inherited CI failure maintained. Source-inclusive full ZIP is authority for code/tests, original binary, CSV/NPZ, complete Korean full theory text, logs and figures.

**Backup:** [Whole raw Google Drive](https://drive.google.com/file/d/1zfOreS6e1kQzhIcSlpMX2Z5Qk_wJcfDX/view), 4,154,196 B, whole SHA256 58815601324ade9871077236dccee25cbbfe126141ee9af3d7da9ed9ffdb56f2 and `cmp` match; Library full ZIP same bytes. Dropbox whole binary NOT_UPLOADED. 20 separate Git stage commit ACKs are retrospective snapshots and not separate stage-time scientific experiments nor independent cloud ZIP uploads.

**Next:** complete source-owner common REI17/BASS21 isotope inventory, Li6/T/fast, photon/thermal, density normalization, H,K/rho, full F/J 21↔17. No physical τ/CMB inference.
