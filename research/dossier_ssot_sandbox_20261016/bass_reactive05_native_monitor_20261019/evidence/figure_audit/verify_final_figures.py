#!/usr/bin/env python3
"""Read-only BR05 figure audit; writes only an explicitly selected audit directory.

This reconstructs the published plot objects from their exact recorded input CSVs.
The plotting script is imported unchanged. ROOT and its save callback are redirected
to the audit directory; no original figure, CSV, source, or manifest is overwritten.
This is a visualization check, not a new physical run or convergence test.
"""
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import importlib.util
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--unit', type=Path, required=True)
    ap.add_argument('--out-dir', type=Path, required=True)
    args = ap.parse_args()
    unit = args.unit.resolve()
    out = args.out_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert not out.is_relative_to(unit), 'audit output must be outside the frozen unit'
    provenance_path = unit/'figures/FIGURE_PROVENANCE.json'
    provenance = json.loads(provenance_path.read_text())
    script = unit/'scripts/plot_br05.py'
    protected = [script, provenance_path]
    protected += [unit/r['path'] for r in provenance['inputs']]
    protected += sorted((unit/'figures').glob('*.png'))
    protected += sorted((unit/'figures').glob('*.pdf'))
    protected += sorted((unit/'figures').glob('*.csv'))
    before = {str(p.relative_to(unit)): sha(p) for p in protected}
    checks = []

    def check(name, condition, detail=None):
        checks.append(dict(name=name, passed=bool(condition), detail=detail))

    for r in provenance['inputs']:
        check('recorded input hash '+r['path'], sha(unit/r['path']) == r['sha256'])
    check('recorded plotting source hash', sha(script) == provenance['script_sha256'])

    # Independent scalar reductions; the histogram is a display statistic only.
    finals = rows(unit/'evidence/independent/pair/NATIVE_FINALS.csv')
    bygrid = {(int(r['N_t']), int(r['r'])):r for r in finals}
    check('complete finite rectangle', set(bygrid) == {(n,r) for n in (16,32) for r in (2,4,8)})
    mixed = {r['field']:r for r in rows(unit/'evidence/independent/pair/NATIVE_INTERACTION_COMPARISON.csv')}
    bar_reference = {}
    with localcontext() as ctx:
        ctx.prec = 96
        for field in ('photons_com3','mean_age_s','second_age_s2','q2'):
            def dtr(r):
                return Decimal(bygrid[(32,2*r)][field])-Decimal(bygrid[(16,2*r)][field])-Decimal(bygrid[(32,r)][field])+Decimal(bygrid[(16,r)][field])
            d2,d4 = dtr(2),dtr(4)
            ratio = abs(d4/d2)
            original = mixed[field]
            scale = max(abs(d2),abs(d4),Decimal('1e-100'))
            check('finite mixed differences '+field,
                  abs(d2-Decimal(original['D_tr_r2_to4'])) < scale*Decimal('1e-85') and
                  abs(d4-Decimal(original['D_tr_r4_to8'])) < scale*Decimal('1e-85'))
            check('mixed magnitude ratio '+field,
                  abs(ratio-Decimal(original['interaction_magnitude_ratio'])) < Decimal('1e-80'))
            bar_reference[field] = dict(D2=str(d2),D4=str(d4),ratio=str(ratio))
    newborn = rows(unit/'evidence/independent/monitor/NEWBORN_MEASURE_COMPARISON.csv')
    increment_max_defect = 0.0
    for r in newborn:
        ref=float(r['exact_constant_source_frozen'])
        source=float(r['source_frozen']); accepted=float(r['accepted'])
        increment_max_defect=max(increment_max_defect,
            abs((source-ref)/ref-float(r['source_clock_relative_shift'])),
            abs((accepted-source)/ref-float(r['transport_relative_shift'])),
            abs(float(r['source_clock_relative_shift'])+float(r['transport_relative_shift'])-float(r['combined_relative_shift'])))
    check('all 16 additive newborn increment definitions', len(newborn)==16 and increment_max_defect<5e-15,
          {'maximum_dimensionless_roundoff':increment_max_defect})
    rules=rows(unit/'evidence/independent/monitor/RULE_REFERENCE_COMPARISON.csv')
    envelope=rows(unit/'figures/MONITOR_ENVELOPE_DATA.csv')
    all_envelope=[]
    for r in envelope:
        energy=float(r['energy_ev'])
        rr=[v for v in rules if float(v['energy_ev'])==energy]
        expected={'W1_s_min':min(float(v['kernel_W1_s']) for v in rr),
                  'W1_s_max':max(float(v['kernel_W1_s']) for v in rr),
                  'CDF_sup_min':min(float(v['kernel_cdf_sup']) for v in rr),
                  'CDF_sup_max':max(float(v['kernel_cdf_sup']) for v in rr)}
        all_envelope.append(len(rr)==16 and all(float(r[k])==v for k,v in expected.items()))
    check('all 768 rule values enter 48 nonstatistical step envelopes', len(rules)==768 and len(envelope)==48 and all(all_envelope))

    import numpy as np
    histrows=rows(unit/'figures/RETAINED_AGE_HISTOGRAM_DATA.csv')
    edge=np.array([float(r['left_s']) for r in histrows]+[float(histrows[-1]['right_s'])])
    mass=[]; ages=[]; zeros=0
    with (unit/'evidence/native/monitor_n16_r8/MONITOR_FINAL_COHORTS.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            ages.append(float(r['age_s'])); mass.append(float(r['retained_count_com3']))
            zeros += float(r['retained_count_com3']) == 0.0
    mass=np.array(mass); ages=np.array(ages)
    check('all actual final cohorts positive age and nonnegative mass', len(mass)==314624 and np.all(ages>0) and np.all(mass>=0))
    check('histogram covers every actual age', np.all(ages>=edge[0]) and np.all(ages<=edge[-1]))
    hist,_=np.histogram(ages,bins=edge,weights=mass/mass.sum())
    supplied=np.array([float(r['retained_probability']) for r in histrows])
    check('all 32 histogram values reproduce', len(hist)==32 and np.array_equal(hist,supplied))
    check('histogram unit mass within floating point tolerance', abs(float(hist.sum())-1.0)<5e-13,
          {'sum':float(hist.sum()),'zero_weight_cohorts':zeros,'age_min_s':float(ages.min()),'age_max_s':float(ages.max())})

    # Reconstruct artist layouts in a separate directory, without saving new PNG/PDFs.
    capture=out/'artist_capture'
    capture.mkdir(exist_ok=True)
    link=capture/'evidence'
    if not link.exists():
        link.symlink_to(unit/'evidence',target_is_directory=True)
    else:
        assert link.resolve()==unit/'evidence'
    spec=importlib.util.spec_from_file_location('br05_plot_readonly',script)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT=capture
    import matplotlib
    from PIL import Image
    from pypdf import PdfReader
    layouts=[]

    def inspect(fig, output, stem, width_mm):
        fig.canvas.draw()
        renderer=fig.canvas.get_renderer()
        all_text=[]; tick_checks=[]
        for aidx,ax in enumerate(fig.axes):
            candidates=[ax.xaxis.label,ax.yaxis.label,ax.xaxis.get_offset_text(),ax.yaxis.get_offset_text()]
            candidates += [x for x in ax.get_children() if isinstance(x,matplotlib.text.Text)]
            if ax.get_legend() is not None:
                candidates += list(ax.get_legend().get_texts())
            for orientation,axis,lims in [('x',ax.xaxis,ax.get_xlim()),('y',ax.yaxis,ax.get_ylim())]:
                lo,hi=sorted(lims); visible=[]
                for which,ticks in [('major',axis.get_major_ticks()),('minor',axis.get_minor_ticks())]:
                    for tick in ticks:
                        value=tick.get_loc()
                        if not lo<=value<=hi:
                            continue
                        for label in (tick.label1,tick.label2):
                            if label.get_visible() and label.get_text():
                                candidates.append(label)
                                visible.append((value,which,label))
                visible.sort(key=lambda item:item[0])
                boxes=[(value,which,label,label.get_window_extent(renderer)) for value,which,label in visible]
                gaps=[]; collisions=[]
                for previous,current in zip(boxes,boxes[1:]):
                    gap=(current[3].x0-previous[3].x1 if orientation=='x' else current[3].y0-previous[3].y1)*72/fig.dpi
                    gaps.append(gap)
                    if gap<0:
                        collisions.append({'left':previous[2].get_text(),'right':current[2].get_text(),'gap_pt':gap})
                tick_checks.append(dict(panel=aidx+1,axis=orientation,
                    labels=[dict(value=value,kind=which,text=label.get_text()) for value,which,label in visible],
                    minimum_adjacent_gap_pt=min(gaps) if gaps else None,collisions=collisions))
            seen=set()
            for text in candidates:
                if id(text) in seen or not text.get_visible() or not text.get_text():
                    continue
                seen.add(id(text)); box=text.get_window_extent(renderer)
                all_text.append(dict(panel=aidx+1,text=text.get_text(),font_pt=text.get_fontsize(),
                    inside_canvas=box.x0>=-1 and box.y0>=-1 and box.x1<=fig.bbox.width+1 and box.y1<=fig.bbox.height+1))
        minimum_font=min(r['font_pt'] for r in all_text)
        check(stem+f' {width_mm}mm visible text boundary', all(r['inside_canvas'] for r in all_text))
        check(stem+f' {width_mm}mm minimum font 7.5pt', minimum_font>=7.5)
        check(stem+f' {width_mm}mm major and minor tick separation', not any(r['collisions'] for r in tick_checks))
        image_path=unit/'figures'/f'{stem}_{width_mm}mm.png'
        pdf_path=image_path.with_suffix('.pdf')
        with Image.open(image_path) as im:
            size=im.size; dpi=im.info.get('dpi')
        expected_height=142 if width_mm==182 else 234
        expected=(width_mm/25.4*220,expected_height/25.4*220)
        check(stem+f' {width_mm}mm PNG print dimensions', all(abs(s-e)<1.01 for s,e in zip(size,expected)))
        reader=PdfReader(pdf_path)
        page=reader.pages[0]
        pdf_mm=[float(page.mediabox.width)*25.4/72,float(page.mediabox.height)*25.4/72]
        check(stem+f' {width_mm}mm PDF exact media box', len(reader.pages)==1 and abs(pdf_mm[0]-width_mm)<1e-7 and abs(pdf_mm[1]-expected_height)<1e-7)
        layouts.append(dict(stem=stem,width_mm=width_mm,height_mm=expected_height,axes=len(fig.axes),
            layout='2 by 2' if width_mm==182 else '4 by 1',minimum_font_pt=minimum_font,
            png_size=size,png_dpi=dpi,pdf_mm=pdf_mm,png_sha256=sha(image_path),pdf_sha256=sha(pdf_path),
            visible_text=all_text,ticks=tick_checks))
        module.plt.close(fig)
        return dict(stem=stem,width_mm=width_mm,audit_only=True)

    module.save=inspect
    module.main()
    for name in ('MONITOR_ENVELOPE_DATA.csv','RETAINED_AGE_HISTOGRAM_DATA.csv'):
        check('read-only reconstructed derived CSV '+name, sha(capture/'figures'/name)==sha(unit/'figures'/name))
    after={str(p.relative_to(unit)):sha(p) for p in protected}
    check('all protected source/data/final figures unchanged during audit', before==after)
    report=dict(schema='BR05_READONLY_FIGURE_NUMERIC_AND_LAYOUT_AUDIT_V1',
        status='PASS' if all(r['passed'] for r in checks) else 'FAIL',
        scope='Visualization arithmetic, print-size and visible-text checks only; no physical solver or convergence tests rerun.',
        original_unit=str(unit),source_provenance_sha256=sha(provenance_path),
        script_sha256=sha(script),input_and_figure_hashes=before,
        bar_reference=bar_reference,checks=checks,layouts=layouts,
        visual_gate='Separate direct viewing and hostile/residual written review is required.')
    def scalar_json(value):
        if isinstance(value,np.generic):
            return value.item()
        raise TypeError(f'Unsupported audit JSON value: {type(value).__name__}')
    (out/'FIGURE_NUMERIC_LAYOUT_AUDIT.json').write_text(json.dumps(report,indent=2,default=scalar_json)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed':[r for r in checks if not r['passed']]}))
    raise SystemExit(0 if report['status']=='PASS' else 1)


if __name__=='__main__':
    main()
