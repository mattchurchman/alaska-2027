import json, math
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union
LON0,LON1,LAT0,LAT1=-140.6,-121.9,47.0,60.7
BL0,BL1,BA0,BA1=-148.0,-114.0,44.0,64.0
K=math.cos(math.radians(54.0)); S=100.0
def P(lon,lat): return ((lon-LON0)*K*S, (LAT1-lat)*S)
bb=box(BL0,BA0,BL1,BA1)
geoms=[]
for f in ('geo/land10.geojson','geo/minor.geojson'):
    for ft in json.load(open(f))['features']:
        g=shape(ft['geometry'])
        if g.intersects(bb): geoms.append(g.intersection(bb))
land=unary_union(geoms)
def ring(coords):
    pts=[P(x,y) for x,y in coords]
    out=[]; last=None
    for x,y in pts:
        t=(round(x,1),round(y,1))
        if t!=last: out.append(t); last=t
    if len(out)<4: return ''
    s='M'+' '.join(f'{x:g},{y:g}' for x,y in out[:1])
    s+='L'+' '.join(f'{x:g},{y:g}' for x,y in out[1:])+'Z'
    return s
def polys(g):
    return [g] if g.geom_type=='Polygon' else list(g.geoms) if hasattr(g,'geoms') else []
for tol,name in ((0.004,'hi'),):
    simp=land.simplify(tol,preserve_topology=True)
    d=''
    for p in polys(simp):
        if p.area<0.0004: continue
        d+=ring(p.exterior.coords)
        for i in p.interiors: d+=ring(i.coords)
    print(name,len(d))
    open(f'geo/land_{name}.txt','w').write(d)
# border
b=[]
for ft in json.load(open('geo/border.geojson'))['features']:
    g=shape(ft['geometry'])
    if g.intersects(bb):
        gi=g.intersection(bb)
        for ln in ([gi] if gi.geom_type=='LineString' else list(gi.geoms)):
            pts=[P(x,y) for x,y in ln.simplify(0.01).coords]
            b.append('M'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts))
open('geo/border.txt','w').write(''.join(b)); print('border',len(''.join(b)))
W,H=P(LON1,LAT0); print('W,H',W,H)
