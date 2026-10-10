# CR-PHYS03 receiver: FS10 `xi=0.1` 고정 knot

상태: `PASS_SCOPED` (독립 Astra xhigh 검토 승인).

Receiver는 `CRP_L17_MD14_RUDD_FS10_XI010_CONDITIONAL_V1`에 대응하는 별도
source-manifest와 packet을 compiled Rust에 고정했다. `xi=.01` 및 `xi=.1`만
binary64 정확 비교로 선택하며, 그 밖의 값은 `CR_PACKET_COMPOSITION_NOT_PINNED`로
거부한다. packet/state/geometry/ledger 결속은 기존처럼 모두 ON 경로에서 검사한다.

Native probe `cr_deposition_probe -- 0.1`는 실제 axisymmetric local derivative를
실행해 ON/OFF 차이를 보고한다. 이는 100 K, `x_HII=x_HeII=.1`, `x_HeIII=0`의
고정 snapshot 성분 검사이며 solver interval은 0이다. 인과 secondary delay,
임의 조성, cold REC IC, CR/IGM history를 주장하지 않는다.

중요한 identity 경계: 기존 `.01` Rust fixture는 historical provider manifest
`79835c5e...dd901`에 결속한다. 변경된 provider source로 `.01`을 새로 만들면
manifest가 `6d0332ea...f9bf1`이다. 이는 historical/current source 차이이며,
현재 default provider가 old fixture byte identity를 재생성한다고 주장하지 않는다.

다음 최소 과학 gate는 CR-PHYS02의 causal secondary-delay kernel이며, 이후에도
CR-PHYS04 losses와 결합 전에는 history node가 열리지 않는다.

독립 검토는 upstream bytes, provider packet과 Rust fixture의 모든 identity/numeric
필드, 30개 독립 quadrature 비교 및 해상도 비교를 재현했고 native `xi=.1` ON/OFF
derivative를 확인했다. 이 검토는 receiver integration의 scoped use만 승인한다.
