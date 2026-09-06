<h1 align="center">KiCad 10 CI/CD Template — BDM Powertrain</h1>

<p align="center">
  <img alt="BDM Powertrain" src="Logos/SAE Electric Logo.png" height=200>
</p>

This is our Formula SAE team's **KiCad 10** project template. It uses [KiBot](https://github.com/INTI-CMNB/KiBot/tree/master) in a GitHub Actions pipeline to automatically:

- Render top/bottom/angled 3D views of the PCB and embed them in `README.md`,
- Export a STEP 3D model of the board,
- Run whichever of ERC/DRC is applicable for the project's current stage on every push, and fail the pipeline if either finds errors (see [PROJECT STAGES](#project-stages)).

Nothing else is generated automatically (no gerbers, BOM, or PDFs) — this keeps every project's repository small and lets it be browsed directly with [KiCAD-Prism](#using-kicad-prism), a web-based KiCad viewer (see below).

> [!NOTE]
> This template is adapted from [nguyen-v/KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot), trimmed down to the three automations above. See [CREDITS & RESOURCES](#credits--resources) for the original project (fabrication/assembly documents, BoM, changelog sync, KiCost, etc.).

## TABLE OF CONTENTS

- [TABLE OF CONTENTS](#table-of-contents)
- [FEATURES](#features)
- [STARTING A NEW PROJECT FROM THIS TEMPLATE](#starting-a-new-project-from-this-template)
- [USAGE](#usage)
  - [CI/CD Workflow](#cicd-workflow)
  - [Running Locally](#running-locally)
- [PROJECT STAGES](#project-stages)
- [ADDING THE PCB RENDER TO THE SCHEMATIC COVER PAGE](#adding-the-pcb-render-to-the-schematic-cover-page)
- [DIRECTORY STRUCTURE](#directory-structure)
- [USING KICAD-PRISM](#using-kicad-prism)
- [CREDITS & RESOURCES](#credits--resources)

## FEATURES

- **Automated PCB renders**: top, bottom, angled-top and angled-bottom 3D views are exported as standalone PNGs in `Images/`, embedded in the generated `README.md`, and permanently embedded into the schematic's cover page (see [below](#adding-the-pcb-render-to-the-schematic-cover-page)).

- **Automated 3D STEP export** of the board, in `3D/`.

- **ERC/DRC verification** on a separate CI runner: whichever checks are applicable for the current [project stage](#project-stages) run on every push and fail the pipeline if errors are found, without blocking the render/STEP/README job.

- **Automated README.md**: renders and board dimensions are kept up to date automatically on every push.

- **Robust workflow** with two branches (`main` and `dev`) and semantic versioning tags.

- **Can be run locally** via [`kibot_launch.sh`](kibot_launch.sh), for faster iteration than a CI round-trip.

- **[KiCAD-Prism](https://github.com/krishna-swaroop/KiCAD-Prism)-compatible layout**: the `.kicad_pro`, `.kicad_sch` and `.kicad_pcb` files stay at the project root (no custom KiBot folder template moves them), so any project made from this template can be browsed directly in Prism.

## STARTING A NEW PROJECT FROM THIS TEMPLATE

1. Go to your KiCad templates folder.

    **Windows**:

    ```
    cd "C:\Program Files\KiCad\10.0\share\kicad\template"
    ```

    **Linux**:
    ```
    cd ~/.local/share/kicad/10.0/template
    ```

2. Clone this repository into that folder:

    ```
    git clone git@github.com:BDMPowertrain/KiCad_10_Template.git
    ```

3. Install the fonts inside [`kibot_resources/fonts`](kibot_resources/fonts) if not already installed on your system.

   **Linux**:

   ```
   cp -i KiCad_10_Template/kibot_resources/fonts/*.ttf ~/.fonts/
   fc-cache
   ```

4. A custom color theme ([`Altium_Theme.json`](kibot_resources/colors/Altium_Theme.json)) is provided in [`kibot_resources/colors`](kibot_resources/colors). Copy it to your KiCad Themes folder.

    **Windows**:

    `xcopy "KiCad_10_Template\kibot_resources\colors\Altium_Theme.json" "C:\Users\%USERNAME%\AppData\Roaming\kicad\10.0\colors\" /-Y`

    **Linux**:

    `cp -i KiCad_10_Template/kibot_resources/colors/Altium_Theme.json ~/.config/kicad/10.0/colors/`

5. In KiCad, create a new project with:

    **File → New Project From Template** and select `KiCad_10_Template`

> [!CAUTION]
> Under Linux, the `.github` folder from the template needs to be copied to the root of the new project directory, since it is not copied when creating a project from a template in KiCad.

6. Create a new GitHub repository for your project, push it, then create a `dev` branch — this is your working branch, `main` is reserved for reviewed/tagged work:

   ```
   git checkout -b dev
   ```

7. Update the metadata in [`kibot_yaml/kibot_main.yaml`](kibot_yaml/kibot_main.yaml) for your project:
    ```
      # Metadata ===================================================================

      PROJECT_NAME: Project Name
      BOARD_NAME: Board Name

      LOGO: 'Logos/SAE Electric Logo.png'
      GIT_URL: 'https://github.com/BDMPowertrain/<your-project-repo>'

      # Preflight ==================================================================

      CHECK_ZONE_FILLS: false

      # 3D Viewer rotations (in steps) =============================================

      3D_VIEWER_ROT_X: 2
      3D_VIEWER_ROT_Y: -1
      3D_VIEWER_ROT_Z: 1
      3D_VIEWER_ZOOM: -1
      KEY_COLOR: '#00FF00' # background color to remove
    ```

8. The [`kibot_resources/templates/readme.txt`](kibot_resources/templates/readme.txt) file is the template used to generate `README.md` on every push — update the logo/text for your project. **Once you push, this current README will be overwritten by the generated one.**

9. Edit [`*.kicad_dru`](KDT_Hierarchical_KiBot.kicad_dru) according to your manufacturer's design rules. It currently targets PCBWay 6-layer boards (2oz outer / 1oz inner), optimized for lowest cost.

## USAGE

### CI/CD Workflow

Pushing to `main` or `dev` (see [`.github/workflows/ci.yaml`](.github/workflows/ci.yaml)) runs two independent jobs on separate runners:

- **`generate_outputs`** — always runs, regardless of ERC/DRC status. Renders the PCB, exports the STEP file, regenerates `README.md`, and commits/pushes those files back to the branch that triggered the run.
- **`verify_erc_drc`** — runs whichever of ERC/DRC is applicable for the current [project stage](#project-stages) (no outputs are generated or committed). If a check that ran reports errors, this job fails and the overall pipeline is marked failed, but it does not block `generate_outputs`. The ERC/DRC reports are uploaded as a downloadable build artifact (`erc_drc_reports`) on the run's Actions summary page.

This means every push always gets fresh renders/STEP/README, and a red ❌ on the pipeline is your team's signal that ERC or DRC found a real problem to fix — check the `erc_drc_reports` artifact or the job log for details.

- The `kibot_variant` variable in [.github/workflows/ci.yaml](.github/workflows/ci.yaml#L27) controls which components are shown/hidden (DNP) in the 3D render and STEP export, **and** which of ERC/DRC are applicable yet — see [PROJECT STAGES](#project-stages) for exactly what each value does and where to change it:

  ```
    kibot_variant: DRAFT
  ```

- The `kicad_version` variable in [.github/workflows/ci.yaml](.github/workflows/ci.yaml#L30) should match the KiCad version you're using (this template targets 10).

- Schematic text (revision, company, page titles, DNP notes, etc.) is set and maintained manually in KiCad — nothing in this pipeline injects text variables or changelog data into the schematic.

- You should work locally on the `dev` branch. Push your changes; CI will commit updated renders/STEP/README back to `dev`. **Pull those changes back down** before continuing to work, to avoid conflicts — in particular, avoid editing the `.kicad_pro` file locally between a push and pulling the bot's commit back.

- When ready to merge into `main`, open a pull request from `dev`. To tag a release (for example `1.1.1`), push a tag on `main`:

  ```
  git checkout main
  git pull
  git tag 1.1.1
  git push origin 1.1.1
  ```

  This re-runs the pipeline with `kibot_variant` overridden to `RELEASED`. No GitHub Release is created — it just regenerates the renders/STEP/README for that tagged state.

### Running Locally

Optional — only needed if you want faster iteration than a CI round-trip. Install KiBot per the [official documentation](https://kibot.readthedocs.io/en/master/installation.html), then run:

```
./kibot_launch.sh
```

This defaults to the `CHECKED` variant and generates outputs at the project root. Use `-v <VARIANT>` for a different variant (see [PROJECT STAGES](#project-stages) for what each one does), or `./kibot_launch.sh --help` for all options. A custom (non-standard) variant name writes to the `Variants` folder instead.

> [!WARNING]
> Generating outputs locally can conflict with the outputs generated by the remote CI/CD workflow. Pull the latest bot commit before running locally, and resolve any conflicts before pushing.

## PROJECT STAGES

`kibot_variant` (set in [`.github/workflows/ci.yaml`](.github/workflows/ci.yaml#L27), and passed to [`kibot_launch.sh`](kibot_launch.sh) with `-v` for local runs) represents what stage the *whole project* is currently in. Besides controlling DNP visibility in the 3D render/STEP export, it also gates which of ERC/DRC are "applicable" yet — no point failing the pipeline over an incomplete PCB layout while the schematic is still being drafted.

| Stage | Entry criteria | ERC | DRC | What it's for |
|---|---|---|---|---|
| **DRAFT** | Schematic capture started | — | — | Early WIP. Neither check runs; expect the schematic to be incomplete. |
| **PRELIMINARY** | Schematic complete | ✅ runs | — | PCB layout underway. ERC should be clean before entering this stage; DRC is still expected to be dirty. |
| **CHECKED** | Schematic + layout complete | ✅ runs | ✅ runs | Both must be clean. Reviewed by someone other than the author. This is the "ready to send to fab" gate. |
| **RELEASED** | A semver tag pushed to `main` | ✅ runs | ✅ runs | Automatic — `ci.yaml` overrides `kibot_variant` to `RELEASED` on tag push. Renders/STEP at this point should reflect exactly what got manufactured. |

**How to advance a stage:** someone on the team (e.g. the electrical lead) edits `kibot_variant` in `ci.yaml` and pushes — that's the whole mechanism, there's no automatic promotion between DRAFT/PRELIMINARY/CHECKED. `RELEASED` is the one exception: it's set automatically whenever a version tag is pushed to `main` (see [CI/CD Workflow](#cicd-workflow)).

**Where the ERC/DRC gating actually lives** (change all of these together if you want a different policy):
- `.github/workflows/ci.yaml` → `verify_erc_drc` job → the **"Determine which checks are applicable"** step.
- `kibot_launch.sh` → the `case "$variant" in ...)` block right before the command is built.
- The table above, and the `kibot:` comment block in `kibot_yaml/kibot_main.yaml`, should be updated to match so the docs don't drift from the actual behavior.

**Recommendation (not yet set up):** to make "CHECKED means ERC/DRC-clean" an actual enforced gate rather than a convention, add a GitHub branch protection rule on `main` requiring the `verify_erc_drc` status check to pass before a PR can merge. This leaves `dev` free to be red during DRAFT/PRELIMINARY. (Settings → Branches → Branch protection rules, on GitHub.com — a repo admin needs to set this up.)

## ADDING THE PCB RENDER TO THE SCHEMATIC COVER PAGE

KiBot's own `kibot_image_<output>` mechanism (naming a text box `kibot_image_png_3d_viewer_top`, for example) only pastes the generated image into a **printed/exported** schematic (e.g. a schematic PDF or SVG output) — it's a temporary substitution, restored right after that export finishes. Since this template intentionally generates no such documentation output, that mechanism has nothing to hook into on its own.

To get a render that's actually visible when someone opens the schematic in KiCad, the `generate_outputs` CI job runs [`kibot_resources/scripts/embed_render_images.py`](kibot_resources/scripts/embed_render_images.py) right after the renders are generated. It permanently replaces the `kibot_image_png_3d_viewer_top`/`_bottom` placeholder text boxes on the cover page with the actual rendered PNGs (same position/scale math KiBot itself uses), and on later runs updates that same embedded image in place rather than duplicating it — so the cover page always reflects the latest render, no manual step needed.

This step is marked `continue-on-error` in the workflow: if it ever fails (for example, after a future KiCad/KiBot update changes something it depends on), the run shows a warning on that step instead of blocking the renders/STEP/README from being committed. If you ever see that warning, or if you'd rather do it by hand for a one-off render, you can still embed an image manually:

1. Generate the PNGs in [`Images/`](Images) (a CI run, or `./kibot_launch.sh` locally).
2. In KiCad's schematic editor, use **Place → Image** and select the PNG.
3. Position/scale it over the existing placeholder text box (or the previously embedded image), then delete the text box if it's still there.
4. Commit the updated `.kicad_sch`.

## DIRECTORY STRUCTURE
The following directory structure is used in the template. Folders marked as 'optional' are not crucial for KiBot to work. Other folders are generated automatically during a KiBot run.

```
├─ 3D                 # STEP 3D model export
├─ Images             # Pictures and renders
│
├─ kibot_resources
│  ├─ colors          # Color theme for KiCad
│  ├─ fonts           # Fonts used in the project
│  ├─ scripts         # External scripts used with KiBot
│  └─ templates       # Templates for KiBot generated reports
│
├─ kibot_yaml         # KiBot YAML config files
├─ Logos              # Logos (optional)
├─ Reports            # Reports for ERC/DRC
├─ Templates          # Title block templates
│
└─ Variants           # Outputs for custom (non-standard) variants (optional)
```

The project's `.kicad_pro`, `.kicad_sch`, and `.kicad_pcb` files stay at the repository root — nothing in this template moves them into a subfolder, which is what keeps the layout compatible with Prism (below).

## USING KICAD-PRISM

[KiCAD-Prism](https://github.com/krishna-swaroop/KiCAD-Prism) is a web-based viewer that can browse a KiCad project directly from its GitHub repository, without anyone needing KiCad installed locally. Because this template keeps the core project files at the repository root, any project created from it can be pointed at Prism as-is.

We'll expand this section with our team's specific setup/workflow for Prism later — for now, see the [KiCAD-Prism repository](https://github.com/krishna-swaroop/KiCAD-Prism) for setup instructions.

## CREDITS & RESOURCES

Adapted from [nguyen-v/KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot) by [@nguyen-v](https://github.com/nguyen-v) — the original also includes fabrication/assembly documents, BoM, KiCost integration, and changelog sync, in case a future project needs those. Built on [KiBot](https://github.com/INTI-CMNB/KiBot/tree/master) by [@set-soft](https://github.com/set-soft).

- [KiBot Documentation](https://kibot.readthedocs.io/en/latest/)
- [KiCAD-Prism](https://github.com/krishna-swaroop/KiCAD-Prism)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
