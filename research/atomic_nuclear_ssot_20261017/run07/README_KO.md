# RUN07: native 48셀 국소 photon–H/He/D 공동 기준해

2026-10-17. RUN06 복원 archive SHA256 ea8deff415e0b161ef66fddb933620b0e22c69f2ebf3bfcf19d6c2f1d8539a45를 검증하고 P4-S4C-OPACITY-COUPLED-REFERENCE의 국소 child를 실행했다. RUN06 이전 원격 게시가 완료되지 않아 Git parent는 마지막 확인된 RUN05 46de10fa11df1db75b56eb05f10599e3f32202ec이다. 이 branch는 원본 production/main/기존checkpoint를 수정하지 않는 add-only 연구 기록이다. Local/Codex/NCP/SSH 및 native independent subagent는 NOT_RUN.

## 실제 모델과 이론

BASS121 SIGNED_MINUS X=.7에서 실제 native 상태와 MD14/BB50k 48개 original energy mean/source fractions를 읽었다. 고유시간 길이는 X=.7→.7004의 h=9.670370928242e12 s. 그러나 이번 모델은 고유부피,기하,광원율,광자에너지,Tcmb=28.422308155153218 K를 해당 초기값으로 고정한다. 팽창/적색편이/방향수송/새Einstein반작용은 없다. 초기 T10000K,HII=DII=.1,He=(.8,.15,.05),D/H2.5e-5,D defect.0037eV는 기존 제조입력이다. REC donor 또는 정밀 isotope spectroscopy가 아니다. RUN05/06 expanding history와 같은 방정식이 아니므로 최종온도 차이를 적분기 오차로 비교하면 안 된다.

같은 fixed energy의 코호트는 같은 gas-dependent hazard를 공유하므로 그 수를 합하면 dP_j/dt=J_j-kappa_j(n)P_j가 정확히 닫힌다. 비선형 gas feedback은 이 factorization을 깨지 않지만 birth-dependent redshift는 일반적으로 깬다. 따라서 이 closure는 local fixed-energy에만 적용한다. kappa_j=c sum_a n_lower,a sigma_a(E_j),R_ja=c n_lower,a sigma_a P_j를 photon loss,species source,heat=(E_j-chi_a)R_ja에 한 번씩 적용한다. 기존 Grackle/Verner/Savin/DAtomicProvider와 RUN06 gas continuous RHS를 재사용하며 gas use_photo=false. H/D/He nuclei와 chemical+thermal+escape+CMB+photon-source energy identities는 Wolfram에서 residual0을 확인했다.

새 joint_slab.rs, joint_slab_server.rs와 Python joint_integrator.py는 27parent gas/reservoir+48photon+10photo/source accumulator=85상태를 함께 적분한다. Original72 Rust files(12owners 포함)와11입력은 byte-identical. lib.rs에 pub mod joint_slab;만 추가한다. 원래 source spectrum을 재정규화하지 않았다. Native trial negativity는 거절하고 accepted nodes도 검사했지만 SciPy의 전역 positivity theorem은 주장하지 않는다.

## 실제 결과와 제한

- 최종 fresh native138/138(기존130+신규8),신규Python6/6,strictClippy,new-code rustfmt PASS. Python vectorized photo assembly+별도 unchanged gas server를24개 양의 다른 상태에서 비교했다. 핵심 photo누락 및 invalid-negative-step에는 실제 red→green 로그가 있다. 모든 test를 TDD였다고 주장하지 않는다.
- Radau(rtol3e-10),DOP853(3e-10),tightRadau(3e-12) 공동 reference3행; frozen-opacity photo then precise gas Lie와 dynamic-opacity photo then precise gas Lie 각각n1..64 7행; gas-half/dynamic-photo/gas-half Strang n1..128 8행. 총25개 완료. Frozen source birth는 정확한 Phi로 처리해 birth quadrature error를 제거한 새 local comparator이며 기존 cosmological discrete driver의 byte-copy가 아니다.
- tight reference T=10002.319246808906 K,P_surv=5.779167203904059e-4 m^-3,xDII=.1011715094828502. Photo HI/HeI/HeII/DI events=(.06292955636105396,.004561490901297208,3.84855717245615e-6,1.5717651611824035e-6) m^-3. 초기 max kappa*h=341.7744,continuous born=.0680743843051 m^-3. Baseline에서 gas depletion은 약하며 강한 고갈 전체기체 캠페인을 새로 실행하지 않았다.
- Radau vs DOP853: T absolute3.63798e-12 K,survivor absolute1.08420e-19 m^-3. 같은 native RHS 공유이므로 독립 atomic-data validation 또는 rigorous enclosure는 아니다.
- n1 errors vs tight reference: frozenLie ΔT=-.0305692498041 K,ΔP/P=-3.04173459732e-4,ΔxDII=+1.86626519849e-7;dynamicLie ΔT=-.0306182235090,ΔP/P=+1.27184328233e-5,ΔxDII=+1.85876331160e-7;Strang ΔT=-.0004366708290,ΔP/P=+6.27566657248e-6,ΔxDII=+2.12431294763e-7. Opacity 동결을 제거해도 분할 온도오차가 남고 coarse Strang의 D오차는 Lie보다 크다.
- Lie n32→64 T orders1.00269/1.00285. Strang n64→128 T order1.94189,survivor1.88702,DII1.99807. Strang n128 errors ΔT=-3.08230e-7 K,ΔP/P=7.05958e-9,ΔxDII=1.51911e-10. 모든 종별event가 같은2차에 도달했다는 주장은 없다. 모든 error는 동일 local model의 수치reference 대비이며 global Bianchi error가 아니다.
- Max photonledger1.26395e-14,nuclei3.99818e-15,energy/initialtotal2.02110e-15,energy/source1.12211e-12. 작은 ledger가 stateaccuracy를 보장하지 않는다.
- 25개 완료 integration wall합60.6591267s;compile/tests/discovery/restore 제외. Full final ZIP을 새 directory에 복원해168payload hashes,138native+6Python,strictClippy,representative joint85state를 재검산했고 endpoint가 binary64 exact equality로 재생성됐다. 전체25campaign을 다시 실행한 것은 아니다. 복원 최대RSS248624KiB,buildjob1,4GiB sandbox.

