---
name: readme-and-release
description: Write a README that gets a stranger running your app in two minutes, generate a changelog from git commits grouped by type, and publish a GitHub release with the exe or installer attached. Use for "write a README", "add screenshots", "changelog", "release notes", "tag a release", "gh release create", "publish my app on GitHub".
---

# README and release

Two files decide whether anyone uses a small utility: the README (what it is, how to run it) and the release (a download that works without building anything). A **changelog** is the list of what changed between versions; writing it by hand is where it goes wrong, so generate it from commit subjects. A **release** is a git tag plus notes plus attached files (exe, installer, zip) on GitHub.

## Pattern

**1. README.md** at the repo root, in this order. Everything above "Install" must fit on one screen.

````markdown
# FanTray

Tray app that reads and sets PC fan speeds through an Arduino. Windows 11, .NET 8.

![FanTray menu and settings window](docs/screenshot.png)

## Install
1. Download `FanTray-Setup-1.2.0.exe` from [Releases](../../releases/latest).
2. Run it. Windows may warn about an unknown publisher; the file is unsigned (SHA-256 is in the release notes).
3. Plug in the Arduino, right-click the tray icon, choose Settings, pick the COM port.

## Usage
- Left-click the icon: settings. Right-click: Exit.
- Fan speed is 0-100 %. The app remembers it in `%APPDATA%\FanTray\settings.json`.

## Build from source
```powershell
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```
Needs the .NET 8 SDK. The Arduino sketch is in `firmware/fanctl/`.

## Hardware
Arduino Uno, two 4-pin fans on pins 9 and 10, protocol in `docs/protocol.md`.

## License
MIT
````

Screenshots: PNG about 800 px wide in `docs/`, relative path, real data, no personal paths or serial numbers. A short GIF shows a tray menu better than a still. Keep the `Install` steps true to what a user without Visual Studio has.

**2. Changelog.** Write commit subjects as `type(scope): what` (`feat(serial): reconnect after unplug`, `fix: crash on empty port`). Then:

```bash
python <skill-dir>/scripts/changelog.py --since v1.1.0 --version v1.2.0 --output CHANGELOG.md
```

Run it from the project folder; `--repo <path>` points it at another one. Output is Markdown grouped by type, newest first within each group, with commit links when `origin` is on GitHub:

```markdown
## v1.2.0 (2026-10-22)

### Features
- **serial:** reconnect after unplug ([a1b2c3d](https://github.com/you/fantray/commit/a1b2c3d...))

### Bug fixes
- crash on empty port ([e4f5a6b](...))
```

`--since` takes a tag or any commit. Without it the script starts at the latest tag, or at the first commit when there are no tags. It exits with the list of recent tags when the name is wrong.

**3. Release.** After the tag's commits are pushed and `dist/` holds the files:

```bash
gh release create v1.2.0 --notes-file CHANGELOG.md dist/*
```

This creates the tag `v1.2.0` on GitHub if it does not exist, publishes the release with `CHANGELOG.md` as its notes, and uploads every file in `dist/`. Run `gh auth login` once beforehand. This skill documents the command only: it is public and hard to take back, so show the user the notes and the file list and wait for a clear yes before running it.

## Variations

- **Review first**: add `--draft` and publish from the GitHub page, or `--prerelease` for a beta. `--title "FanTray 1.2.0"` overrides the default title.
- **PowerShell does not expand `dist/*`** for native programs. List files (`dist\FanTray-Setup-1.2.0.exe dist\FanTray-1.2.0.zip`) or pass `(Get-ChildItem dist -File).FullName`.
- **Checksums for the notes**: `Get-FileHash dist\*.exe -Algorithm SHA256 | Format-List Path, Hash`, pasted under the changelog block; users can verify an unsigned file.
- **Cumulative history**: the script writes only the new block, so `CHANGELOG.md` above is this release's notes. Keep a full `HISTORY.md` by prepending each block to it.
- **First release**: no tag yet, so `python <skill-dir>/scripts/changelog.py --all --version v1.0.0 --output CHANGELOG.md`. `--strict` accepts only `type:` prefixes; `--no-links` prints plain hashes.

## Pitfalls

- **Push first.** The release attaches to what GitHub has. Unpushed commits are missing from the tag; use `--target main` if the tag does not exist yet.
- **Vague commits make a vague changelog.** "WIP" and "stuff" land under "Other changes". Reword with `git rebase` before releasing, or edit the Markdown by hand.
- **Version drift**: the tag, the `.csproj` `<Version>`, the installer `AppVersion` and the file names must agree. Bump all of them in one commit.
- **Do not commit `dist/` or build output.** Add it to `.gitignore`; attach files to the release instead.
- **Test the asset, not the build folder.** Download the exe from the draft release on a clean machine or VM before announcing.
- **Unsigned exes** trigger SmartScreen. Say so in the README; do not tell users to disable Defender.

## Related skills

- `windows-tray-app` for building the exe and installer that go into `dist/`
- `arduino-serial` for the protocol document and firmware folder the README links to
