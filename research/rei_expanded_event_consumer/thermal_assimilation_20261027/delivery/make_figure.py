"""Render one presentation from saved stdout only; no source evaluation."""
from __future__ import annotations

import signal
import time
signal.signal(signal.SIGPROF, signal.SIG_DFL)
remaining = 3.5 - time.process_time()
if remaining <= 0:
    raise SystemExit("presentation child startup CPU exhausted")
signal.setitimer(signal.ITIMER_PROF, remaining)

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

UNIT = Path(__file__).resolve().parents[1]
RAW = UNIT / "implementation/attempt01/stdout.json"
RAW_SHA256 = "3f6e942336cb18cf1422ce4736984fb5d7f7d85ca1af39aa0f126748a0c66d99"
FIGURES = UNIT / "delivery/figures"
raw = RAW.read_bytes()
if hashlib.sha256(raw).hexdigest() != RAW_SHA256:
    raise ValueError("saved scientific stdout changed")
saved = json.loads(raw)
if saved["status"] != "PASS_PENDING_INDEPENDENT_REVIEW" or saved["check_count"] != 118:
    raise ValueError("unexpected saved execution identity")
obs = saved["observations"]
power = obs["component_plot_data"]
state = obs["state"]
FIGURES.mkdir(parents=True, exist_ok=True)
png = FIGURES / "THERMAL_ASSIMILATION_LOCAL_SOURCE.png"
pdf = FIGURES / "THERMAL_ASSIMILATION_LOCAL_SOURCE.pdf"
datafile = FIGURES / "PLOT_DATA.json"
caption = FIGURES / "CAPTION_KO.md"
if any(path.exists() for path in (png, pdf, datafile, caption)):
    raise FileExistsError("preserve existing presentation; no automatic rerender")

labels = ["Photo → fast store", "Fast store → bath", "RR kinetic loss", "DR kinetic loss",
          "Planck Compton", "Net bath power"]
keys = ["photo_primary", "assimilation_heat", "RR_kinetic_loss", "DR_kinetic_loss",
        "Compton_CMB", "net_thermal_power"]
values = [power[key] for key in keys]
colors = ["#777777", "#E69F00", "#56B4E9", "#0072B2", "#4477AA", "#009E73"]
map_keys = ["proper", "physical", "reference", "eta"]
map_labels = ["Proper", "Density", "Reference", "η clock"]
steps = ["0.0002", "0.0001"]
errors = {step: [obs["finite_difference"][step][name]["residual_max"]
                 for name in map_keys] for step in steps}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 12, "axes.labelsize": 11, "axes.spines.top": False,
    "axes.spines.right": False, "figure.facecolor": "white", "savefig.facecolor": "white"})
fig = plt.figure(figsize=(14, 8))
ax_power = fig.add_axes([.18, .31, .34, .47])
ax_fd = fig.add_axes([.68, .31, .29, .47])
y = list(range(len(labels)))
ax_power.barh(y, values, color=colors, height=.62, edgecolor="white", linewidth=.6)
ax_power.scatter([values[3]], [3], s=16, color=colors[3], zorder=4)
ax_power.set_yticks(y, labels)
ax_power.invert_yaxis()
ax_power.set_xscale("symlog", linthresh=1e-49, linscale=1.0, base=10)
ax_power.set_xlim(-2e-34, 2e-34)
ax_power.set_xticks([-1e-35, -1e-42, 0, 1e-42, 1e-35],
    [r"$-10^{-35}$", r"$-10^{-42}$", "0", r"$10^{-42}$", r"$10^{-35}$"])
ax_power.axvline(0, color="#333333", linewidth=.7)
ax_power.grid(axis="x", color="#dddddd", linewidth=.6)
ax_power.set_axisbelow(True)
ax_power.set_title("a  Signed source powers", loc="left", pad=15, fontweight="bold")
ax_power.set_xlabel("Power [W m$^{-3}$] · symmetric log scale", labelpad=10)
for position, value in enumerate(values):
    ax_power.text(1.025, position, f"{value:+.3e}", transform=ax_power.get_yaxis_transform(),
                  va="center", ha="left", fontsize=10, clip_on=False)

positions = list(range(4))
width = .33
ax_fd.bar([i - width / 2 for i in positions], errors[steps[0]], width,
          color="#4477AA", label=r"$h=2\times10^{-4}$")
ax_fd.bar([i + width / 2 for i in positions], errors[steps[1]], width,
          color="#EE7733", label=r"$h=10^{-4}$")
ax_fd.set_yscale("log")
ax_fd.set_ylim(1e-11, 6e-8)
ax_fd.set_xticks(positions, map_labels)
ax_fd.set_ylabel("Maximum row-scaled JVP error", labelpad=7)
ax_fd.grid(axis="y", color="#dddddd", linewidth=.6)
ax_fd.set_axisbelow(True)
ax_fd.axhline(2e-8, color="#CC3311", linestyle="--", linewidth=1.2)
ax_fd.text(.03, 2.45e-8, r"Frozen criterion: $2\times10^{-8}$", color="#AA2211",
           transform=ax_fd.get_yaxis_transform(), fontsize=10)
