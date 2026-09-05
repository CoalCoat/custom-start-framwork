# The Cyber Bear / 赛博贝爷

**Custom start perk pack** for **Probably Stolen Playtest**, **Rock Bottom** (StartType **12**) only. Bear Grylls blundered through a spacetime rift into neon cyber slums—fieldcraft turned into salvage appraisal, with scavenging tools, appraisal gear, emergency supplies, and **+$200** starting cash.

**自定义开局 Perk 配置包**，适用于 **Probably Stolen Playtest** 的 **一贫如洗（Rock Bottom）** 职业。贝爷误闯时空裂隙坠入赛博底层，野外本能化作识货眼光，附拾荒经营工具、识货装备与应急补给，额外现金 +200。

---

## English

### Description

Bear Grylls blundered through a spacetime rift during a survival shoot and landed in neon-lit cyber slums. Fieldcraft turned into salvage appraisal—a large backpack on his shoulders, flashlight and scanner as compass, combat knife as insurance. Includes scavenging tools, appraisal gear, emergency supplies, and **+$200** starting cash.

### Summary

| Field | Value |
|---|---|
| Profile ID | `the_cyber_bear_12` |
| Start type | Rock Bottom (StartType **12**) |
| Perk type | Neutral (type **2**) |
| Perk cost | 0 |
| Extra cash | +200 |
| Extra rent | 0 |
| Faction rep | Lower district **+30** |

### Starting items

| Item ID | Name |
|---|---|
| `labeler` | Labeler |
| `magnifier` | Magnifying Glass |
| `scav_token` | Scavenger's Token |
| `ingot_book` | Metallurgy Manual |
| `backpack_large` | Backpack (Large) |
| `metal_scanner` | Scav Scanner |
| `flashlight` | Flashlight |
| `combat_knife` | Combat Knife |
| `energy_drink` | Energy Drink |
| `cat_bar` | Cat Chocolate Bar |
| `hemostatic_bandage_item` ×2 | Hemostatic Bandage |

### Requirements

1. **[MelonLoader](https://melonwiki.xyz/)** installed for **Probably Stolen Playtest**
2. **Custom Start Framework** (`CustomStartFramework.dll` v1.0.0+) — loads profiles from `UserData/custom-start/`; see the framework release `README.md` for setup

> This pack does **not** include the framework DLL. Install the framework mod separately.

### Installation

1. Install **Custom Start Framework** (copy `CustomStartFramework-1.0.1.dll` → rename to `CustomStartFramework.dll` → place in game `Mods/`)
2. Copy the entire `the_cyber_bear_12` folder to:

   ```text
   <GameDir>/UserData/custom-start/the_cyber_bear_12/
     profile.json
     icon.png          # optional custom perk icon
   ```

3. Launch the game → **New Game** → choose **Rock Bottom** → select **The Cyber Bear** in starting perks

You may also extract `the_cyber_bear_12.zip` into that folder if the release includes a zip.

### Files

| File | Purpose |
|---|---|
| `profile.json` | Perk definition (name, description, items, cash, reputation, etc.) |
| `icon.png` | Optional 32×32 perk icon; framework default used if omitted |

---

## 中文

### 描述

贝爷在极限求生拍摄中误闯时空裂隙，坠入霓虹赛博底层，野外本能化作识货眼光。旧背包在肩，手电扫描仪作指南针，战斗匕首作保险。附拾荒经营工具、识货装备与应急补给，额外现金 +200。

### 效果摘要

| 项目 | 内容 |
|---|---|
| Profile ID | `the_cyber_bear_12` |
| 可见职业 | 一贫如洗（StartType **12**） |
| Perk 类型 | 中性（type **2**） |
| Perk 费用 | 0 |
| 额外现金 | +200 |
| 额外租金 | 0 |
| 派系声望 | 下层区 **+30** |

### 起始物品

| 物品 ID | 名称 |
|---|---|
| `labeler` | 标签打印机 |
| `magnifier` | 放大镜 |
| `scav_token` | 拾荒者信物 |
| `ingot_book` | 冶金手册 |
| `backpack_large` | 背包（大） |
| `metal_scanner` | 拾荒扫描仪 |
| `flashlight` | 手电筒 |
| `combat_knife` | 战斗匕首 |
| `energy_drink` | 能量饮料 |
| `cat_bar` | 猫咪巧克力棒 |
| `hemostatic_bandage_item` ×2 | 止血绷带 |

### 依赖

1. **[MelonLoader](https://melonwiki.xyz/)** — 已安装于 **Probably Stolen Playtest**
2. **Custom Start Framework**（`CustomStartFramework.dll` v1.0.0+）— 自定义开局 Perk 框架，负责加载 `UserData/custom-start/` 下的 profile；安装说明见框架发布包 `README.md`

> 本配置包**不包含**框架 DLL，需单独安装框架 Mod。

### 安装

1. 安装 **Custom Start Framework**（将 `CustomStartFramework-1.0.1.dll` 重命名为 `CustomStartFramework.dll` 放入游戏 `Mods/`）
2. 将整个 `the_cyber_bear_12` 文件夹复制到：

   ```text
   <游戏目录>/UserData/custom-start/the_cyber_bear_12/
     profile.json
     icon.png          # 可选，自定义 Perk 图标
   ```

3. 启动游戏 → **新游戏** → 选择起始职业 **一贫如洗** → 在开局 Perk 列表中选择 **赛博贝爷**

也可解压 `the_cyber_bear_12.zip` 到上述目录（若发布包内含 zip）。

### 文件说明

| 文件 | 说明 |
|---|---|
| `profile.json` | Perk 定义（名称、描述、物品、现金、声望等） |
| `icon.png` | 可选；32×32 Perk 图标，缺省时使用框架默认图标 |

---

## License

Configuration content follows the Custom Start Framework project license (MIT). Game assets belong to the original developers.
