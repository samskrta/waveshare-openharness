from pathlib import Path
import math
import numpy as np
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkIOGeometry import vtkSTLReader
from vtkmodules.vtkRenderingCore import vtkRenderer,vtkRenderWindow,vtkActor,vtkPolyDataMapper,vtkWindowToImageFilter,vtkTextActor
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkCommonTransforms import vtkTransform
import vtkmodules.vtkRenderingOpenGL2
import vtkmodules.vtkRenderingFreeType
ROOT=Path(__file__).resolve().parents[1]
A=math.radians(26);R=np.array([[0,-math.cos(A),math.sin(A)],[1,0,0],[0,math.sin(A),math.cos(A)]])
O=np.array([-20.3760920904,0,26.0136054828]);T=np.eye(4);T[:3,:3]=R.T;T[:3,3]=-R.T@O
colors={'Housing_Waveshare_Cased':(.93,.39,.13),'Front_Bezel':(.20,.23,.28),'Speaker_Cradle':(.22,.68,.75),'Speaker_Strap':(.15,.52,.62),'Bottom_Cover':(.29,.34,.42),'Cased_Module_REFERENCE':(.055,.085,.12),'Speaker_REFERENCE':(.63,.67,.72)}
files={p.stem[8:]:p for p in (ROOT/'source').glob('preview_*.stl')}
window=vtkRenderWindow();window.SetSize(2200,1600);window.SetOffScreenRendering(1);window.SetMultiSamples(8)

def text(r,label,x,y,size=21):
 t=vtkTextActor();t.SetInput(label);t.SetPosition(x,y);p=t.GetTextProperty();p.SetFontFamilyToArial();p.SetFontSize(size);p.SetColor(.09,.14,.19);r.AddActor2D(t)

def panel(viewport,names,title,camera,focal,up,scale,local=True,offsets=None):
 r=vtkRenderer();r.SetViewport(*viewport);r.SetBackground(.955,.965,.975);window.AddRenderer(r)
 for name in names:
  reader=vtkSTLReader();reader.SetFileName(str(files[name]));reader.Update()
  mapper=vtkPolyDataMapper();mapper.SetInputConnection(reader.GetOutputPort())
  actor=vtkActor();actor.SetMapper(mapper);p=actor.GetProperty();p.SetColor(*colors[name]);p.SetInterpolationToPhong();p.SetDiffuse(.83);p.SetAmbient(.17);p.SetSpecular(.16);p.SetSpecularPower(28)
  mat=np.eye(4)
  if local:mat=T.copy()
  if offsets and name in offsets:mat[:3,3]+=np.array(offsets[name])
  trans=vtkTransform();trans.SetMatrix(mat.ravel());actor.SetUserTransform(trans);r.AddActor(actor)
 c=r.GetActiveCamera();c.SetPosition(*camera);c.SetFocalPoint(*focal);c.SetViewUp(*up);c.ParallelProjectionOn();c.SetParallelScale(scale);r.ResetCameraClippingRange()
 text(r,title,35,670,23)
 return r
names=list(files)
r=panel((0,.49,.5,.94),names,'ASSEMBLED  |  Top USB-C access',(-90,-25,160),(0,0,-12),(0,1,0),45)
r=panel((.5,.49,1,.94),['Housing_Waveshare_Cased','Speaker_Cradle','Speaker_Strap','Speaker_REFERENCE'],'FRONT OPEN  |  Cased-module seat + speaker',(-55,-35,150),(0,0,-14),(0,1,0),45)
r=panel((0,.04,.5,.49),names,'EXPLODED  |  Five printable parts',(-130,-145,95),(0,0,-5),(0,0,1),72,offsets={'Front_Bezel':(0,0,32),'Cased_Module_REFERENCE':(0,0,16),'Speaker_Strap':(0,0,-7),'Speaker_Cradle':(0,0,-20),'Speaker_REFERENCE':(0,0,-20),'Bottom_Cover':(0,0,-35)})
r=panel((.5,.04,1,.49),['Housing_Waveshare_Cased','Bottom_Cover'],'UNDERSIDE  |  Vented removable cover',(-95,-90,-80),(-22,0,10),(0,0,1),45,local=False)
head=vtkRenderer();head.SetViewport(0,.94,1,1);head.SetBackground(.955,.965,.975);window.AddRenderer(head);text(head,'HARNESS / WAVESHARE 1.75-B - STOCK CASE RETAINED',40,42,29);text(head,'51 mm display case | 30 x 20 x 7 mm rounded speaker | CAD-checked prototype: print fit coupons first',40,10,18)
foot=vtkRenderer();foot.SetViewport(0,0,1,.04);foot.SetBackground(.955,.965,.975);window.AddRenderer(foot);text(foot,'Orange: housing    Grey: bezel / cover    Cyan: speaker cradle / strap    Dark device and silver speaker: reference envelopes only',40,20,17)
window.Render();capture=vtkWindowToImageFilter();capture.SetInput(window);capture.ReadFrontBufferOff();capture.Update();writer=vtkPNGWriter();writer.SetFileName(str(ROOT/'Assembly_Preview.png'));writer.SetInputConnection(capture.GetOutputPort());writer.Write();window.Finalize();print('Rendered assembly with depth buffer',flush=True)
