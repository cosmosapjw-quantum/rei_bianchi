"""Exact-source derived examples: mandatory selectors only, no history-body edits."""
from pathlib import Path
import difflib
import hashlib
import json

V12_SHA='2ec4ef9c9830dae400328f49e8bf343f23be4cae839e12b62a2a7f6cbd3fea27'
V13_SHA='70029e2b2ada5ba9f2a7fee01c5c346c5d69cafe49db813e7202a642363745d5'
CASES=['D1_X1E5','D1_X1E4','D5_X1E5']
MODES12=['owner_like_be','ci_mid','ce_mid','ff_mid','cmb_mid','thermal_mid','chemical_mid','all_mid']
MODES13=['be_control','gas_mid','gas_opacity_mid','gas_opacity_exp','symmetric_be','combined','source_off']
LEVELS=[8,16,32,64,128,256]

def derive(source,destination,variant):
    source=Path(source);destination=Path(destination);raw=source.read_bytes()
    expected=V12_SHA if variant=='v12'else V13_SHA
    if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('IMMUTABLE_EXAMPLE_SOURCE_IDENTITY_MISMATCH')
    text=raw.decode();insertions=[]
    def insert(anchor,extra):
        nonlocal text
        if text.count(anchor)!=1:raise ValueError('selector anchor is not unique')
        text=text.replace(anchor,anchor+extra,1);insertions.append({'anchor':anchor,'inserted':extra})
    selector='''    let shard_case = std::env::var("LRS_SHARD_CASE").map_err(|_| "mandatory LRS_SHARD_CASE")?;
    let shard_mode = std::env::var("LRS_SHARD_MODE").map_err(|_| "mandatory LRS_SHARD_MODE")?;
    let shard_n: usize = std::env::var("LRS_SHARD_N").map_err(|_| "mandatory LRS_SHARD_N")?.parse().map_err(|_| "invalid LRS_SHARD_N")?;
'''
    if variant=='v12':
        selector+='''    if !CASES.iter().any(|(name,_,_)| *name == shard_case) || !MODES.iter().any(|mode| mode.as_str() == shard_mode) || !N_STEPS.contains(&shard_n) { return Err("invalid mandatory shard selector".into()); }
'''
        insert('fn main() -> Result<(), String> {\n',selector)
        insert('            for n in N_STEPS {\n','                if case != shard_case || mode.as_str() != shard_mode || n != shard_n { continue; }\n')
    elif variant=='v13':
        # Preserve all original argument parsing and numerical checks. Insert before File::create.
        selector+='''    if !["1e-5","1e-4"].contains(&shard_case.as_str()) || shard_case.parse::<f64>().map_err(|_| "invalid shard Xend")? != xend || !["be_control","gas_mid","gas_opacity_mid","gas_opacity_exp","symmetric_be","combined","source_off"].contains(&shard_mode.as_str()) || ![8usize,16,32,64,128,256].contains(&shard_n) || shard_n > max_n { return Err("invalid mandatory shard selector".into()); }
'''
        anchor='    let mut w = BufWriter::new(File::create(&args[1]).map_err(|e| e.to_string())?);'
        if text.count(anchor)!=1:raise ValueError('selector anchor is not unique')
        # Record this prefix insertion by its exact reversal, just as the append insertions.
        text=text.replace(anchor,selector+anchor,1);insertions.append({'before':anchor,'inserted':selector})
        insert('        while n <= max_n {\n','            if name != shard_mode || n != shard_n { n *= 2; continue; }\n')
    else:raise ValueError('unknown variant')
    reconstructed=text
    for item in reversed(insertions):
        if 'anchor'in item:reconstructed=reconstructed.replace(item['anchor']+item['inserted'],item['anchor'],1)
        else:reconstructed=reconstructed.replace(item['inserted']+item['before'],item['before'],1)
    if reconstructed.encode()!=raw:raise ValueError('NONSELECTOR_EDIT_DETECTED')
    if destination.exists()and destination.read_text()!=text:raise FileExistsError('different derived example exists')
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(text)
    result={'variant':variant,'original':str(source),'original_sha256':expected,'derived':str(destination),'derived_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'only_edits':'mandatory selector declarations/validation before CSV creation and loop skip guards','original_bytes_reconstructed_exactly':True,'insertions':insertions}
    destination.with_suffix('.selector.json').write_text(json.dumps(result,indent=2)+'\n')
    destination.with_suffix('.selector.diff').write_text(''.join(difflib.unified_diff(raw.decode().splitlines(keepends=True),text.splitlines(keepends=True),fromfile=source.name,tofile=destination.name)))
    return result
