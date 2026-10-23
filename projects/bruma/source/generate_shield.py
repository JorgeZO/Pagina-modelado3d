#!/usr/bin/env python3
"""Original procedural round medieval shield. Python 3 + NumPy + Pillow.
Writes a self-contained GLB with UVs, tangents, four PBR materials and 512px maps.
Coordinates: metres, Y up, front +Z. No external model or texture assets.
"""
from pathlib import Path
import json, struct, math, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'dist/assets'; TEX=ROOT/'source/textures'
ASSETS.mkdir(parents=True,exist_ok=True); TEX.mkdir(parents=True,exist_ok=True)
N=512; rng=np.random.default_rng(211026)
y,x=np.mgrid[0:N,0:N].astype(float); u=x/N; v=y/N

def noise(sx,sy,amp=1):
    a=rng.integers(0,256,(sy,sx),dtype=np.uint8)
    return (np.array(Image.fromarray(a).resize((N,N),Image.Resampling.BICUBIC)).astype(float)/255-.5)*amp

def save(a,path,quality=88):
    im=Image.fromarray(np.uint8(np.clip(a,0,255)))
    if path.suffix=='.jpg': im.save(path,quality=quality,optimize=True)
    else: im.save(path,optimize=True)

def make_maps(name,base,height,rough,metal,strength):
    d=TEX/name; d.mkdir(exist_ok=True)
    save(base,d/'basecolor.jpg')
    rough=np.broadcast_to(rough,(N,N)); metal=np.broadcast_to(metal,(N,N))
    save(rough*255,d/'roughness.png'); save(metal*255,d/'metallic.png')
    save(np.dstack([np.ones((N,N))*255,rough*255,metal*255]),d/'metallic-roughness.png')
    dy,dx=np.gradient(height); normals=np.dstack([-dx*strength,dy*strength,np.ones((N,N))])
    normals/=np.linalg.norm(normals,axis=2,keepdims=True)
    save(np.round((normals*.5+.5)*255),d/'normal.png')
    save(height*255,d/'height.png')
    return d

# Ash planks, with two diagonally opposed painted quarters. All 512 px.
grain=noise(450,9,1)+noise(210,18,.4)
growth=np.sin(u*570+noise(8,14,6)+np.sin(v*14+u*9)*1.5)
broad=noise(9,17,1); planks=np.floor(u*8)
seams=np.exp(-(np.sin(u*8*np.pi)/.025)**2)
knots=np.zeros_like(u)
for cx,cy in [(.29,.27),(.71,.65),(.58,.12)]:
    rad=np.sqrt(((u-cx)*4)**2+((v-cy)*1.35)**2)
    knots+=np.exp(-rad*15)*(np.sin(rad*150)*.4-.4)
tone=grain*.10+growth*.025+broad*.20-seams*.32+knots*.19+np.sin(planks*3.2)*.025
wood=np.dstack([163+tone*150,130+tone*122,87+tone*85])
wh=np.clip(.51+grain*.032+growth*.008+broad*.014-seams*.16+knots*.03,0,1)
rr=np.hypot(u-.5,v-.5)
# Paint wears at plank edges and in occasional narrow chips, revealing real wood.
quarters=((u<.5) != (v<.5)).astype(float)
chips=np.clip((noise(280,32,1)-.30)*5,0,1)
edgewear=np.clip((rr-.44)*12,0,.30)
paint=quarters*(1-np.clip(chips+edgewear+seams*.16,0,.75))
blue=np.dstack([35+grain*12+broad*11,66+grain*18+broad*14,78+grain*20+broad*15])
painted=wood*(1-paint[...,None])+blue*paint[...,None]
woodrough=np.clip(.75+broad*.1+grain*.06,.55,.90)
make_maps('Madera',painted,wh*(1-paint*.16)+paint*.08,woodrough*(1-paint)+paint*.61,0,5)
# Alternative PBR set: color, packed metallic/roughness and normal, loaded on demand.
natural_dir=make_maps('Fresno',wood,wh,woodrough,0,5)
for src,dest in [('basecolor.jpg','fresno-basecolor.jpg'),('metallic-roughness.png','fresno-mr.png'),('normal.png','fresno-normal.png')]:
    (ASSETS/dest).write_bytes((natural_dir/src).read_bytes())
