"""Saved JSON only: deliberately has no import of either scientific module."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--saved-json",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    source=Path(args.saved_json)
    data=json.loads(source.read_text())
    if not data["validation"]["success"]:raise SystemExit("cannot plot failed validation")
    number=lambda x:float(Fraction(x))
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout="constrained")
    for curve in data["map_curves"]:
        axes[0,0].plot([number(x) for x,y in curve["points"]],[float(y) for x,y in curve["points"]],label=f'e={curve["e"]}: {curve["topology"]}')
    axes[0,0].set(xlabel="CM cosine mu",ylabel="Laboratory cosine F(mu)",title="Independent Decimal80 Lorentz boost")
    axes[0,0].legend(fontsize=7)
    rows=data["native_rows"]
    x=[row["e"] for row in rows]
    for key,label in [("coincidence","Coincidence Y"),("hit_a","Hit A"),("hit_b","Hit B")]:
        axes[0,1].plot(x,[(number(row[key]["lower"])+number(row[key]["upper"]))/2 for row in rows],"o-",label=label)
    axes[0,1].set(xlabel="Incident energy [MeV]",ylabel="Manufactured measure",title="NIST declared masses; manufactured density")
    axes[0,1].legend(fontsize=8)
    bounds=data["bound_comparison"]
    axes[1,0].bar(["Default","Manual 1/16"],[number(bounds["default"]["width"]),number(bounds["manual"]["width"])])
    axes[1,0].axhline(number(bounds["sigma"])/2**40,color="black",linestyle="--",label="sigma / 2^40")
    axes[1,0].set(yscale="log",ylabel="Actual hit-A enclosure width",title="Actual bounds preserve manual-delta semantics")
    axes[1,0].legend(fontsize=8)
    axes[1,1].plot(x,[number(row["G"]) for row in rows],"o-",label="Exact G=A+e")
    ratios=[]
    for row in rows:
        y=row["coincidence"]
        # Centers only for display; exact interval scaling was tested and saved.
        ratios.append((number(row["pair_energy_MeV"]["lower"])+number(row["pair_energy_MeV"]["upper"]))/ (number(y["lower"])+number(y["upper"])))
    axes[1,1].scatter(x,ratios,marker="x",s=60,label="Saved pair-energy / Y")
    axes[1,1].set(xlabel="Incident energy [MeV]",ylabel="MeV per coincident pair",title="Shared-event physical energy closure")
    axes[1,1].legend(fontsize=8)
    for axis in axes.flat:axis.grid(alpha=.2)
    fig.suptitle("KINEMATIC08: conditional continuous-measure evidence",fontsize=13)
    output=Path(args.output)
    for extension in ["svg","png"]:
        path=output/f"KINEMATIC08.{extension}"
        if path.exists():raise FileExistsError(path)
        fig.savefig(path,dpi=140)
    plt.close(fig)
    receipt={"input_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"scientific_function_calls":0,"input":str(source),"outputs":["KINEMATIC08.svg","KINEMATIC08.png"]}
    with (output/"PLOT_RECEIPT.json").open("x") as handle:json.dump(receipt,handle,indent=2)
