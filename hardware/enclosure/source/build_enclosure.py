"""Refined cased Waveshare housing: continuous rim, smooth analytic shell,
an underside display/speaker cartridge and concealed fasteners. Units: mm.
The original Autonomous housing/photo informs the silhouette; this is a new
parametric model, not a claim of identical original surfaces or proven fit.
"""
from pathlib import Path
import math, json
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
for folder in ['stl','step','source']: (ROOT/folder).mkdir(exist_ok=True,parents=True)
for p in (ROOT/'source').glob('preview_*.stl'): p.unlink()
# Superseded generated parts are not compatible with this three-part revision.
for name in ['Front_Bezel','Speaker_Cradle','Bottom_Cover','Display_Retainer','Retention_Key']:
 for folder,ext in [('stl','stl'),('step','step')]:
  p=ROOT/folder/f'{name}.{ext}'
  if p.exists(): p.unlink()
P={
 'case_diameter':51.0,'case_depth':12.1,'case_bore':51.6,
 'front_aperture':49.8,'front_outer_diameter':55.2,
 'case_front_z':-1.5,'front_lip_back_z':-1.3,'front_padding':0.2,
 'sphere_radius':31.9,'sphere_center_z':12.0,'shell_thickness':1.9,'face_tilt_deg':26.0,
 'usb_slot_width':14.0,'usb_slot_height':7.0,'usb_center_depth':10.3,
 'usb_corner_radius':2.0,'usb_plug_reference_width':13.4,'usb_plug_reference_height':6.4,
 'usb_plug_reference_insertion':15.0,'rim_coupon_depth':11.0,
 'speaker_width':30.0,'speaker_height':20.0,'speaker_depth':7.0,
 'speaker_pocket_width':30.8,'speaker_pocket_height':20.8,'speaker_corner_radius':2.0,
 'speaker_center_y':4.5,'speaker_shift_z':0.0,'speaker_back_z':-21.2,
 'base_thickness':2.4,'pilot_diameter':1.7,'clearance_diameter':2.3,
}
A=math.radians(P['face_tilt_deg'])
N=cq.Vector(math.sin(A),0,math.cos(A))
CENTRE=cq.Vector(-24,0,P['sphere_center_z'])
FACE_DISTANCE=math.sqrt(P['sphere_radius']**2-(P['front_outer_diameter']/2)**2)
ORIGIN=CENTRE+N*FACE_DISTANCE
P['front_center_height']=ORIGIN.z
PLANE=cq.Plane(ORIGIN,xDir=(0,1,0),normal=N);LOC=PLANE.location
def world(s): return s.moved(LOC)
def local(s): return s.moved(LOC.inverse)
SPEAKER_PLANE=cq.Plane((-28.5,0,P['base_thickness']-.1+22.8),xDir=(0,1,0),normal=(0,0,1))
def speaker_world(s): return s.moved(SPEAKER_PLANE.location)
def box(x,y,z,c): return cq.Workplane('XY').box(x,y,z).val().translate(c)
def cyl(r,h,z=0,x=0,y=0): return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def clean(s):
 if not s.isValid(): raise RuntimeError('Invalid boolean result')
 s=s.clean()
 if not s.isValid(): raise RuntimeError('Invalid cleaned result')
 return s
def cut(s,t):
 for tol in [None,.0000001,.00001,.0001]:
  try:
   v=s.copy().cut(t.copy(),tol=tol)
   if v.isValid() and .0001 < v.Volume() <= s.Volume()+.01: return clean(v)
  except Exception: pass
 raise RuntimeError('No valid cut result')
def fuse(s,*others):
 for t in others:
  found=False
  for tol in [None,.0000001,.00001,.0001]:
   try:
    v=s.copy().fuse(t.copy(),tol=tol)
    if v.isValid() and v.Volume() >= max(s.Volume(),t.Volume())-.01:
     s=clean(v);found=True;break
   except Exception: pass
  if not found: raise RuntimeError('No valid fuse result')
 return s
def rr(w,h,r,z,d,x=0,y=0):
 return cq.Workplane('XY').rect(w,h).extrude(d).edges('|Z').fillet(r).val().translate((x,y,z))
def radial_slot(angle,w,h,z,inner=24.6,length=20,r=1.2):
 return (cq.Workplane('XY').box(length,w,h).edges('|X').fillet(r).val()
  .translate((inner+length/2,0,z)).rotate((0,0,0),(0,0,1),angle))