# Satin steel: subtle hammer texture with fine scratches; avoid excessive chrome.
hammer=noise(42,42,1); micro=noise(220,180,1); streak=noise(480,20,1)
steelheight=.50+hammer*.018+micro*.004+streak*.003
steel=np.dstack([150+hammer*13+streak*7,160+hammer*13+streak*7,166+hammer*13+streak*7])
make_maps('Acero',steel,steelheight,np.clip(.45+hammer*.09+streak*.05,.31,.60),1,3)
# Interlaced wave engraving for the outer annulus; linework lives in the normal map.
a=np.arctan2(.5-v,u-.5); r=np.hypot(u-.5,v-.5)
line1=np.exp(-((r-(.427+.010*np.sin(a*24)))/.0022)**2)
line2=np.exp(-((r-(.427-.010*np.sin(a*24)))/.0022)**2)
edge=np.exp(-((r-.406)/.0020)**2)+np.exp(-((r-.448)/.0020)**2)
# Concentric tooling on the central bronze collar.
inner=np.exp(-((r-.33)/.0025)**2)+np.exp(-((r-.40)/.0025)**2)
ticks=np.exp(-(np.sin(a*32)/.13)**2)*((r>.345)&(r<.385))
engrave=np.clip(line1+line2+edge+inner+ticks,0,1)
patina=noise(25,25,1)
bronze=np.dstack([169+patina*26,123+patina*24,59+patina*17])-engrave[...,None]*9
make_maps('Bronce',bronze,.55-engrave*.15+noise(130,130,.007),np.clip(.41+patina*.12,.29,.60),1,4)
leathergrain=noise(145,145,1)+noise(30,30,.35)
leather=np.dstack([57+leathergrain*19,34+leathergrain*14,23+leathergrain*10])
make_maps('Cuero',leather,.5+leathergrain*.08,np.clip(.83+leathergrain*.12,.65,.96),0,3)
# Geometry: triangles are merged into one mesh primitive per material (4 draw calls).
MATS=['Madera','Acero','Bronce','Cuero']; pieces={n:[] for n in MATS}
part_counts={}
def unit(a):
    a=np.array(a,float); return a/max(np.linalg.norm(a),1e-12)
def tri(mat,pts,uvs=None,norms=None):
    p=np.array(pts,float)
    if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))<1e-10:return
    if uvs is None:uvs=[(.5+q[0]/.96,.5-q[1]/.96) for q in p]
    if norms is None:norms=[unit(np.cross(p[1]-p[0],p[2]-p[0]))]*3
    pieces[mat].append((p,np.array(uvs,float),np.array(norms,float)))
def quad(mat,p,uv=None,n=None):
    p=np.asarray(p,dtype=float)
    uv=np.asarray([(.5+q[0]/.96,.5-q[1]/.96) for q in p] if uv is None else uv,dtype=float)
    def uv_area(ix):
        a,b=uv[ix[1]]-uv[ix[0]],uv[ix[2]]-uv[ix[0]]
        return abs(a[0]*b[1]-a[1]*b[0])
    if uv_area((0,1,2))+uv_area((0,2,3))<1e-12:
        # Automatic planar island in the actual face plane for vertical walls.
        # Use all four corners so the diagonal shares continuous UVs; these
        # small repeated parts intentionally reuse the full material texture.
        edges=p[1:]-p[0]
        axis_u=unit(edges[np.argmax(np.linalg.norm(edges,axis=1))])
        perpendicular=edges-np.outer(edges@axis_u,axis_u)
        axis_v=unit(perpendicular[np.argmax(np.linalg.norm(perpendicular,axis=1))])
        projected=np.column_stack([(p-p[0])@axis_u,(p-p[0])@axis_v])
        span=np.ptp(projected,axis=0)
        if np.all(span>1e-12):uv=(projected-projected.min(axis=0))/span
    for ix in [(0,1,2),(0,2,3)]:
        tri(mat,[p[i] for i in ix],[uv[i] for i in ix],None if n is None else [n[i] for i in ix])

