# THEORY07 — executed two-tube certificate

The exact Wolfram input is `TUBE_CERTIFICATE_CHECK.wl` (SHA256 `ae1d5dfe6743ee0b73d016ae5e088e37dc221c5bdfcaf0822775200a11661c22`). Its 14 named groups all returned `true` in Wolfram 15.0.1, Linux x86-64, kernel elapsed 0.019472 s. The complete captured result is `../evidence/TUBE_CERTIFICATE_RESULT.json`, SHA256 `881a66af1a5733249d83182f8840cd36e905b6a221a78defaf0d9f191e65176a`. Raw output is preserved separately; there was one tube evaluator call and no recapture execution.

## 1. Fixed parameter rectangles and exact inequalities

All values in the certificate are exact rational quantities or rational upward enclosures produced by `Ceiling[10^12 value]/10^12`. Decimals in this note are displays of those values. The family is \(\|\xi\|_\infty\le1/100\); every member has the full unchanged source and fixed non-gas inputs.

| Quantity | Tube 1 | Tube 2 |
|---|---:|---:|
| Whole parameter interval, s | \([0,500000000]\) | \([500000000,1000000000]\) |
| Fixed preconditioner parameter center, s | 250000000 | 750000000 |
| Chosen predictor bound \(P_j\) | \(2/5\) | \(77/100\) |
| Certified predictor bound from actual coefficients | 0.383361979889 | 0.76110187134 |
| Radius \(\rho_j\) | \(1/50\) | \(1/10\) |
| Physical margin \(1-\eta-P_j-\rho_j\) | \(57/100\) | \(3/25\) |
| Full-Jacobian contraction cap \(q_j\) | 0.023012093111 | 0.046670186416 |
| Minimum strict self-map margin \(\min_i[\rho_j-Y_{j,i}-\rho_jz_{j,i}]\) | 0.01032621961478 | 0.0601894501334 |
| Predictor-to-root error \(e_j\) | 0.009430555340586003 | 0.03686398004577188 |

The exact contraction caps are

\[
q_1=\frac{23012093111}{10^{12}},\qquad
q_2=\frac{2916886651}{62500000000}.
\tag{N1}
\]

The exact minimum tube margins are

\[
\frac{516310980739}{50000000000000}>0,\qquad
\frac{300947250667}{5000000000000}>0.
\tag{N2}
\]

These are all-parameter row-norm estimates: each inequality covers its entire \(h\) interval, every \(\xi\) in the compact old-gas cube, all seven endpoint variables, and the declared \(\mu\) interval.

## 2. Seven-row residual and Jacobian caps

The following exact terminating decimals are the upward rational caps used in the strict inequalities.

| Row | \(Y_{1,i}\) | \(z_{1,i}\) | \(Y_{2,i}\) | \(z_{2,i}\) |
|---|---:|---:|---:|---:|
| \(\zeta_1\) | 0.009213538523 | 0.023012093111 | 0.035143531225 | 0.046670186416 |
| \(\zeta_2\) | 0.002907672447 | 0.008714271492 | 0.011095808456 | 0.019053971655 |
| \(\zeta_3\) | 0.000259291956 | 0.000752707201 | 0.000991251421 | 0.001631064977 |
| \(t\) | 0.000706853705 | 0.001724033427 | 0.002700259873 | 0.003461871632 |
| \(m_x\) | 0.000000143374 | 0.000000349691 | 0.000000550938 | 0.00000070633 |
| \(m_y\) | 0.000000143374 | 0.000000349691 | 0.000000550938 | 0.00000070633 |
| \(m_z\) | 0.000000143374 | 0.000000349691 | 0.000000550938 | 0.00000070633 |

The preconditioners differ from identity only in their frozen chemical blocks. Their actual displayed values are

\[
A_1^{chem}\simeq
\begin{pmatrix}
0.999694005620251&0.0000783366616913&0.000155716891207\\
0.000000265047836&0.999128678117008&-0.000750800544000\\
-0.000000002545212&0.000120102870073&0.999999817618592
\end{pmatrix},
\]

\[
A_2^{chem}\simeq
\begin{pmatrix}
0.999098912507280&0.000240592831064&0.000472696829553\\
0.000001280662564&0.997405780479713&-0.002233076015753\\
-0.000000000982804&0.000359252090594&0.999999023252401
\end{pmatrix}.
\]

