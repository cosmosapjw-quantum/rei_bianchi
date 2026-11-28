# 사용자 변경분: matter/radiation anisotropic stress 분리

2026-10-21 사용자가 `pi_ab는 matter와 radiation을 별도로 고려`하도록 지정했다. 이 문서는 앞선 total-Pi 계약을 지우지 않고 현재 출력·해석의 기준을 확장한다. 완료된28case/C15결과는 재적분하지 않는다.

## 기본 변수

    pi_ab = pi_ab^m + pi_ab^r
    Sigma = ||sigma||_F/H
    Pi_m = kappa_t ||pi^m||_F/H²
    Pi_r = kappa_t ||pi^r||_F/H²

H[s^-1], stress[J/m³] convention이므로 kappa_t=8*pi*G/c²다. 기존 Pi_F는 `Pi_total`의 호환 alias로만 해석한다. 핵심 sweep 좌표는 (Sigma,Pi_m,Pi_r)와 필요한 방향·종별분포 정보다.

LRS에서 pi^X=diag(-p_X,-p_X,2p_X), v_X=kappa_t*sqrt(6)*p_X/H²를 보존한다. Pi_X=|v_X|이다.

    v_total = v_m + v_r
    Pi_total = |v_m+v_r|
    |Pi_m-Pi_r| <= Pi_total <= Pi_m+Pi_r.

두 크기를 무조건 더하지 않는다. 일반 tensor에서

    Pi_total² = Pi_m² + Pi_r² + 2 eta_mr Pi_m Pi_r,
    eta_mr = (pi^m:pi^r)/(||pi^m|| ||pi^r||).

LRS의 nonzero components에서는 eta_mr=sign(v_m*v_r)다. zero component에서는 정렬각이 정의되지 않으므로 출력 chi=0은 zero 분기 표시다.

## 저장 source별 partition

| Source | matter | radiation | 변환 |
|---|---|---|---|
| canonical PR147 | Pi_matter_J_m3 | Pi_gamma_J_m3 + Pi_nu_J_m3 | 이미 p_X=deltaP/3 |
| C15 native H/He | Pi_massive | Pi_gamma + Pi_nu + Pi_UV | 각 stored deltaP를3으로 나눔 |

gas/dust의 trace-free stress가0인 것은 이 두 closure의 가정이다. 일반적으로 matter stress가 항상 massive 한 종과 같다고 주장하지 않는다. C15 gravity source를 끈 control에도 위 physical partition을 유지한다.

## 분리된 동역학 해석

    du/dln(a) = (q_dec-2)u + v_m + v_r.

종별 shear work는 sigma:pi^X=6*s*p_X=(H³/kappa_t)*u*v_X이다. 반대부호 성분이 total stress를 줄여도 각 성분의 stress나 work가 없어지는 것은 아니다. energy exchange/source Q_X가 있는 모델에서는 각 성분의 에너지식을 그 Q_X와 함께 유지해야 한다. C15의 외부 UV공급을 포함한 system을 여기서 임의의 closed matter+radiation 보존계로 바꾸지 않는다.

## 이번 actual pilot의 범위

28case의 initial massive_A=0을 그대로 유지한다. actual initial Pi_m 최대2.1111496372470002e-19로 roundoff수준이다. 따라서 **초기 Pi_m≈0 단면에서 Sigma와 radiation Pi_r를 변화시킨 pilot**이며 independent three-parameter grid를 완료했다고 부르지 않는다. 진행 중 anisotropic redshift로 matter stress는0이 아닌 값으로 생길 수 있다.

새 postprocessor는 canonical2828행과 C15512행에서 component coordinates, full histories와 first/final endpoints를 만든다. 총합과 이전 signed total의 최대 차는 각각3.2526065174565133e-19와1.6263032587282567e-19이며 연산 순서의 binary64 roundoff다. 기존 원시28case와 guarded solver/adapter source는 바꾸지 않았다. component cancellation/UV partition fixture2개만 추가했다.

향후 독립 Pi_m0 sweep은 massive angular distribution amplitude와 density/pressure normalization의 역변환을 별도 고정한 뒤 추가해야 한다. 오늘 기존 완료case를 다른 이름으로 다시 돌리거나, Pi_m0가0인 자료를 임의의3D surface로 보간하지 않는다. 이 변경으로 전체 EoR/triaxial/continuous-convergence/HPC-speedup claim은 승격되지 않는다.

## 후속 독립 초기조건 실행

이 문서의 저장값 분리 범위를 완료한 뒤 `SPLIT_INITIAL_CONTRACT_KO.md`를 별도로 고정했다. 새12건을 실행하고 기존6건을 재사용한18점 view를 완료했다. 기존28건은 여전히 initial Pi_m≈0 단면이며, 이번 전체 고유 적분 수는40이다. 기존28건 재실행0이다.
