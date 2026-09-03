# Custom Start Framework

**v2.0** — open-source perk-driven custom start framework for **Probably Stolen Playtest** (MelonLoader / IL2CPP).

Author: **Nico's Lab**  
Community: **Nicoの游戏工坊** QQ group `1064193070`

## Layout

```text
framework/              # Framework source (C#), GUIDE, editor
shared/                 # I18n helpers linked by the framework
example/                # Sample profiles
docs/                   # Item ID reference (GAME_GUIDE.md)
scripts/                # Build & pack scripts
dist/release/           # Release output (DLLs gitignored)
```

## Prerequisites

- [MelonLoader](https://melonwiki.xyz/) in **Probably Stolen Playtest**
- [.NET 6 SDK](https://dotnet.microsoft.com/download/dotnet/6.0) to build from source

## Setup (developers)

1. Copy `Directory.Build.props.user.example` → `Directory.Build.props.user`
2. Set `GameDir` to your game folder (must contain `MelonLoader/`)

## Build

```powershell
.\scripts\Build.ps1           # zh + en
.\scripts\Build.ps1 -Language zh
.\scripts\Pack.ps1            # dist/release/ + custom-start-framework.zip
.\scripts\Pack-Example.ps1
```

Output: `dist/release/CustomStartFramework-X.Y.Z.dll` (zh) and `CustomStartFramework.en-X.Y.Z.dll` (en).  
Rename to `CustomStartFramework.dll` in the game `Mods/` folder.

## Install (players)

1. Copy `CustomStartFramework-*.dll` → game `Mods/CustomStartFramework.dll`
2. Add profiles under `UserData/custom-start/{id}/profile.json` (optional `icon.png`)
3. New game → select the perk when `allowedStartTypes` matches your start type

Editor (bundled in release zip or repo):

```bash
python framework/editor/edit_profiles.py -r "path/to/UserData/custom-start"
```

## Documentation

| Doc | Purpose |
|---|---|
| [framework/GUIDE.md](framework/GUIDE.md) | Author guide (schema, hooks) |
| [framework/README.md](framework/README.md) | Quick start (zh/en) |
| [docs/GAME_GUIDE.md](docs/GAME_GUIDE.md) | Item IDs & gameplay fields |
| [example/](example/) | Sample profiles |

## License

MIT — see [LICENSE](LICENSE).

---

# Custom Start Framework（中文）

Probably Stolen 自定义开局 Perk 框架（MelonLoader），开源仓库 **custom-start-framework**。

## 构建

1. 配置 `Directory.Build.props.user` 中的 `GameDir`
2. `.\scripts\Build.ps1`
3. 打包：`.\scripts\Pack.ps1`

## 安装

DLL 放入游戏 `Mods/CustomStartFramework.dll`，配置放在 `UserData/custom-start/{id}/profile.json`。  
详见 [GUIDE.md](framework/GUIDE.md)。

## 许可

MIT — [LICENSE](LICENSE).
