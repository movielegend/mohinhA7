"""B11 reconstruction from seven supplied renders; inferred millimetres, export metres."""
import ast,math,pickle
from pathlib import Path
import numpy as np
import trimesh,manifold3d as mf
from PIL import Image
ROOT=Path(__file__).parent;OUT=ROOT/'b11-model';OUT.mkdir(exist_ok=True)
from b11_geometry import rr, prism, disc, rounded_prism, lathe, dome
def mat(n,c,m=0,r=.4):return trimesh.visual.material.PBRMaterial(name=n,baseColorFactor=c,metallicFactor=m,roughnessFactor=r)
CREAM=mat('Warm ivory satin housing',[226,215,193,255],.025,.36)
FACE=mat('Ivory front ribs',[238,226,201,255],.02,.45)
GROOVE=mat('Recessed warm grooves',[179,159,125,255],.02,.6)
TRIM=mat('Champagne lens bezel',[185,164,128,255],.36,.28)
DARK=mat('Dark charcoal polymer',[41,43,42,255],.02,.56)
BLACK=mat('Unlit recess',[7,9,11,255],0,.88)
METAL=mat('Connector metal',[159,166,173,255],.85,.27)
GLASS=mat('Blue violet optical glass',[255,255,255,255],.35,.085)
scene=trimesh.Scene();items=[]
def add(name,obj,material,colors=None):
 if name in scene.geometry:name=name+' / '+str(len(items))
 if isinstance(obj,mf.Manifold):
  r=obj.to_mesh();m=trimesh.Trimesh(r.vert_properties[:,:3],r.tri_verts,process=True)
 else:m=obj.copy()
 assert len(m.faces),name
 m.fix_normals();m=trimesh.graph.smooth_shade(m,angle=np.deg2rad(38))
 if hasattr(obj,'visual') and getattr(obj.visual,'uv',None) is not None:
  m.visual=obj.visual;m.visual.material=material
 else:
  m.visual=trimesh.visual.TextureVisuals(material=material)
 if colors is not None:
  rgb=colors(m.vertices);m.visual=trimesh.visual.ColorVisuals(m,vertex_colors=np.c_[np.clip(rgb,0,255),np.full(len(rgb),255)].astype('uint8'));m.visual.material=material
 # Recess is modelled directly in geometry coordinates.
 m.vertices/=1000;scene.add_geometry(m,node_name=name,geom_name=name);items.append((name,m,np.eye(4)))
 return m

def ring(name,R,r,z,x=22,y=166,material=TRIM):
 return add(name,disc(R,1.0,(x,y,z),inner=r,segments=128),material)
print('B11: housing, true diagonal vents',flush=True)
body=rounded_prism(250,78,4.2,235,2.0).translate((0,166,0))-prism(247,75,3,246,pos=(0,166,0))
vents=[]
for side in [-1,1]:
 for iy in range(9):
  for iz in range(15):
   yy=146+iy*4.8;zz=20+iz*4.8+(iy%2)*2.4
   slot=prism(1.9,5.3,.92,12).rotate((0,0,43)).rotate((0,90,0)).translate((side*124,yy,zz))
   vents.append(slot)
body=body-mf.Manifold.compose(vents)
add('HOUSING / ivory shell with pierced diagonal vents',body,CREAM)
add('HOUSING / internal dark chamber',rounded_prism(244,71,3,224,1).translate((0,166,0)),BLACK)
# Thin lid seam on both sides.
for side in [-1,1]:
 add('LID / side assembly seam '+str(side),prism(230,.45,.2,.22,'x',(side*125.05,200.5,0)),GROOVE)
add('LID / flat top plate',rounded_prism(249,233,3.4,1.7,.65).rotate((-90,0,0)).translate((0,204.55,0)),CREAM)
# Front surround and inset face with fine real diagonal ribbing.
front=rounded_prism(250,78,4.2,3.5,1.1).translate((0,166,118))-prism(242,70,2.2,8,pos=(0,166,118))
add('FRONT / rolled narrow frame',front,FACE)
face=rounded_prism(241.6,69.6,2.1,1.6,.45).translate((0,166,118.0))
cut=disc(28.4,12,(22,166,121))+prism(23,14,6.8,12,pos=(-87,163,120))
add('FRONT / recessed grooved field',face-cut,GROOVE)
# Clip parallel diagonal raised ribs against the front outline and optical apertures.
ribs=[]
for q in np.arange(-155,158,2.8):
 ribs.append(prism(.92,310,.43,.95).rotate((0,0,45)).translate((q,166,119.05)))
