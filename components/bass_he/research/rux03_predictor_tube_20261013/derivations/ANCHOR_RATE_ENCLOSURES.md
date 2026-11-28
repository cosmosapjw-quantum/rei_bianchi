# Source-pinned anchor intervals and the rational H/He predictor

Unit: HERE_RUX03_PREDICTOR_TUBE_AND_REANCHORED_FAMILY_07. Contribution: anchor coefficient and predictor author. Independent adoption is recorded separately by the final review. This document does not adopt the parent's tube certificate or native implementation.

## 1. Result and reuse boundary

At the declared anchor, the actual FT03 CI3/RR3/two-DR coefficients, their RR/DR captured-kinetic coefficients, and all twelve active species–ray Verner cross sections have narrow exact rational enclosures. Their interval midpoints define a full seven-component rational predictor with the original photon denominators. For every `0 <= h <= 10^9 s` and every fixed `mu in [10^9,1.5*10^9] eV/H`,

\[
 \|p(h)\|_\infty\le
 P_{\rm anchor}=\frac{38055093567}{50000000000}
 =0.76110187134 .
 \tag{A1}
\]

The uniform difference between this rational predictor and the exact source-defined anchor step \(hG_h(0)\) is bounded by

\[
 \|hG_h(0)-p(h)\|_\infty
 \le \frac{98035661}{1250000000000000000000000}
 =7.84285288\,10^{-17}.
 \tag{A2}
\]

These bounds are obtained from analytic positive-denominator inequalities and the exact coefficient enclosures, uniformly in h. The calculation is not a time trajectory, nonlinear stage solve or sample-based bound.

