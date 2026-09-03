# Custom Start Framework / 自定义开局框架

**v1.0.0** — 开源 Perk 驱动自定义开局框架（Probably Stolen / MelonLoader）。

示例与旧版配置见 [`../example/`](../example/)，**不包含在本框架发布包内**。

---

## 中文

### 安装

1. `CustomStartFramework-1.0.0.dll` → 游戏 `Mods/CustomStartFramework.dll`
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

Open-source **Custom Start Framework**. In-game mod: **CustomStartFramework.dll**.  
Profiles under `UserData/custom-start/{id}/`. Examples ship separately under `example/`.

Pack: `.\scripts\Pack.ps1` from repository root.

See [GUIDE.md](./GUIDE.md) for schema and hooks.

---

## License

MIT — see [LICENSE](../LICENSE).
