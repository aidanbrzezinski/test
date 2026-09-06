<p align="center" width="100%">
  <img alt="Logo" width="33%" src="Logos/dummy_logo.svg">
</p>

<h1 align="center">Board Name</h1>

<p align="center" width="100%">
  <a href="/actions/workflows/ci.yaml">
    <img alt="CI Badge" src="/actions/workflows/ci.yaml/badge.svg?branch=">
  </a>
</p>

<p align="center">
  <img alt="3D Top" src="Images/Test-top.png" width="45%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="3D Bottom" src="Images/Test-bottom.png" width="45%">
</p>

***

<p align="center">
  <img alt="3D Top Angled" src="Images/Test-angled_top.png" width="45%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="3D Bottom Angled" src="Images/Test-angled_bottom.png" width="45%">
</p>

***

## SPECIFICATIONS

| Parameter | Value |
| --- | --- |
| Dimensions | 100.0 × 50.0 mm |

***

## DIRECTORY STRUCTURE

    .
    ├─ 3D                 # STEP 3D model export
    ├─ Computations       # Misc calculations
    ├─ Images             # Pictures and renders
    │
    ├─ kibot_resources    # External resources for KiBot
    │  ├─ colors          # Color theme for KiCad
    │  ├─ fonts           # Fonts used in the project
    │  ├─ scripts         # External scripts used with KiBot
    │  └─ templates       # Templates for KiBot generated reports
    │
    ├─ kibot_yaml         # KiBot YAML config files
    │
    ├─ lib                # KiCad footprint and symbol libraries
    │  ├─ 3d_models       # Component 3D models
    │  ├─ lib_fp          # Footprint libraries
    │  └─ lib_sym         # Symbol libraries
    │
    ├─ Logos              # Logos
    ├─ Reports            # Reports for ERC/DRC
    ├─ Templates          # Title block templates
    │
    └─ Variants           # Outputs for custom (non-standard) variants
