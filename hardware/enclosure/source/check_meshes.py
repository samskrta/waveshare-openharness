from pathlib import Path
import json, math
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
validation=json.loads((ROOT/'validation.json').read_text())
for p in (ROOT/'stl').glob('*.stl'):
 m=trimesh.load(p,force='mesh',process=True)
 stats={'watertight':bool(m.is_watertight),'consistent_winding':bool(m.is_winding_consistent),
 'components':len(m.split(only_watertight=False)),'triangles':len(m.faces),'volume_mm3':float(m.volume),
 'bounds_mm':m.bounds.tolist()}
 if not stats['watertight'] or not stats['consistent_winding'] or stats['components']!=1: raise RuntimeError(str(p)+str(stats))
 validation['parts'][p.stem]['mesh']=stats
 print(p.name,stats,flush=True)
(ROOT/'validation.json').write_text(json.dumps(validation,indent=2)+'\n')