def radial_hole(angle,r,z):
 return cq.Solid.makeCylinder(r,20,cq.Vector(24,0,z),cq.Vector(1,0,0)).rotate((0,0,0),(0,0,1),angle)

# Analytic spherical skin: smooth, compact and free of loft seams or facets.
# The circular face and flat foot are clean cuts through the same sphere.
FOOT=cq.Vector(-24,0,0)
outer_world=cq.Solid.makeSphere(P['sphere_radius'],CENTRE,angleDegrees1=-90,angleDegrees2=90)
outer_world=outer_world.intersect(world(box(160,160,100,(0,0,-50))))
outer_world=outer_world.intersect(box(180,180,90,(-24,0,45)))
outer_world=world(cq.Workplane('XY').newObject([local(outer_world)]).edges('>Z').fillet(.35).val())
body=local(outer_world)
inner_world=cq.Solid.makeSphere(P['sphere_radius']-P['shell_thickness'],CENTRE,angleDegrees1=-90,angleDegrees2=90)
inner_world=inner_world.intersect(world(box(160,160,100,(0,0,P['front_lip_back_z']-50))))
# The case first enters vertically with its centre at the sphere's centre,
# then moves along the display normal into the front lip.
ENTRY_OFFSET=N*(-FACE_DISTANCE-(P['case_front_z']-P['case_depth']/2))
ENTRY_CLEARANCE=box(80,P['case_bore'],100,(-24,0,0))
BASE_SCREWS=[(-24,27.3),(-24,-27.3)]
for x,y in BASE_SCREWS:
 boss=cut(cyl(1.8,6,P['base_thickness'],x,y),ENTRY_CLEARANCE)
 inner_world=cut(inner_world,boss)
body=cut(body,local(inner_world))
body=cut(body,cyl(P['front_aperture']/2,85,-80))
body=cut(body,cq.Solid.makeCone(24.9,25.25,.35,cq.Vector(0,0,-.35)))
print('analytic shell',body.Volume(),body.isValid(),flush=True)
# Keep the cover split on the underside only; no front seam or separate bezel.
body=cut(body,local(box(180,180,20,(-25,0,P['base_thickness']-10))))

# Top USB is a rounded tunnel entirely BEHIND the continuous front rim.
usb_cut=radial_slot(90,P['usb_slot_width'],P['usb_slot_height'],-P['usb_center_depth'],r=P['usb_corner_radius'])
body=cut(body,usb_cut)
# Tiny acoustic bores and recessed tool access replace the giant side windows.
for a in [56,124]: body=cut(body,radial_hole(a,.7,-5.3))
for a in [236,304]: body=cut(body,radial_hole(a,1.0,-8.8))
# microSD is serviced from underneath after releasing the internal module.

# The underside cartridge cups the case's outer rear rim. Its register centers
# the retained case without front fasteners or a loose internal locking ring.
ring=cut(cyl(26.8,1.8,-15.4),cyl(23.4,2.2,-15.6))
ring=fuse(ring,cut(cyl(26.8,2.3,-13.7),cyl(25.8,2.5,-13.8)))

# The supplied speaker lives in the same removable underside cartridge.
dy=P['speaker_center_y']-4.5;dz=P['speaker_shift_z'];ear_y=-5.5+dy
tray=rr(34.4,24.4,3,-22.8+dz,8.8,0,P['speaker_center_y'])
tray=cut(tray,rr(P['speaker_pocket_width'],P['speaker_pocket_height'],2,-21.8+dz,8,0,P['speaker_center_y']))
for sign in [-1,1]:
 tray=fuse(tray,cyl(2.8,2,-16+dz,sign*18.3,ear_y))
 tray=cut(tray,cyl(1.15,3,-16.5+dz,sign*18.3,ear_y))
tray=cut(tray,box(8,4,6,(17,P['speaker_center_y'],-16+dz)))
for x in [-13.3,13.3]:
 for y in [-4.4+dy,13.4+dy]: tray=fuse(tray,box(1.4,.8,.6,(x,y,-21.5+dz)))
for y in [-2+dy,1.25+dy,4.5+dy,7.75+dy,11+dy]: tray=cut(tray,rr(25,1.6,.65,-23.2+dz,2,0,y))
strap=rr(41.8,5.6,2.4,-14+dz,1.2,0,ear_y)
for x in [-18.3,18.3]:
 strap=cut(strap,cyl(1.15,2,-14.2+dz,x,ear_y))
 strap=cut(strap,cq.Solid.makeCone(1.15,2,.85,cq.Vector(x,ear_y,-13.65+dz)))