# Circular shield, 64 outline segments, in metres. Front points toward +Z.
SEG=64; R=.47; angles=np.arange(SEG)*2*np.pi/SEG
outline=np.array([[R*np.cos(a),R*np.sin(a)] for a in angles]); L=SEG
def front(x,y):return .078-.15*(x*x+y*y)
def fn(x,y):return unit([.30*x,.30*y,1])
# Gently convex wooden body. Its small radial grid preserves curvature.
for j in range(6):
    for i in range(SEG):
        k=(i+1)%SEG;pts=[]
        for scale,ind in [(j/6,i),((j+1)/6,i),((j+1)/6,k),(j/6,k)]:
            xx,yy=outline[ind]*scale*.967;pts.append([xx,yy,front(xx,yy)])
        quad('Madera',pts,n=[fn(*p[:2]) for p in pts])
# Rear follows the same curvature; the side uses a strip UV so it is not collapsed.
for j in range(3):
    for i in range(SEG):
        k=(i+1)%SEG;pts=[]
        for scale,ind in [(j/3,k),((j+1)/3,k),((j+1)/3,i),(j/3,i)]:
            xx,yy=outline[ind]*scale*.967;pts.append([xx,yy,front(xx,yy)-.036])
        quad('Madera',pts,[(.25+p[0]/.96*.48,.25-p[1]/.96*.48) for p in pts],n=[-fn(*p[:2]) for p in pts])
for i in range(SEG):
    k=(i+1)%SEG; a=outline[i]*.967;b=outline[k]*.967
    quad('Madera',[[*a,front(*a)],[*a,front(*a)-.036],[*b,front(*b)-.036],[*b,front(*b)]],[(i/SEG,0),(i/SEG,1),((i+1)/SEG,1),((i+1)/SEG,0)])
# Rotational profiles with continuous normals. Planar UVs align ring engravings.
def lathe(mat,cx,cy,z,profile,seg=64,uvdiam=.96,curve=False,back=False):
    rings=[];normals=[]
    for j,(rr,zz) in enumerate(profile):
        rp,zp=profile[max(j-1,0)];rn,zn=profile[min(j+1,len(profile)-1)]
        if curve:zp+=front(rp,0);zn+=front(rn,0)
        dr,dz=rn-rp,zn-zp
        ring=[];ns=[]
        for ang in np.arange(seg)*2*np.pi/seg:
            zz2=z+zz+(front(rr,0) if curve else 0)
            ring.append([cx+rr*np.cos(ang),cy+rr*np.sin(ang),-zz2 if back else zz2])
            nn=unit([-dz*np.cos(ang),-dz*np.sin(ang),dr]);nn[2]*=-1 if back else 1;ns.append(nn)
        rings.append(ring);normals.append(ns)
    for j in range(len(profile)-1):
        for i in range(seg):
            k=(i+1)%seg
            order=[(j,i),(j+1,i),(j+1,k),(j,k)]
            if back:order=order[::-1]
            pts=[rings[jj][ii] for jj,ii in order]
            uv=[(.5+(p[0]-cx)/uvdiam,.5-(p[1]-cy)/uvdiam) for p in pts]
            quad(mat,pts,uv,[normals[jj][ii] for jj,ii in order])
# Steel rolled rim, bevels and rear return. Bronze inner fillet and decorated band.
lathe('Acero',0,0,0,[(.450,-.038),(.450,.004),(.458,.015),(.475,.015),(.483,.004),(.483,-.039),(.474,-.045),(.450,-.038)],64,curve=True)
lathe('Bronce',0,0,0,[(.438,.002),(.442,.012),(.449,.012),(.453,.004)],64,curve=True)
lathe('Bronce',0,0,0,[(.386,.003),(.390,.012),(.425,.012),(.429,.003)],96,curve=True)
# Central boss is a low-resolution dome. Bronze ring surrounds it, with fine tooling.
cz=front(0,0)+.003
lathe('Bronce',0,0,cz,[(.118,.016),(.124,.029),(.141,.029),(.151,.018),(.151,.008)],64,.34)
lathe('Acero',0,0,cz,[(0,.133),(.028,.129),(.061,.113),(.090,.086),(.111,.052),(.120,.024),(.126,.018)],64,.26)
# Rivet heads along the perimeter and collar; no spherical high-poly objects.
for ang in np.arange(24)*2*np.pi/24:
    xx=.465*np.cos(ang);yy=.465*np.sin(ang)
    lathe('Bronce',xx,yy,front(xx,yy)+.017,[(0,.006),(.0045,.005),(.0065,.001),(.0065,0)],8,.022)
