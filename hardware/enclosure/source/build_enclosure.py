"""OpenHarness housing adaptation for cased Waveshare 1.75-B + supplied speaker.
Units: mm. CQ 2.8 / OCP 7.9.3.1.1. Original housing from OpenHarness a270d3e.
Global frame keeps the upstream desk plane; local frame is the upright display.
"""
from pathlib import Path
import math, json
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
for folder in ["stl", "step", "source"]: (ROOT/folder).mkdir(exist_ok=True,parents=True)
P={
 'outer_scale':1.20,'case_diameter':51.0,'case_depth':12.1,
 'case_bore':51.6,'case_seat_depth':12.6,'front_aperture':49.8,
 'speaker_width':30.0,'speaker_height':20.0,'speaker_depth':7.0,
 'speaker_pocket_width':30.8,'speaker_pocket_height':20.8,'speaker_corner_radius':2.0,
 'speaker_center_y':4.5,'speaker_back_z':-21.2,
 'usb_window_width':16.0,'usb_window_height':11.0,'usb_window_depth':5.0,
 'pilot_diameter':1.7,'clearance_diameter':2.3,'bezel_thickness':2.2,
 'floor_thickness':2.4,'base_radius':24.0,'rear_cavity_radius':23.7,
}
BASE=cq.Vector(-22.196025762,0,0)
OLD_FRONT=cq.Vector(-20.679414369,0,21.678004569)
ORIGIN=BASE+(OLD_FRONT-BASE)*P['outer_scale']
N=cq.Vector(math.sin(math.radians(26)),0,math.cos(math.radians(26)))
PLANE=cq.Plane(ORIGIN,xDir=(0,1,0),normal=N)
LOC=PLANE.location

def world(s): return s.moved(LOC)
def local(s): return s.moved(LOC.inverse)
def box(x,y,z,center): return cq.Workplane('XY').box(x,y,z).val().translate(center)
def cyl(r,h,z=0,x=0,y=0): return cq.Solid.makeCylinder(r,h,cq.Vector(x,y,z))
def rr(w,h,r,z0,depth,x=0,y=0):
 s=cq.Workplane('XY').rect(w,h).extrude(depth).edges('|Z').fillet(r).val()
 return s.translate((x,y,z0))
def healed(s): return s.clean()

def cut(s,tool): return healed(s.cut(tool))
def fuse(s,*others):
 for t in others: s=healed(s.fuse(t))
 return s

def radial_window(s,angle,width,height,z,inner=22,length=20):
 t=box(length,width,height,(inner+length/2,0,z)).rotate((0,0,0),(0,0,1),angle)
 return cut(s,t)

# Rebuild the upstream exterior form with clean surfaces. The original imported
# offset/trimmed skin fails further booleans; it remains a dimensional reference.
bottom=cq.Workplane('XY').circle(P['base_radius']).val().translate(BASE)
mid=cq.Workplane('XY').circle(31.5).val().translate(BASE+cq.Vector(0,0,10.0))
front=cq.Workplane(PLANE).circle(25.98*P['outer_scale']).val()
envelope=cq.Solid.makeLoft([bottom,mid,front],ruled=True)
body=envelope
# Flat desk mating plane and a planar bezel interface.

body=local(body)

case_void=cyl(P['case_bore']/2,16,-P['case_seat_depth'])
body=cut(body,case_void)
# Open rear plenum, leaving the desk floor and an annular case seat untouched.
rear=world(cyl(P['rear_cavity_radius'],32,-44.6))
inner_bottom=cq.Workplane('XY').circle(21.6).val().translate(BASE+cq.Vector(0,0,2.4))
inner_mid=cq.Workplane('XY').circle(29.1).val().translate(BASE+cq.Vector(0,0,10.0))
inner_front=cq.Workplane(PLANE).circle(28.776).val()
inner_envelope=cq.Solid.makeLoft([inner_bottom,inner_mid,inner_front],ruled=True)
rear=healed(rear.intersect(inner_envelope))
body=cut(body,local(rear))
# Three front fasteners; avoid the left USB/mics and right button cutouts.
BEZEL_ANGLES=[60,120,270]
for a in BEZEL_ANGLES:
 x=28.3*math.cos(math.radians(a)); y=28.3*math.sin(math.radians(a))
 body=fuse(body,cyl(2.8,8,-8,x,y))
 body=cut(body,cyl(P['pilot_diameter']/2,8.2,-8.1,x,y))
