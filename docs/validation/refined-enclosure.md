# Refined Rev B enclosure — 2026-10-30

The first model met fit-envelope checks but missed the reference design's finish: the front screws, interrupted bezel, large access windows and ruled loft were conspicuous. Rev B replaces those with an analytic spherical shell, continuous rounded front rim, small service bores and a rounded top USB tunnel behind the face. The stock protective case and supplied speaker are retained.

The underside cartridge now supports both the cased display and a horizontal speaker. Its two external countersunk screws are confined to the underside; two additional screws retain the internal speaker strap. The former separate bezel/cradle/cover parts are superseded. Firmware and the saved rotation setting are unchanged; use Top.

## Completed CAD checks

- 6 printable pieces: three main parts and three fit coupons. Each is one valid CAD solid and one watertight, consistently wound connected STL mesh.
- 15 pairwise checks across printed parts and simplified case, speaker and compact-plug envelopes: maximum overlapping material 0.000000 mm³.
- Full 360° front-rim band: missing material 0.000000 mm³. This checks an actual closed band, not an image that conceals a notch.
- Cartridge, strap and case containment: no calculated protrusion outside the analytic exterior envelope.
- Case insertion: 245 sampled placements along a two-stage path, with a 0.1 mm case-envelope margin and at most 0.2 mm between samples; maximum overlap 0.000000 mm³. Entry first brings the tilted module toward the sphere center from underneath, then toward the front lip along the display normal.
- Cartridge vertical insertion: 9 sampled offsets; maximum overlap 0.000000 mm³. These are sampled checks, not an exhaustive tolerance/assembly simulation.
- Visual review covers the assembled shell, empty/plugged USB tunnel, internal cartridge and underside. Images are rendered from the actual exported CAD meshes.

The analytic shell avoids the original reference STEP's invalid offset/trim surfaces and the first remodel's faceted ruled loft. The original STEP is retained for provenance; this is not an exact copy of its surfaces.

## Still requires physical acceptance

The simplified case does not model every rear connector, wire or protrusion. Port centers were inferred from the vendor drawing where dimensions were absent. Print the 11 mm-deep USB-rim coupon with the actual cased unit and cable before the complete shell. The assumed compact plug body is 13.4 × 6.4 mm in a 14 × 7 mm rounded slot. Also check case/speaker coupons, screw engagement, rim/glass loading, actual assembly access, service holes, sound and FDM strength/finish. No full enclosure has been printed or fitted yet.

Build and mesh logs are separate from this physical acceptance. The firmware's already-confirmed display/touch rotation is not evidence that the new enclosure fits.
