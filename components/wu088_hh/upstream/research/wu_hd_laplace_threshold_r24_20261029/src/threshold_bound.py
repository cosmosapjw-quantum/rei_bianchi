"""Source-typed finite Laplace necessary conditions for one GL2022 HD channel.

NOT a PES-native energy value, not a physical source correction, not an uncertainty
estimate. Applies only when the rate is a constant-normalized Maxwell average of
T-INDEPENDENT positive cross sections vs ENTRANCE-RELATIVE collision energy.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, localcontext, InvalidOperation
import json
from pathlib import Path
import re

K_B_J_K = Decimal("1.380649e-23")  # exact 2019 SI
E_J = Decimal("1.602176634e-19")  # exact 2019 SI electronvolt
EXPECTED_T = ("15","55","105","255","505","1005","1505","2005","2505","3005")
EXPECTED_TOKENS = ("3.99(14)","2.92(11)","1.15(10)","2.74(10)","3.33(10)","3.18(10)","2.85(10)","2.55(10)","2.30(10)","2.08(10)")
EXPECTED_LOCKS = {
    "parent_R23_head": "2f214319ca8600475b1d4e85d1ca21a0249136a8",
    "source_R18_head": "f7371c7c389cac9c1b504f6e741b80ea80d776f1",
    "source_R18_git_blob": "08fdadd5dc366c00b8b546fcc9820bf030f3ae6c",
    "primary_doi": "10.1063/5.0128598",
    "original_supplement_pdf_sha256": "a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754",
    "article_pdf_sha256_from_R18_receipt": "5c9d97511c46fa83ddf8e9db0fec0b2fb362f6cca00f58666a63e86a63f25bbc",
}

class SourceContractError(ValueError):
    pass


def nominal_printed_rate(s: str) -> Decimal:
    """3.99(14) is the printed 3.99*10^-14, NOT +/-14 standard deviation."""
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\((-?\d+)\)",s)
    if match is None:
        raise SourceContractError("invalid original token")
    return Decimal(match.group(1)).scaleb(-int(match.group(2)))


def validate_source(d: dict) -> None:
    if type(d) is not dict or d.get("schema") != "wu.r24.gl2022_pinned_single_channel.v1":
        raise SourceContractError("wrong source schema")
    for k,v in EXPECTED_LOCKS.items():
        if d.get(k) != v:
            raise SourceContractError("immutable original source identity drift: "+k)
    if d.get("channel") != "H+ + HD(v=0,j=2) -> D+ + H2(v'=0,j'=1)":
        raise SourceContractError("mismatched physical channel")
    rates=d.get("rates")
    if not isinstance(rates,dict) or tuple(rates.get("temperature_K",()))!=EXPECTED_T or tuple(rates.get("printed_tokens",()))!=EXPECTED_TOKENS:
        raise SourceContractError("native printed source table drift")
    if rates.get("unit") != "cm^3 s^-1" or rates.get("external_odd_J_spin_weight_applied") is not False:
        raise SourceContractError("source spin or volume unit misbound")
    if d.get("energy_axis_assumption") != "CONDITIONAL_ENTRANCE_RELATIVE_COLLISION_KINETIC_ENERGY" or d.get("collision_cross_section_T_independent") != "CONDITIONAL_ASSUMPTION":
        raise SourceContractError("do not assert source-native kinetic convention")
    if (d.get("gl2022_pes_native_threshold_meV") is not None or d.get("physical_Q_event_J") is not None
            or d.get("physical_bath_J") is not None or d.get("owner_ACK") is not None):
        raise SourceContractError("PES, physical Q, bath or owner cannot be promoted")
    if (d.get("canonical_WU_DAG")!="34/49_UNCHANGED" or d.get("R6_distinct_author")!="NOT_RUN"
       or d.get("C9_distinct_author")!="NOT_RUN" or d.get("HH_R10")!="OFF"
       or d.get("production")!="NOT_ISSUED" or d.get("L4") is not False):
        raise SourceContractError("unauthorized gate change")
    if d.get("spectroscopic_external_Q_meV") != "-20.95002099384045759056749544382632657967":
        raise SourceContractError("external spectroscopy target drift")


def bound_pair(beta_i: Decimal, k_i: Decimal, beta_j: Decimal, k_j: Decimal) -> Decimal:
    """Necessary theta upper bound; beta_i > beta_j, positive k values.

    F(beta)=k(beta)/beta^(3/2)/C; its constant prefactor cancels exactly.
    For support E>=theta: F(beta_i)<=exp[-theta*(beta_i-beta_j)]F(beta_j).
    """
    if not (beta_i > beta_j > 0 and k_i > 0 and k_j > 0):
        raise ValueError("beta must descend and rates be positive")
    with localcontext() as ctx:
        ctx.prec=70
        return ((k_j/k_i).ln()+Decimal("1.5")*(beta_i/beta_j).ln())/(beta_i-beta_j)


def analyze(d: dict) -> dict:
    validate_source(d)
    with localcontext() as ctx:
        ctx.prec=70
        kb_mev = K_B_J_K / E_J * Decimal(1000)
        temps=[Decimal(x) for x in EXPECTED_T]
        beta=[1/(kb_mev*T) for T in temps]
        kc=[nominal_printed_rate(x) for x in EXPECTED_TOKENS]
        # conversion cm3 -> m3; a constant factor, cannot move threshold bounds
        km=[x*Decimal("1e-6") for x in kc]
        neighbor=[bound_pair(beta[i],km[i],beta[i+1],km[i+1]) for i in range(9)]
        all_pairs=[bound_pair(beta[i],km[i],beta[j],km[j]) for i in range(10) for j in range(i+1,10)]
        # Under the explicit nearest-0.01 mantissa display assumption only, not model Q error.
        lo15=Decimal("3.985e-14")*Decimal("1e-6")
        hi55=Decimal("2.925e-11")*Decimal("1e-6")
        display_upper=bound_pair(beta[0],lo15,beta[1],hi55)
        physical_theta=-Decimal(d["spectroscopic_external_Q_meV"])
        gap=physical_theta-neighbor[0]
        # Fixed k55 normalization: predicted k15 / nominal k15 at theta>=spectroscopic theta
        ratio=(-gap*(beta[0]-beta[1])).exp()
        # log F convexity gives ordered neighbor energy secants across ascending T.
        convex=[neighbor[i+1]-neighbor[i] for i in range(8)]
        return {
            "schema":"wu.r24.conditional_laplace_support_result.v1",
            "source_r18_blob":d["source_R18_git_blob"],
            "selected_reaction":d["channel"],
            "input_T_K":list(EXPECTED_T),
            "input_k_m3_s":[str(x) for x in km],
            "kB_meV_per_K":str(kb_mev),
            "beta_inv_meV":[str(x) for x in beta],
            "adjacent_theta_upper_meV":[str(x) for x in neighbor],
            "all_45_pair_min_upper_meV":str(min(all_pairs)),
            "adjacent_convexity_secant_increments_meV":[str(x) for x in convex],
            "necessary_log_convexity_at_10_nodes":all(x>0 for x in convex),
            "most_constraining_pair_T_K":["15","55"],
            "theta_nominal_upper_meV":str(neighbor[0]),
            "theta_nearest_display_rounding_upper_meV":str(display_upper),
            "rounding_semantics":"hypothetical nearest 0.01 displayed mantissa, not model uncertainty or data likelihood",
            "spectroscopic_candidate_theta_meV":str(physical_theta),
            "candidate_minus_nominal_bound_meV":str(gap),
            "max_15K_ratio_if_theta_ge_spectroscopic":str(ratio),
            "nominal_15K_to_max_ratio":str(1/ratio),
            "conditional_contract":"entrance-relative collision E; nonnegative, T-independent cross section; ordinary Maxwell integral exactly; no hidden T-dependent prefactor",
            "conclusion":"conditional necessary mismatch, NOT GL2022 physical/PES invalidity proof",
            "GL2022_PES_native_threshold_meV":None,
            "physical_Q_event_J":None,
            "physical_bath_J":None,
            "owner_ACK":None,
            "DAG":{"completed":34,"total":49,"promotions":0},
            "R6_distinct_author":"NOT_RUN","C9_distinct_author":"NOT_RUN",
            "HH_R10":"OFF","L4":False,"production":"NOT_ISSUED"
        }


def main():
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=a.parse_args(); data=json.loads(args.source.read_text(encoding='utf8'))
    result=analyze(data);args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('x',encoding='utf8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')

if __name__=='__main__':main()