body=cut(body,case_void)
# Cased-unit side access. Left is 9 o'clock viewed with the text upright.
body=radial_window(body,180,P['usb_window_width'],P['usb_window_height'],-P['usb_window_depth'])
for a in [146,214]: body=radial_window(body,a,6,6,-4.5)
for a in [-34,34]: body=radial_window(body,a,10.5,9,-7.0)
body=radial_window(body,0,16,5,-3.8)
# Wire relief through the rear annular seat.
body=cut(body,box(12,7,5,(22,4.5,-13.1)))
# Speaker cradle screws/rails are joined to the wall, not floating bosses.
for sign in [-1,1]:
 x=sign*18.3
 body=fuse(body,cyl(2.8,6.0,-22.0,x,-5.5),box(8.5,5.6,3,(sign*22.0,-5.5,-17.5)))
 body=cut(body,cyl(.85,6.4,-22.2,x,-5.5))
# Clear the case and wire-relief again after adding the rails.
body=cut(body,case_void)
# Bottom access and three self-tapping screw lands in global desk coordinates.
body=world(body)
body=cut(body,cyl(18.8,12,-1,BASE.x,0))
BASE_ANGLES=[0,120,240]
for a in BASE_ANGLES:
 x=BASE.x+21.5*math.cos(math.radians(a)); y=21.5*math.sin(math.radians(a))
 body=cut(body,cyl(.85,8,-.1,x,y))
body=healed(body)

bezel=cut(cyl(31.176,2.2,0),cyl(P['front_aperture']/2,3,-.4))
# Open the left bezel edge too, so a cable overmold can reach the recessed port.
bezel=radial_window(bezel,180,P['usb_window_width'],4,1.1)
for a in BEZEL_ANGLES:
 x=28.3*math.cos(math.radians(a)); y=28.3*math.sin(math.radians(a))
 bezel=cut(bezel,cyl(1.15,3,-.1,x,y))
 bezel=cut(bezel,cyl(2.1,1.15,1.05,x,y))

# Rounded cavity matches the 2030 Type-B speaker. Small corner seats support
# only its plastic rim; its outward-facing diaphragm is spaced above the grill.
tray=rr(34.4,24.4,3,-22.8,8.8,0,4.5)
tray=cut(tray,rr(P['speaker_pocket_width'],P['speaker_pocket_height'],P['speaker_corner_radius'],-21.8,8.0,0,P['speaker_center_y']))
for sign in [-1,1]:
 tray=fuse(tray,cyl(2.8,2,-16,sign*18.3,-5.5))
 tray=cut(tray,cyl(1.15,3,-16.5,sign*18.3,-5.5))
 # Leads exit from the right side in the supplied speaker drawing.
tray=cut(tray,box(8,4,6,(17,4.5,-16)))
for x in [-13.3,13.3]:
 for y in [-4.4,13.4]: tray=fuse(tray,box(1.4,.8,.6,(x,y,-21.5)))
for y in [-2.0,1.25,4.5,7.75,11.0]:
 tray=cut(tray,rr(25,1.6,.65,-23.2,2.0,0,y))
# A removable strap touches the speaker's closed back, never its diaphragm.
strap=rr(41.8,5.6,2.4,-14,1.2,0,-5.5)
for x in [-18.3,18.3]:
 strap=cut(strap,cyl(1.15,2,-14.2,x,-5.5))
 strap=cut(strap,cq.Solid.makeCone(1.15,2.0,.85,cq.Vector(x,-5.5,-13.65)))

base=cyl(24,2.4,-2.4,BASE.x,0)
for a in BASE_ANGLES:
 x=BASE.x+21.5*math.cos(math.radians(a)); y=21.5*math.sin(math.radians(a))
 base=cut(base,cyl(1.15,3,-2.7,x,y))
 base=cut(base,cyl(2.1,1.1,-2.4,x,y))
# Downward sound path and ventilation. Rubber feet must raise it >=1.5 mm.
for xx in [-12,-6,0,6,12]:
 for yy in [-12,-6,0,6,12]:
  if xx*xx+yy*yy<17.2**2:
   base=cut(base,cyl(1.7,3,-2.7,BASE.x+xx,yy))

