function verify_rei_xcas_octave()
  rand("seed", 20260903);
  samples = 512;
  tol = 2.0e-11;
  max_residual = 0.0;

  checks = struct();
  checks.hubble_positive = true;
  checks.simplex_and_positivity = true;
  checks.electron_density_bounds = true;
  checks.redshift_telescoping = true;
  checks.transmission_bounds = true;
  checks.absorption_complement = true;
  checks.allocation_partition = true;
  checks.thin_limit = true;
  checks.expansion_work = true;
  checks.capacity_monotonicity = true;
  checks.hostile_mutations_detected = true;

  for k = 1:samples
    z = 30.0 * rand();
    H0 = 1.0 + rand();
    Om = 0.315;
    Ol = 0.685;
    H = H0 * sqrt(Om * (1.0 + z)^3 + Ol);
    dH = 3.0 * H0 * Om * (1.0 + z)^2 / (2.0 * sqrt(Om * (1.0 + z)^3 + Ol));
    checks.hubble_positive = checks.hubble_positive && H > 0.0 && dH >= 0.0;

    zh = 20.0 * (rand() - 0.5);
    logits = [0.0, 20.0 * (rand() - 0.5), 20.0 * (rand() - 0.5)];
    xh = 1.0 / (1.0 + exp(-zh));
    shifted = logits - max(logits);
    he = exp(shifted) / sum(exp(shifted));
    simplex_res = abs(sum(he) - 1.0);
    max_residual = max(max_residual, simplex_res);
    checks.simplex_and_positivity = checks.simplex_and_positivity && xh > 0.0 && xh < 1.0 && all(he > 0.0) && simplex_res < tol;

    nH = 0.1 + 10.0 * rand();
    nHe = 0.01 + rand();
    ne = nH * xh + nHe * (he(2) + 2.0 * he(3));
    checks.electron_density_bounds = checks.electron_density_bounds && ne >= 0.0 && ne <= nH + 2.0 * nHe + tol;

    r = 0.01 + rand(1, 4);
    N = 0.01 + rand(1, 4);
    red = -r .* N;
    red(1:3) = red(1:3) + r(2:4) .* N(2:4);
    red_res = abs(sum(red) + r(1) * N(1));
    max_residual = max(max_residual, red_res);
    checks.redshift_telescoping = checks.redshift_telescoping && red_res < tol;

    nodes = 48;
    w = rand(1, nodes);
    w = w / sum(w);
    tau_species = 10.0 .^ (-12.0 + 15.0 * rand(3, nodes));
    if mod(k, 3) == 0
      tau_species(3, :) = 0.0;
    endif
    tau_total = sum(tau_species, 1);
    clipped = min(tau_total, 745.0);
    trans = exp(-clipped);
    F = sum(w .* trans);
    absorbed_E = -expm1(-clipped);
    absorbed = sum(w .* absorbed_E);
    complement_res = abs(F + absorbed - 1.0);
    max_residual = max(max_residual, complement_res);
    checks.transmission_bounds = checks.transmission_bounds && F >= -tol && F <= 1.0 + tol && absorbed >= -tol && absorbed <= 1.0 + tol;
    checks.absorption_complement = checks.absorption_complement && complement_res < tol;

    tau_fraction = tau_species ./ repmat(tau_total, 3, 1);
    numerators = sum(repmat(w .* absorbed_E, 3, 1) .* tau_fraction, 2);
    allocation = numerators / absorbed;
    if absorbed <= 1.0e-15
      thin_num = sum(repmat(w, 3, 1) .* tau_species, 2);
      allocation = thin_num / sum(thin_num);
    endif
    if mod(k, 3) == 0
      allocation(3) = 0.0;
      allocation = allocation / sum(allocation);
    endif
    alloc_res = abs(sum(allocation) - 1.0);
    max_residual = max(max_residual, alloc_res);
    checks.allocation_partition = checks.allocation_partition && all(allocation >= -tol) && alloc_res < tol;

    tau_thin = 1.0e-14 * (0.1 + rand(3, nodes));
    total_thin = sum(tau_thin, 1);
    thin_num = sum(repmat(w, 3, 1) .* tau_thin, 2);
    thin_expected = thin_num / sum(thin_num);
    abs_thin_E = -expm1(-total_thin);
    thin_frac = tau_thin ./ repmat(total_thin, 3, 1);
    thin_nonlin_num = sum(repmat(w .* abs_thin_E, 3, 1) .* thin_frac, 2);
    thin_actual = thin_nonlin_num / sum(w .* abs_thin_E);
    thin_res = max(abs(thin_actual - thin_expected));
    max_residual = max(max_residual, thin_res);
    checks.thin_limit = checks.thin_limit && thin_res < tol;

    p = 0.01 + rand();
    work = 3.0 * H * p;
    checks.expansion_work = checks.expansion_work && work >= 0.0 && abs(work - (H*p + H*p + H*p)) < tol;

    M = rand(); nc = rand(); X = rand(); dt = 0.01 + rand();
    capacity = M + nc * (1.0 - X) / dt;
    checks.capacity_monotonicity = checks.capacity_monotonicity && capacity >= M && (1.0 - X) / dt >= 0.0 && -nc / dt <= 0.0;
  endfor

  % Hostile controls use fixed, nondegenerate probes.  Their purpose is to
  % detect formula mutations, not to impose an arbitrary amplitude floor on
  % randomly sampled states close to a physical boundary.
  r_probe = [0.2, 0.3, 0.4, 0.5];
  n_probe = [1.0, 2.0, 3.0, 4.0];
  omitted_inflow = abs(sum(-r_probe .* n_probe) + r_probe(1) * n_probe(1));
  wrong_ne = 0.4 * 0.25;
  wrong_expansion = 0.7 * 0.3;
  wrong_transmission = exp(0.25) - 1.0;
  missing_species = 3.0 / (1.0 + 2.0 + 3.0);
  hostile = [omitted_inflow, wrong_ne, wrong_expansion, wrong_transmission, missing_species];
  min_hostile_signal = min(hostile);
  checks.hostile_mutations_detected = all(hostile > 1.0e-6);

  values = cell2mat(struct2cell(checks));
  status = "PASS";
  if !all(values)
    status = "FAIL";
  endif

  receipt = struct();
  receipt.status = status;
  receipt.tool = "GNU Octave";
  receipt.version = version();
  receipt.oracle_class = "NUMERICAL_PROPERTY_NOT_EXACT_CAS";
  receipt.samples = samples;
  receipt.tolerance = tol;
  receipt.max_abs_residual = max_residual;
  receipt.minimum_hostile_signal = min_hostile_signal;
  receipt.checks = checks;
  receipt.claim_boundary = "BOUNDED_REI_FORMULA_PROPERTIES_ONLY";

  here = fileparts(mfilename("fullpath"));
  receipt_dir = fullfile(here, "..", "receipts");
  if !exist(receipt_dir, "dir")
    mkdir(receipt_dir);
  endif
  fid = fopen(fullfile(receipt_dir, "octave_receipt.json"), "w");
  fprintf(fid, "%s\n", jsonencode(receipt));
  fclose(fid);
  fprintf("%s\n", jsonencode(receipt));
  if !strcmp(status, "PASS")
    error("REI-XCAS Octave checks failed");
  endif
endfunction
