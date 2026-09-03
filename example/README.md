# Examples / 示例

本目录与 **Custom Start Framework** 独立发布，不参与框架默认打包。  
游戏内需已安装 **CustomStartFramework.dll**。

## 职业示例 Perk

每个 profile 仅对对应起始职业可见（`allowedStartTypes` 绑定）。  
**一贫如洗 (12)** 单独保留「赛博贝爷」示例；其余 12 个职业各一套主题 loadout。

| Profile ID | 名称 | 职业 | 现金 |
|---|---|---|---|
| `deep_well_supplier_1` | 深井供应商 | 水商 (1) | -200 |
| `counter_apprentice_2` | 柜台学徒 | 学徒 (2) | — |
| `dump_diver_3` | 垃圾场潜水员 | 拾荒者 (3) | -200 |
| `gray_market_broker_4` | 灰市中间人 | 销赃者 (4) | -150 / 租金 +50 |
| `cellar_brewer_5` | 地窖酿师 | 私酿酒师 (5) | -50 |
| `back_alley_chemist_6` | 后巷化学家 | 化学家 (6) | -150 |
| `cold_chain_courier_7` | 冷链跑腿 | 器官贩子 (7) | +100 |
| `corner_pharmacist_8` | 街角药剂师 | 药剂师 (8) | +50 |
| `neon_noodle_stall_9` | 霓虹面摊 | 街头小吃摊 (9) | +100 |
| `moisture_farmer_10` | 湿气农夫 | 农场主 (10) | -100 |
| `bench_gunsmith_11` | 工位枪匠 | 枪匠 (11) | -450 |
| `the_cyber_bear_12` | 赛博贝爷 | 一贫如洗 (12) | -400 |
| `rat_ranch_starter_13` | 养鼠起步 | 养鼠人 (13) | -50 |

### 安装

将整个 `custom-start/` 目录（或单个 `{id}/` 文件夹）复制到 `UserData/custom-start/`。

也可用框架自带的编辑器新建或修改 profile：

```bash
python framework/editor/edit_profiles.py -r "UserData/custom-start"
```

重新生成职业示例（不含赛博贝爷）：

```bash
python scripts/generate_example_profiles.py
```

### 打包

```powershell
.\scripts\Pack-Example.ps1
```

---

## English

Independent from the **Custom Start Framework** release.

Each profile is visible only for its bound start type. **Rock Bottom (12)** uses *The Cyber Bear*; the other twelve professions each have a themed loadout.

Copy `custom-start/` (or individual `{id}/` folders) to `UserData/custom-start/`, or use the bundled profile editor.