clip=prism(240,68,2,2,pos=(0,166,119.05))-cut
add('FRONT / individually modelled diagonal ribs',mf.Manifold.compose(ribs)^clip,FACE)
print('B11: optical assembly',flush=True)
barrel_profile = [(28.3, 118.8), (28.0, 118.4), (26.4, 117.2), (24.6, 116.0), (23.2, 115.2), (22.2, 114.8), (21.5, 114.5), (21.8, 114.0)]
barrel = lathe(barrel_profile, 22, 166)
add('LENS / low profile champagne bezel', barrel, TRIM)
ring('LENS / pale outer rolled rim', 22.8, 21.6, 115.0, material=FACE)
ring('LENS / black retaining ring', 21.6, 20.0, 114.8, material=DARK)
ring('LENS / inner optical seat', 20.0, 19.2, 114.5, material=METAL)
lens_tex_path = ROOT / 'lens_texture.png'
lens_img = Image.open(lens_tex_path).convert('RGB') if lens_tex_path.exists() else None
glass_mesh = dome(22, 166, 19.2, 114.4, 0.35)
if lens_img is not None:
    w_t, h_t = lens_img.size
    dx = (glass_mesh.vertices[:, 0] - 22.0) / 19.2
    dy = (glass_mesh.vertices[:, 1] - 166.0) / 19.2
    u = np.clip(0.5 + 0.5 * dx, 0, 1)
    v = np.clip(0.5 + 0.5 * dy, 0, 1)
    arr_t = np.array(lens_img)
    px = np.clip(np.round(u * (w_t - 1)), 0, w_t - 1).astype(int)
    py = np.clip(np.round((1.0 - v) * (h_t - 1)), 0, h_t - 1).astype(int)
    rgb = arr_t[py, px]
    lens_mat = trimesh.visual.material.PBRMaterial(name='Blue violet optical glass', baseColorFactor=[255, 255, 255, 255], metallicFactor=0.25, roughnessFactor=0.08, baseColorTexture=lens_img)
    glass_mesh.visual = trimesh.visual.TextureVisuals(uv=np.c_[u, v], image=lens_img, material=lens_mat)
    add('LENS / recessed shallow optical glass', glass_mesh, lens_mat, lambda _: rgb)
else:
    add('LENS / recessed shallow optical glass', glass_mesh, GLASS)
sensor_window=rounded_prism(23,14,6.8,.65,.18).translate((-87,163,118.25))-disc(3.45,3,(-84,163,118.4))
add('SENSOR / flush pill shaped window',sensor_window,DARK)
add('SENSOR / inset miniature camera ring',disc(3.43,.25,(-84,163,118.3),inner=3.0),mat('Sensor dark rim',[67,76,73,255],.2,.42))
add('SENSOR / recessed miniature camera glass',disc(3.0,.2,(-84,163,118.23)),mat('Sensor glass',[33,62,65,255],.32,.16))
add('SENSOR / subtle camera glint',disc(.40,.025,(-84.7,164.05,118.35)),METAL)
print('B11: rear grille and connectors',flush=True)
rear=rounded_prism(250,78,4.2,3.0,1).translate((0,166,-118))
slots=[]
for yy in np.arange(137,177,5.6):
 # AC inlet interrupts only the lower left (as viewed from the rear).
 if yy<156:
  slots.extend([prism(159,2.7,1.3,10,pos=(-38,yy,-118)),prism(32,2.7,1.3,10,pos=(101,yy,-118))])
 else:slots.append(prism(234,2.7,1.3,10,pos=(0,yy,-118)))
slots.extend([prism(73,16,1.7,10,pos=(33,190,-118)),prism(36,21,2.5,10,pos=(62,145.7,-118)),disc(1.7,10,(-8,181,-118))])
rear=rear-mf.Manifold.compose(slots)
add('REAR / horizontal slotted cover',rear,CREAM)
for xx,ww in [(83,72),(-8,25),(-105,27)]:
 add('REAR / shallow channel backing',prism(ww,45,1,.6,pos=(xx,156,-116.7)),CREAM)
# Internal fins visible through the wide horizontal slots.
for xx in np.arange(-95,-23,2.4):add('REAR / heatsink fin '+str(xx),prism(.7,43,.2,3,pos=(xx,155,-115.3)),METAL)
add('REAR / connector inset',rounded_prism(72.5,15.5,1.4,1.5,.45).translate((33,190,-118.0)),CREAM)
# In rear view positive X appears at left: round button, HDMI, audio, USB.
add('REAR / round control button',disc(5.1,.6,(62,189,-119)),TRIM)
add('REAR / button face',disc(4.6,.6,(62,189,-119.4)),CREAM)
# HDMI rounded trapezoid, made as a polygon with an inset dark socket.
poly=np.array([[-9,3.4],[9,3.4],[9,-1],[6.7,-4],[-6.7,-4],[-9,-1]])
def polyport(poly,depth,pos):return mf.CrossSection([poly[::-1]]).extrude(depth).translate((pos[0],pos[1],pos[2]-depth/2))
add('REAR / HDMI metal mouth',polyport(poly,.7,(45,191,-119.4)),METAL)
add('REAR / HDMI cavity',polyport(poly*.83,.5,(45,191,-119.85)),BLACK)
add('REAR / HDMI tongue',prism(12,.9,.2,.2,pos=(45,190,-120.15)),DARK)
add('REAR / audio jack',disc(3.0,.8,(24,189,-119.5)),BLACK)
add('REAR / USB metal shell',prism(16,7.5,.45,.75,pos=(6,191,-119.4)),METAL)
add('REAR / USB mouth',prism(14.1,5.7,.25,.6,pos=(6,191,-119.85)),BLACK)
add('REAR / USB inner tongue',prism(12,1.0,.15,.3,pos=(6,189.6,-120.2)),DARK)
add('REAR / AC inlet outer frame',rounded_prism(36,21,2.5,2,.6).translate((62,145.7,-118.4)),DARK)
for xx in [57,67]:
 add('REAR / figure eight socket '+str(xx),disc(5.3,.7,(xx,145.7,-119.8)),BLACK)
 add('REAR / AC pin '+str(xx),disc(.85,1.0,(xx,145.7,-120.25)),METAL)
