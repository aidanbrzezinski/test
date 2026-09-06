<h1 align="center">KiCad 8/9 Template for CI/CD with KiBot</h1>

<p align="center">
  <a href=https://www.kicad.org/>
    <img alt="Light" src="https://gitlab.com/uploads/-/system/group/avatar/6593371/kicadlogo.png" height=200>
  </a>
&nbsp; &nbsp; &nbsp; &nbsp;
  <a href=https://kibot.readthedocs.io/en/latest/>
    <img alt="Dark" src="https://raw.githubusercontent.com/INTI-CMNB/KiBot/dev/docs/images/kibot_740x400_logo.png" height=200>
  </a>
</p>

A **KiCad 8/9** template for **automated**, professional documentation generation with **Continuous Integration and Continuous Development** (CI/CD) using [KiBot](https://github.com/INTI-CMNB/KiBot/tree/master).

A video tutorial for setting up this template is available [here](https://www.youtube.com/watch?v=63R6Wnx44uY).

An example project using this template can be found [here](https://github.com/nguyen-v/amulet_controller_kibot/tree/master).

> [!NOTE]
> This file will be overridden by a KiBot run.

## TABLE OF CONTENTS

- [TABLE OF CONTENTS](#table-of-contents)
- [FEATURES](#features)
- [GETTING STARTED](#getting-started)
- [USAGE](#usage)
  - [CI/CD Workflow and Semantic Versioning](#cicd-workflow-and-semantic-versioning)
  - [Running Locally](#running-locally)
- [PROJECT CONVERSION GUIDE](#project-conversion-guide)
  - [Folders](#folders)
  - [Schematic](#schematic)
- [DIRECTORY STRUCTURE](#directory-structure)
- [CREDITS](#credits)
- [RESOURCES](#resources)
- [CONTRIBUTING](#contributing)

## FEATURES

- **Automated PCB renders**: top and bottom 3D views are injected directly into the schematic and README.md, with angled top/bottom views exported alongside them.

- **Automated 3D STEP export** of the board.

- **ERC/DRC verification**: both checks run on every push and fail the pipeline if errors are found.

- **Automated README.md**: renders and board dimensions are kept up to date automatically.

- **Robust workflow** with two branches (`main` and `dev`) and semantic versioning

- **Can be run locally** with Docker

- **Prism-compatible layout**: the `.kicad_pro`, `.kicad_sch` and `.kicad_pcb` files stay at the project root, so the repository can be parsed by web viewers such as [KiCAD-Prism](https://github.com/krishna-swaroop/KiCAD-Prism).

## GETTING STARTED

1. Go to your KiCad templates folder
   
    **Windows**:

    ```
    cd "C:\Program Files\KiCad\8.0\share\kicad\template"
    ```

    **Linux**:
    ```
    cd ~/.local/share/kicad/8.0/template
    ```

2. Clone the repository

    ```
    git clone https://github.com/nguyen-v/KDT_Hierarchical_KiBot.git
    ```

3. Install the fonts inside of [`kibot_resources/fonts`](kibot_resources/fonts) if not already installed on the system.

   **Linux**:

   ```
   cp -i KDT_Hierarchical_KiBot/kibot_resources/fonts/*.ttf ~/.fonts/
   fc-cache
   ```

5. A custom color theme ([`Altium_Theme.json`](kibot_resources/colors/Altium_Theme.json)) is also provided in [`kibot_resources/colors`](kibot_resources/colors).
You should move this file to your KiCad Themes folder.

    **Windows**:

    `xcopy "KDT_Hierarchical_KiBot\kibot_resources\colors\Altium_Theme.json" "C:\Users\%USERNAME%\AppData\Roaming\kicad\8.0\colors\" /-Y`

    **Linux**:

    `cp -i KDT_Hierarchical_KiBot/kibot_resources/colors/Altium_Theme.json ~/.config/kicad/8.0/colors/`

> [!NOTE]
> In the steps above, replace ```8.0``` with ```9.0``` for KiCad 9

5. Create a new project with:

    **File → New Project From Template** and select `KDT_Hierarchical_KiBot`

> [!CAUTION]
> Under Linux, the ```.github``` folder from the template needs to be copied at the root of the project directory, as it is not copied when creating a project from a template in KiCad.

6. Create a new `dev` branch. This will be the working branch. 
   
   ```
   git checkout -b dev
   ```
   
7. Modify the following fields in [`kibot_main.yaml`](kibot_yaml/kibot_main.yaml) according to your project:
    ```
      # Metadata ===================================================================

      PROJECT_NAME: Project Name
      BOARD_NAME: Board Name

      LOGO: 'Logos/dummy_logo.png'
      GIT_URL: 'https://github.com/nguyen-v/KDT_Hierarchical_KiBot'

      # Preflight ==================================================================

      CHECK_ZONE_FILLS: false

      # 3D Viewer rotations (in steps) =============================================

      3D_VIEWER_ROT_X: 2
      3D_VIEWER_ROT_Y: -1
      3D_VIEWER_ROT_Z: 1
      3D_VIEWER_ZOOM: -1
      KEY_COLOR: '#00FF00' # background color to remove
    ```

8. The [`kibot_resources/templates/readme.txt`](kibot_resources/templates/readme.txt) file should also be modified according to your project. It is the template used to generate `README.md`.

9. Edit the [`*.kicad_dru`](KDT_Hierarchical_KiBot.kicad_dru) if necessary according to your design rules. Right now, it has been set for PCBWay 6-layer PCBs with 2oz outer 1oz inner, focusing on lowest cost.

## USAGE

### CI/CD Workflow and Semantic Versioning

This template is meant to be used in a CI/CD environment on GitHub. The workflow is as follows:

- Any custom font used in the project must be added to the [`kibot_resources/fonts`](kibot_resources/fonts) folder.

> [!NOTE]
> KiCad 9 allows for fonts to be embedded in the schematic. However, it is still good practice to add the fonts in the folder mentioned.

- There are two branches, a `main` and a `dev` branch. The `dev` branch is the working branch. The `main` should only be used for pull requests and releases.

- Schematic text (revision, company, page titles, etc.) is managed manually in KiCad. KiBot no longer injects any text variables or changelog data into the schematic.

- The `variant` variable in [.github/workflows/ci.yaml](.github/workflows/ci.yaml#L21) should be selected according to the project progress. It only affects which components are shown/hidden (DNP) in the 3D render and STEP export.

  ```
    # DRAFT: only schematic in progress
    # PRELIMINARY: PCB layout in progress
    # CHECKED: schematic and PCB finalized
    # RELEASED: same as CHECKED, automatically selected when pushing a tag to main

    kibot_variant: CHECKED
  ```

  ERC and DRC always run, regardless of variant, and will fail the pipeline if errors are found.

- The `kicad_version` variable in [.github/workflows/ci.yaml](.github/workflows/ci.yaml#L24) should be selected according to the desired KiCad version.

- You should work locally on the `dev` branch. When a change is made, the changes should be pushed to GitHub which will trigger the KiBot workflow. The generated PCB renders, STEP file, and README.md will be committed and pushed back to the repository.

- After a successful KiBot run on the remote repository, you should pull back the changes into your local repository.

- To avoid conflicts, you should avoid modifying the `.kicad_pro` file locally before pulling from the remote (after the completion of a KiBot run). Otherwise, you will need to solve merge conflicts when pulling the file.

- When ready for a release, you should open a pull request and merge the changes into main. Currently the workflow is set **not to trigger on pull requests**, as we assume the changes coming from `dev` are up-to-date.

- To tag a release, push a tag on the `main` branch with the version number (for example `x.x.x = 1.1.1`):

  ```
  git checkout main
  git pull
  git tag x.x.x
  git push origin x.x.x
  ```

  This will start a KiBot run with the variant set as `RELEASED`. It only regenerates the renders, STEP file, and README.md — no GitHub Release is created.

- After a tag push, you will need to update your `main` branch to be up-to-date with the remote:

  ```
  git pull
  ```

  And you will also need to rebase your `dev` branch to the `main` branch:

  ```
  git checkout dev
  git rebase main
  ```

> [!NOTE]
> You are free to modify the [.github/workflows/ci.yaml](.github/workflows/ci.yaml) file to suit your workflow needs.

***

### Running Locally

KiBot can be installed if you want to run some of the scripts locally. If you only plan to use it in a CI/CD workflow, this step can be skipped.
Installation steps can be found on the [official documentation](https://kibot.readthedocs.io/en/master/installation.html). 
The easiest way to install KiBot if custom development is not required is with dockers.

1.  Install **and run** [Docker Desktop](https://docs.docker.com/desktop/)
  
2.  Run the script `docker_kibot_windows.bat` or `docker_kibot_linux.sh` depending on your platform in [`kibot_resources/scripts`](kibot_resources/scripts). Currently tested on Windows and WSL2. This should pull and start a docker running the `dev` branch of KiBot. You should have access to your local files.

***
**KiCad 8**

  Windows:

  ```
  .\docker_kibot_windows.bat
  ```

  Linux:

  ```
  ./docker_kibot_linux.sh
  ```

***
**KiCad 9**

  Windows:

  ```
  .\docker_kibot_windows.bat -v 9
  ```

  Linux:

  ```
  ./docker_kibot_linux.sh -v 9
  ```
  ***

Once in the docker, you can use the [`kibot_launch.sh`](kibot_launch.sh) script to generate and visualize outputs.

```
./kibot_launch.sh
```

You can get more information about the usage with

```
./kibot_launch.sh --help
```

When running the script with no arguments, it will default to the `CHECKED` variant and generate all outputs (PCB renders, STEP export, ERC/DRC reports, README.md). A variant can be set with the `-v` flag. If a custom variant is used (i.e. other than the default variants `DRAFT`, `PRELIMINARY`, `CHECKED`, `RELEASED`), the outputs will be generated in the `Variants` folder.

The variant only affects which components are shown/hidden (DNP) in the 3D render and STEP export. ERC and DRC always run and will fail the run if errors are found, regardless of variant.

> [!WARNING]
> When generating outputs locally, it could conflict with the outputs generated by the remote CI/CD workflow. In this case, you should decide how to resolve the conflicts.

## PROJECT CONVERSION GUIDE

This section will describe the necessary steps to convert an existing project to work with this template. This will also give more insights into how the template works in general. For more information, you should refer to the template.

***

### Folders

You should keep the folder structure as defined in [DIRECTORY STRUCTURE](#directory-structure). The folders marked as optional are not mandatory for the project to work, as long as the relevant file paths are correct (e.g. logos). You should then go through the same steps as in [GETTING STARTED](#getting-started) and [USAGE](#usage).

### Schematic

You should select [`Templates/KDT_Template_GIT.kicad_wks`](Templates/KDT_Template_GIT.kicad_wks) as your Drawing Sheet in:

**File → Page Settings → Drawing Sheet**

The `Revision` and `Company` fields, page titles, and any other schematic text (e.g. `Variant`, release date) are set and maintained manually in KiCad — KiBot no longer injects any text variables into the schematic.

<p align="center">
  <img alt="Drawing Sheet" src="https://github.com/user-attachments/assets/311f4e13-cdb9-45cb-9fcf-1a88f8432416">
</p>

To get 3D pictures of the PCB in the schematic, you can create text boxes with the desired size, with the following names: `kibot_image_png_3d_viewer_top` and `kibot_image_png_3d_viewer_bottom`. These are the "dedicated spots" already present on the cover page of this template, and are filled in automatically by every KiBot run.

<p align="center">
  <img alt="kibot_image_png_3d_viewer_top, kibot_image_png_3d_viewer_bottom" src="https://github.com/user-attachments/assets/2f7f23fa-e233-4a54-b656-860f69a33d36">
</p>

> You can add any image generated by a KiBot output by changing the name to `kibot_image_<output_name>` (e.g. `kibot_image_png_3d_viewer_angled_top`).

## DIRECTORY STRUCTURE
The following directory structure is used in the template. Folders marked as 'optional' are not crucial for KiBot to work. Other folders will be generated automatically during a KiBot run.

```
├─ 3D                 # STEP 3D model export
├─ Computations       # Misc calculations (optional)
├─ Images             # Pictures and renders
│
├─ kibot_resources
│  ├─ colors          # Color theme for KiCad
│  ├─ fonts           # Fonts used in the project
│  ├─ scripts         # External scripts used with KiBot
│  └─ templates       # Templates for KiBot generated reports
│
├─ kibot_yaml         # KiBot YAML config files
│
├─ lib                # Footprint and symbol libraries (optional)
│  ├─ 3d_models       # Component 3D models
│  ├─ lib_fp          # Footprint libraries
│  └─ lib_sym         # Symbol libraries
│
├─ Logos              # Logos (optional)
├─ Reports            # Reports for ERC/DRC
├─ Templates          # Title block templates
│
└─ Variants           # Outputs for custom (non-standard) variants (optional)
```

## CREDITS

[@set-soft](https://github.com/set-soft) for his amazing work on [KiBot](https://github.com/INTI-CMNB/KiBot/tree/master). Check out the [documentation](https://kibot.readthedocs.io/en/latest/) for more!

## RESOURCES

- [Video Tutorial for this template](https://www.youtube.com/watch?v=63R6Wnx44uY)

- [Example project (from the video tutorial)](https://github.com/nguyen-v/KiBot_Project_Test)

- [Example project (Amulet)](https://github.com/nguyen-v/amulet_controller_kibot/tree/master)

- [(Outdated) Best practices and tips for good schematics](https://www.youtube.com/watch?v=_ZjyeltLMAg)

- [GitHub Actions Documentation](https://docs.github.com/en/actions)

- [KiBot Documentation](https://kibot.readthedocs.io/en/latest/)

- [KiBot Repository](https://github.com/INTI-CMNB/KiBot)

- [KiCAD-Prism (repository viewer)](https://github.com/krishna-swaroop/KiCAD-Prism)

## CONTRIBUTING

Feel free to open a pull request if you have any cool features to add!
