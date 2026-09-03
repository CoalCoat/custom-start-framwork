---
name: custom-start-framework
description: >-
  Custom Start Framework for Probably Stolen (MelonLoader / IL2CPP).
  Perk-driven custom starts via UserData/custom-start/profile.json.
  In-game mod: CustomStartFramework.dll.
---

# Custom Start Framework

## 先读这些

1. [framework/GUIDE.md](../../../framework/GUIDE.md) — 框架作者指南（v1.0.0）
2. [framework/README.md](../../../framework/README.md) — 安装与快速上手
3. [docs/GAME_GUIDE.md](../../../docs/GAME_GUIDE.md) — 物品 ID（写 loadout 时查）

## 框架定位

仓库 **custom-start-framework**，MelonLoader 插件 **CustomStartFramework.dll**。  
扫描 `UserData/custom-start/{id}/profile.json` 注册为开局 Perk。

## 本地构建

```powershell
.\scripts\Build.ps1
.\scripts\Pack.ps1
```

## profile.json 要点

| 字段 | 说明 |
|---|---|
| `id` | ASCII perk id，与文件夹名一致 |
| `allowedStartTypes` | `StartType` 编号或 `[]` 表示全部职业（见 `editor/start_types.json`） |
| `items` | 字符串 ID 或 `{ id, charge, water, volumeMl }` |

## 编辑器

```bash
python framework/editor/edit_profiles.py -r UserData/custom-start
```

## 验证清单

- [ ] `MelonLoader/Latest.log` 无 Patch 失败
- [ ] 扫描 profile 数量正确
- [ ] Perk 仅在 `allowedStartTypes` 下可见

## 进一步细节

- [GUIDE.md](../../../framework/GUIDE.md)
- [GAME_GUIDE.md](../../../docs/GAME_GUIDE.md)