# Underbody feet and service cover.
for xx in [-96,96]:
 for zz in [-98,98]:
  m=trimesh.creation.icosphere(subdivisions=3,radius=5);m.apply_scale([1,.55,1]);m.apply_translation((xx,125.8,zz));add('BOTTOM / rubber foot',m,DARK)
add('BOTTOM / service hatch',rounded_prism(86,72,2,1,.3).rotate((-90,0,0)).translate((0,127.0,-23)),CREAM)
for xx in [-39,39]:
 for zz in [-54,8]:add('BOTTOM / recessed screw',disc(1.5,.4,(xx,126.4,zz),'y'),DARK)
print('B11: tapered continuous U stand',flush=True)
# Continuous formed band: deep at the base, narrower at the hinge.
path=[];sx=128;radius=9
for yy in np.linspace(176,14,32,endpoint=False):path.append((-sx,yy))
for t in np.linspace(np.pi,1.5*np.pi,28,endpoint=False):path.append((-sx+radius+radius*np.cos(t),14+radius*np.sin(t)))
for xx in np.linspace(-sx+radius,sx-radius,64,endpoint=False):path.append((xx,5))
for t in np.linspace(-np.pi/2,0,28,endpoint=False):path.append((sx-radius+radius*np.cos(t),14+radius*np.sin(t)))
for yy in np.linspace(14,176,32):path.append((sx,yy))
path=np.array(path);v=[];f=[]
for i,(xx,yy) in enumerate(path):
 tangent=path[min(i+1,len(path)-1)]-path[max(0,i-1)];tangent/=np.linalg.norm(tangent);normal=np.array([-tangent[1],tangent[0]])
 width=80-36*np.clip((yy-14)/162,0,1)
 for aa,bb in rr(5.0,width,1.6,8):v.append((xx+aa*normal[0],yy+aa*normal[1],bb))
n=32
for k in range(len(path)-1):
 for i in range(n):
  j=(i+1)%n;f.extend([(k*n+i,k*n+j,(k+1)*n+j),(k*n+i,(k+1)*n+j,(k+1)*n+i)])
v.extend([np.mean(v[:n],axis=0),np.mean(v[-n:],axis=0)]);lo=len(v)-2;hi=len(v)-1
for i in range(n):j=(i+1)%n;f.extend([(lo,j,i),(hi,(len(path)-1)*n+i,(len(path)-1)*n+j)])
add('STAND / one piece tapered ivory U band',trimesh.Trimesh(v,f,process=True),CREAM)
for side in [-1,1]:
 add('STAND / soft upper shoulder',rounded_prism(44,14,5.5,5.0,1.5).rotate((0,90,0)).translate((side*128,176,0)),CREAM)
 add('HINGE / inner pivot boss',disc(11.5,5,(side*126.7,166,0),'x'),TRIM)
 cap=rounded_prism(27,29,4.5,4.5,1.5).rotate((0,90,0)).translate((side*131.2,166,0))
 add('HINGE / rounded square outer shell',cap,CREAM)
 add('HINGE / dark square friction cap',rounded_prism(20,22,1.9,.9,.3).rotate((0,90,0)).translate((side*133.8,166,0)),DARK)
for xx in [-102,102]:add('STAND / underside grip',prism(25,48,3,1,'y',(xx,1.95,0)),DARK)
scene.metadata={'description':'B11 ivory projector rebuilt from seven supplied views. Scale and hidden structure inferred; not manufacturing CAD.'}
scene.export(OUT/'b11-projector.glb')
with open(OUT/'scene.pkl','wb') as f:pickle.dump(items,f)
check=trimesh.load(OUT/'b11-projector.glb',force='scene');assert np.isfinite(check.bounds).all();assert len(check.geometry)==len(items)
print('Exported',len(items),'parts',sum(len(m.faces) for _,m,_ in items),'triangles',(OUT/'b11-projector.glb').stat().st_size,'bytes',flush=True)
