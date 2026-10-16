"""Read-only PR166 native cohort audit from the immutable verified private archive.

This is not a native execution. All arrays come from actual previously executed
PR166 snapshot_q*_axis1_level{1,2,4}.txt. The byte SHA-256 of the whole archive
is checked before extracting any source. Never rename an effective log-survival
optical depth into a microscopic Verner or Grackle opacity.
"""
import argparse
import hashlib
import json
import math
import re
import zipfile
from pathlib import Path

LOCKED_ARCHIVE_SHA256='2ebab11829b793eb19a0b91e5d04a3a8637e346e456ac0931c372585ef7e21de'
SUBDIR='research/rei_source_age_native_owner_bind_20261016/'


def split_numbers(text:str)->list[float]:
    return [float(t.strip()) for t in text.split(',') if t.strip()]


def parse_cohorts(snapshot:str)->list[dict]:
    blocks=snapshot.split('Cohort { birth: Birth {')[1:]
    out=[]
    for index,chunk in enumerate(blocks):
        fields={}
        for key in ('x','lower_x','upper_x','quadrature_weight_dln_a','j_per_h_dln_a'):
            match=re.search(r'\b'+key+r': ([-+.0-9eE]+)',chunk)
            if match is None: raise ValueError(f'cohort {index} field {key} missing')
            fields[key]=float(match.group(1))
        nums=[]
        for token in ('original','surviving'):
            match=re.search(r'\b'+token+r': PhotonState \{ number: \[([^\]]+)\]',chunk)
            if match is None:raise ValueError(f'cohort {index}: {token} number missing')
            array=split_numbers(match.group(1))
            if not array or any((not math.isfinite(n) or n<0) for n in array):raise ValueError('invalid photon count')
            nums.append(math.fsum(array))
        original,survived=nums
        fields['original_n']=original
        fields['survivor_n']=survived
        fields['log_survival_depth']=-math.log(survived/original) if survived>0 and original>0 else None
        fields['normalized_source_expected']=fields['j_per_h_dln_a']*fields['quadrature_weight_dln_a']
        fields['source_mass_relative_defect']=(original-fields['normalized_source_expected'])/original if original>0 else 0.
        out.append(fields)
    return out


def summarize(cohorts:list[dict])->dict:
    if not cohorts:raise ValueError('empty cohorts')
    born=math.fsum(r['original_n'] for r in cohorts)
    survived=math.fsum(r['survivor_n'] for r in cohorts)
    n=len(cohorts)
    share=cohorts[-1]['survivor_n']/survived if survived else None
    t_width=cohorts[-1]['upper_x']-cohorts[0]['lower_x']
    dist_to_end=cohorts[-1]['upper_x']-cohorts[-1]['x']
    lastdepth=cohorts[-1]['log_survival_depth']
    return {'age_panels':n,'emitted_n_per_H':born,'survived_n_per_H':survived,
            'survival_fraction':survived/born,'last_cohort_share_of_survivors':share,
            'last_birth_log_survival_depth':lastdepth,
            'last_age_to_endpoint_dln_a':dist_to_end,
            'effective_terminal_depth_per_dln_a':lastdepth/dist_to_end if lastdepth is not None else None,
            'inferred_whole_interval_effective_depth':lastdepth/dist_to_end*t_width if lastdepth is not None else None,
            'source_time_interval_dln_a':t_width,'max_source_quad_relative_defect':max(abs(r['source_mass_relative_defect']) for r in cohorts),
            'cohorts':cohorts}


def audit(archive:Path)->dict:
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest!=LOCKED_ARCHIVE_SHA256:raise ValueError(f'archive SHA mismatch: {digest}')
    groups={}
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failed')
        for q in ('-0.1','0','0.1'):
            grp={}
            for m in (8,16,32):
                suffix={8:'1',16:'2',32:'4'}[m]
                n=SUBDIR+f'evidence/repaired_local/snapshot_q{q}_axis1_level{suffix}.txt'
                grp[str(m)]=summarize(parse_cohorts(z.read(n).decode('utf-8')))
            ns=[grp[str(m)]['survived_n_per_H'] for m in (8,16,32)]
            totals=[grp[str(m)]['emitted_n_per_H'] for m in (8,16,32)]
            grp['observed_ratio_16_over_8']=ns[1]/ns[0]
            grp['observed_ratio_32_over_16']=ns[2]/ns[1]
            grp['effective_constant_opacity_depth_from_first_ratio']=32*math.acosh(ns[1]/ns[0])
            grp['effective_constant_opacity_depth_from_second_ratio']=64*math.acosh(ns[2]/ns[1])
            grp['total_emission_relative_span']=(max(totals)-min(totals))/max(totals)
            groups[q]=grp
        bad=json.loads(z.read(SUBDIR+'evidence/repaired_source_reference/first_invalid_trial_q-0.1.json'))
    return {'source_archive_sha256':digest,'source_PR166_HEAD':'553ce556d9f8662290c000ec675c7e6007c9d895',
            'native_source':'35d9747a0bbedcafdb568467ce7c1e7a25f965b6',
            'scope':'Previously executed native accepted outputs; not rerun or authoritative continuum solution',
            'fixed_opacity_fit_policy':'Effective depth is cohort-integrated spectral survival; not a single microscopic opacity',
            'by_signed_s_over_H':groups,'failed_internal_DOP853_trial':bad}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('archive',type=Path);p.add_argument('--out',type=Path,required=True);args=p.parse_args()
    result=audit(args.archive);args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    for q,v in result['by_signed_s_over_H'].items():
        print('shear',q,'source_span',v['total_emission_relative_span'],'ratios',v['observed_ratio_16_over_8'],v['observed_ratio_32_over_16'])
        for n in ('8','16','32'):
            x=v[n];print(n,'emitted',x['emitted_n_per_H'],'survived',x['survived_n_per_H'],'last_cohort_share',x['last_cohort_share_of_survivors'],'eff_depth_full',x['inferred_whole_interval_effective_depth'])