ax_fd.set_title("b  Same-direction finite differences", loc="left", pad=15, fontweight="bold")
ax_fd.legend(loc="upper center", bbox_to_anchor=(.5, -.17), ncol=2, frameon=False, fontsize=10)

fig.text(.5, .965, "Native thermal join at the saved PW19 node", ha="center",
         va="top", fontsize=18, fontweight="bold")
fig.text(.5, .91,
    f"Real cached background: z = 2.479   |   T = {state['T_K']:,.2f} K   |   n_b = {state['nb_m3']:.6f} m⁻³",
    ha="center", va="top", fontsize=12)
fig.text(.5, .86,
    f"MANUFACTURED fast pool: ζ = (q·Y)/4 = {state['zeta']:.8f},   w = {state['w_nt']:.5e} J/baryon",
    ha="center", va="top", fontsize=11, color="#333333")
fig.text(.18, .19, r"Bath balance: $Q_{\rm th}=Q_A-L_{\rm RR}-L_{\rm DR}+Q_C$.", fontsize=11)
fig.text(.18, .155, "Photo primary power enters the fast store; it is separate from this bath sum.", fontsize=10)
fig.text(.18, .105,
    f"CONDITIONAL ν = {state['nu_s_inverse']:.6e} s⁻¹: independent parameter, numerically H_snapshot.",
    fontsize=11, fontweight="bold")
fig.text(.18, .066, "Local source only. No trajectory or qualified physical stopping-rate claim.", fontsize=11)
fig.text(.18, .032,
    "Native case-A Mao2017 RR hybrid + DR cooling; isotropic Planck reference. Both FD steps use the same fixed row-unit scales.",
    fontsize=9, color="#444444")
fig.savefig(png, dpi=180)
fig.savefig(pdf, metadata={"Title": "Conditional native thermal assimilation at the saved PW19 node",
                          "Subject": "Presentation of saved local-source output; no scientific reevaluation"})
plt.close(fig)

plot_data = {"source_path": str(RAW.relative_to(UNIT)), "source_sha256": RAW_SHA256,
    "power_unit": power["power_unit"], "power_labels": labels, "power_keys": keys,
    "power_values": values, "FD_map_keys": map_keys, "FD_steps": steps,
    "FD_row_scaled_errors": errors, "FD_criterion": 2e-8,
    "state_annotation": {key: state[key] for key in
        ("T_K", "nb_m3", "zeta", "w_nt", "nu_s_inverse", "H_s_inverse")},
    "source_evaluations": 0, "scientific_imports": [],
    "matplotlib_version": matplotlib.__version__}
datafile.write_text(json.dumps(plot_data, indent=2) + "\n")
caption.write_text(
    "# 그림 설명\n\n"
    "저장된 PW19 z=2.479 배경에서 조건부 thermal assimilation을 평가한 결과이다. "
    "빠른 전자 집단의 수와 에너지 모멘트는 ζ=q·Y/4 및 w=ζK_J/Γ로 구성했으며, "
    "ν는 저장된 H와 수치적으로 같게 선택한 독립 매개변수다. 이 집단의 우주론적 이력이나 물리적 정지율을 추정하지 않았다.\n\n"
    "왼쪽 패널은 photo→fast store, fast store→bath, RR·DR 냉각, Planck Compton 및 순수 bath 전력을 구분한다. "
    "Bath 열수지는 Q_A−L_RR−L_DR+Q_C이며 photo primary 항을 직접 더하지 않는다. "
    "DR 항까지 보이도록 대칭 로그축을 사용했고, 각 값은 W/m³로 적었다.\n\n"
    "오른쪽 패널은 같은 혼합 방향에서 h=2e−4와 h=1e−4로 얻은 네 표현의 최대 행별 정규화 JVP 오차다. "
    "두 step은 같은 해석적 operand scale을 사용하며, 동결 허용오차 2e−8을 모두 충족한다. "
    "이 그림은 기존 stdout만 읽었고 물리 source나 도함수를 다시 계산하지 않았다.\n\n"
    f"원문 SHA256: `{RAW_SHA256}`. 수치와 직접 대응하는 자료는 PLOT_DATA.json에 있다.\n",
    encoding="utf-8")
print(json.dumps({"status": "PRESENTATION_COMPLETE_FROM_SAVED_RAW", "source_sha256": RAW_SHA256,
    "outputs": [str(path.relative_to(UNIT)) for path in (png, pdf, datafile, caption)],
    "matplotlib_version": matplotlib.__version__, "scientific_evaluations": 0}, indent=2), flush=True)
