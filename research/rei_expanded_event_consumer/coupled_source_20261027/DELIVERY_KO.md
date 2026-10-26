# 연구 루프 게시·백업 완료 기록

원본 전체 DAG는 **32/88(+0)**이다. REC-COUPLED는 검증된 25좌표 photo-source/JVP를 추가한 **PARTIAL**이며 원래 전체 gate는 열려 있다. 중앙 승인본은 unmerged 27/88이고 L4 및 최종 all-selected physical pilot은 미완료다.

과학 source commit: `eda4c1c0424fc2da17280c52ac8143507b5c39bc`.
이 두 최종 기록의 metadata commit은 이 파일을 포함하는 commit에서 확인한다.
[PR236](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/236)은 draft/open/unmerged이며 PR235 위에 쌓인 상태다. 제목과 본문을 현재 결합 source 결과로 갱신했다. 65개 게시 경로의 Git blob SHA-1·크기·mode·type을 대조해 65/65 일치했다.

독립 검토는 PASS_SCOPED다. 첫 시도에서 통과한 28개 검사를 재사용하고 후속 68개 검사가 통과했다. 정확한 부동소수점 0을 요구한 검사 실패와 검사 시작 전 runner 감시 실패를 각각 보존했다. 새로운 IVP는 0회다.

307개 항목을 담은 고정 ZIP은 3,477,069 bytes이며 SHA256은
`1b80efed0892f3368dc307e3cd6757b93dc444a4d7d2d186b352b926e230648a`이다.
로컬 CRC 및 roundtrip 검증을 통과했다.

- Drive: [저장된 ZIP](https://drive.google.com/file/d/1yV3Ov6xvujLI7Jye9m5SQsQG2aXuN9fi/view), 업로드 성공 및 별도 metadata 크기 3,477,069 bytes 확인.
- Dropbox: `/bianchi/research_backups/rei_bianchi/REI_COUPLED_SOURCE_20261027_1b80efed0892.zip`, id `id:BSpOijBcT10AAAAAAECMsg`, 완료 ACK 및 별도 metadata 크기 3,477,069 bytes 확인.

원격 ZIP을 다시 내려받아 SHA256을 대조하지는 않았다. 최종 게시·백업 기록은 고정 ZIP 밖에 있으며 ZIP을 재포장하지 않았다.

Planning 알려진 누적은 측정값과 명시적 보수 reserve를 포함해 12.196274495 CPU s다. 일시 cap14는 만료했고 원래 cap10으로 복귀했다. Presentation은 packaging까지 30.360058297 CPU s, 24.971073188 wall s이며 일시 cap36은 만료하고 원래 cap30으로 복귀했다. 어느 누적 debit도 초기화하지 않았다. Main은 595.225063/600 CPU s, NO_MORE_IVPs를 유지한다. Metadata·remote·미측정 tail은 UNKNOWN_NOT_ZERO다.

다음 단계는 검증된 stopping/assimilation 입력 또는 명시적으로 선택한 closure를 마련해 비열적 전자의 수·에너지 전달과 native RR/DR·Compton의 thermal electron bath를 일치시키는 것이다. H6 source-matched history, HD same-fit precision deck, V6 client 등은 별도 열린 의무다. [HANDOFF_KO.md](HANDOFF_KO.md)의 복사 가능한 문맥을 이어서 사용한다.

