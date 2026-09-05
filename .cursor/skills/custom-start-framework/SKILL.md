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

**数值字段：`extra*` / `*Delta` = 在起始职业默认值上增减，不是存档绝对值。**

| 字段 | 说明 |
|---|---|
| `id` | ASCII perk id，与文件夹名一致 |
| `allowedStartTypes` | `StartType` 编号或 `[]` 表示全部职业（见 `editor/start_types.json`） |
| `items` | 字符串 ID 或 `{ id, charge, water, volumeMl }`；发到**柜台** |
| `removeItems` | 从柜台移除（在 items 之前） |
| `extraCash` / `extraRent` | 额外现金 / 租金 Δ |
| `retailMarkupDelta` | 零售加价 Δ（百分点） |
| `contrabandMarkupDelta` | 违禁品加价 Δ；整数=四级同加，或 `{ low, mid, high, critical }` |
| `baseStoreAttractivenessDelta` | 店铺吸引力 Δ（基线约 250） |
| `unlockedUpgrades` | Wilds Network 升级 ID 列表 |
| `factionReputationDelta` | 派系声望 Δ（非存档 amount 绝对值） |
| `compensateWildFavorForLowerRep` | 默认 true：lower Δ 不改 wildFavor |

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
