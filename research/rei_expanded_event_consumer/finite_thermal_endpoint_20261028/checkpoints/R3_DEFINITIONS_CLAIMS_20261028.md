# R3: definitions, assumptions and claim boundaries

Date: 2026-10-28 KST. New unit 3/20; original DAG working 33/88, central 28/88, delta 0. Status: COMPLETE_PREMISE_ALIGNMENT, not independent scientific admission.

## Caloric variables

V0 is a fixed reference volume, Va=V0 and Vb=R V0 with R>0. N is thermal translational-particle count divided by V0, in reference m^-3. U is gas translational energy divided by V0, in J per reference m^3. Thus physical right-endpoint number and energy densities are N/R and U/R. N is not the number of translational degrees of freedom.

The conditional caloric law is U=c_v N T with the same specified positive constant c_v throughout one transaction. Its units are J K^-1 per particle. For a nonrelativistic, single-temperature, monatomic ideal bath c_v=3 k_B/2. The R1 JSON key c means this c_v, not the speed of light; this notation clarification does not alter the immutable R1 file. A tangent delta c_v changes a parameter of the family, not an unmodelled time-dependent heat capacity. A general EOS is treated separately in R5.

The common bath contains each participating heavy atom/ion once and each thermal free electron once. Fast electrons, photons and atomic binding/excitation storage are excluded from U and from the thermal count, except that an explicitly modelled fast-to-thermal transfer changes the thermal count and U through its own ports. A common scalar temperature is an assumption; two independently heated species or a general nonthermal distribution need not satisfy it.

Q is signed integrated event energy delivered to the gas, per V0. W is signed integrated gas geometry work, per V0. Q>0 heats the energy store, not necessarily its temperature. W already contains its assigned volume work and is used once. No second adiabatic factor or 1/H is applied to integrated events. Atomic storage and retained/escaping radiation are separate ports, not aliases for Q.

## Two endpoint routes and three residuals

For supplied Na,Ta,c_v>0, define D=Na+deltaN and E=c_v Na Ta+Q+W. The algebraic event route requires D>0 and E>0 and returns T_hat=E/(c_v D).

The stored route takes Ua,Ub,Nb as independent supplied saved values, requires Ub>0 and Nb>0, and returns T_b=Ub/(c_v Nb). Preserve:

r0=Ua-c_v Na Ta,
r_bal=Ub-Ua-Q-W,
rN=Nb-D,
rE=r0+r_bal=Ub-E.

R1's rE remains the aggregate residual Ub-E. The new split r0+r_bal diagnoses initial EOS mismatch separately from the interval energy balance. Adding r0 again to an already aggregate rE would count the initial mismatch twice. None of these quantities is overwritten, clipped or used to repair the source.

For the selected H contribution, deltaN_H=deltaNeutral+deltaIon+deltaThermalElectron=sum(deltaFine)+deltaContinuum. Its fine-stock sum is retained even if it is a small nonzero source residual. Other bath particles and their increments must be supplied or explicitly fixed by the selected model; H stock alone does not establish the complete recipient bath.

## Assumptions and evidence status

| Statement | Status and scope |
|---|---|
| Translational energy and changing kinetic-particle count enter matter temperature | Literature-supported physical accounting in the cited recombination setting; exact finite formulas derived separately |
| Frozen storage consumer exposes distinct gas, atomic, photon and geometry-work ports | Source-code read at 53dea7d4; previous scoped tests reused, not rerun |
| Finite map, tangent, defect bound and volume composition | Targets for direct proof in R5, not already verified by the R1 theorems list |
| General caloric inverse | Conditional on a specified monotone EOS, a bracket and an explicit positive derivative lower bound |
| Physical native25 or temperature update for the BASS recipient | Unresolved: matched bath/EOS and native normalization not supplied |
| Small saved algebraic residual is a physical error radius | Not justified; physical radii remain null |

A matched U,N and caloric EOS determine temperature without a separate baryon density. The baryon density is additionally needed for abundance/native25 normalization. The present physical-temperature hold follows from missing matched bath/EOS, not a universal theorem that temperature always requires nb. Missing radii are unknown, never zero.

Independent review, numerical evaluation and implementation verification remain separate obligations. No source pin, physical input, original DAG status or resource ceiling changes in this stage.
