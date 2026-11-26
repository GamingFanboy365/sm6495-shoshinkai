# showfloor
![showfloorlogo](https://github.com/user-attachments/assets/255078c5-d31c-4284-a720-f1f2ddcefd4f)

## Introduction

**showfloor** is a recreation of the Shoshinkai 1995 demo of Super Mario 64, based on [The Preservation Project](https://github.com/Sunlitspace542/tpp-mirror) (TPP). It aims to continue TPP's legacy with greater accuracy to the source material.

## Compiling

The build process is the same as the [SM64 Decomp's](https://github.com/n64decomp/sm64).
Follow their [README](https://github.com/n64decomp/sm64/blob/master/README.md#installation) for setup steps and prerequisites (dependencies, baserom, etc).

Clone and build:

```sh
git clone https://github.com/96flashbacks/showfloor.git
cd showfloor
make
```
## Nintendo 3DS port

showfloor can also be built as a Nintendo 3DS homebrew application (`.3dsx`), using
the [sm64_3ds](https://github.com/sm64-port/sm64_3ds) renderer/audio/input backends on top of
[sm64-port](https://github.com/sm64-port/sm64-port). The 3DS build uses the English translation by default.

Requirements:

- [devkitPro](https://devkitpro.org/wiki/Getting_Started) with the `3ds-dev` group (devkitARM, libctru, citro3d, 3dstools, picasso)
- `baserom.jp.z64` as for the N64 build, plus a Super Mario 64 (USA) ROM at `baserom.us.z64`
  for the English font (not needed with `TEXT_LANG=jp`)

```sh
export DEVKITPRO=/opt/devkitpro
make TARGET_N3DS=1
```

The result is `build/jp_3ds_en/sm64.jp.3dsx`. Copy it to the `/3ds/` folder of your SD card and start it
from the Homebrew Launcher. The port targets the New Nintendo 3DS family (New 3DS, New 3DS XL, New 2DS XL).

Sound requires the DSP firmware dump at `/3ds/dspfirm.cdc` on the SD card, like all homebrew that uses
libctru's audio. Most custom firmware setups already have it; otherwise run
[DSP1](https://github.com/zoogie/DSP1) once to create it. Without it the game runs silently.

Options:

- `TEXT_LANG=jp` - keep the original Japanese text (output in `build/jp_3ds/`)
- `N3DS_ANTIALIASING=0` - render at native resolution (faster on an Old 3DS; default `1`)
- `N3DS_WIDE=1` - use the 800px wide top-screen mode (sharper; real New 3DS/3DS XL/2DS XL only, not Old 2DS or emulators)
- `WIDESCREEN=0` - render in 4:3 instead of widescreen

Controls: Circle Pad = Control Stick, A/B = A/B, R or ZL = Z, L or ZR = R (area map), C-Stick or D-Pad = C Buttons, START = START.

## English translation

`TEXT_LANG=en` also works for N64 builds (`make TEXT_LANG=en`, output in `build/jp_en/`). The English font is
read from `baserom.us.z64` at build time (`tools/extract_en_font.py`), and the translated text lives in `text/en/`.

## Patches

If you just want to play the game, go to the Releases section and download a patch from Continuous Pre-releases for the newest build. A Japanese Super Mario 64 ROM is required for patching. Patches labeled with "HLE" run without issue on real hardware and most emulators. Patches without the "HLE" label use code from the U64 Aging Cartridge and only work on accurate emulators or real hardware.

### RSP Microcode

This project uses the same `GRUCODE` build variable as the SM64 Decomp, but with different options.

Default is `f3d_102695`.

- `f3d_102695`: gspFast3D from Ultra 64 OS release 102695 (U64 Aging Cartridge). Not HLE-compatible.
- `f3d_20E`: gspFast3D from OS 2.0E (bbgames' ostrees). HLE-compatible.

Build with a specific microcode:

```sh
make GRUCODE=f3d_20E
```

## Q&A

**Can I use this as a base for another project?**
- Yes, but not recommended, as many vanilla assets were removed or edited, so you'd need to re-add them.

**Can I contribute to this repository?**
- Contributions are welcome. Please open an issue to report problems or suggest improvements, and feel free to submit pull requests.

For more questions, join our [Discord server](https://discord.gg/ynabeAS4eD).

## Credits

#### Main Programming
- stalechilibeans
- 1up Guy

#### Additional Programming
- Phil564
- klorfmorf/Fluvian
- diesel64
- penguinlambz
- ummheather
- iProgramInCpp
- crackaddictkonata

#### Assets
- Scraps
- ummheather
- 1up Guy
- stalechilibeans
- `K-Dubs΄
- toonjoey
- Lurondor
- icehotlemonade
- Neverax
- Diamond Hero
- Holo
- Mr. Hatsman/sonicdude143

#### Music & Audio
- skibidigurt
- toonjoey
- RetroDev
- emlimate
- XKoop7321
- `K-Dubs΄
- 1up Guy
- stalechilibeans
- ummheather

#### Research & Playtesting
- Scraps
- Sleekflash16
- toonjoey
- Xiartic
- Lurondor
- Zucchino
- duskewl/jadu
- `K-Dubs΄

#### Miscellaneous Help
- pxan_valleys
- Xiartic
- Woohale54
- RM05
- timmy6259
- Zucchino
- Xerox
  
#### Special Thanks
- na0micakes
- toonjoey
- Matsilagi
- lunr
- CharD
- RM05
- icehotlemonade
- Tony (Hard4Games)
- aaali

## Original 'The Preservation Project' Credits

#### Programming
- klorfmorf/Fluvian
- Marionova
  
#### Assets
- EmmaNerd
- CDi-Fails
- Lurondor
- Robichu
- Zucchino
- Holo

#### Research & Playtesting
- Xiartic
- lunr
  
#### Original 'The Preservation Project' GitHub Contributors
- 1up Guy
- Guestpiki
- iProgramInCpp
- Toru the Red Fox
- CreamDream
- Diamond Hero

### Tools & Resources
- [Fast64](https://github.com/Fast-64/fast64)
- [SM64 Decomp](https://github.com/n64decomp/sm64)
- [64History’s Archives](https://archive.org/details/sm64-beta-content)
- [Dudaw’s Archives](https://archive.org/details/sm64brp_src_abandoned)
- [Roovahlees’s Archives](https://archive.org/details/@roovahlees)
- [VGM & Other Instrument Sources Spreadsheet](https://docs.google.com/spreadsheets/d/1JJBlHHDc65fhZmKUGLrDTLCm6rfUU83-kbuD8Y0zU0o/edit?gid=2047725819#gid=2047725819)
- [Retro Aesthetics’ Mario Series Matches](https://retroaesthetics.net/mario-series-matches/)
- [TCRF’s Page](https://tcrf.net/Prerelease:Super_Mario_64_(Nintendo_64)/Shoshinkai_1995_Demo)
- [Original TPP Source Code](https://github.com/Sunlitspace542/tpp-mirror)
