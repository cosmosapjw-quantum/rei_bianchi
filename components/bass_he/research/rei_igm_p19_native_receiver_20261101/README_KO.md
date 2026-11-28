# BASS_HE → REI IGM | original source–receiver H/He/HeII photon-heat compatibility

이 파일의 **연구 소유 repo는 `cosmosapjw-quantum/BASS_HE`**이며 REI original 88-node owner는 변경하지 않는다.

`SCIENTIFIC_REPORT_KO.md`: 단위와 source-authority 구분, z=5.95의 46,080-node 실측 source-conditioned 계산과 결론.
`crosswalk.py`: 원본 3개 물리 데이터 ZIP의 SHA, 원본 12-row 가열 표 Git blob을 검증한 후 원래 46k node/두 보간 시나리오/source group event/heating CSV와 summary JSON을 생성.
`independent_audit.py`: 다른 구현, Decimal72 기반의 실제 46k CSV의 사건수·원소량·광가열 총량 독립 합산 및 source invariant 확인.
`tests/test_crosswalk.py`: 16/16 정상 및 16/16 `-O` 테스트, 발표 source 단위·인터폴레이션·본래 owner·위험한 입력 변조 및 46k 데이터 체크.
`plot_science.py`: 원본 실제 node T-decile excess heat, 종별 photon source 비교에 관한 2 PNG/2 SVG.
`results/`: 원본 실제 46k node CSV.gz, JSON, 9 원본 node 증인, 4 group 에너지 표, 독립감사.
`inputs/`: P19 BASS_HE PR141 원천 projection 아카이브, 원본 REI PR320/PR332 GitHub Actions ZIP, 원본 Git blob과 byte exact REI 가열 owner CSV. 저자 발표 표 외 외부 source를 임의 대체하지 않음.
`STAGE_LEDGER.json`: R01–R10/C01–C10 항목마다 독립 evidence/backup과 REI **28/88** 및 BASS_HE **14/18** 고정. 20개 체크포인트는 하나의 물리 실험 기록이지 20개 독립 계산/PR이 아님.

실행: `bash REPRODUCE.sh`; 결과는 같은 기준/원본 source로 재생성한다. `python VERIFY_PACKAGE.py`는 아카이브에 포함된 기존 모든 파일의 SHA checksum을 검사하므로 재생성 전후에 다른 파일 identity를 주장하지 않는다. 컨테이너에 matplotlib/numpy 설치 필요 (본 연구환경에서 검증). 원본 REI 입력을 GitHub Public 저장소의 Draft 파일로 새로 배포하지 않고 완전한 비공개 재현 ZIP 및 연결된 Drive로 보존, Git에는 검증 가능한 코드·report·요약·증인만 게시한다.

**RUX02** = P19 published neutral-weighted effective input available; **RUX03** = original native high-energy spectrum/opacity/HeII photon-source mismatch; **RUX04** = NOT_ADMITTED; **BASS_HE RUX12** optional still. **No 46k canonical new IVP, no source swap, production HOLD.**