#!/usr/bin/env python3
"""Exact saved-point SVG/PDF plots. Standard library only; no solver or resampling.

Coordinates are mapped once and shared by SVG and PDF. Every finite saved point
is retained. Log axes break at nonpositive samples; no replacement floor.
"""
import json, math, html
from pathlib import Path

COLORS = ['#111111','#0072B2','#D55E00','#009E73','#CC79A7','#E69F00','#56B4E9','#882255','#44AA99','#AA4499','#332288','#999933','#661100','#6699CC','#117733','#AA4466','#777777']
DASHES = [[],[5,2],[1.2,2],[7,2,1.2,2]]

def n(v): return ('%.4f'%v).rstrip('0').rstrip('.') or '0'
def rgb(c): return [int(c[i:i+2],16)/255 for i in (1,3,5)]
def pdfstr(s): return str(s).replace('\\','\\\\').replace('(','\\(').replace(')','\\)').encode('latin1','replace').decode('latin1')

class Canvas:
    def __init__(self,w,h):
        self.w,self.h=w,h
        self.svg=['<svg xmlns="http://www.w3.org/2000/svg" width="%spt" height="%spt" viewBox="0 0 %s %s">'%(w,h,w,h),'<rect width="100%" height="100%" fill="white"/>']
        self.pdf=[]
    def line(self,pts,color='#111111',width=.8,dash=None):
        if not pts:return
        if len(pts)==1:
            x,y=pts[0];r=.65
            self.svg.append('<rect x="%s" y="%s" width="1.3" height="1.3" fill="%s"/>'%(n(x-r),n(y-r),color))
            self.pdf.append('%s rg %s %s 1.3 1.3 re f'%(' '.join(map(n,rgb(color))),n(x-r),n(self.h-y-r)))
            return
        ds=dash or []
        self.svg.append('<polyline fill="none" stroke="%s" stroke-width="%s"%s points="%s"/>'%(color,n(width),(' stroke-dasharray="%s"'%' '.join(map(n,ds))) if ds else '', ' '.join(n(x)+','+n(y) for x,y in pts)))
        self.pdf.append('%s RG %s w [%s] 0 d %s m %s S'%(' '.join(map(n,rgb(color))),n(width),' '.join(map(n,ds)),n(pts[0][0])+' '+n(self.h-pts[0][1]),' '.join(n(x)+' '+n(self.h-y)+' l' for x,y in pts[1:])))
    def text(self,x,y,s,size=9,anchor='start',rotate=0,bold=False):
        s=str(s)
        self.svg.append('<text x="%s" y="%s" font-family="Helvetica,Arial,sans-serif" font-size="%s" text-anchor="%s"%s%s>%s</text>'%(n(x),n(y),n(size),anchor,' font-weight="bold"' if bold else '',(' transform="rotate(%s %s %s)"'%(n(rotate),n(x),n(y))) if rotate else '',html.escape(s)))
        # AFM-like width estimate is used only for text anchoring, not data.
        sw=sum(.278 if c in ' .,:;ilI1' else .75 if c in 'MW' else .556 for c in s)*size
        dx=0 if anchor=='start' else -sw/2 if anchor=='middle' else -sw
        a=math.radians(-rotate); co,si=math.cos(a),math.sin(a)
        self.pdf.append('0 g BT /%s %s Tf %s %s %s %s %s %s Tm (%s) Tj ET'%('F2' if bold else 'F1',n(size),n(co),n(si),n(-si),n(co),n(x+co*dx),n(self.h-y+si*dx),pdfstr(s)))
    def save(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        path.with_suffix('.svg').write_text('\n'.join(self.svg+['</svg>']))
        stream=('\n'.join(self.pdf)+'\n').encode('latin1')
        objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %s %s] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>'%(self.w,self.h)).encode(),b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'endstream']
        out=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
        for i,o in enumerate(objs,1):offsets.append(len(out));out.extend(str(i).encode()+b' 0 obj\n'+o+b'\nendobj\n')
        start=len(out);out.extend(('xref\n0 %d\n0000000000 65535 f \n'%(len(objs)+1)).encode())
        for v in offsets[1:]:out.extend(('%010d 00000 n \n'%v).encode())
        out.extend(('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'%(len(objs)+1,start)).encode());path.with_suffix('.pdf').write_bytes(out)

