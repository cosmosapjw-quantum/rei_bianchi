# REI-ACCEL01: broad-redshift reduced history contract

## Objective and authority

Execute a new, additive, source-pinned volume-filling-factor reionization campaign over **mean-volume redshift 20 to 4**. Determine Q_HII, midpoint/completion redshifts, photon accounting and segment Thomson optical depth, with finite-shear and astrophysical sensitivity. Current user explicitly authorized planning, implementation, repo propagation and durable checkpoints. This is an architectural research split, not admission of the old native coupled solver.

The root model runtime identity is UNKNOWN; the user's previously selected Astra v4 research/coding harness is retained without claiming a model switch. Independent decision review is required for scoped promotion. Public repo files and posted reports were read; private ChatGPT conversation contents were not directly accessible.

## Protected meanings

- Metric (-,+,+,+), non-tilted axisymmetric Bianchi I, a_perp=a exp(-b), a_parallel=a exp(2b), s=b_dot, sigma²=3s².
- Reuse the existing exact dust+Lambda background at `research/physical_provider_20261010/background.py`, SHA256 b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d. Reparameterize its public constructor; do not relax any native source-bound receiver gate.
- Fix Robertson2015 reference cosmology h=.6774, Omega_m=.309, Omega_Lambda=.691, Omega_b=.02230/h², Y=.2453; keep baryon density and source versus mean a fixed between FLRW and Bianchi. These are historical model parameters, not a new observational fit. Ignore radiation and gas/radiation stress backreaction as an explicit dust+Lambda approximation.
- r=s_i/H_i at z_i=20; cases r=0,+/-.01,+/-.05,+/-.1. These are controlled sensitivity cases, not CMB-admitted cosmologies. Hfid is the reference scale, not the sheared present Hubble rate.
- R15 SFRD=.01376(1+z)^3.26/[1+((1+z)/2.59)^5.68] Msun yr^-1 Mpc^-3. Escaping effective H-ionizing rate=fesc*10^53.14*SFRD, fesc=.2. Above observed support this is the explicitly adopted published model continuation; no new inference. Initial Q=0 at20 is a separate approximation; probe Q_i=.001.
- H case-B recombination uses the Hui-Gnedin1997 published fit, at fixed ionized-zone T=20000K. C_HII=3; He is singly ionized inside HII regions and neutral outside, n_e=(nH+nHe)Q. This standard effective closure does not solve a He photon budget, HeIII, temperature evolution, residual electrons or spatial morphology.
- dx=d ln a, A=S/H and B=C alpha_B(nH+nHe)/H. Pre-overlap Q'=A-BQ. At Q=1 divert excess A-B to a nonnegative *unassigned post-overlap photon budget*. This is not a transported radiation field, escaped energy or a photon spectrum. Recombination photons are on-the-spot (Case B), not separately added.
- Emitter/source, recombination and excess counters satisfy Q-Q_i+Nrec+Nexcess=Nemit. tau'=c sigma_T(nH+nHe)Q/H. tau(20→4) is a segment only, not total CMB tau. At fixed proper-time endpoints it is direction-independent; mean z is not directional observed z.
- CR=OFF in this **independent reduced baseline**. CR provider completion remains HOLD. RCT and HH molecular precision are likewise not represented. No photon-only substitution is claimed to meet CR requirements.

## Algorithm and predeclared acceptance

Use exact positivity-preserving frozen-coefficient scalar evolution on midpoint log-a steps, with analytic overlap time and integrated Q. No clipping of failed negative abundances or changing thresholds. Run the whole20→4 interval at2048/4096/8192 steps; report actual wall time, source/code hashes and outputs. Save a completion checkpoint after every case, and restart only when case config and producer identities match.

Observable convergence (4096 vs8192): max |delta Q|≤1e-7; |delta tau|≤1e-8; |delta z50|,|delta z90|≤1e-5; normalized photon-ledger residual≤1e-10. Independent adaptive DOP853/event reference must agree within same Q/tau/epoch budgets; it shares published coefficients but not the midpoint stepping or overlap accounting. Exact constant-source/recombination tests cover zero sink, source-off recombination and overlap with nonzero excess. Shear parity at matched +/-r should hold to1e-12; this tests the mean-volume model only, not angular radiation.

Probe fesc=.1/.3, C=2/5, T=10000/30000K one parameter at a time at8192 steps. These are scenario sensitivities, not statistical confidence intervals or atomic fit errors. Stop optional testing after these gates; do not replay PHYS21/22, CR02B, HE E13C3 or HH precision suites.

## Completion and remaining program

Completion here means a reviewed, reproducible reduced-model scientific history plus explicit full-model DAG. It cannot mean all original atomic physics is solved. Next full-native tasks are cold CaseA gas provider plus physical emissivity, scalable continuous photon source/remap with owner-defined observable budget, then Bianchi source/gas/geometry coupling. CR requires selecting between genuinely different causal lineages before stitching energy domains. RCT requires actual spectrum/heat/recoil inputs. Original precision lanes retain their last input hashes and next commands.
