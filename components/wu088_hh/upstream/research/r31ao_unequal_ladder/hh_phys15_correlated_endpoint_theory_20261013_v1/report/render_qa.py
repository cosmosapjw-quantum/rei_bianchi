#!/usr/bin/env python3
"""Render every PDF page with Poppler and make auditable contact sheets."""
from pathlib import Path
from PIL import Image, ImageDraw
import fitz
import hashlib
import json
import os
import subprocess
from io import BytesIO

HERE = Path(__file__).resolve().parent
PDF = HERE / 'WU088_HH_PHYS15_THEORY_20261013.pdf'
OUT = HERE / 'qa' / 'final_pages'
OUT.mkdir(parents=True, exist_ok=True)
subprocess.run(['pdftoppm', '-png', '-r', '115', str(PDF), str(OUT/'page')], check=True)
doc = fitz.open(PDF)
render_repairs = []
page_files = []
for i in range(len(doc)):
    path = OUT / f'page-{i+1:02d}.png'
    try:
        with Image.open(path) as im:
            im.load()
    except Exception as error:
        # Re-render only a concretely incomplete image produced by Poppler.
        render_repairs.append({'page': i+1, 'error': str(error)})
        subprocess.run(['pdftoppm', '-f', str(i+1), '-l', str(i+1),
                        '-singlefile', '-png', '-r', '115', str(PDF),
                        str(path.with_suffix(''))], check=True)
        with Image.open(path) as im:
            im.load()
    page_files.append(path)
contacts = []
for start in range(0, len(page_files), 4):
    batch = page_files[start:start+4]
    thumb_w, thumb_h = 780, 1104
    rows = 2 if len(batch) > 2 else 1
    canvas = Image.new('RGB', (2*thumb_w+60, rows*(thumb_h+34)+50), '#e9edf1')
    draw = ImageDraw.Draw(canvas)
    for k, path in enumerate(batch):
        im = Image.open(path).convert('RGB')
        im.thumbnail((thumb_w, thumb_h))
        x, y = 20+(k%2)*(thumb_w+20), 20+(k//2)*(thumb_h+34)
        draw.text((x, y), path.name, fill='black')
        canvas.paste(im, (x, y+24))
    path = HERE / 'qa' / f'final_contact_{start+1:02d}_{min(start+4,len(page_files)):02d}.jpg'
    canvas.save(path, quality=94)
    contacts.append(str(path.relative_to(HERE)))
records = []
for i, page in enumerate(doc):
    spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
             for line in b['lines'] for s in line['spans']]
    outside = [{'text': s['text'], 'bbox': s['bbox']} for s in spans
               if not page.rect.contains(fitz.Rect(s['bbox']))]
    body = [s for s in spans if 70 < s['bbox'][1] < 775]
    records.append({
        'page': i+1, 'spans': len(spans),
        'body_min_y': min(s['bbox'][1] for s in body) if body else None,
        'body_max_y': max(s['bbox'][3] for s in body) if body else None,
        'text_outside_page': outside,
        'replacement_char_count': page.get_text().count('\ufffd'),
        'render_png': str(page_files[i].relative_to(HERE)),
    })
report = {
    'pdf': PDF.name,
    'sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),
    'pages': len(doc),
    'render_dpi': 115,
    'contact_sheets': contacts,
    'render_repairs': render_repairs,
    'outside_page_total': sum(len(r['text_outside_page']) for r in records),
    'replacement_chars_total': sum(r['replacement_char_count'] for r in records),
    'page_records': records,
}
(HERE/'qa'/'PAGE_BOUNDS.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
subprocess.run(['pdftotext', '-layout', str(PDF), str(HERE/'qa'/'extracted_layout.txt')], check=True)
print(json.dumps({k:v for k,v in report.items() if k!='page_records'}, ensure_ascii=False, indent=2))

# Save independent, atomic JPEG derivatives as the final inspection surfaces.
# Some large Poppler PNG writes were observed to become truncated on this host.
stable = HERE/'qa'/'stable_pages'
stable.mkdir(exist_ok=True)
def atomic_bytes(target, data):
    temp = target.with_suffix('.tmp')
    with temp.open('wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    temp.replace(target)

stable_files = []
for i, page in enumerate(doc):
    data = page.get_pixmap(matrix=fitz.Matrix(115/72, 115/72), alpha=False).pil_tobytes(format='JPEG', quality=97)
    target = stable/f'page-{i+1:02d}.jpg'
    atomic_bytes(target, data)
    with Image.open(target) as im:
        im.load()
    stable_files.append(target)
stable_contacts = []
for start in range(0, len(stable_files), 4):
    batch = stable_files[start:start+4]
    width, height = 780, 1104
    rows = 2 if len(batch)>2 else 1
    canvas = Image.new('RGB', (2*width+60, rows*(height+34)+50), '#e9edf1')
    draw = ImageDraw.Draw(canvas)
    for k, target in enumerate(batch):
        im = Image.open(target).convert('RGB')
        im.thumbnail((width, height))
        x, y = 20+(k%2)*(width+20), 20+(k//2)*(height+34)
        draw.text((x,y), target.name, fill='black')
        canvas.paste(im,(x,y+24))
    target=HERE/'qa'/f'stable_contact_{start+1:02d}_{min(start+4,len(stable_files)):02d}.jpg'
    buffer=BytesIO()
    canvas.save(buffer, format='JPEG', quality=96)
    atomic_bytes(target, buffer.getvalue())
    stable_contacts.append(str(target.relative_to(HERE)))
stable_manifest = {
    'pdf_sha256': report['sha256'], 'page_count': len(doc),
    'format': 'JPEG', 'dpi': 115, 'renderer': 'PyMuPDF',
    'prior_poppler_full_render': True, 'atomic_write_fsync': True,
    'pages': [str(p.relative_to(HERE)) for p in stable_files],
    'contact_sheets': stable_contacts,
}
(HERE/'qa'/'STABLE_RENDER_MANIFEST.json').write_text(json.dumps(stable_manifest, indent=2)+'\n')