The exact matrices are the rational inverse expressions defined in the preserved WL input. Their norms satisfy

\[
\|A_1\|_\infty\le\frac{500059961517}{500000000000},\qquad
\|A_2\|_\infty\le\frac{500179138163}{500000000000}.
\tag{N3}
\]

The determinants of the blocks being inverted have positive lower bounds \(1.00117852898\) and \(1.003505386333\). Exact multiplication by their computed inverses returns identity. The certificate uses the full source's inherited seven-row derivative bounds, so it also covers the thermal and momentum feedback not present in the frozen preconditioner approximation.

## 3. Extension and connection

At the new endpoint,

\[
H_2B=\frac{2007609719349141}{1250000000000000}
=1.6060877754793128>1.
\tag{N4}
\]

Thus the zero-centered unit-cube self-map bound that supplied the parent branch cannot certify this new endpoint. The two translated predictor tubes do certify it. Since both centers are \(\xi+p(h)\), the first endpoint box at \(h=5\times10^8\) is contained in the second endpoint box by \(1/50<1/10\). Their roots coincide. At \(h=0\) the endpoint equals \(\xi\), and for \(\xi=0\) uniqueness identifies the new branch with the adopted THEORY06 branch on the overlap.

## 4. Cube uniqueness, input sensitivity and predictor accuracy

The stronger inherited derivative estimate, evaluated at the new endpoint and rounded upward, is

\[
\|hD_XG_h\|_\infty\le
q_Q=\frac{22546206219}{500000000000}=0.045092412438<1.
\tag{N5}
\]

It proves uniqueness throughout the physical unit cube and gives

\[
\|F_X^{-1}\|_\infty\le\frac{500000000000}{477453793781}<\frac{21}{20},
\]

\[
\|D_\xi(X-\xi)\|_\infty\le
\frac{22546206219}{477453793781}<\frac1{20}.
\tag{N6}
\]

The exact predictor-to-root error bounds are

\[
e_1=\frac{9213538523}{976987906889},\qquad
 e_2=\frac{35143531225}{953329813584}.
\tag{N7}
\]

The uniform midpoint coefficient error at the anchor produces a maximum displacement defect bounded by

\[
\frac{98035661}{1250000000000000000000000}
=7.84285288\times10^{-17}
\tag{N8}
\]

for \(0\le h\le10^9\) s. Its difference from (N7) is instructive: the certified predictor-to-root width is dominated by endpoint variation of the real nonlinear source, not by rational enclosure of anchor coefficients.

At \(h=10^9\) s, the midpoint predictor first four components are

\[
(0.7611018713393163,\ 0.1099592289862403,\ 0.009590372389136660,\ 0.03110852545258848).
\tag{N9}
\]

The transverse components vanish exactly. The longitudinal component is \(2.820730017415528\times10^{-7}\) at \(\mu=10^9\); its actual formula retains \(1/a_*(\mu)\). All these are predictor values, not a numerically solved endpoint. Combining (N7) with the predictor yields the certified root enclosures.

Using the selected scalar \(P_2\), \(\|X\|_\infty\le\eta+P_2+e_2<0.817\). Therefore the inherited primitive estimates give the convenient outward physical bounds

\[
|T-50000\,\mathrm K|<1144\,\mathrm K,\qquad
|\beta-\beta_*|_2<2.451\times10^{-6}.
\tag{N10}
\]

The exact expressions are \(1400(\eta+P_2+e_2)\) and \(3\times10^{-6}(\eta+P_2+e_2)\); the displayed values are approximately 1143.609572064081 K and \(2.450591940137316\times10^{-6}\).

For ten exact preconditioned corrector updates initiated at the predictor, the proven error bound \(q_j^{10}e_j\) is approximately \(3.92734\times10^{-19}\) and \(1.80717\times10^{-15}\) in the two tubes. The exact inequality \(\max_jq_j^{10}e_j<10^{-12}\) returned true. Executed corrector updates: zero. A native finite-precision implementation must add its real rounding and residual bounds before using the theorem.

## 5. Proof and execution status

The new outcome is a nonempty, explicitly constructed full-source family through \(H_2=10^9\) s. It extends the adopted interval, gives improved endpoint enclosures, proves input sensitivity and supplies an affine reanchoring contract. The stage parameter labels implicit BE equations with a fixed old input; temporal truncation and a changing-input time history remain separate coding/research obligations. No maximal-time claim, fold crossing or new no-go result is made.