The parent authority is [BASS_HE PR34](https://github.com/cosmosapjw-quantum/BASS_HE/pull/34), exact head `3932669f7904f7f68f2f07dced4cf1da9d472480`. Its [rate envelopes](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/derivations/RATE_ENVELOPES.md), [physical primitive cube](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/derivations/PRIMITIVE_DIFFERENTIAL_BOUNDS.md) and [full-source equations](https://github.com/cosmosapjw-quantum/BASS_HE/blob/3932669f7904f7f68f2f07dced4cf1da9d472480/research/rux03_continuation_certificate_20261013/derivations/FULL_SOURCE_CONTINUATION_CERTIFICATE.md) are reused. No successful parent whole-box cap or derivative check was re-executed.

The fresh minimal source read found PR34 and [provider PR114](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/114) unchanged. The provider remains `a5c958c414dea41216b445c05f58df837f05cacb`. Exact retained files and hashes are in [CURRENT_SOURCE.json](../source_map/CURRENT_SOURCE.json). The mathematical functions use the source's real decimal literals; binary64 evaluation error remains a separate implementation obligation.

## 2. Fixed input and exact Doppler cells

The setting remains a fixed local Eulerian tetrad and volume with one common gas velocity, signature \((-+++)\), and \(D=\gamma n_H\). Use cm, s and erg for native constants,

\[
 c=29979245800\ {\rm cm/s},\quad
 k_B=1.380649\,10^{-16}\ {\rm erg/K},\quad
 \epsilon=1.602176634\,10^{-12}\ {\rm erg/eV}.
\]

The point is

\[
 D=10^{-3}\ {\rm cm^{-3}},\quad f=2/25,\quad
 T_*=50000\ {\rm K},\quad
 \zeta_*=(1/2,1/50,1/50),\quad
 \beta_*=(0,0,41/841),\quad\gamma_*=841/840.
 \tag{A3}
\]

Here \(\zeta=(x_{\rm HII},f x_{\rm HeII},f x_{\rm HeIII})\) is per H. Thus

\[
 e_H=\zeta_1+\zeta_2+2\zeta_3=14/25,\quad
 y=(1/2,1/25,1/50),\quad v=(1/2,1/50,1/50).
\]

The six ordered nodes are \((23{\rm eV},+x),(23{\rm eV},-x),(35{\rm eV},+y),(35{\rm eV},-y),(70{\rm eV},+z),(70{\rm eV},-z)\). Each has \(p_q^-=N_q^-/D=1/100\) and \(S_q=0\). Photon energies satisfy \(\epsilon E_q=\hbar\omega_q\); c and \(\hbar\) retain their physical meanings.

Writing \(b_q=1-\beta_*\cdot e_q\), \(\delta_q=\gamma_*b_q\), the exact Doppler factors are

\[
 \delta=(841/840,841/840,841/840,841/840,20/21,21/20),
\]
\[
 E'_q=\delta_q E_q=
 (19343/840,19343/840,841/24,841/24,200/3,147/2)\ {\rm eV}.
 \tag{A4}
\]

The active rows H I/He I/He II are respectively `111111`, `001111` and `000011`. This is twelve active species–ray cells; equal transverse pairs yield nine distinct species–energy evaluations. The source fit cutoffs \(13.60,24.59,54.42\) eV remain distinct from the binding values

\[
 \chi=(13.598434599702,\ 24.587389011,\ 54.41776)\ {\rm eV}.
\]

No recombination emission spectrum is introduced. The retained Case A kinetic-plus-binding escape is consumed by its original gas energy/momentum ledger.

## 3. Exact point enclosures and machine-readable schema

The full actual input is [ANCHOR_RATE_CHECK.wl](ANCHOR_RATE_CHECK.wl). It reuses the THEORY06 positive-interval operations, exact rational-power bracketing proof and n=64 exponential Taylor-tail enclosure. The bracket proposal grid is refined from \(10^{16}\) to \(10^{24}\) for this new point calculation:

\[
 \ell^q\le x^p\le u^q,\qquad 0<\ell\le u,
 \quad x>0,\quad p/q\in\mathbb Q.
\]

The 80-digit approximation only proposes endpoints; every acceptance comparison is exact. Negative p is covered because \(x^p\) is a positive rational. Exponentials use

\[
 S_{64}=\sum_{j=0}^{64}\frac{x^j}{j!},\quad
 S_{64}\le e^x\le
 S_{64}+\frac{x^{65}/65!}{1-x/66},
 \qquad 0\le x<66,
\]

followed by positive interval inversion for \(e^{-x}\). The reused analytic source formulas determine the point input to these helpers. Every compact output interval is rounded outward from the helper interval. All positive returned intervals satisfy relative width less than \(10^{-11}\); inactive cross sections are exactly zero.

The [actual result JSON](../evidence/ANCHOR_RATE_RESULT.json) uses **integer strings**, preserving values larger than a JSON consumer's exact binary64 integer range. Multiply each endpoint by the associated power of ten:

- `CI/RR/DR`: `grid_exponents.rates = -30`, units cm³/s.
- `KRR/KDR`: `grid_exponents.kinetic_erg = -40`, units erg cm³/s.
- `sigma`: `grid_exponents.sigma_cm2 = -34`, units cm², shape 3 species × 6 ordered rays × 2 endpoints.

The K entries are captured-kinetic **coefficients**, before multiplication by proper densities and before erg-to-eV conversion.

| Key / channel | Integer lower endpoint | Integer upper endpoint | Power of ten |
|---|---:|---:|---:|
| CI — H I → H II | 620696733347037265809 | 620696733347037286628 | −30 |
| CI — He I → He II | 18004708786742312958 | 18004708786742313563 | −30 |
| CI — He II → He III | 4479061309971466 | 4479061309971468 | −30 |
| RR — H II → H I | 126562738938060877 | 126562738938060878 | −30 |
| RR — He II → He I | 147458798047659920 | 147458798047659921 | −30 |
| RR — He III → He II | 732186839322161245 | 732186839322161246 | −30 |
| DR — He II → He I, resonance 1 | 14255481015487447 | 14255481015487448 | −30 |
| DR — He II → He I, resonance 2 | 652668751013474 | 652668751013475 | −30 |
| KRR — RR H II | 6002147996700655 | 6002147996700656 | −40 |
| KRR — RR He II | 8611808019379263 | 8611808019379264 | −40 |
| KRR — RR He III | 39179398395598723 | 39179398395598724 | −40 |
| KDR — DR resonance 1 | 9249735993288251 | 9249735993288252 | −40 |
| KDR — DR resonance 2 | 508184631417351 | 508184631417352 | −40 |


Every cell below is multiplied by \(10^{-34}\ {\rm cm^2}\).

| Node / gas-frame energy | H I integer endpoints | He I integer endpoints | He II integer endpoints |
|---|---|---|---|
| 23 eV +x / 19343/840 | [14910376653151553, 14910376653151554] | [0, 0] | [0, 0] |
| 23 eV −x / 19343/840 | [14910376653151553, 14910376653151554] | [0, 0] | [0, 0] |
| 35 eV +y / 841/24 | [4494628848629438, 4494628848629440] | [40563966639887996, 40563966639887997] | [0, 0] |
| 35 eV −y / 841/24 | [4494628848629438, 4494628848629440] | [40563966639887996, 40563966639887997] | [0, 0] |
| 70 eV +z / 200/3 | [669134932795894, 669134932795896] | [10762992324476187, 10762992324476188] | [9153530903211954, 9153530903211955] |
| 70 eV −z / 147/2 | [497940117889978, 497940117889980] | [8554953390959487, 8554953390959488] | [7000339884297802, 7000339884297803] |


Midpoint displays from the actual evaluator are

\[
\begin{split}
 k^{\rm CI}&\simeq(6.206967333470373\,10^{-10},
 1.800470878674231\,10^{-11},4.479061309971467\,10^{-15}),\\
 k^{\rm RR}&\simeq(1.265627389380609\,10^{-13},
 1.474587980476599\,10^{-13},7.321868393221612\,10^{-13}),\\
 k^{\rm DR}&\simeq(1.425548101548745\,10^{-14},
 6.526687510134745\,10^{-16})
\end{split}
\]

in cm³/s. The machine consumer must construct exact midpoint rationals from the integer endpoint strings, not from these displays.

## 4. From the same point coefficients to all source components

Let a hat denote the exact rational midpoint of a returned interval. Define

\[
 d_* =D\gamma_*^{-2}e_H,\qquad
 \widehat R_i^{\rm CI}=d_* y_i\widehat k_i^{\rm CI},\quad
 \widehat R_i^{\rm RR}=d_* v_i\widehat k_i^{\rm RR},\quad
 \widehat R_k^{\rm DR}=d_*v_2\widehat k_k^{\rm DR}.
 \tag{A5}
\]

The density factor is the inherited per-H conversion of two proper densities. No additional time-dilation factor is inserted. The midpoint kinetic and binding escape powers are

\[
 \widehat K=\frac{d_*}{\epsilon}
 \left(\sum_i v_i\widehat\kappa_i^{\rm RR}
             +v_2\sum_k\widehat\kappa_k^{\rm DR}\right),
\quad
 \widehat B_{\rm esc}=\sum_i\chi_i\widehat R_i^{\rm RR}
             +\chi_2\sum_k\widehat R_k^{\rm DR}.
 \tag{A6}
\]

Here and below indices \(i=1,2,3\) label the H I, He I, He II edges, so \(\chi_2\) is the He I binding threshold. The actual midpoint displays are

\[
 \widehat K\simeq1.447796333744005\,10^{-16},\qquad
 \widehat B_{\rm esc}\simeq9.705480781128937\,10^{-16}
 \quad{\rm eV/(H\,s)}.
\]

For photons retain

\[
 \widehat\lambda_{iq}=cD y_i b_q\,\widehat\sigma_{iq},\quad
 \widehat\Lambda_q=\sum_i\widehat\lambda_{iq},\quad
 \widehat R^\gamma_{iq}(h)=
 \frac{p_q^-\widehat\lambda_{iq}}{1+h\widehat\Lambda_q}.
 \tag{A7}
\]

Every total \(\widehat\Lambda_q\) is positive. Its six midpoint displays in s⁻¹ are

\[
 (2.235009233277059\,10^{-11},\,2.235009233277059\,10^{-11},
 1.160158765772246\,10^{-11},\,1.160158765772246\,10^{-11},
 2.703929138367891\,10^{-12},\,2.298871104371068\,10^{-12}).
\]

The source at the anchor has \(\Gamma_*=-u_*\cdot u_*=1\). Therefore its affine thermal row has exact RR/DR binding cancellation:

\[
 S_t=\sum_{iq}(E'_q-\chi_i)R^\gamma_{iq}
                  -\sum_i\chi_iR_i^{\rm CI}-K .
 \tag{A8}
\]

The full momentum source still contains kinetic **and** binding escape,

\[
 S_{m_j}=\sum_{iq}E_q e_{qj}R^\gamma_{iq}
                   -(\gamma_*\beta_*)_j(K+B_{\rm esc}).
 \tag{A9}
\]

In particular \((\gamma_*\beta_*)_z=41/840\). Equations (A5)–(A9) retain every CI, RR, both DR and active photo channel.

### Exact transverse parity

For this anchor and this ordered inventory,
\(\widehat\lambda_{i,+x}=\widehat\lambda_{i,-x}\) and
\(\widehat\lambda_{i,+y}=\widehat\lambda_{i,-y}\). The totals and photon denominators are identical within each pair. Equal incoming inventories then cancel their transverse lab momentum terms exactly for every h. The anchor gas escape also has no transverse component. Thus

\[
 p_5(h)=p_6(h)=0.
 \tag{A10}
\]

The same parity holds for the true point coefficients, not only for their midpoints, because their function arguments are identical. This is an anchor predictor identity. It does not discard transverse variables or source derivatives in the full tube, where the candidate velocity can move away from \(\beta_*\).

## 5. Compact rational predictor and the actual mu scale

Use the inherited affine coordinates \((\zeta,t,\mathbf m)\) and normalized X scale

\[
 (10^{-3},10^{-3},10^{-3},1/4,a_*10^{-6},a_*10^{-6},a_*10^{-6}),
\quad
 a_*=\mu+B_*,\quad B_*=\frac{8871068060291}{10^{12}}\ {\rm eV/H}.
 \tag{A11}
\]

The fixed reference parameter \(\mu\) is retained for each stage. Its family range is \([10^9,1.5\,10^9]\) eV/H.

The result stores the nonzero row indices `predictor.rows = [1,2,3,4,7]`, a length-five vector `predictor.A`, a 5×6 matrix `predictor.B` and six denominators `predictor.Lambda`, all as exact rational strings. These A/B objects are **predictor coefficients**, distinct from the parent's 7×7 corrector preconditioners.

For the first four rows,

\[
 p_i(h)=h\left[A_i+\sum_{q=1}^6
          \frac{B_{iq}}{1+h\widehat\Lambda_q}\right],
 \qquad i=1,2,3,4.
 \tag{A12}
\]

The fifth stored row corresponds to component 7 and has

\[
 p_7(h)=\frac h{a_*}\left[A_7+\sum_{q=1}^6
          \frac{B_{7q}}{1+h\widehat\Lambda_q}\right].
 \tag{A13}
\]

Together with (A10), these are all seven components. The first four rows are independent of \(\mu\). The only \(\mu\) dependence of this anchor predictor is the actual \(a_*\) divisor in the longitudinal momentum row. Its physical scale remains \(a_*10^{-6}\); no substitution of the lower-bound number 1000 is made in the predictor.

The exact coefficient definitions, using the midpoint events in (A5)–(A7), are

\[
\begin{split}
 A_1&=1000(\widehat R_1^{\rm CI}-\widehat R_1^{\rm RR}),\\
 A_2&=1000(\widehat R_2^{\rm CI}-\widehat R_2^{\rm RR}
          -\widehat R_3^{\rm CI}+\widehat R_3^{\rm RR}
          -\widehat R_1^{\rm DR}-\widehat R_2^{\rm DR}),\\
 A_3&=1000(\widehat R_3^{\rm CI}-\widehat R_3^{\rm RR}),\\
 A_4&=-4\left(\sum_i\chi_i\widehat R_i^{\rm CI}+\widehat K\right),\\
 A_7&=-10^6\frac{41}{840}(\widehat K+\widehat B_{\rm esc}),
\end{split}
 \tag{A14}
\]

and

\[
\begin{split}
 B_{1q}&=1000p_q^-\widehat\lambda_{1q},\\
 B_{2q}&=1000p_q^-(\widehat\lambda_{2q}-\widehat\lambda_{3q}),\\
 B_{3q}&=1000p_q^-\widehat\lambda_{3q},\\
 B_{4q}&=4p_q^-\sum_i(E'_q-\chi_i)\widehat\lambda_{iq},\\
 B_{7q}&=10^6p_q^- E_q e_{qz}\widehat\Lambda_q .
\end{split}
 \tag{A15}
\]

The actual Wolfram batch verified that this compact representation equals the direct source construction in every stored row. Each denominator remains the sum of the same opacity coefficients used in its event numerator.

## 6. Uniform absolute-value majorant and the two parent radii

For \(H_2=10^9\) s define

\[
 M_i(H_2)=H_2|A_i|+
 \sum_q\frac{H_2|B_{iq}|}{1+H_2\widehat\Lambda_q}.
 \tag{A16}
\]

The elementary derivative
\(d[h/(1+h\Lambda)]/dh=(1+h\Lambda)^{-2}>0\)
shows that \(|p_i(h)|\le M_i(H_2)\) for the first four rows and all \(h\in[0,H_2]\). For row 7, divide its bound by
\(a_{\min}=10^9+B_*\), which bounds the family uniformly without altering the actual predictor in (A13).

The actual outward componentwise cap is

\[
 \left(
 \frac{38055093567}{50000000000},
 \frac{109959228987}{10^{12}},
 \frac{4803317151}{500000000000},
 \frac{25025319907}{500000000000},
 0,0,\frac{174661}{50000000000}
 \right).
 \tag{A17}
\]

This gives (A1). For comparison, the point evaluation at \(h=H_2,\mu=10^9\) returned

\[
 p(H_2)\simeq
 (0.7611018713393163,\ 0.1099592289862403,\
 0.00959037238913666,\ 0.0311085254525885,\
 0,0,\ 2.820730017415528\,10^{-7}).
 \tag{A18}
\]

The display is an algebraic evaluation of the explicit rational function, not an executed stage iteration.

The parent selected \(H_1=H_2/2\), predictor allowances \(P_1=2/5\), \(P_2=77/100\), \(\eta=1/100\) and \(\rho_1=1/50,\rho_2=1/10\). The point coefficients already justify the predictor allowances without redoing the source calculation. Each exact \(\widehat\Lambda_q<3\,10^{-11}\ {\rm s}^{-1}\), as follows by integer comparison of the stored rational totals. For each positive-denominator term,

\[
 \frac{H_1/(1+H_1\Lambda)}{H_2/(1+H_2\Lambda)}
 =\frac12\,\frac{1+H_2\Lambda}{1+H_1\Lambda}
 \le\frac{103}{200}.
\]

The constant term ratio is \(1/2\), so

\[
 \sup_{0\le h\le H_1}\|p(h)\|_\infty
 \le\frac{103}{200}P_{\rm anchor}<\frac25,\qquad
 P_{\rm anchor}<\frac{77}{100}.
 \tag{A19}
\]

For the first strict inequality, the exact integer comparison is
\(103(38055093567)=3919674637401<4000000000000\).
Equation (A19) is a direct consequence of the recorded rational coefficients and (A16); no additional evaluator call was made for it. The parent separately certifies full-tube residual/preconditioner bounds and same-root connection. The anchor bound alone is not that tube certificate.

## 7. Uniform midpoint defect supplied to the tube calculation

Let \(\delta\lambda_{iq}\) be the half-width of the opacity interval obtained by multiplying the compact cross-section interval by \(cDy_i b_q\), and let \(\delta\Lambda_q=\sum_i\delta\lambda_{iq}\). Every true coefficient lies in its compact interval, whose midpoint is the hat coefficient. An exact difference identity gives

\[
 \begin{split}
 \frac{\lambda_i}{1+h\Lambda}
 -\frac{\widehat\lambda_i}{1+h\widehat\Lambda}
 &=
 \frac{\lambda_i-\widehat\lambda_i}{1+h\Lambda}
 +\frac{h\widehat\lambda_i(\widehat\Lambda-\Lambda)}
 {(1+h\Lambda)(1+h\widehat\Lambda)},\\
 |R^\gamma_{iq}-\widehat R^\gamma_{iq}|
 &\le p_q^-\left(\delta\lambda_{iq}
       +H_2\widehat\lambda_{iq}\delta\Lambda_q\right)
       =:\varepsilon^\gamma_{iq}.
 \end{split}
 \tag{A20}
\]

All denominator factors are at least one. No division by a possibly small opacity is used. The right side is independent of h for \(0\le h\le H_2\).

Atomic event half-widths are \(d_*y_i\delta k_i^{\rm CI}\),
\(d_*v_i\delta k_i^{\rm RR}\), and \(d_*v_2\delta k_k^{\rm DR}\).
Likewise define \(\delta K\) and \(\delta B_{\rm esc}\) by the positive sums in (A6), using coefficient half-widths. The absolute chemical incidence sums, thermal weights \(|E'_q-\chi_i|\), binding losses \(\chi_i\delta R_i^{\rm CI}\), and longitudinal momentum weights \(E_q|e_{qz}|\) then give rowwise source error bounds \(E_i\). The input implements these positive sums explicitly, retaining both DR events and both escape contributions.

For example,

\[
\begin{split}
 E_1&=1000\left(\sum_q\varepsilon^\gamma_{1q}
                +\delta R_1^{\rm CI}+\delta R_1^{\rm RR}\right),\\
 E_4&=4\left(\sum_{iq}|E'_q-\chi_i|\varepsilon^\gamma_{iq}
             +\sum_i\chi_i\delta R_i^{\rm CI}+\delta K\right),\\
 E_7&=\frac{10^6}{a_{\min}}
 \left(\sum_{iq}E_q|e_{qz}|\varepsilon^\gamma_{iq}
        +\frac{41}{840}(\delta K+\delta B_{\rm esc})\right).
\end{split}
 \tag{A21}
\]

\(E_5=E_6=0\) follows from the exact true and midpoint parity, not from neglecting any transverse channel. Thus \(|hG_{h,i}(0)-p_i(h)|\le H_2 E_i\). The compact JSON's `uniform_point_midpoint_error_cap` is an outward rational cap on this vector; its maximum is (A2).

For a parent residual bound requiring an error in \(\widehat G_h(0)\) rather than h times that source, the **uniform source cap** is the recorded vector divided by \(H_2\). It is valid even at h=0 because it arises from the independent \(E_i\) bound in (A20)–(A21). It is not obtained by dividing a pointwise defect by a variable h. This distinction permits a sound parameter-uniform tube residual.

## 8. Actual execution, identities and implementation use

One new Wolfram evaluator call completed all **10 expression-check groups**. Internal exact witnesses numbered **112 rational-power brackets** and **5 exponential enclosures**; they are not additional independent theorems or native tests. The actual measured kernel time was **0.303558 s**, with Wolfram Language **15.0.1** on Linux x86-64.

The complete serialized inner JSON was 6,143 characters, and the complete returned tool text was 6,622 characters. No middle was omitted. Timing, kernel and system metadata were appended using `Join` and actually returned. No successful scientific calculation was repeated for capture or metadata.

- [Actual code](ANCHOR_RATE_CHECK.wl): SHA256 `63aa12d23c88d91aa820015587f8e554aaf46100bd123ac533410928bd5fb6b1`.
- [Actual call input](../evidence/ANCHOR_RATE_CALL_INPUT.json): SHA256 `49a6deaf461dab7c5ce6eadb94170d65b0f0d1ea62a1fabf6529f709d6fe1bd2`.
- [Unmodified raw tool result](../evidence/ANCHOR_RATE_RAW_RESULT.json): SHA256 `44d13fa3c0be946d1dfef17328e1795232f56fd577bcab6bb246885acae76eb9`.
- [Decoded result](../evidence/ANCHOR_RATE_RESULT.json): SHA256 `75284946ef8297f34120f9cee1eefa62f01e4fce5b92ede65861cd1aa13941ac`.
- [Execution record](../evidence/ANCHOR_RATE_EXECUTION_RECORD.json): SHA256 `32c8d93ef4c860dad9bd670adcb553d522ec11256ba51adceabd7f74f5503022`.

The normalization decoded the complete quoted Out[1] JSON and then parsed that JSON. No scientific field was changed or supplemented. Source/input/raw/result files were written atomically with file and directory fsync. The auxiliary Wolfram context lookup is not a mathematical premise or an additional evaluator call.

The tube author consumes `predictor.A/B/Lambda` together with the actual \(a_*\), fixed chart and old state. It may recompute the rational midpoint primitive rates from the grids for the proposed frozen-thermal chemical Jacobian, while retaining the electron closure and every photon denominator. Such a preconditioner and its full-tube validity belong to the parent's new calculation. This anchor contribution does not certify frozen rates away from the anchor.

Native build, native tests, chemical RHS, nonlinear solve, Picard/Newton trajectory, ODE/history and scientific Python executions were all zero. Future native consumers still require their own input/rounding/provider/primitive residual enclosure and owned event evidence.
