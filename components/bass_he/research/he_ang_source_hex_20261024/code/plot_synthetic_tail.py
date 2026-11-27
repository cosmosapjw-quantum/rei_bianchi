"""Authorized manufactured counterexample; never reads physical provider data."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from hex_intake import evaluate, exact_tail


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    c = [2, 0, 2]  # SYNTHETIC dimensionless manufactured amplitude
    xs = [i/200 for i in range(201)]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), layout='constrained')
    axes[0].plot(xs, [evaluate(c, x).real for x in xs], label='Full: C₀/2 + C₂T₂', color='#155e75')
    axes[0].plot(xs, [evaluate(c, x, m=2).real for x in xs], '--', label='First-small prefix m = 2', color='#b45309')
    axes[0].scatter([.5], [-1], color='#155e75')
    axes[0].set(xlabel='Normalized coordinate x ∈ [0,1]', ylabel='Manufactured amplitude (dimensionless)', title='Late nonzero coefficient: C = (2,0,2)')
    axes[0].legend(fontsize=8)
    ms = [1, 2, 3]
    axes[1].plot(ms, [float(exact_tail(c, m)) for m in ms], 'o-', label='Exact represented-coefficient bound τₘ', color='#155e75')
    axes[1].plot(ms, [abs(evaluate(c, .5)-evaluate(c, .5, m=m)) for m in ms], 'x--', label='Error at x = 1/2', color='#b45309')
    axes[1].set(xlabel='Retained coefficient count m', ylabel='Absolute truncation error / bound', title='Control the entire omitted suffix', xticks=ms, ylim=(-.1, 2.4))
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=.2)
    fig.suptitle('SYNTHETIC manufactured amplitude — no physical provider values', fontsize=11)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    main()
