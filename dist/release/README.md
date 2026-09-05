# Custom Start Framework / 自定义开局框架

**v1.0.1** — Open-source custom-start perk framework; download the editor from [GitHub Releases](https://github.com/nql1314/custom-start-framwork/releases).

**v1.0.1** — 开源自定义开局 Perk 框架；编辑器请从 [GitHub Releases](https://github.com/nql1314/custom-start-framwork/releases) 下载。

Examples ship separately — see [`../example/`](../example/), **not included in this release**.  
示例与旧版配置见 [`../example/`](../example/)，**不包含在本框架发布包内**。

---

GitHub: https://github.com/nql1314/custom-start-framwork

## English

### Install

1. `CustomStartFramework-1.0.1.dll` → game `Mods/CustomStartFramework.dll`
2. Place custom-start perks under `UserData/custom-start/` (create with the editor)
3. Start a new game and select the perk to apply

### Profile directory

```text
UserData/custom-start/<id>/
  profile.json
  icon.png          # optional
```

The mod scans and loads all profiles on startup.

**Start types**: `allowedStartTypes` accepts any combination of `StartType` IDs; leave as `[]` to show the perk for all start types. See `editor/start_types.json` in the editor for the full list.

### Editor

Download: [GitHub Releases](https://github.com/nql1314/custom-start-framwork/releases) — extract the `editor/` package, then run:

```bash
python edit_profiles.py -r "Game/UserData/custom-start"
```

### Pack

```powershell
.\scripts\Pack.ps1
```

Output: `dist/release/` and `dist/custom-start-framework.zip`

### Documentation

- [GUIDE.md](./GUIDE.md) — Mod author guide (zh/en)
- [../example/](../example/) — Sample profiles such as scavenger start (packaged separately)

---

## 中文

### 安装

1. `CustomStartFramework-1.0.1.dll` → 游戏 `Mods/CustomStartFramework.dll`
2. 在 `UserData/custom-start/{id}/profile.json` 放置配置（或用编辑器创建）
3. 新游戏选择对应 Perk 后生效

### 配置目录

```text
UserData/custom-start/<id>/
  profile.json
  icon.png          # 可选
```

Mod 启动时自动扫描并加载全部 profile。

**起始职业**：`allowedStartTypes` 可填任意 `StartType` 编号组合；留空 `[]` 表示全部职业可见。编辑器职业列表见 `editor/start_types.json`。

### 编辑器

下载：[GitHub Releases](https://github.com/nql1314/custom-start-framwork/releases) — 解压 `editor/` 包后运行：

```bash
python edit_profiles.py -r "游戏/UserData/custom-start"
```

### 打包

```powershell
.\scripts\Pack.ps1
```

输出：`dist/release/` 与 `dist/custom-start-framework.zip`

### 文档

- [GUIDE.md](./GUIDE.md) — Mod 作者指南（中英）
- [../example/](../example/) — 拾荒开局等示例（独立打包）

---

## License

MIT — see [LICENSE](../LICENSE).
