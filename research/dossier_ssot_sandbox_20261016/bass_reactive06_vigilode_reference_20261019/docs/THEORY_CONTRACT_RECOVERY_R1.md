# BR06 frozen-operator contract — reconstructed text, recovery R1

This text reconstructs the previously derived physical contract from retained conversation payloads. It is not a claim that the deleted original document bytes or numerical evidence have been restored.

## Fixed physical problem

Use the actual recorded BR05 step-1 corrector gas on t in [0, 5e11 s], midpoint tm=2.5e11 s. Freeze its comoving inventory, so n_s(t)=n_s(tm_recorded)*V(tm_recorded)/V_case(t). The same recorded inventory anchors both SIGNED_MINUS and SIGNED_PLUS controls. Use the unchanged original MD14/BB50k source at actual birth geometry, original source normalization and all original spectral/angular labels.

Axisymmetric Bianchi-I has a_perp=a*exp(-b), a_parallel=a*exp(2b), V=a^3, signature (-,+,+,+). Preserve signed s/H separately from sqrt(3)*abs(s/H). For each birth beta, K_i=a_i(beta)*E_b*n_bi and E(t)=sqrt(sum_i(K_i/a_i(t))^2). These are the original energy-scaled Killing constants. E'=-E*sum_i(H_i*n_i^2); c remains explicit in kappa_s=c*n_s*sigma_s.

Atomic gates and binding energies are different inputs. H binding is 13.598434599702 eV, Verner H fitting gate 13.60 eV, and the manufactured D gate is 13.602134599702 eV with H-equality cross section. Original He binding/fit parameters must be re-read from restored source rather than guessed. No replacement of CI/RR/CX/CE/free-free/CMB owners or the S10 four-corner controller is authorized.

## Positive characteristic measures

For one birth, D(t)=integral_beta^t kappa(v)dv, kappa=sum_s kappa_s, P=exp(-D). Define A_s=integral P*kappa_s dt, Q_s=integral P*kappa_s*(E-chi_s)dt*eV_J on active channels, B_s=chi_s*A_s*eV_J, and W=integral P*E' dt*eV_J. Nonnegative rates and positive birth weights give nonnegative photon/species/heat measures.

P(end)+sum_s A_s=1 and E(end)*P(end)*eV_J+sum_s(Q_s+B_s)=E_birth*eV_J+W. Source-integrating the same measures preserves the ownership of thermal, binding, source, absorption and photon geometry work. The gas is not advanced in this diagnostic. Parent MONITOR geometry_work includes gas and photon work and is not a photon-only W oracle.

Constant j,kappa gives N_new=j*dt*Phi(tau), Phi(tau)=-expm1(-tau)/tau with Phi(0)=1. Species receive the absorbed mass times kappa_s/kappa for kappa>0, and zero at kappa=0.

## Independent numerical construction

Reconstruct the source-pinned donor Hermite polynomial and integrate dx/dq=dt*H(x) with independent SciPy DOP853, q=t/dt. Use positive global Gaussian birth quadrature and direct physical-time Gaussian event quadrature, with a separately integrated opacity primitive. Every birth retains its actual geometry, Killing constants, weight, age and label. Split known threshold roots before integrating smooth pieces.

The previously used native optical-depth range was modest enough for high-order global Gaussian quadrature, but its convergence must be measured anew after input restoration. It is not an arbitrary-optical-depth AP or rigorous whole-operator interval certificate.

The Rust positive optical-event route uses F=-expm1(-D), z=-log1p(-F*q), and inversion of the actual opacity primitive; P*kappa*dt=F*dq. Positive competitive fractions then preserve the real-arithmetic photon-number ledger. The previously repaired V2 selected positive physical-time event shapes for complete-path tau<=1e-8 to avoid subnormal divisions. Recovery must bind the reconstructed source and rerun its counterexamples before asserting this behavior verified.

## Separate birth-age and path errors

For tau-dependent fitted weights and nodes, sum_i w_i(tau)*exp(-tau*x_i(tau))=Phi(tau) implies

-Phi'(tau)=sum_i w_i*x_i*exp(-tau*x_i)+sum_i[tau*w_i*x_i'-w_i']*exp(-tau*x_i).

The represented raw-age moment is therefore not fixed by exact Phi alone. Check J10=-Phi' and J20=Phi'' separately. At fixed emitted birth nodes and weights, changing only the path integral isolates path discretization. Comparing that matched path reference to the continuous birth measure then isolates birth representation in the frozen problem.

C0 means constant midpoint source/opacity; C1 means actual source-time dependence with constant opacity; C2 means actual source with variable BASS/frozen-comoving gas. C2-C1 includes physical dilution and Killing redshift. It is not itself a numerical error.

W from energy subtraction is ill-conditioned when source energy is much larger than W. Report both W-relative discrepancy and source-energy-normalized discrepancy, and also independently integrate W. A small ledger residual is not an accuracy certificate.

## VigilODE scalar moment mapping

J_jk(z)=integral_0^1 exp(-z*x)*x^j*(1-x)^k dx. Splitting at one half and applying the two affine maps yields

J_jk(2z)=2^[-(j+k+1)]*[sum_l binom(k,l)*J_jl(z)+exp(-z)*sum_r binom(j,r)*J_rk(z)].

All coefficients are positive and the whole domain is retained. For chronological birth fraction u=1-x and j(u)=left*(1-u)+right*u, the survived mass is dt*[left*J10+right*J01]. Directed interval arithmetic and the pinned original kernel are additional implementation obligations. Native scalar interval containment must be freshly reproduced against exact represented binary64 input points.

The admitted BASS donor tables require positive directional expansion. Their manufactured near-edge witnesses are redshift exits. No blueshift-entry or nonlinear-history admission follows from this frozen reference.
