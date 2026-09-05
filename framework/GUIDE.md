# Custom Start Framework Guide / 自定义开局框架指南

> **Custom Start Framework v1.0.1**。示例见 [`../example/`](../example/)。

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

完整字段见下表。**凡名称含 `extra` 或 `Delta` 的数值字段，均为在「当前起始职业默认值」上的增减量，不是存档里的最终绝对值。**

### 2.1 字段一览

| 字段 | 类型 | 含义 | 常见误解 |
|---|---|---|---|
| `version` | int | 配置格式版本，目前为 `1` | — |
| `id` | string | Perk ID，与文件夹名一致 | 不要用中文或空格 |
| `name` / `description` | `{ zh, en }` | 显示名与描述 | — |
| `cost` | int | Perk 点数消耗（可为负） | 与 `extraCash` 无关 |
| `type` | int | `0` 正面 / `1` 负面 / `2` 中性 | 只影响 UI 底色 |
| `allowedStartTypes` | int[] | 可见的起始职业 ID；`[]` = 全部 | 不是强制改 startType |
| `items` | string 或 object[] | 开局**额外**发放到**柜台**的物品 | 不是背包/展柜；见 `LoadoutItem` |
| `removeItems` | string[] | 从柜台**移除**的物品 ID（在 `items` 之前执行） | 只扫柜台，不含背包 |
| `extraCash` | int | **额外**现金（加到 `playerCash`） | ❌ 不是存档里的 `playerCash` 总数 |
| `extraRent` | int | **额外**租金（同时加 `startingRent` 与 `rentValue`） | ❌ 不是最终月租；一贫如洗默认 200 |
| `retailMarkupDelta` | int | **零售加价**增减（百分点，加在 `retailMarkup`） | ❌ 不是设为 5% 就覆盖为 5；0 表示不改；**且仅对适用零售加价的合法卖出价生效**（见 §2.5） |
| `contrabandMarkupDelta` | int 或 object | **违禁品加价**增减；整数 = 四级同加；object 见下 | ❌ 不是覆盖默认值 |
| `contrabandMarkupDelta.low/mid/high/critical` | int | 分别对应 `contrabandMarkupLow/Mid/High/Critial` | 游戏拼写为 `Critial` |
| `baseStoreAttractivenessDelta` | int | **店铺吸引力**增减（加在 `baseStoreAttractiveness`） | ❌ 不是设为 250；默认基线约 250，注入后最低 clamp 0 |
| `unlockedUpgrades` | string[] | 开局解锁的 Wilds Network 升级 ID | 需满足 prerequisite，否则游戏内仍锁 |
| `factionReputationDelta` | object | 六派系声望 **Δ**（`lower/upper/security/black_market/revolution/cartel`） | ❌ 不是存档 `amount` 绝对值 |
| `compensateWildFavorForLowerRep` | bool | 默认 `true`：`lower` Δ 不连带改 `wildFavor` | 设为 `false` 则下层声望会按游戏 ×40 同步 Wild Favor |

### 2.2 新局默认基线（一贫如洗 startType 12 参考）

写 Δ 时可对照（其他职业可能不同）：

| 游戏字段 | 典型初始值 |
|---|---|
| `playerCash` | 0（再叠加职业/Perk 发钱） |
| `startingRent` / `rentValue` | 200 |
| `retailMarkup` | 0 |
| `contrabandMarkupLow/Mid/High/Critial` | 35 / 70 / 100 / 200 |
| `baseStoreAttractiveness` | 250 |

示例：希望开局月租 150 → `"extraRent": -50`（200−50），**不要**写 `"extraRent": 150`。

### 2.3 contrabandMarkupDelta 写法

```json
"contrabandMarkupDelta": 10
```

四级各 +10（低 45 / 中 80 / 高 110 / 严重 210）。

```json
"contrabandMarkupDelta": { "low": 5, "mid": 0, "high": -10, "critical": 0 }
```

仅改指定 tier。

### 2.4 items 高级字段

字符串即物品 ID；对象可带：

| 键 | 说明 |
|---|---|
| `id` | 物品 ID |
| `charge` | 电量（`PowerHelper`） |
| `water` | 液体类型：`pure` / `high_quality` / `base` / `ghost` / `rust` / `gutterflow` |
| `volumeMl` | 毫升；省略或 `-1` 表示装满；`0` 表示清空容器 |

### 2.5 零售加价何时生效

Mod 会正确写入 `PlayerStore.retailMarkup`（日志可见 `retailMarkup delta … (now …)`），但**成交价**只有同时满足时才变：

1. 物品：`GameItem.IsApplyMarkUp()` 为 true（常带 `Retail Markup` 特征）。
2. 顾客：`StoreClient.acceptRetailMarkup` 为 true。
3. 计价：走 `GetCurrentValue(useRetailMarkup: true)`（柜台默认展示价往往不含零售加价）。

**junk、匕首、能量饮料、多数拾荒物通常不吃零售加价**；赃物/违禁品用 `contrabandMarkupDelta`。较易感知：**自动售水机**（+10% 且 applicable 时叠加）。

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
