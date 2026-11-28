"""Generate a conditional response-envelope sensitivity figure; NOT detector data."""
from pathlib import Path
from fractions import Fraction as F
import argparse, json
import matplotlib.pyplot as plt
from response_ratio_bridge import ratio_from_symmetric_relative_error, reweight_bounds


def build_figure(results_path, image_path):
    model = json.loads(Path(results_path).read_text())
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    for L, item in model['cases'].items():
        lo, hi = F(item['b_source_outer_low']), F(item['b_source_outer_high'])
        ds = [F(i, 1000) for i in range(0, 201, 4)]
        out = [reweight_bounds(lo, hi, ratio_from_symmetric_relative_error(d)) for d in ds]
        x = [100 * float(d) for d in ds]
        l, = ax.plot(x, [float(v[0]) for v in out], label=f'L={L} lower')
        ax.plot(x, [float(v[1]) for v in out], linestyle='--', color=l.get_color(), label=f'L={L} upper')
    ax.set(xlabel='Hypothetical response-shape envelope delta (%)',
           ylabel='Conditional outer bound on b_q',
           title='Angular response-ratio sensitivity (not measured detector data)')
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    Path(image_path).parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(image_path,dpi=180)
    plt.close(fig)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--results',default=str(Path(__file__).resolve().parents[1]/'RESULTS.json'))
    p.add_argument('--out',default='response_sensitivity.png')
    opts = p.parse_args()
    build_figure(opts.results,opts.out)
