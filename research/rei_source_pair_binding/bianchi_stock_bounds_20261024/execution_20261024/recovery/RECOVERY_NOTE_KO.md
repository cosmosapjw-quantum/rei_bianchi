# Final C 복구와 자료 가용성

일시 작업공간에서 기존 파일이 사라진 사실을 관측했다. 실제 원격 A/B/이전 C archive를 root가 내려받았고 전체 SHA256이 기존 기록과 일치했다. Worker는 A/B의 실제 payload bytes 및 보존된 원래 publication tree content를 읽어 복구했다. root 문서는 게시된 path mapping으로 원위치에 되돌렸으며 75개 published 파일의 SHA256·Git blob·크기가 모두 일치한다. 기존 stock16개와 work core9개 및 실제 child raw8개를 보존한다. 요약문에서 소스나 결과를 만들어내지 않았고 과학 실행·테스트·새 심사를 하지 않았다.

외부 full primary/Exa/SciSpace 원문, owner/private inventory, 상세 survey 및 transport raw처럼 앞선 패키지에 export하지 않은 로컬 자료는 현재 LOST_LOCAL_ONLY / NOT_RECONSTRUCTED다. 남아 있는 이전 omissions 기록의 경로·크기·해시를 LOSS note에 옮겼다. 당시 로컬 보존이라는 역사적 설명은 당시 snapshot이며 현재 가용성은 이 note가 설명한다. 새 recrawl은 하지 않았다. 자체 과학 claim에 필수인 이론·동결 구현/fixture·입력 raw·실제 stdout/stderr/자원 receipt·독립 심사·root 판정에는 복구 불가능한 파일이 없다.

이전 C는 지정된 실제 archive bytes 그대로 ancestors/에 포함하며 내부를 다시 열거나 재귀 scan하지 않았다. 현재 C의 미래 cloud IDs/ACK는 외부 delivery receipt에 적고, 자기 참조를 위해 archive를 재생성하지 않는다.