# Full-footprint cover. Two vertical screw bosses and countersunk heads are
# confined to the underside, never on the face.
base=outer_world.intersect(box(180,180,P['base_thickness'],(-25,0,P['base_thickness']/2)))
base=clean(base)
for x,y in BASE_SCREWS:
 body=cut(body,local(cyl(.85,6.2,P['base_thickness']-.1,x,y)))
 base=cut(base,cyl(1.15,5,-.5,x,y))
 base=cut(base,cq.Solid.makeCone(2.0,1.15,.85,cq.Vector(x,y,0)))

foot_x=FOOT.x
body=world(clean(body))
body=body.intersect(box(180,180,90,(-25,0,P['base_thickness']+45)))
# Three pillars behind the case's outer rim. Their angled ends meet the cradle
# ring; all are part of the base, so none obstructs inserting the cased module.
carrier=base
for a in [0,180,270]:
 x=24.7*math.cos(math.radians(a));y=24.7*math.sin(math.radians(a))
 pt=ORIGIN+PLANE.xDir*x+PLANE.yDir*y+N*(-14.2)
 post=cyl(2.0,40,P['base_thickness']-.1,pt.x,pt.y)
 post=post.intersect(world(box(160,160,80,(0,0,-54.2))))
 carrier=fuse(carrier,post)
carrier=fuse(carrier,world(ring))
for sign in [-1,1]:
 post=speaker_world(cyl(2.8,44.1,-60,sign*18.3,ear_y))
 post=post.intersect(box(180,180,70,(-25,0,P['base_thickness']-.1+35)))
 carrier=fuse(carrier,post)
carrier=fuse(carrier,speaker_world(tray))
for sign in [-1,1]: carrier=cut(carrier,speaker_world(cyl(.85,6.4,-22.2,sign*18.3,ear_y)))
for y in [-2,1.25,4.5,7.75,11]: carrier=cut(carrier,speaker_world(rr(25,1.6,.65,-26,5,0,y)))
# Clearance slots around stationary shell bosses run through the moving cradle,
# while the underside retains its ordinary countersunk fixing holes.
for x,y in BASE_SCREWS: carrier=cut(carrier,cyl(2.1,50,P['base_thickness'],x,y))
# Keep the carrier clear of the shared USB tunnel when the port sits farther back.
carrier=cut(carrier,world(usb_cut))

module=cyl(P['case_diameter']/2,P['case_depth'],P['case_front_z']-P['case_depth'])
speaker=rr(P['speaker_width'],P['speaker_height'],3,P['speaker_back_z'],P['speaker_depth'],0,P['speaker_center_y'])
# Conservative compact-plug envelope: 0.3 mm clearance per side in the slot.
plug=radial_slot(90,P['usb_plug_reference_width'],P['usb_plug_reference_height'],-P['usb_center_depth'],inner=P['case_diameter']/2,length=P['usb_plug_reference_insertion'],r=1.7)
case_coupon=cut(cyl(P['case_bore']/2+2.2,3),cyl(P['case_bore']/2,4,-.5))
speaker_coupon=cut(rr(34.4,24.4,3,0,3),rr(30.8,20.8,2,-.5,4))
depth=P['rim_coupon_depth']
usb_coupon=local(body).intersect(box(160,160,depth,(0,0,-depth/2))).translate((0,0,depth))
parts={'Housing_Waveshare_Cased':body,'Base_Carrier':carrier,'Speaker_Strap':speaker_world(strap)}
print_parts={'Housing_Waveshare_Cased':body.translate((0,0,-P['base_thickness'])),'Base_Carrier':carrier.translate((-foot_x,0,0)),
 'Speaker_Strap':strap.translate((0,-ear_y,14-dz)),
 'Case_Fit_Coupon':case_coupon,'Speaker_Fit_Coupon':speaker_coupon,'USB_Rim_Fit_Coupon':usb_coupon}
validation={'revision':'refined-continuous-rim','frame':{'origin_world_mm':ORIGIN.toTuple(),'tilt_deg':P['face_tilt_deg']},'parameters':P,'parts':{},'intersections_mm3':{},
 'original_base_commit':'a270d3e787aed01e9b204abd11b0d8952a4fc071',
 'caveat':'CAD-checked prototype, not physically fitted. USB port depth is inferred from the vendor drawing; verify the rim coupon with the actual cased unit and cable.'}
