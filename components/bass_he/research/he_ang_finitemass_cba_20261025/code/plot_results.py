"""Two-panel finite-M figure from saved JSON only; no science module import."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io_utils import atomic_json

UNIT = Path(__file__).resolve().parents[1]


def main():
    source = UNIT/'results/ANALYSIS.json'
    raw = source.read_bytes(); data = json.loads(raw.decode('utf-8'))
    if not data['pass']:
        raise RuntimeError('plot requires accepted numerical checks in saved analysis')
    rows, trend = data['illustration'], data['mass_trend']
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.7), constrained_layout=True)
    colors = {'M2_synthetic': '#b44731', 'proton': '#246a8d', 'infinite_parent100': '#252525'}
    for key, label, style in [('M2_synthetic', 'M=2 synthetic', '-'), ('proton', 'Proton mass', '--'),
                               ('infinite_parent100', 'Infinite mass (parent100)', ':')]:
        axes[0].plot([r['oriented_k_angle_degree'] for r in rows], [r[key+'_per_eV'] for r in rows],
                     style, color=colors[key], linewidth=1.8, label=label)
    axes[0].set(xlabel='Oriented relative-pair k angle (degree)', ylabel=r'Jacobi TDCS ($a_0^2$ / (eV sr$^2$))',
                title='Direct CBA at fixed Jacobi variables', xlim=(-180, 180))
    axes[0].legend(fontsize=8); axes[0].grid(alpha=.22)
    axes[1].loglog([r['M'] for r in trend], [r['absolute_difference_per_eV'] for r in trend],
                   'o-', color='#66479b', linewidth=1.8, markersize=4)
    axes[1].set(xlabel=r'Nucleus/electron mass ratio $M$',
                ylabel=r'Absolute TDCS difference ($a_0^2$ / (eV sr$^2$))',
                title=r'Finite-M difference from infinite mass, $\theta_k=-50^\circ$')
    axes[1].grid(which='both', alpha=.22)
    fig.suptitle('Labelled direct channel; exchange absent\n'
                 r'$E_0=250$ eV, $E_r=5$ eV (relative pair, not lab $E_B$), $\theta_q=3^\circ$', fontsize=11)
    figures = UNIT/'results/figures'; figures.mkdir(parents=True, exist_ok=True)
    for extension in ['png', 'svg']:
        fig.savefig(figures/('FINITE_M_CBA.'+extension), dpi=170)
    plt.close(fig)
    atomic_json(figures/'FIGURE_METADATA.json', {'saved_input_sha256': hashlib.sha256(raw).hexdigest(),
                'saved_input': 'results/ANALYSIS.json', 'new_science_evaluations': 0,
                'panels': ['73-angle Jacobi curves M2/proton/infinite', 'Absolute finite-M trend at -50degree'],
                'energy': 'Er relative pair; not lab EB', 'scope': 'Model illustration; no physical provider admission'})
    print(json.dumps({'figures': ['FINITE_M_CBA.png', 'FINITE_M_CBA.svg'], 'saved_JSON_only': True}))


if __name__ == '__main__': main()