for ang in np.arange(8)*2*np.pi/8:
    xx=.137*np.cos(ang);yy=.137*np.sin(ang)
    lathe('Acero',xx,yy,cz+.031,[(0,.004),(.003,.003),(.0045,0)],8,.018)
# Four narrow wrought steel radial bands, lying flush beneath the bronze rings.
# Their long UV axis preserves scratch direction, while the boss hides the inner joins.
for ang in np.arange(4)*np.pi/2:
    d=np.array([np.cos(ang),np.sin(ang)]);s=np.array([-d[1],d[0]])
    for j in range(5):
        r0=.149+j*.046;r1=r0+.046
        pp=[]
        for rr,side in [(r0,-1),(r1,-1),(r1,1),(r0,1)]:
            xy=d*rr+s*side*.005
            pp.append([*xy,front(*xy)+.005])
        quad('Acero',pp,[(j/5,0),((j+1)/5,0),((j+1)/5,1),(j/5,1)],n=[fn(*p[:2]) for p in pp])
# Back: two leather arm loops; surface, reverse and edges all have UV area.
for yc in [-.145,.145]:
    for j in range(14):
        t0=j/14;t1=(j+1)/14
        def pp(t,side):
            xx=-.18+.36*t;yy=yc+side*.026
            return [xx,yy,front(xx,yy)-.043-.12*np.sin(np.pi*t)]
        quad('Cuero',[pp(t0,-1),pp(t1,-1),pp(t1,1),pp(t0,1)],[(t0,0),(t1,0),(t1,1),(t0,1)])
        quad('Cuero',[np.array(pp(t0,1))+[0,0,-.006],np.array(pp(t1,1))+[0,0,-.006],np.array(pp(t1,-1))+[0,0,-.006],np.array(pp(t0,-1))+[0,0,-.006]],[(t0,0),(t1,0),(t1,1),(t0,1)])
        for side in [-1,1]:
            p0=pp(t0,side);p1=pp(t1,side)
            quad('Cuero',[p0,p1,np.array(p1)+[0,0,-.006],np.array(p0)+[0,0,-.006]],[(t0,0),(t1,0),(t1,1),(t0,1)])
    for xx in [-.18,.18]:
        lathe('Bronce',xx,yc,-front(xx,yc)+.044,[(0,.005),(.006,.004),(.008,0)],10,.024,back=True)

# Assemble compact glTF 2.0 binary; shared material batches preserve 4 draw calls.
binary=bytearray(); views=[]; access=[]; images=[]; textures=[]
def blob(data,target=None):
    while len(binary)%4:binary.append(0)
    off=len(binary);binary.extend(data);view={'buffer':0,'byteOffset':off,'byteLength':len(data)}
    if target:view['target']=target
    views.append(view);return len(views)-1
def accessor(a,typ,component=5126,target=34962):
    a=np.asarray(a,dtype='<f4' if component==5126 else '<u2')
    item={'bufferView':blob(a.tobytes(),target),'componentType':component,'count':len(a),'type':typ}
    if typ=='VEC3':item.update(min=a.min(axis=0).tolist(),max=a.max(axis=0).tolist())
    access.append(item);return len(access)-1
def texture(path):
    images.append({'name':path.parent.name+'_'+path.stem,'bufferView':blob(path.read_bytes()),'mimeType':'image/jpeg' if path.suffix=='.jpg' else 'image/png'})
    textures.append({'source':len(images)-1,'sampler':0});return len(textures)-1
