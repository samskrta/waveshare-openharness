# Hank custom pet

An import-ready Harness custom pet based on the supplied Hank superhero illustration.

In Harness Device settings, choose this `hank` folder (or choose `hank_spritesheet.png` directly), preview the state mapping, and apply it to all agents. The standard row mapping is already used:

1. idle
2. running right
3. running left
4. waving
5. jumping
6. failed
7. waiting / asking
8. running / working
9. review / listening

The source pose reference is under `source/`. Regenerate the exact 1536 × 1872 RGBA sheet and preview with:

```sh
python firmware/scripts/hank_pet.py
```

The pet is transferred at runtime and resent after reconnect; it is not compiled into or persisted by the device firmware. The first generated animation uses restrained whole-pose motion so the costume remains consistent on the small display.
