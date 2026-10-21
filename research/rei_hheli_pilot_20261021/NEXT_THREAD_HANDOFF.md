# 다음 대화에서 그대로 붙여 넣을 프롬프트

$physmath-research-loop $exa $scispace $wolfram

cosmosapjw-quantum/rei_bianchi의 통합 연구를 이어가라. 새 H/He/Li sandbox pilot은 draft PR218, branch research/rei-hheli-sandbox-pilot-20261021, task research/rei_hheli_pilot_20261021/에 있다. 최신 head와 PUBLICATION_RECEIPT/FINAL_ACK를 실제로 읽고 시작하라. 이 handoff가 포장된 시점 이후 head를 과거 SHA로 추정하지 마라.

이미 완료된 신규 계산은79nominal+3controls=82IVPs,각257samples,z20→2,실패0,실제wall66.031348s/childCPU250.578735s다. PNG/PDF10종과 raw, CASE_PROVENANCE_LEDGER, 독립 PHYS-MATH/CODE/RAW/FIGURE 감사가 있다. 최종 판정은 PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID다. 완료된82개나 기존PR198/B175/D9를 근거 없이 재실행하지 마라.

물리 core SHA256은30dd7fef781a51ddfc9ea763be55679f690caa5ddc3efff34c4bd771e7f5f77b, contract SHA256은dd3950150be8718d1bb60eed4f1ba3f4cd7447b377adc92476abf28ba8369dee다. HE32 donor pin은BASS_HE e8bb035d31f59e34734947b9082bdbd60128b799다. 실행은샌드박스filehash로식별하며나중publicationcommit을실행당시commit으로소급하지마라.

Linux/Python3.12 및pilot/requirements.txt의NumPy2.3.5/SciPy1.17.0/Matplotlib3.10.8환경에서 repository root의 다음 명령은0신규IVP로 원자료를 검토하고 그림을 재생성한다:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B research/rei_hheli_pilot_20261021/pilot/code/run_pilot.py --audit-existing

선택모형은21heavy-particle상태(n,H1/D/Tq0..1,He3/He4q0..2,Li6/Li7q0..3)와별도전자chargeclosure다. 같은원소isotope간 electronic rates는같다고가정한다. n/T는초기0이며핵생성반응이없다. UV5–60eV및초기조건에서LiIII/IV는해석적으로0이고수치잔차는clipping하지않았다. Vernerphoto+totalRR,HeIa행을쓴다. CI/DR/CX/분자/음이온/19핵반응및닫힌열·복사에너지는미구현·미확립이다. “모든19핵반응이완료됐다”고말하지마라.

Sigma와Pi는fullFrobenius다. signedtensor를합친후norm을취한다. PR198half-contraction에sqrt(2)를곱하는것은축변환일뿐trajectoryreuse허가가아니다. pi_m은nonbaryonicmassive10%성분이고원자baryon은isotropicpi_b=0이다. 계산된ne가photonThomson산란에연결되며neutrino는collisionless다. 초기totalPi가상쇄된두실제case에서z2signedshear -1.1093244e-4및+5.5461860e-5가발생했다. 유한모형의결과이며보편적중첩정리는아니다.

먼저다른branch/repo/접근가능대화/Drive·Dropbox에서새결과가생겼는지확인하고문서주장과실제raw를구분하라. 이전조사는798refs/38sourceblobs였고Drive100개cap이라는coverage한계가있었다. 실제runtime은매turn재probe하라. 다른세션·dirtycheckout·process를건드리지말고가용자원만사용하라.

다음단일과학노드는 harderUV의LiIinner-shell/Auger와RR/DRenergy-moment원본source·유효범위·daughter·energybookkeeping계약확정이다. 이를통과하기전에새전체grid를실행하지마라. Nuclear19는독립lane으로유지하라. PR198scopedPASS,B175완료,D9closed,PR199AGEconvergenceHOLD,GrackleboundNOT_ESTABLISHED,productionNOT_ISSUED를보존하라.

매단계DAG/게시/백업/다음노드를기록하고expected-headfast-forward만허용하라. no force, no merge,draft유지. 최종source/raw/그림은Git전체readback및Drive·Dropbox의실제uploadACK/fullGET/byte/SHA256/member검증으로닫아라. 현재확인된RustformatCI실패를Pythonpilot실패나greenCI로오인하지마라. 마지막에는복사할수있는Codex및다음대화handoff를갱신하라.