materials=[]
for name in MATS:
    d=TEX/name
    materials.append({'name':name,'pbrMetallicRoughness':{'baseColorTexture':{'index':texture(d/'basecolor.jpg')},'metallicRoughnessTexture':{'index':texture(d/'metallic-roughness.png')},'metallicFactor':1,'roughnessFactor':1},'normalTexture':{'index':texture(d/'normal.png'),'scale':1},'doubleSided':False})
prims=[];total=0;vcounts={}
for mat,faces in pieces.items():
    pos=[];uv=[];norm=[];tans=[]
    for p,t,n in faces:
        e1=p[1]-p[0];e2=p[2]-p[0];d1=t[1]-t[0];d2=t[2]-t[0];det=d1[0]*d2[1]-d1[1]*d2[0]
        if abs(det)>1e-10:
            tt=(e1*d2[1]-e2*d1[1])/det;bb=(e2*d1[0]-e1*d2[0])/det
        else:tt=np.array([1,0,0.]);bb=np.array([0,-1,0.])
        for k in range(3):
            nn=unit(n[k]);tanraw=tt-nn*np.dot(nn,tt)
            if np.linalg.norm(tanraw)<1e-8:tanraw=np.cross([0,1,0] if abs(nn[1])<.9 else [1,0,0],nn)
            tan=unit(tanraw);sign=-1 if np.dot(np.cross(nn,tan),bb)<0 else 1
            pos.append(p[k]);uv.append(t[k]);norm.append(nn);tans.append([*tan,sign])
    # Deduplicate full corner attributes, preserving seams and hard edges.
    packed=np.round(np.column_stack([pos,norm,uv,tans]),6).astype('<f4')
    unique,indices=np.unique(packed,axis=0,return_inverse=True)
    attrs={'POSITION':accessor(unique[:,:3],'VEC3'),'NORMAL':accessor(unique[:,3:6],'VEC3'),'TEXCOORD_0':accessor(unique[:,6:8],'VEC2'),'TANGENT':accessor(unique[:,8:12],'VEC4')}
    prims.append({'attributes':attrs,'indices':accessor(indices,'SCALAR',5123,34963),'material':MATS.index(mat)})
    total+=len(faces);vcounts[mat]={'triangles':len(faces),'vertices':len(unique)}
gltf={'asset':{'version':'2.0','generator':'Escudo de la Bruma — original procedural model','copyright':'CC0 1.0 — original geometry and procedural textures'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'Escudo de la Bruma','mesh':0}],'meshes':[{'name':'Escudo optimizado — 4 lotes por material','primitives':prims}],'materials':materials,'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],'textures':textures,'images':images,'bufferViews':views,'accessors':access,'buffers':[{'byteLength':len(binary)}]}
j=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4);binary+=b'\0'*((-len(binary))%4)
glb=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
(ASSETS/'escudo-de-la-bruma.glb').write_bytes(glb)
stats={'name':'Escudo de la Bruma','triangles':total,'vertices':sum(s['vertices'] for s in vcounts.values()),'materials':len(MATS),'drawCalls':4,'textureResolution':512,'textureCount':12,'bytes':len(glb),'dimensionsMeters':{'width':round(.483*2,3),'height':round(.483*2,3)},'parts':vcounts,'sha256':hashlib.sha256(glb).hexdigest()}
(ASSETS/'model-stats.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False))
# An honest UV preview, one panel per material. Tiling/reuse is intentional for studs.
uvim=Image.new('RGB',(1024,1024),'#161a1b');draw=ImageDraw.Draw(uvim)
for m,faces in pieces.items():
    mi=MATS.index(m);ox=(mi%2)*512;oy=(mi//2)*512
    for p,t,n in faces:
        points=[(ox+int(np.clip(q[0],0,1)*490)+10,oy+int(np.clip(q[1],0,1)*490)+10) for q in t]
        draw.line(points+[points[0]],fill=['#cb9854','#a4b9c8','#d2ac62','#a88773'][mi],width=1)
    draw.text((ox+18,oy+18),m,fill='white')
uvim.save(ROOT/'source/uv-layout.png')
print(json.dumps(stats,indent=2,ensure_ascii=False))