def save_bundle(canvases,path):
    """Multipage native vector PDF; reuse the identical authored page streams."""
    kids=' '.join('%d 0 R'%(5+2*i) for i in range(len(canvases)))
    objs=[b'<< /Type /Catalog /Pages 2 0 R >>',('<< /Type /Pages /Kids [%s] /Count %d >>'%(kids,len(canvases))).encode(),b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>']
    for i,c in enumerate(canvases):
        stream=('\n'.join(c.pdf)+'\n').encode('latin1')
        objs.extend([('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %s %s] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents %d 0 R >>'%(c.w,c.h,6+2*i)).encode(),b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'endstream'])
    out=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n');offsets=[0]
    for i,o in enumerate(objs,1):offsets.append(len(out));out.extend(str(i).encode()+b' 0 obj\n'+o+b'\nendobj\n')
    start=len(out);out.extend(('xref\n0 %d\n0000000000 65535 f \n'%(len(objs)+1)).encode())
    for v in offsets[1:]:out.extend(('%010d 00000 n \n'%v).encode())
    out.extend(('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'%(len(objs)+1,start)).encode());Path(path).write_bytes(out)

def ticks(lo,hi,log=False):
    if log:
        a,b=math.ceil(math.log10(lo)),math.floor(math.log10(hi));step=max(1,math.ceil((b-a+1)/6))
        return [(10.**k,'1e%d'%k) for k in range(a,b+1,step)]
    span=hi-lo
    if not span:return [(lo,n(lo))]
    raw=span/4;power=10**math.floor(math.log10(raw));v=raw/power;step=(1 if v<=1 else 2 if v<=2 else 5 if v<=5 else 10)*power
    return [(i*step,('%g'%(i*step))) for i in range(math.ceil(lo/step),math.floor(hi/step)+1)]

def panel(c,box,x,series,title,ylabel,yscale='linear',xscale='linear',ylim=None,zticks=None,xlim=None,legend=True,xlabel='Elapsed time, t (Myr)',toplabel='Mean redshift, z'):
    l,t,w,h=box;logx=xscale=='log';logy=yscale=='log'
    validx=[v for v in x if math.isfinite(v) and (v>0 or not logx)]
    xmin,xmax=xlim or (min(validx),max(validx))
    vals=[v for s in series for xx,v in zip(x,s['y']) if xmin<=xx<=xmax and math.isfinite(v) and (v>0 or not logy)]
    if ylim:ymin,ymax=ylim
    elif vals:
        ymin,ymax=min(vals),max(vals)
        if logy:ymin=10**math.floor(math.log10(ymin));ymax=10**math.ceil(math.log10(ymax))
        else:
            pad=(ymax-ymin)*.07 or max(abs(ymin)*.07,1e-16);ymin-=pad;ymax+=pad
    else:raise ValueError('No valid data '+title)
    if ymin==ymax:ymax=ymin*10 if logy else ymin+1
    fx=math.log10 if logx else float;fy=math.log10 if logy else float
    def X(v):return l+(fx(v)-fx(xmin))/(fx(xmax)-fx(xmin))*w
    def Y(v):return t+h-(fy(v)-fy(ymin))/(fy(ymax)-fy(ymin))*h
    if not logy and ymin<=0<=ymax:c.line([(l,Y(0)),(l+w,Y(0))],'#888888',.6)
    for v,label in ticks(ymin,ymax,logy):
        yy=Y(v);c.line([(l,yy),(l+w,yy)],'#dddddd',.35);c.line([(l-3,yy),(l,yy)],width=.65);c.text(l-5,yy+3,label,8,'end')
    for v,label in ticks(xmin,xmax,logx):
        xx=X(v);c.line([(xx,t+h),(xx,t+h+3)],width=.65);c.text(xx,t+h+14,label,8,'middle')
    for v,label in zticks or []:
        if xmin<=v<=xmax and (v>0 or not logx):
            xx=X(v);c.line([(xx,t-3),(xx,t)],width=.65);c.text(xx,t-7,label,8,'middle')
    if zticks or toplabel:c.text(l+w/2,t-22,toplabel,9,'middle')
    c.line([(l,t),(l+w,t),(l+w,t+h),(l,t+h),(l,t)],width=.65)
    for k,s in enumerate(series):
        color=s.get('color',COLORS[k%len(COLORS)]);dash=s.get('dash',DASHES[(k//7)%4]);seg=[]
        for xx,yy in zip(x,s['y']):
            good=math.isfinite(xx) and math.isfinite(yy) and xmin<=xx<=xmax and ymin<=yy<=ymax and (xx>0 or not logx) and (yy>0 or not logy)
            if good:seg.append((X(xx),Y(yy)))
            else:
                c.line(seg,color,.9,dash);seg=[]
        c.line(seg,color,.9,dash)
    c.text(l,t-40,title,11,bold=True);c.text(l+w/2,t+h+30,xlabel,9,'middle');c.text(l-51,t+h/2,ylabel,9,'middle',-90)
    if legend:
        cols=min(4,len(series));rowh=14;colw=w/cols
        for k,s in enumerate(series):
            xx=l+(k%cols)*colw;yy=t+h+49+(k//cols)*rowh
            c.line([(xx,yy-3),(xx+17,yy-3)],s.get('color',COLORS[k%len(COLORS)]),1.2,s.get('dash',DASHES[(k//7)%4]));c.text(xx+22,yy,s['label'],8)
    counts=[]
    for s in series:
        counts.append({'label':s['label'],'positive_below_y':sum(0<v<ymin for v in s['y']),'positive_above_y':sum(v>ymax for v in s['y']),'nonpositive_y':sum(v<=0 for v in s['y']),'outside_x':sum(not xmin<=v<=xmax for v in x)})
    return {'title':title,'xlim':[xmin,xmax],'ylim':[ymin,ymax],'series':len(series),'samples_per_series':len(x),'xscale':xscale,'yscale':yscale,'per_series_counts':counts}
