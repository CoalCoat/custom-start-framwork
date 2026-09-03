# Custom Start Framework / 自定义开局框架

**v1.0.0** — 自定义开局Perk框架，开源，附带编辑器，可自定义开局。

---

## 中文

### 安装

1. `CustomStartFramework-1.0.0.dll` → 游戏 `Mods/CustomStartFramework.dll`
2. 在 `UserData/custom-start/` 放置自定义开局Perk（用编辑器创建）
3. 新游戏选择对应 Perk 后生效

### 配置目录

```text
UserData/custom-start/<id>/
  profile.json
  icon.png          # 可选
```

Mod 启动时自动扫描并加载全部 profile。

**起始职业**：`allowedStartTypes` 可填任意 `StartType` 编号组合；留空 `[]` 表示全部职业可见。编辑器职业列表见 `editor/start_types.json`。

### 编辑器（含于发布包 editor/）

```bash
python framework/editor/edit_profiles.py -r "游戏/UserData/custom-start"
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

## English

**v1.0.0** — Open-source custom-start perk framework with a bundled editor for creating your own starts.

### Install

1. `CustomStartFramework-1.0.0.dll` → game `Mods/CustomStartFramework.dll`
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

### Editor (bundled in release `editor/`)

```bash
python framework/editor/edit_profiles.py -r "Game/UserData/custom-start"
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

## License

MIT — see [LICENSE](../LICENSE).
