# HE-RCT-STEP01-DESIGN: FT03 갱신과 RCT 잔차·장부의 결속

DESIGN_VERIFIED_CONDITIONAL. 실제 소비기 handoff가 지정한 병렬 설계를 완료했다. 새 native/원자율/history 실행0, consumer mutation0, physical admission=false다. F08 source owner 예약 전 ft03_controlled.rs/coupled_primary.rs를 수정하지 않는다. 이 결과는 actual stepper 구현이 아니다.

입력 BASS_HE37d99878f578a4472ee4e11f5959752b5655a952, REI7c5469101f8d6ef027c8c3119cc5c053e15ba1d9. 실제 ft03_controlled.rs(blob370fd2fa60521f2dc121ee81c7d24013a3b0d1e5) 전체와 he_rct.rs(blob37f83f83bb67cf0ad174b56ee748cf6733857701)의 event/energy 경로를 결속했다. 원격 source original bytes를 여기서 복사했다고 하지 않는다.

## 최소 양성 갱신

고정 nH,nHe>0, 단일 상수 k, 명시적 고정 Ebar에 대해 현재 Picard 블록의 두 유효율만 다음처럼 추가하는 설계다:

    I_H_eff = I_H + k*nHe*z_guess
    D_HeIII_eff = D_HeIII + k*nH*(1-x_guess)

electron density를 추가로 곱하지 않는다. 기존 수소·헬륨 생멸 블록의 positivity 구조를 유지하며, 고정점에서 양쪽 RCT는 동일한 R=k*nH*nHe*(1-x_new)*z_new다. 중간 iteration의 수소/헬륨 frozen event는 일반적으로 다르므로 accepted ledger로 쓰지 않는다. candidate thermal/escape와 최종 endpoint residual 모두 actual combined_ft03_rhs를 사용해야 한다. residual만 바꾸고 기존 블록을 유지하는 잘못된 조합의 비영 반례를 기록했다.

## 정확 미분 구조

f=nHe/nH, U=(x,y,z,w,p0,p1,p2), w=u/(nH*eV_erg), p=n_gamma/nH, g=Q-Ebar를 쓰면

    r=R/nH=k*nH*f*(1-x)*z,
    v=(1,1/f,-1/f,g,0,0,0)^T,
    F_RCT=v*r,
    J_RCT=v*grad(r)^T,
    nonzero eigenvalue=-k*nH*((1-x)+f*z),
    Taylor remainder=-k*nH*f*dx*dz*v (exact).

따라서 일반 내부점에서 Jacobian rank1, x-z 혼합 Hessian만 비영, 삼차 미분0이다. 이것은 RCT 항 자체의 명제이지 full FT03 안정성/implicit-root 인증이 아니다. isolated Picard 고정점은 rho^2=[alpha*z/(1+alpha*z)]*[beta*(1-x)/(1+beta*(1-x))]<1이지만 stiff limit에서1에 접근한다. full coupled convergence를 보장하지 않는다.

A0=I-dt*J0의 분해가 실제로 존재할 때만 rank-one solve를 후보로 둔다. A0*q=b,A0*s=v,den=1-dt*grad(r)^T*s에서 delta=q+dt*s*(grad(r)^T*q)/den이다. 현재 solver에 A0 factorization이 있다고 가정하지 않는다. A0=[[1,-4],[0,1]],v=(1,-1),grad=(-1/2,1/2),dt=1은 detA0=1과 RCT 고유값-1에도 den=0, coupled determinant0인 합성 반례다. 무조건적인 역행렬 갱신은 금지한다.

## Domain과 accepted 장부

s=1+f+x+f*(y+2z), B=2*eV_erg/(3*kB)에서 T=B*w/s다. Tguard는 B*w-Tmin*s>=0, Tmax*s-B*w>=0의 affine 후보조건이므로 line search에 직접 사용할 수 있다. 종/광자 positivity도 affine다. 이것은 candidate domain이지 exact time-flow domain 인증이 아니며 이전 HE-F2C 반례는 그대로 유지한다.

final endpoint J=dt*R를 하나만 만들고 nH*Dx=S_H+J, nHe*Dy=S_HeI-S_HeII+J, nHe*Dz=S_HeII-J로 검사한다. S_HeI에는 기존 DR sink가 포함된다. RCT는 기존 RR/DR가 아닌 별도 event다. chemical=-QJ, heat=(Q-Ebar)J, escape=EbarJ, emitted/escaped photon count=J, retained photon increment0이다. source energy moments는 null이다.

two-half는 J1+J2와 각 에너지 장부를 합하고 full candidate는 버린다. 미래 stage별 Ebar에서 최종 Ebar*(J1+J2)를 사용하면 (Ebar2-Ebar1)*J1 오차가 생긴다. OFF는 기존 baseline에 직접 위임하는 것을 권고한다. rejection은 모든 state/count를 commit하지 않는다.

normalized 잔차를 구현하면 기존 floors도 단위변환해야 한다: sw=max(w0,1e-30/(nH*eV_erg)), sp=max(p0,1e-30/nH). 원래 residual/local/public-width gate는 변경하지 않는다. RCT ordinary product의 underflow 문제를 본 기호 검산으로 해결됐다고 하지 않는다.

## 실행과 전달

python -B -W error verify_design.py: exit0, 기호23그룹/139scalar, 유리수20예제, 비영·특이 반례4개. 신규 native test가 아니라 독립 수학적 설계 검산이다. script는 실제 실행본과 byte-identical하며 evidence/DESIGN_RUN.log가 최종 로그다. 기존 mixed2/274와 원자/전체 suites는 재실행하지 않았다.

PEER_NATIVE_INTAKE.json은 같은 mixed finite gate의 양쪽 반환 수신을 종료한다. 동일 gate의 동시 실행을 새 milestone으로 합산하지 않는다. 기존 root의 ACK_PENDING 표시만을 이유로 세 번째 실행이나 수신확인 루프를 만들지 않는다. 최신 whole-crate/production 채택은 별개다. root/TASKS는 보존했다.

전체 상세 REPORT_KO.md, 실행 결과의 개별 식·예제·반례, 소스 projection, OWNER_PATCH_PLAN.json 원문은 BASS_HE_RCT_STEP01_DESIGN_20261005_v1.zip에 있다. Git의 본 README/계약 요약은 전체 ZIP과 구분하며, 실제 archive/cloud identity는 DELIVERY_RECEIPT.json이 소유한다. HE-F2 global=false, HE-F3 WAIT_REI_F09_RESULT, RCT OFF, physical HOLD, Eq55 NOT_RUN, legacy PARKED_OPEN을 유지한다.
