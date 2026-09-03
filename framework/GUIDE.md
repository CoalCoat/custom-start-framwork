# Custom Start Framework Guide / 自定义开局框架指南

> **Custom Start Framework v2**。示例见 [`../example/`](../example/)。

---

## 1. 目录结构

```text
custom-start-framework/
  framework/              ← 框架源码（本指南）
  example/
    custom-start/
```

玩家运行时：

```text
UserData/custom-start/{id}/
  profile.json
  icon.png
```

---

## 2. profile.json

见 README；字段：`id`, `name`, `description`, `cost`, `type`, `allowedStartTypes`, `items`, `removeItems`, `extraCash`, `extraRent`, `unlockedUpgrades`, `factionReputationDelta`。

### allowedStartTypes（起始职业绑定）

- 取值：正整数，对应 `NewGameData.StartType` 枚举（见 `editor/start_types.json`）
- `[]`（空数组）或未配置：Perk 对 **全部职业** 可见
- `[12]`：仅一贫如洗可见；`[2, 12, 14]`：多职业组合
- 游戏更新新增职业时，在 `start_types.json` 追加编号即可，无需改 Mod 代码

---

## 3. 框架 API

```csharp
CustomStartProfileLoader.LoadAll(userDataDir);
CustomStartPerkRegistry.Register(profile);
CustomStartPerkRegistry.TryResolveActiveProfile(startType, out profile);
```

仅当 `StartingPerk.IsPerkActive(id)` 为 true 时注入。

---

## 4. 编辑器

`framework/editor/edit_profiles.py` — 扫描 / 新建 / 编辑 `UserData/custom-start/` 下全部 profile。  
起始职业列表来自同目录 `start_types.json`，可自由追加编号。

---

## 5. 独立打包

| 包 | 脚本 |
|---|---|
| 框架 | `scripts/Pack.ps1` |
| 示例 profile | `scripts/Pack-Example.ps1` |

`scripts/Build.ps1` **仅**构建框架，不包含 example。

示例 profile：复制 `example/custom-start/` 到 `UserData/custom-start/`，或用编辑器直接创建。

---

## Hooks

| Hook | 作用 |
|---|---|
| `StartingPerkList.InitStartingPerk` | 注册 Perk |
| `PerkUIController.OpenUI` | 按 allowedStartTypes 显示 |
| `PlayerStore.InitialSave` + 店铺生命周期 | 注入 loadout |