Admission PASS_SCOPED_LOCAL_NATIVE48_CONTINUOUS_SOURCE_JOINT_PHOTO_GAS_REFERENCE. 상위 full retarded reference는 PARTIAL. 다음 P4-S4C-RETARDED-JOINT-REFERENCE는 같은 실제 BASS geometry/finite graded birth bundle/dilution/work에서 공동 photon+gas 적분을 구현해야 한다. Globaltime/spectrum/angle/fullEoR/FLRW-CONV/BI-SIGNED/ISO-COUPLE full/Einsteinreactionfeedback/nuclearT1–T8는 HOLD. Original45/26DAG는 ancestor에 보존했다.

## source와복원

REI_RUN07_IMPLEMENTATION_DELTA.tar.xz는10개 actual new source/test/driver/DAG/resume 파일이다. 12640bytes;SHA256 cf2adb9598dc41757606af944aa82f6b9bf11c13afaea2dd224157bf0e12c0ed;Gitblob11188fe5d756949eee73950d94b304f0de24a1af. RUN06 코드와 lib.rs의 pub mod joint_slab;추가를 필요로 한다. 단독Gitcheckout으로전체복원된다고주장하지 않는다. RUN06 pending Git source전체를이번commit에서게시한것도아니다.

실제 전체소스/입력/25행결과/실패/RUN06archive는 full recovery ZIP에 포함된다.
REI_ATOMIC_NUCLEAR_RUN07_JOINT_OPACITY_20261017.zip:3684870bytes,169entries,168payload hashes.
SHA256 578a7e8e72fe216f033f216dc5531685dd7bfe74dca3b9b62cf071434a7cd0bc.
Drive https://drive.google.com/file/d/1aCYmFgV7KO-7f7bQPoZ9FVKHaOhpLkSv/view?usp=drivesdk :upload and authenticated full download SHA256 matched.
Dropbox /BASS_DERIVATION_DOSSIERS_20260912/REI_ATOMIC_NUCLEAR_RUN07_JOINT_OPACITY_20261017.zip :id:BSpOijBcT10AAAAAAD-oBQ,upload completed,provider contenthash2906dd44734a3aefd5b033b14e9d4f9eaa09f43cf91a3228c850780a33a1360e matches local. Independent Dropbox full-byte download not completed; runtime URL gate on prior attempt remains documented.
RUN06 missing Drive backup was uploaded now as1CH7EFv0r_3yPGE4cP6n7rJvF1E5Upn8V and authenticated download SHA256 matched. RUN06 Dropbox already existed id:BSpOijBcT10AAAAAAD-n4Q;nooverwrite and no new-upload claim,providerhash0d04bf5e7f2543584d27316641759918d7973c32f9376829de78f36915f7eba9 matched local. This is metadata/contenthash confirmation,not independent rawdownload.

FullZIP: scripts/REPLAY_OFFLINE.sh verify|build|tests|lint|reference are separate bounded commands with externally supplied Rust1.94.1;toolchain notbundled. Final external DELIVERY_RECEIPT.json owns remoteIDs,hashlevels,restorelogs;no recursive archive hashes.

Primary methodology: Reynolds,Hayes,Paschos,Norman arXiv0901.1110v3 DOI10.1016/j.jcp.2009.06.006 (joint radiation/chemistry/energy inside hydro splitting);PawlikSchaye arXiv1008.1071 (matched-rate multifrequency thermochemistry comparisons);SciPy1.17.0 solve_ivp documentation (Radau/DOP853 definitions). They do not certify this study's numerical values or novelty.
