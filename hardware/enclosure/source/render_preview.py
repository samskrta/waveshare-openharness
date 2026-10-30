from pathlib import Path
import math, json
import numpy as np
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import vtkRenderer,vtkRenderWindow,vtkActor,vtkPolyDataMapper,vtkWindowToImageFilter,vtkTextActor
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
import vtkmodules.vtkRenderingOpenGL2
import vtkmodules.vtkRenderingFreeType
ROOT=Path(__file__).resolve().parents[1]
A=math.radians(26);R=np.array([[0,-math.cos(A),math.sin(A)],[1,0,0],[0,math.sin(A),math.cos(A)]])
O=np.array(json.loads((ROOT/'validation.json').read_text())['frame']['origin_world_mm']);T=np.eye(4);T[:3,:3]=R.T;T[:3,3]=-R.T@O
colors={'Housing_Waveshare_Cased':(.93,.39,.13),'Base_Carrier':(.93,.39,.13),'Speaker_Cradle':(.22,.68,.75),'Speaker_Strap':(.25,.28,.32),'Cased_Module_REFERENCE':(.055,.085,.12),'Speaker_REFERENCE':(.63,.67,.72),'USB_Plug_REFERENCE':(.08,.09,.10)}
files={p.stem[8:]:p for p in (ROOT/'source').glob('preview_*.stl')}
window=vtkRenderWindow();window.SetSize(2200,1600);window.SetOffScreenRendering(1);window.SetMultiSamples(8)

def text(r,label,x,y,size=21):
 t=vtkTextActor();t.SetInput(label);t.SetPosition(x,y);p=t.GetTextProperty();p.SetFontFamilyToArial();p.SetFontSize(size);p.SetColor(.09,.14,.19);r.AddActor2D(t)

def panel(viewport,names,title,camera,focal,up,scale,local=True,offsets=None):
 r=vtkRenderer();r.SetViewport(*viewport);r.SetBackground(.955,.965,.975);window.AddRenderer(r)
 for name in names:
  reader=vtkSTLReader();reader.SetFileName(str(files[name]));reader.Update()
  normals=vtkPolyDataNormals();normals.SetInputConnection(reader.GetOutputPort());normals.SetFeatureAngle(30);normals.SplittingOn();normals.ConsistencyOn();normals.ComputePointNormalsOn();normals.Update()
  mapper=vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
  actor=vtkActor();actor.SetMapper(mapper);p=actor.GetProperty();p.SetColor(*colors[name]);p.SetInterpolationToPhong();p.SetDiffuse(.83);p.SetAmbient(.17);p.SetSpecular(.16);p.SetSpecularPower(28)
  mat=np.eye(4)
  if local:mat=T.copy()
  if offsets and name in offsets:mat[:3,3]+=np.array(offsets[name])
  trans=vtkTransform();trans.SetMatrix(mat.ravel());actor.SetUserTransform(trans);r.AddActor(actor)
 c=r.GetActiveCamera();c.SetPosition(*camera);c.SetFocalPoint(*focal);c.SetViewUp(*up);c.ParallelProjectionOn();c.SetParallelScale(scale);r.ResetCameraClippingRange()
 text(r,title,35,670,23)
 return r
names=list(files)
r=panel((0,.49,.5,.94),['Housing_Waveshare_Cased','Base_Carrier','Cased_Module_REFERENCE'],'ONE-PIECE FACE  |  Continuous rim; no front screws',(-75,-35,175),(0,0,-12),(0,1,0),43)
r=panel((.5,.49,1,.94),['Housing_Waveshare_Cased','Base_Carrier','Cased_Module_REFERENCE','USB_Plug_REFERENCE'],'TOP CABLE ENTRY  |  Rounded slot behind the rim',(60,145,85),(0,5,-12),(0,1,0),47)
r=panel((0,.04,.5,.49),[n for n in names if n!='USB_Plug_REFERENCE'],'INSIDE  |  Three main parts; speaker lies flat',(-100,-130,130),(0,0,-10),(0,1,0),67,offsets={'Housing_Waveshare_Cased':(0,0,28),'Cased_Module_REFERENCE':(0,0,10),'Speaker_Strap':(0,0,-8),'Base_Carrier':(0,0,-20),'Speaker_REFERENCE':(0,0,-20)})
r=panel((.5,.04,1,.49),['Housing_Waveshare_Cased','Base_Carrier','Cased_Module_REFERENCE'],'UNDERSIDE  |  Two flush screws; hidden speaker grille',(-90,-70,-95),(-24,0,10),(0,0,1),43,local=False)
head=vtkRenderer();head.SetViewport(0,.94,1,1);head.SetBackground(.955,.965,.975);window.AddRenderer(head);text(head,'HARNESS / REFINED CASED WAVESHARE - CONTINUOUS FRONT RIM',40,42,29);text(head,'Stock protective case retained | Supplied 30 x 20 x 7 mm speaker | Prototype: verify USB-rim coupon before the full print',40,10,18)
foot=vtkRenderer();foot.SetViewport(0,0,1,.04);foot.SetBackground(.955,.965,.975);window.AddRenderer(foot);text(foot,'Orange: continuous shell + underside cartridge    Grey: speaker strap    Dark device, plug and silver speaker: reference envelopes',40,20,17)
window.Render();capture=vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update();writer=vtkPNGWriter();writer.SetFileName(str(ROOT/'Assembly_Preview.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize();print('Rendered assembly with depth buffer',flush=True)

# Presentation views use the same exported CAD meshes, not a styled replacement.
from vtkmodules.vtkFiltersSources import vtkPlaneSource

def save_view(name):
 window.Render()
 capture=vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update()
 writer=vtkPNGWriter();writer.SetFileName(str(ROOT/name));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize()

window=vtkRenderWindow();window.SetSize(1800,1400);window.SetOffScreenRendering(1);window.SetMultiSamples(8)
r=panel((0,0,1,1),['Housing_Waveshare_Cased','Base_Carrier','Cased_Module_REFERENCE'],'',
        (80,-70,145),(-24,0,18),(0,0,1),44,local=False)
ground=vtkPlaneSource();ground.SetOrigin(-150,-125,-.08);ground.SetPoint1(100,-125,-.08);ground.SetPoint2(-150,125,-.08)
mapper=vtkPolyDataMapper();mapper.SetInputConnection(ground.GetOutputPort())
actor=vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(.945,.955,.965);actor.GetProperty().SetAmbient(1);actor.GetProperty().SetDiffuse(0);r.AddActor(actor)
text(r,'Refined cased Waveshare enclosure | actual CAD geometry | physical fit pending',35,35,21)
save_view('Refined_Hero.png')
window=vtkRenderWindow();window.SetSize(1800,900);window.SetOffScreenRendering(1);window.SetMultiSamples(8)
for index,plug in enumerate([False,True]):
 shown=['Housing_Waveshare_Cased','Base_Carrier','Cased_Module_REFERENCE']+(['USB_Plug_REFERENCE'] if plug else [])
 r=panel((index*.5,0,(index+1)*.5,1),shown,'',(0,130,15),(0,27,-4),(0,0,1),19)
 text(r,'Compact plug envelope' if plug else 'USB slot behind the continuous rim',30,830,23)
 text(r,'13.4 x 6.4 mm body; 0.3 mm nominal clearance per side' if plug else 'Rounded 14 x 7 mm opening; no notch through the face',30,35,16)
save_view('USB_Port_Detail.png')
