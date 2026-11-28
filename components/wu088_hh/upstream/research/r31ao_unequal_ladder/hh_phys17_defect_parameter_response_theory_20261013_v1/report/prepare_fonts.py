#!/usr/bin/env python3
"""Subset full Noto Serif CJK fonts for this report's complete TeX text."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--font-source', type=Path, required=True)
args = parser.parse_args()
tex_files = sorted(HERE.glob('*.tex'))
text = ''.join(p.read_text(encoding='utf-8') for p in tex_files)
text += ''.join(chr(c) for c in range(32, 127)) + '–—−×·…•‘’“”§'
(HERE / 'fonts').mkdir(exist_ok=True)
records = []
for name in ['NotoSerifCJKkr-Regular.otf', 'NotoSerifCJKkr-Bold.otf']:
    source = args.font_source / name
    options = subset.Options()
    options.name_IDs = ['*']
    options.name_legacy = True
    options.name_languages = ['*']
    font = subset.load_font(str(source), options)
    original_cmap = set(font.getBestCmap())
    sub = subset.Subsetter(options=options)
    sub.populate(text=text)
    sub.subset(font)
    target = HERE / 'fonts' / name
    subset.save_font(font, str(target), options)
    final_cmap = set(TTFont(target).getBestCmap())
    requested = {ord(c) for c in text}
    dropped = sorted((requested & original_cmap) - final_cmap)
    if dropped:
        raise RuntimeError(f'Unexpected subset loss: {dropped}')
    records.append({
        'name': name,
        'full_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'subset_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'full_cmap_entries': len(original_cmap),
        'subset_cmap_entries': len(final_cmap),
        'subset_bytes': target.stat().st_size,
        'requested_source_supported_glyphs_lost': dropped,
    })
for source in args.font_source.iterdir():
    if source.suffix.lower() in ('.txt', '.md'):
        shutil.copy2(source, HERE / 'fonts' / source.name)
manifest = {
    'purpose': 'Fresh subset from full CJK fonts, including every current TeX file',
    'tex_files': [p.name for p in tex_files],
    'tex_source_sha256': {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in tex_files
    },
    'fonts': records,
}
(HERE / 'FONT_SUBSET_MANIFEST.json').write_text(
    json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
)
print(json.dumps(records, ensure_ascii=False, indent=2))