for name,s in print_parts.items():
 if not s.isValid() or len(s.Solids())!=1: raise RuntimeError(f'Invalid/disconnected {name}: {s.isValid()} {len(s.Solids())}')
 cq.exporters.export(s,str(ROOT/'step'/f'{name}.step'))
 cq.exporters.export(s,str(ROOT/'stl'/f'{name}.stl'),tolerance=.015,angularTolerance=.05)
 b=s.BoundingBox();validation['parts'][name]={'valid':True,'solids':1,'volume_mm3':s.Volume(),'bounds_mm':[b.xlen,b.ylen,b.zlen]}
 print(name,validation['parts'][name],flush=True)
check={**parts,'Cased_Module_REFERENCE':world(module),'Speaker_REFERENCE':speaker_world(speaker),'USB_Plug_REFERENCE':world(plug)}
for i,(name,s) in enumerate(check.items()):
 for other,t in list(check.items())[i+1:]:
  v=s.intersect(t).Volume();validation['intersections_mm3'][name+' / '+other]=v
  if v>.03: print('INTERFERENCE',name,other,v,flush=True)
# Check the two-stage underside entry before the cartridge is installed.
# This is a simplified cased-cylinder envelope, not a full wired-board model.
module_clear=world(cyl(P['case_diameter']/2+.1,P['case_depth']+.2,P['case_front_z']-P['case_depth']-.1))
path_overlaps=[]
for n in range(201):
 pos=ENTRY_OFFSET+cq.Vector(0,0,-40+n*.2)
 path_overlaps.append(body.intersect(module_clear.translate(pos)).Volume())
normal_steps=math.ceil(ENTRY_OFFSET.Length/.2)
for n in range(normal_steps+1):
 pos=ENTRY_OFFSET*(1-n/normal_steps)
 path_overlaps.append(body.intersect(module_clear.translate(pos)).Volume())
validation['module_insertion']={'method':'vertical entry with module centered at sphere center, then along display normal',
 'case_envelope_margin_mm':.1,'maximum_sample_step_mm':.2,'samples':len(path_overlaps),
 'max_overlap_mm3':max(path_overlaps),'entry_offset_world_mm':ENTRY_OFFSET.toTuple()}
print('Module insertion:',validation['module_insertion'],flush=True)
validation['carrier_insertion_samples_mm3']={}
for dz in [-40,-30,-20,-10,-5,-2,-1,-.5,0]:
 validation['carrier_insertion_samples_mm3'][str(dz)]=body.intersect(carrier.translate((0,0,dz))).Volume()
validation['outside_envelope_mm3']={name:s.cut(outer_world).Volume() for name,s in
 [('Base_Carrier',carrier),('Speaker_Strap',speaker_world(strap)),('Cased_Module_REFERENCE',world(module))]}
band=cut(cyl(27.2,.8,-.8),cyl(25.25,1.0,-.9))
validation['continuous_front_rim_missing_mm3']=world(band).cut(body).Volume()
print('Carrier path:',validation['carrier_insertion_samples_mm3'],flush=True)
print('Outside envelope:',validation['outside_envelope_mm3'],flush=True)
print('Front rim missing:',validation['continuous_front_rim_missing_mm3'],flush=True)
(ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
if (any(v>.03 for v in validation['intersections_mm3'].values()) or max(path_overlaps)>.03 or
 any(v>.03 for v in validation['carrier_insertion_samples_mm3'].values()) or
 any(v>.03 for v in validation['outside_envelope_mm3'].values()) or validation['continuous_front_rim_missing_mm3']>.03):
 raise RuntimeError('Interference: do not publish these exports')
assembly=cq.Assembly(name='Harness_Refined_Cased_Prototype')
colors={'Housing_Waveshare_Cased':cq.Color(.95,.36,.08),'Base_Carrier':cq.Color(.95,.36,.08),
 'Speaker_Strap':cq.Color(.25,.28,.32)}
for name,s in parts.items(): assembly.add(s,name=name,color=colors[name])
for name,s in check.items():
 if name not in parts: assembly.add(s,name=name+'_NOT_PRINT',color=cq.Color(.08,.10,.12) if 'Module' in name else cq.Color(.45,.48,.50))
assembly.save(str(ROOT/'step/Harness_Waveshare_Cased_Assembly.step'))
for name,s in check.items(): cq.exporters.export(s,str(ROOT/'source'/f'preview_{name}.stl'),tolerance=.015,angularTolerance=.05)
print('DONE',flush=True)
