# 세 원자 스레드의 FLRW 세 방정식 관련 최신 증분

이전 검토 commit과 현재 ref를 직접 비교했다. bass_cr는 936f78d→3e52c309, WU088_HH는 b0fb3a7→13d8fd65로 각각 문서 commit 두 개만 추가됐다. BASS_HE는 9df4f335 그대로다. 새 원자 native 실행이나 production 코드 변경은 없다. 네 개 추가 원문을 직접 읽고 remote Git blob과 바이트를 대조했다.

| 스레드 | 새 결과 | 실제 소비기에 남은 일 |
|---|---|---|
| bass_cr | local rate, spectral/integrated photon number, filling-factor exact defect를 유도. 기존 게시 Wolfram 항등식 20개 기록 | 실제 F03/local RHS·F01 photon ledger·물리 edge flux를 source-bound 실행으로 연결 |
| WU088_HH | 같은 세 환원식과 phase/density/storage 반례. 기존 게시 bounded checks 30개 | actual top-level regression, 실제 phase/averaging closure |
| BASS_HE | 새 변경 없음. 실제 RCT 제외와 generic F01의 제한 확인을 재사용 | RCT를 선택할 때만 별도 source/domain/열·광자 closure 필요 |

CR와 HH 모두 receiver의 FLRW01을 읽고 **REI-CHAT-FLRW02_SOURCE_BOUND_THREE_EQUATION_REGRESSION** 하나로 후속 작업을 합치라고 명시한다. 독립적인 새 이론 패킷이나 solver를 두 스레드에서 또 만들 필요가 없다. 이 검토는 그 과거 검산을 재실행하거나 독립 심사로 세지 않는다.

## 국소 rate 식에서 보존할 조건

H nuclei continuity를 제거한 분율식에는 추가적인 -3H*x가 없다. Pure H의 n_e=n_H*x에서는 재결합이 -alpha*n_H*x^2다. 고정 n_e의 F02 scalar oracle와 구분해야 한다. alpha의 Case, Gamma의 photon measure, cross-section 및 상수 pin을 맞춘 실제 RHS를 비교한다.

첫 세 방정식 benchmark에서 CR·HH collisional ionization·He CX를 제외할 수 있다. 이 선택은 해당 물리 source가 자연적으로 0이라는 판정이 아니다. HHe 모형이라면 n_e=n_H*x_HII+n_He*(x_HeII+2*x_HeIII)를 쓰고, helium photon absorption은 별도 event owner로 남겨야 한다. BASS_HE의 scalar RCT율을 photon/thermal moment로 자동 전환하지 않는다.

## Photon-number 식에서 보존할 조건

Spectral proper number의 expansion 계수 2H, integrated proper number의 3H, integrated energy의 4H를 구별한다. 고정 물리 문턱 위의 comoving photon number에는 -H*nu0*N_nu(nu0)가 남는다. 전체 frequency의 comoving conservation을 ionizing band에 그대로 적용할 수 없다.

같은 primary absorption이 species ionization과 photon loss 양쪽을 소유하도록 actual F01 함수에서 loss/proper-volume=sum(species events)를 확인한다. 내부 edge flux의 telescoping만으로 continuum recovery가 닫히지 않는다. legacy redshift coefficient는 within-bin spectrum/edge value와 결속해야 하며 upper-edge inflow도 실제 계약을 따른다. 빈 photon reservoir에 양의 emissivity를 주는 초기층은 instantaneous photon-counting 가정의 명확한 대조시험이다.

Case A explicit diffuse, Case B OTS, Case A escape는 서로 다른 closure다. alpha_B sink에 동일 ground recombination photon을 다시 추가하면 중복이다. 재결합 사건수와 ionizing photon yield의 동일성은 ground-one-photon 같은 명시적 범위에서만 쓴다.

## Filling factor에서 보존할 조건

X_M=<n_H*x>/<n_H>, Q_V=<I_HII>, Xi=X_M-Q_V를 구별한다. Photon inventory eta=N_gamma/Nbar_H로 쓰면 실제 budget은

    dot Q_V - (s_star - Q_V/t_ref)
      = -dot eta - l_z - a_other + i_extra - dot Xi
        - (r_eff - Q_V/t_ref)

의 defect를 갖는다. 이는 저장·redshift loss·다른 absorber·추가 ionization·mass/volume 차이·실제 recombination moment를 드러낸다. Uniform x를 Q로 개명하여 classical filling law를 복원했다고 할 수 없다. 현재 homogeneous state에 phase/averaging API가 없다면 detached two-phase manufactured fixture 검산과 actual consumer 부재를 분리해 기록한다.

기존 legacy gate와 optional atomic source의 domain 대기는 유지한다. 이 review가 새 구현이나 물리 admission을 한 것은 아니다. 다음 실제 증분은 owner의 현재 code path를 고정한 제한 회귀검사다.

파일: 저장소별 SNAPSHOT.json은 fresh ref와 bounded diff, SOURCE_INDEX.json은 exact URL/blob, SOURCE_IDENTITY_CHECK.json은 네 원문의 바이트 일치, RECEIVER_REQUIREMENTS.json은 기계 판독용 조건이다. 변경 없는 BASS_HE의 근거는 prior_HE/에 정확한 원문을 재사용한다.
