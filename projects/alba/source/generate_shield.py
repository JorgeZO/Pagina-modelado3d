#!/usr/bin/env python3
"""Original procedural medieval shield. Python 3 + NumPy + Pillow.
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
N=512; rng=np.random.default_rng(71026)
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

# Grain follows the long axis; the same UVs continue across the curved face.
grain=np.sin(u*950+noise(6,10,5)+np.sin(v*16+u*21)*2)
fine=np.sin(u*1250+noise(32,18,6)); broad=noise(10,20,1)
planks=np.floor(u*7); seams=np.exp(-(np.sin(u*7*np.pi)/.045)**2)
# Irregular hand-carved growth lines and several small knots.
knots=np.zeros_like(u)
for cx,cy in [(.22,.31),(.67,.73),(.80,.18)]:
    rad=np.sqrt(((u-cx)*4)**2+((v-cy)*1.4)**2)
    knots+=np.exp(-rad*12)*(np.sin(rad*120)*.5-.6)
wh=np.clip(.52+grain*.045+fine*.016+broad*.07-seams*.20+knots*.10,0,1)
tone=grain*.09+fine*.025+broad*.27-seams*.36+knots*.20+(np.sin(planks*5)*.035)
wood=np.dstack([138+tone*150,82+tone*108,40+tone*65])
make_maps('Madera',wood,wh,np.clip(.72+broad*.12+seams*.10,.42,.92),0,6)
dark=wood*np.array([.53,.54,.60])+np.array([8,4,3]); save(dark,ASSETS/'madera-nogal.jpg')
# Forged steel: restrained hammer marks, directional hairline scratches.
hammer=noise(32,32,1); micro=noise(230,100,1); streak=noise(500,9,1)
sh=.5+hammer*.016+micro*.004+streak*.003
steel=np.dstack([162+hammer*14+streak*13,169+hammer*14+streak*13,173+hammer*14+streak*13])
make_maps('Acero',steel,sh,np.clip(.47+hammer*.08+streak*.06,.3,.64),1,3)
# Bronze engraving is entirely a height/normal texture, including fine concentric
# cuts and ray decorations; turning this map off has a clearly visible effect.
a=np.arctan2(.5-v,u-.5); r=np.hypot(u-.5,v-.5)
engrave=np.zeros_like(r)
for radius in [.245,.268,.322,.34,.415,.438]:
    engrave+=np.exp(-((r-radius)/.0028)**2)
rays=np.exp(-(np.sin(a*24)/.12)**2)*((r>.345)&(r<.41))
petal=np.exp(-((r-(.293+.013*np.cos(a*16)))/.0028)**2)
patina=noise(22,22,1); bronzeheight=.55-.17*np.clip(engrave+petal+rays,0,1)+noise(160,160,.012)
bronze=np.dstack([171+patina*33,119+patina*27,53+patina*20])-np.clip(engrave+petal+rays,0,1)[...,None]*14
make_maps('Bronce',bronze,bronzeheight,np.clip(.37+patina*.12,.22,.60),1,4)
leathergrain=noise(140,140,1)+noise(30,30,.3)
leather=np.dstack([55+leathergrain*20,30+leathergrain*14,19+leathergrain*10])
make_maps('Cuero',leather,.5+leathergrain*.10,np.clip(.83+leathergrain*.12,.6,.97),0,3)

# Geometry: triangles are merged into one mesh primitive per material (4 draw calls).
MATS=['Madera','Acero','Bronce','Cuero']; pieces={n:[] for n in MATS}
part_counts={}
def unit(a):
    a=np.array(a,float); return a/max(np.linalg.norm(a),1e-12)
def tri(mat,pts,uvs=None,norms=None):
    p=np.array(pts,float)
    if np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))<1e-10:return
    if uvs is None:uvs=[((q[0]+.43)/.86,(.56-q[1])/1.16) for q in p]
    if norms is None:norms=[unit(np.cross(p[1]-p[0],p[2]-p[0]))]*3
    pieces[mat].append((p,np.array(uvs,float),np.array(norms,float)))
def quad(mat,p,uv=None,n=None):
    p=np.asarray(p,dtype=float)
    uv=np.asarray([((q[0]+.43)/.86,(.56-q[1])/1.16) for q in p] if uv is None else uv,dtype=float)
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

def bez(p0,p1,p2,p3,t):return (1-t)**3*np.array(p0)+3*(1-t)**2*t*np.array(p1)+3*(1-t)*t*t*np.array(p2)+t**3*np.array(p3)
# Outline sampled clockwise, then reversed to produce a counterclockwise front.
outline=[]
for t in np.linspace(0,1,9,endpoint=False):outline.append([-.365+.73*t,.50+.012*np.sin(np.pi*t)])
for t in np.linspace(0,1,17,endpoint=False):outline.append(bez((.365,.50),(.40,.03),(.26,-.35),(0,-.58),t))
for t in np.linspace(0,1,17,endpoint=False):outline.append(bez((0,-.58),(-.26,-.35),(-.40,.03),(-.365,.50),t))
outline=np.array(outline[::-1]); L=len(outline)
def front(x,y):return .097-.30*x*x-.025*y*y
def fn(x,y):return unit([.60*x,.05*y,1])
# Radial front topology follows curvature without high tessellation.
for j in range(6):
    s0=j/6*.925;s1=(j+1)/6*.925
    for i in range(L):
        k=(i+1)%L
        pts=[]
        for s,ind in [(s0,i),(s1,i),(s1,k),(s0,k)]:
            xx,yy=outline[ind]*s;pts.append([xx,yy,front(xx,yy)])
        quad('Madera',pts,n=[fn(*p[:2]) for p in pts])
# Rear wood panel and endgrain thickness.
for i in range(L):
    k=(i+1)%L;a=outline[i]*.925;b=outline[k]*.925
    pa=[*a,front(*a)-.047];pb=[*b,front(*b)-.047]
    tri('Madera',[[0,0,front(0,0)-.047],pb,pa],norms=[[0,0,-1]]*3)
    quad('Madera',[[*a,front(*a)],[*a,front(*a)-.047],[*b,front(*b)-.047],[*b,front(*b)]])
# Beveled steel rim, closed through the back. Several profile loops form the bevel.
def band(mat,profile):
    rings=[]
    for s,zoff in profile:
        rings.append(np.array([[p[0]*s,p[1]*s,front(*(p*s))+zoff] for p in outline]))
    for j in range(len(rings)-1):
        for i in range(L):
            k=(i+1)%L
            # Calculate normals using the profile and outline tangents.
            ns=[]
            for jj,ii in [(j,i),(j+1,i),(j+1,k),(j,k)]:
                tangent=rings[jj][(ii+1)%L]-rings[jj][(ii-1)%L]
                radial=rings[min(jj+1,len(rings)-1)][ii]-rings[max(jj-1,0)][ii]
                ns.append(unit(np.cross(radial,tangent)))
            quad(mat,[rings[j][i],rings[j+1][i],rings[j+1][k],rings[j][k]],n=ns)
band('Acero',[(.905,-.045),(.905,.006),(.923,.021),(1.005,.021),(1.026,.001),(1.026,-.05),(.995,-.06),(.905,-.045)])
band('Bronce',[(.879,.003),(.888,.016),(.902,.016),(.911,.006)])
# Shallow rotational profiles. UVs on front use planar mapping for radial engraving.
def lathe(mat,cx,cy,z,profile,seg=48,radiusUV=None):
    rings=[]; normals=[]
    for j,(rr,zz) in enumerate(profile):
        rp,zp=profile[max(j-1,0)];rn,zn=profile[min(j+1,len(profile)-1)]
        dr,dz=rn-rp,zn-zp
        rings.append([[cx+rr*np.cos(a),cy+rr*np.sin(a),z+zz] for a in np.arange(seg)*2*np.pi/seg])
        normals.append([unit([-dz*np.cos(a),-dz*np.sin(a),dr]) for a in np.arange(seg)*2*np.pi/seg])
    for j in range(len(profile)-1):
        for i in range(seg):
            k=(i+1)%seg
            p=[rings[j][i],rings[j+1][i],rings[j+1][k],rings[j][k]]
            uv=[(.5+(q[0]-cx)/(radiusUV or .34),.5-(q[1]-cy)/(radiusUV or .34)) for q in p]
            ns=[normals[j][i],normals[j+1][i],normals[j+1][k],normals[j][k]]
            quad(mat,p,uv,ns)
# Raised central bronze disk and boss.
cy=.025; zz=front(0,cy)+.007
lathe('Bronce',0,cy,zz,[(.082,.026),(.088,.033),(.096,.034),(.104,.027),(.139,.027),(.147,.019),(.149,.012),(.149,.004)],64,.32)
lathe('Acero',0,cy,zz,[(0,.083),(.028,.080),(.052,.066),(.073,.048),(.081,.033),(.082,.026)],48,.17)
# Eight bronze sun rays, convex low-poly forms terminating in fine points.
for i in range(8):
    ang=2*np.pi*i/8+np.pi/2
    d=np.array([np.cos(ang),np.sin(ang)]);perp=np.array([-d[1],d[0]])
    tip=.29 if i%2==0 else .23
    p2=[d*.13-perp*.026,d*tip,d*.13+perp*.026,d*.112]
    pts=[[p[0],p[1]+cy,front(p[0],p[1]+cy)+.012] for p in p2]
    ridge=[*(d*(.17 if i%2==0 else .16)+[0,cy]),front(*(d*.16+[0,cy]))+.029]
    for k in range(4):tri('Bronce',[pts[k],pts[(k+1)%4],ridge])
# Copper-colored studs on border, and fine studs around medallion.
for i in range(0,L,2):
    xx,yy=outline[i]*.962
    lathe('Bronce',xx,yy,front(xx,yy)+.024,[(0,.008),(.005,.007),(.0075,.002),(.0075,0)],10,.025)
for a in np.arange(12)*2*np.pi/12:
    xx=.122*np.cos(a);yy=cy+.122*np.sin(a)
    lathe('Acero',xx,yy,zz+.028,[(0,.004),(.0028,.003),(.004,0)],8,.018)
# Back: two leather loops bow away from the board, with a flat steel mounting strip.
for ycenter in [-.17,.20]:
    for j in range(16):
        t0=j/16;t1=(j+1)/16
        def pp(t,side):
            xx=-.19+.38*t; yy=ycenter+side*.027
            return [xx,yy,front(xx,yy)-.055-.13*np.sin(np.pi*t)]
        quad('Cuero',[pp(t0,-1),pp(t1,-1),pp(t1,1),pp(t0,1)])
        quad('Cuero',[np.array(pp(t0,1))+[0,0,-.006],np.array(pp(t1,1))+[0,0,-.006],np.array(pp(t1,-1))+[0,0,-.006],np.array(pp(t0,-1))+[0,0,-.006]])
        for side in [-1,1]:
            p0=pp(t0,side);p1=pp(t1,side)
            quad('Cuero',[p0,p1,np.array(p1)+[0,0,-.006],np.array(p0)+[0,0,-.006]])
    for xx in [-.19,.19]:
        zzr=front(xx,ycenter)-.057
        # Rivets facing backwards, rotate coordinates of front-facing lathe manually.
        before=len(pieces['Bronce']);lathe('Bronce',xx,ycenter,-zzr,[(0,.006),(.006,.004),(.008,0)],10,.025)
        for q in range(before,len(pieces['Bronce'])):
            p,uv,n=pieces['Bronce'][q];p[:,2]*=-1;n[:,2]*=-1
            pieces['Bronce'][q]=(p[[0,2,1]],uv[[0,2,1]],n[[0,2,1]])

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
gltf={'asset':{'version':'2.0','generator':'Escudo del Alba — original procedural model','copyright':'CC0 1.0 — original geometry and procedural textures'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'Escudo del Alba','mesh':0}],'meshes':[{'name':'Escudo optimizado — 4 lotes por material','primitives':prims}],'materials':materials,'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],'textures':textures,'images':images,'bufferViews':views,'accessors':access,'buffers':[{'byteLength':len(binary)}]}
j=json.dumps(gltf,separators=(',',':'),ensure_ascii=False).encode();j+=b' '*((-len(j))%4);binary+=b'\0'*((-len(binary))%4)
glb=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary
(ASSETS/'escudo-del-alba.glb').write_bytes(glb)
stats={'name':'Escudo del Alba','triangles':total,'vertices':sum(s['vertices'] for s in vcounts.values()),'materials':len(MATS),'drawCalls':4,'textureResolution':512,'textureCount':12,'bytes':len(glb),'dimensionsMeters':{'width':round(float(np.ptp(outline[:,0])*1.026),3),'height':round(float(np.ptp(outline[:,1])*1.026),3)},'parts':vcounts,'sha256':hashlib.sha256(glb).hexdigest()}
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