module=cyl(P['case_diameter']/2,P['case_depth'],-P['case_depth'])
speaker=rr(P['speaker_width'],P['speaker_height'],3,P['speaker_back_z'],P['speaker_depth'],0,P['speaker_center_y'])
# Tiny test prints use the exact fit parameters, before printing the body.
case_coupon=cut(cyl(P['case_bore']/2+2.2,3),cyl(P['case_bore']/2,4,-.5))
speaker_coupon=cut(rr(P['speaker_pocket_width']+3.6,P['speaker_pocket_height']+3.6,3,0,3),rr(P['speaker_pocket_width'],P['speaker_pocket_height'],P['speaker_corner_radius'],-.5,4))

parts={'Housing_Waveshare_Cased':body,'Front_Bezel':world(bezel),
       'Speaker_Cradle':world(tray),'Speaker_Strap':world(strap),'Bottom_Cover':base}
print_parts={'Housing_Waveshare_Cased':body,'Front_Bezel':bezel,
 'Speaker_Cradle':tray.translate((0,-4.5,22.8)),
 'Speaker_Strap':strap.translate((0,5.5,14)),
 'Bottom_Cover':base.translate((-BASE.x,0,2.4)),
 'Case_Fit_Coupon':case_coupon,'Speaker_Fit_Coupon':speaker_coupon}
validation={'parameters_mm':P,'parts':{},'intersections_mm3':{},'original_base_commit':'a270d3e787aed01e9b204abd11b0d8952a4fc071',
 'caveat':'CAD-checked prototype. No physical print or fit verification yet. Print both coupons first.'}
for name,shape in print_parts.items():
 if not shape.isValid(): raise RuntimeError('Invalid CAD: '+name)
 solids=shape.Solids()
 if len(solids)!=1: raise RuntimeError(f'{name}: {len(solids)} disconnected solids')
 cq.exporters.export(shape,str(ROOT/'stl'/f'{name}.stl'),tolerance=.035,angularTolerance=.12)
 cq.exporters.export(shape,str(ROOT/'step'/f'{name}.step'))
 b=shape.BoundingBox()
 validation['parts'][name]={'valid':True,'solids':1,'volume_mm3':shape.Volume(),
                         'bounds_mm':[b.xlen,b.ylen,b.zlen]}
 print(name,validation['parts'][name],flush=True)
# Check material interference in assembly coordinates. Contact surfaces are OK.
check={**parts,'Cased_Module_REFERENCE':world(module),'Speaker_REFERENCE':world(speaker)}
for i,(name,s) in enumerate(check.items()):
 for other,t in list(check.items())[i+1:]:
  v=s.intersect(t).Volume()
  validation['intersections_mm3'][name+' / '+other]=v
  if v>.03: print('INTERFERENCE',name,other,v,flush=True)
(ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
if any(v > .03 for v in validation['intersections_mm3'].values()):
 raise RuntimeError('Assembly interference detected; do not use these exports')
assembly=cq.Assembly(name='Harness_Waveshare_Cased_Prototype')
colors={'Housing_Waveshare_Cased':cq.Color(.95,.39,.10),'Front_Bezel':cq.Color(.25,.28,.32),
 'Speaker_Cradle':cq.Color(.30,.64,.75),'Speaker_Strap':cq.Color(.30,.64,.75),'Bottom_Cover':cq.Color(.25,.28,.32)}
for name,s in parts.items(): assembly.add(s,name=name,color=colors[name])
assembly.add(world(module),name='Cased_Module_REFERENCE_NOT_PRINT',color=cq.Color(.12,.14,.18))
assembly.add(world(speaker),name='Speaker_REFERENCE_NOT_PRINT',color=cq.Color(.65,.65,.65))
assembly.save(str(ROOT/'step/Harness_Waveshare_Cased_Assembly.step'))
# Render-friendly mesh copies, all in assembly position (not print orientation).
for name,s in check.items():
 cq.exporters.export(s,str(ROOT/'source'/f'preview_{name}.stl'),tolerance=.10,angularTolerance=.25)
print('DONE',flush=True)
