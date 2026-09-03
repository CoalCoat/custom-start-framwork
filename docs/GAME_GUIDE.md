# Probably Stolen 游戏指南

> 面向玩法理解与 MelonLoader / Harmony 模组开发。  
> 数据来源：Playtest IL2CPP 导出（`tools/Il2CppDumper/dump.cs`）、本地化物品表（`output/items_full_list.md`）、现有插件源码。  
> 游戏版本会随 Steam 更新变化，字段与 ID 以当前 `GameAssembly.dll` 为准。

---

## 目录

1. [游戏概述](#1-游戏概述)
2. [游戏规则](#2-游戏规则)
3. [接口列表](#3-接口列表)
4. [物品模型](#4-物品模型)
5. [事件系统](#5-事件系统)
6. [物品图鉴](#6-物品图鉴)
7. [附录](#7-附录)

---

## 1. 游戏概述

**Probably Stolen** 是一款空间站下层区店铺模拟：玩家经营一家杂货铺，向各派系顾客买卖物资，同时处理租金、检查、违禁品、夜间机器生产和可选的拾荒 / 远征 / 战斗。

核心体验可以概括为：

- **白天**：开门接待顾客，议价买卖，鉴定真伪，应付检查官与通缉犯。
- **夜间**：机器彻夜运转（冶炼、水培、打印、净化……），可能发生盗窃、破坏、停电。
- **长期**：经营声望、Wilds Network 升级、营业许可、房产抵押贷款，以及各职业专属产业链。

货币单位为 **Credit（信用点）**，存在 `PlayerStore.playerCash`。

---

## 2. 游戏规则

### 2.1 一日循环

店铺状态机：`PlayerStore.StoreState`

| 值 | 枚举 | 含义 |
|---|---|---|
| 0 | `CLOSED` | 打烊 / 夜间 |
| 1 | `OPEN` | 营业中 |
| 2 | `MORNING` | 早晨结算 |

典型流程：

1. `BeginDay()` / `OpenShutter()`：拉下卷帘，开始营业。
2. `GetNextClient()` / `TryCallNextClient()`：下一位顾客进店。
3. 交易、鉴定、举报、贿赂或驱离。
4. `EndDay()`：打烊。
5. 夜间：机器工作、服务结算、盗窃判定、伤口恶化。
6. `EndNight()`：进入下一天早晨。

睡觉会触发分析事件 `OnSleepEvent`（记录天数、财富、各派系声望、保险/警报是否开启等）。

### 2.2 开局职业

枚举：`NewGameData.StartType`。编号 `0` 不是可选职业。主菜单显示顺序与枚举值无关。

| 值 | ID | 中文 |
|---|---|---|
| 0 | `NONE` | （无） |
| 1 | `WATER_MERCHANT` | 水商 |
| 2 | `APPRENTICE` | 学徒 |
| 3 | `SCAV` | 拾荒者 |
| 4 | `FENCE` | 销赃者 |
| 5 | `MOONSHINER` | 私酿酒师 |
| 6 | `DRUG_DEALER` | 化学家 |
| 7 | `ORGAN_TRADER` | 器官贩子 |
| 8 | `PHARMACIST` | 药剂师 |
| 9 | `STREET_FOOD_VENDOR` | 街头小吃摊 |
| 10 | `FARMER` | 农场主 |
| 11 | `GUNSMITH` | 枪匠 |
| 12 | `ROCK_BOTTOM` | Rock Bottom |
| 13 | `RANCHER` | 养鼠人 |

开局相关：

- `NewGameData.HandleInitialItem()`：按职业发放起始物品。
- `NewGameData.skipIntro` / `hardMode` / `endlessMode` / `disableTutorialHint`。
- Demo 限时版本用 `PlayerStore.IsStartTypeInLimitedBuild()` 锁定部分职业（本仓库 `character-unlocker` 可覆盖）。

### 2.3 开局天赋（Starting Perk）

玩家可在新游戏时选择若干天赋。类型：`POSITIVE` / `NEGATIVE` / `NEUTRAL`。部分天赋互斥（`incompatiblePerks`）。

`StartingPerkList` 中已实现的工厂方法：

| 方法 | 倾向 | 说明 |
|---|---|---|
| `Saving()` | 正 | 更会攒钱 |
| `BadLease()` | 负 | 糟糕租约 |
| `Convict()` | 负 | 有案底 |
| `ModelCitizen()` | 正 | 模范公民 |
| `WellConnected()` | 正 | 人脉广 |
| `Alert()` | 正 | 警觉 |
| `SawyerCrew()` | 正 | Sawyer 船员 |
| `Diplomatic()` | 正 | 外交手腕 |
| `Intimidating()` | 正 | 威慑 |
| `SideStreet()` | 负 | 偏僻街道 |
| `NicotineAddiction()` | 负 | 尼古丁成瘾 |
| `NarcoticAddiction()` | 负 | 麻醉品成瘾 |
| `AlcoholAddiction()` | 负 | 酒精成瘾 |
| `SecretAdmirer()` | 正 | 秘密崇拜者 |
| `ColorfulCharacter()` | 中 | 有个性 |
| `Blackmail()` | 负 | 把柄在人手上 |
| `Blabbermouth()` | 负 | 嘴碎 |
| `Minimalist()` | 中 | 极简主义 |
| `Sentinel()` | 负 | 哨兵崩溃综合征相关 |
| `WelfareProgram()` | 正 | 福利计划 |
| `ProficientScavenger()` | 正 | 熟练拾荒者 |
| `GamblingAddiction()` | 负 | 赌博成瘾 |
| `Tapehead()` | 中 | 磁带迷 |

另有判定方法但未全部出现在 `StartingPerkList` 工厂里：`IsAgoraphobia`、`IsRevolutionSympathizer`、`IsExpeditionOrganizer`、`IsShortSleeper`、`IsWorkingPipes`、`IsIlliterate`、`IsPrimeRealEstate`、`IsExperiencedChemist`、`IsUnsubscribed` 等。

### 2.4 经济

`PlayerStore` 中的关键字段：

| 字段 | 含义 |
|---|---|
| `playerCash` | 当前现金 |
| `dayUntilRent` / `rentValue` / `startingRent` / `temporaryRent` | 租金周期与金额 |
| `dayUntilLoan` / `loanValue` | 高利贷 |
| `retailMarkup` | 零售加价（百分比） |
| `contrabandMarkupLow/Mid/High/Critial` | 违禁品分级加价（注意代码拼写 `Critial`） |
| `foreclosePercentage` | 断供/没收比例 |
| `contrabandFinePercentage` | 违禁品罚款比例 |
| `wildFavor` | Wilds Network 好感 |
| `IsPropertyPaid` / `isPayingMortgage` / `mortgageWeekLeft` / `mortgageWeeklyPayment` | 房产与按揭 |
| `hasBusinessPermit` | 是否持有营业许可证 |
| `odinBudget` | 治安部侧预算相关 |

租金未付会走 `OnRentNotPaid()`，最终可 `ExecuteGameOver("rent")`。

**配给站（Commissary）**：用食品券 `food_stamp` 兑换物资。`CommissaryData.BuyItem(id)` / `RedeemAllStampInInventory()`。

**彩票**：每周六开奖，`currentWinningLotteryNumber` / `currentLotteryEdition`。刮刮乐为独立物品。

### 2.5 顾客与交易

顾客模型：`StoreClient`。到店实例：`StoreClientInstance`。管理器：`StoreClientManager`。

意图 `StoreClient.ClientIntent`：

| 值 | 枚举 | 含义 |
|---|---|---|
| 0 | `UNDEFINED` | 未指定 |
| 1 | `BUY` | 向玩家购买 |
| 2 | `SELL` | 向玩家出售 |
| 3 | `SELLNBUY` | 既买又卖 |
| 4 | `INSPECTION` | 检查 |
| 5 | `DIALOGUE` | 剧情对话 |
| 6 | `BARTER` | 以物易物 |
| 7 | `RENT` | 收租 |
| 8 | `LOAN_SHARK` | 放贷 |
| 9 | `SPECIAL` | 特殊 |
| 10 | `INFORMATION_DEALER` | 情报贩子 |
| 11 | `PROCUREMENT_OFFER` | 采购要约 |
| 12 | `PROCUREMENT_COLLECT` | 采购交货 |
| 13 | `WHOLESALE` | 批发 |
| 14 | `APPRAISAL_SERVICE` | 鉴定服务 |
| 15 | `GUNSMITH` | 枪匠订单 |
| 16 | `EXPEDITION` | 远征雇员 |

顾客分表（按来源）：`StoreClientListWater`、`Gun`、`Barter`、`Cartel`、`Security`、`Rev`、`Story`、`Wanted`、`Supplier`、`Shortage`、`Surplus`、`Minor`、`Morning`、`Appraisal`、`Information`、`Event`、`Tier*` 等。

交易要点：

- 预算：`SetClientBudget` / `HasBudgetLeftToBuy`。
- 标签过滤：`clientBuyingTagList` / `clientBuyingIdList` / `clientBlackTagList`。
- 议价：`isBargainAvailable`、`dealMakerBargainBonus`、香水加成（+15% / +25%，不可叠加）。
- 顾客可揭开物品隐藏特征：`CanClientExposeThisFeature`。
- 通缉犯：`isWanted` / `isStealthWanted`；举报走 `OnCustomerReported`，误报有上限 `wrongfulReportMax`。
- 改造体（Aug）：`isAug` / `augTier`，可用 `aug_scanner` 100% 确认。

展示柜物品会提高对应类型顾客进店概率（霓虹灯牌、拾荒者信物、枪证、鉴定证书、远征招募牌、暗灯等）。

### 2.6 派系声望

顾客派系常量：

| 常量 | ID | 中文 |
|---|---|---|
| `FACTION_LOWER` | `FACTION_LOWER_LEVEL` | 下层区 |
| `FACTION_UPPER` | `FACTION_UPPER_LEVEL` | 上层区 |
| `FACTION_MIDDLE` | `FACTION_MIDDLE` | 中层 |
| `FACTION_SECURITY` | `FACTION_SECURITY` | 治安部 |
| `FACTION_CRIME` | `FACTION_BLACK_MARKET` | 黑市 |
| `FACTION_TOURIST` | `FACTION_TOURIST` | 游客 |

分析事件里还出现 `RepRevolution`、`RepChurch`、`RepCartel`。声望对象：`StoreReputation`（`amount`、`strength`、`influence`、`canVandalized`）。

交易后调用 `StoreReputation.OnItemTraded(...)`。达到阈值解锁 `StoreReputationPerk`：

**下层区**：`LLREFERAL`、`LLTIPS`、`LLRAREGOOD`、`LLTIGHTLIPS`、`LLPILLAR`、`LLPOORREVIEWS`、`LLDISTRUSTED`、`LLTARGET`、`LLLYNCH`、`LLAVOIDED`

**治安部**：`SEC_WATCHLIST`、`SEC_PRIORITY`、`SEC_THOROUGH_INSPECTION`、`SEC_CONTRABAND_TOLERANCE`、`SEC_IMMEDIATE_ARREST`、`SEC_PROTECTION`、`SEC_SURPLUS`、`SEC_VIP`、`SEC_TRUSTED`、`SEC_REQUISITION`、`SEC_RELIABLE_VENDOR`、`SEC_ALARM_IGNORED`

**黑市**：`BM_DISTRUSTED`、`BM_UNINSURABLE`、`BM_SMALL_TIME_BROKER`、`BM_RELIABLE`、`BM_NETWORK`、`BM_HONOR`

**上层区**：`UL_GOSSIP`、`UL_TIPS`、`UL_HOUSEHOLD_NAME`、`UL_TOP_REVIEW`、`UL_CHARITY`、`UL_TOURISTTRAP`、`UL_HITMAN`、`UL_PETITION`

**革命**：`REV_HIT`、`REV_BLACKLISTED`、`REV_REQUEST`、`REV_RAID_LOOT`、`REV_QUARTERMASTER`、`REV_FRIEND`

**卡特尔**：`CARTEL_RETIRED`、`CARTEL_INCREASED_STIPEND`、`CARTEL_RELIABLE_CHEMIST`、`CARTEL_AUTHORIZED_EXIT`

低声望可能导致砸店（`isVandalized`）、被针对检查、拒保等。枪证要求治安部声望分别不低于 0 / 30 / 60，否则吊销。

### 2.7 检查、违禁品与赃物

检查官到店触发 `InspectorArrivedEvent`。结果 `OnInspectedEvent`：

- `OutcomeType`：结果类型
- `HasSmugglerBay`：是否有走私暗格
- `TotalLostItemValue` / `TotalLostItemCount`：被扣物品
- `HasSecurityGrace` / `UsedSecurityGrace`：治安宽限技能

可贿赂：`InspectionBribeEvent.BribeAmount`。内线服务可提前 2 天 / 1 天 / 当天预警（`NightLog.InspectionWarning*`）。

藏匿容器：`smuggler_bay` / `smuggler_bay_mini` / `smuggler_bay_mod`。

赃物加价由 `StolenHelper` 与 `ItemFeatureList.StolenBonusBuying*` 处理。黑灯 `black_lamp` 放展示柜可吸引销赃客，成功率受黑市声望影响。

治安档案 `SecData` 追踪：脏水、贴错标签的水、伪劣化工、贿赂、劣质弹药、危及公共安全物品等证据等级 `evidenceLevel`。

### 2.8 夜间、盗窃与店铺服务

`StoreService` 常见服务：

| 获取方法 | 作用 |
|---|---|
| `GetPowerService()` | 电力（机器、充能器、PowerBloc 依赖） |
| `GetJanitorialService()` | 清洁（垃圾桶清空、垃圾等级 `garbageLevel`） |
| `GetInsuranceService()` | 保险（失窃赔付；未缴计入 `dayWithoutInsurance`） |
| `GetInspectionEarlyWarningService()` | 检查预警 |
| `GetBuyReferalService()` | 买家介绍 |
| `GetSellReferalService()` | 卖家介绍 |
| `GetWildFixerService()` | 荒野修理工 / 销赃人 |
| `GetCriminelNetworkService()` | 犯罪网络（代码拼写 `Criminel`） |
| `GetCartelProtectionService()` | 卡特尔保护 |

夜间日志 `NightLog` 覆盖：盗窃成功/失败/有警报/有保险、停电、破坏、改造体来访、通缉犯到访、店面未打扫等。

警报系统 `security_alarm` 大幅降低夜间失窃率，需独立电源。`isSecurityAlarmActive` 记录当前是否启用。

### 2.9 Wilds Network 升级

字典：`PlayerStore.networkUpgrade`。单条：`NetworkUpgrade`（`id`、`cost`、`prerequisite`、`isRepeatable`、`cooldownDuration`、`lockInDemo`）。

| ID | 含义 |
|---|---|
| `BREWER` | 酿酒师 |
| `CHEMIST` | 化学家 |
| `PHARMA` | 药剂 |
| `MINER` | 矿工 |
| `LANDLORD_GRACE` | 房东宽限 |
| `SEC_GRACE` | 治安/监狱宽限 |
| `INSPECTION_INFORMANT` | 检查内线 |
| `WILD_FIXER` | 荒野销赃人 |
| `EVIDENCE_REMOVAL` | 清除证据 |
| `BUY_REFERAL` | 购买介绍 |
| `SELL_REFERAL` | 销售介绍 |
| `CRIMINEL_NETWORK` | 犯罪网络 |
| `POWER_HIJACK` | 偷电 |
| `COMMERCIAL_POWER` | 商业电力 |
| `SHOWCASE_I` / `SHOWCASE_II` | 展柜 I / II |
| `GUTTERFLOW_TAP` | 排水管接水 |
| `RUSTWATER_TAP` | 锈水接水 |
| `RUINED_MACHINE_UNLOCK` | 破旧机器解锁 |
| `RETIRED_FARMER` | 退休农夫 |
| `RETIRED_GUNSMITH` | 退休枪匠 |
| `RETIRED_CHEMIST` | 退休化学家 |
| `RETIRED_RANCHER` | 退休养鼠人 |
| `GUN_PERMIT_I/II/III` | 枪证 I–III |
| `WATER_TRADER` | 水商网络 |
| `WINEMAKER` | 葡萄酒酿造 |
| `MARKETPLACE_REQUESTS` | 市场请求 |
| `JACKSON1` / `JACKSON2` | Jackson 投资 |
| `RENOVATION1/2/3` | 翻新 I–III |

Demo 中部分 ID 被 `NetworkUpgrade.IsLockedInDemo` 锁住（本仓库 `wilds-network-unlocker` 可短路）。解锁需满足 `prerequisite`，否则 `GetMissingPrerequisite()` 非空。

### 2.10 机器、模组与夜间生产

多数生产设备「整夜工作」，需要：

1. 电源（`energy_credit` 等，或已缴电费 + PowerBloc / 充能器）
2. 输入材料放在机器库存里
3. 可选模组改变效率 / 性能 / 品质

模组三维（物品说明里的 Module Impact）：

- **Efficiency（效率）**：通常影响耗电
- **Performance（性能）**：速度或产量
- **Quality（品质）**：产出物品质量

通用模组：`system_module_eco`、`efficiancy`（拼写如此）、`performance`、`quality`、`overclock`、`fineness`、`streamlining`、神经核心（受限/无限制，无限制为违禁 AI）。

`turbo_booster` 可立刻完成一次耗时工序（一次性）；`turbo_booster_adv` 可充能重复使用。

机器损坏后可用螺丝刀 / 焊枪 / 剪线钳拆解回收。`module_extractor` 可安全取出卡住的模组。

### 2.11 水、酒、化学、种植、畜牧

**水**：纯度与杂质决定售价与是否构成欺诈。可用试纸、AquaScan、滤芯、净水片、UV 灯、净水器、水分收集器。接水龙头需要网络升级（排水管 / 锈水）。自动售水机只卖基础水 / 优质水 / 纯水，售价 +10% 且计入零售加价，但不受事件修正。

**酒**：荧光莓 + 酵母 + 酒瓶发酵；`age_well` 催陈；合成酵母可产带致癌性的阴光莓果酿。

**化学**：加热板、搅拌机、蒸发器、化学成品机；管制前体可合成芬塔等。卡特尔线要求纯度与交货数量（`cartelRequiredCount` / `cartelRequiredPurity`）。

**水培**：种子 + 营养片 + 水质。作物包括填充草、营养果、韧棉、水芦、梦幻菌盖等。短柄斧清除种植槽。

**畜牧**：饲料分配器、粪便、基因扫描仪、血清、屠宰。累计屠宰数 `animalsButcheredTotal` 可触发剥皮刀奖励。

### 2.12 健康、成瘾与 Afterhours

`HealthData`：

- 成瘾计时：尼古丁 / 酒精 / 麻醉品 / 赌博
- 伤口：`woundState`、`isWoundStable`、`ReceiveMinorWound()` / `ReceiveMajorWound()`，夜间 `HandleNightlyWound()`
- 哨兵：`sentinelPool`、`daysSinceSentinelInjection`
- `wentToAfterhoursLastNight`：昨晚是否去 Afterhours（会有次日 debuff）

`CanRead()` 为文盲天赋服务。成瘾会给买卖双方加上 `AddictionBuyPenalty` / `AddictionSellPenalty` 特征。

### 2.13 拾荒、远征与战斗

**垃圾场拾荒**：`scavengingAttempts`。手电筒降低受伤率；螺丝刀 / 焊枪 / 剪线钳分别提高螺丝、废金属、线缆产量；拾荒扫描仪提高贵重物发现率（同时只生效一台）。

**远征**：展示柜放 `sign_expedition` 招募雇员。`Hireling` 有生命、勇气与特质（Fighter、Coward、Survivor、Lucky、TreasureHunter 等）。状态：`Available` / `OnExpedition` / `Injured` / `Complete`。补给放入 `expedition_box`。过程中可能触发 `ExpeditionAccident`。

**战斗**：物品实现 `CombatAbility`。枪械可装模组（消音器、瞄具、弹匣、枪托……）。弹药分普通 / 非致命 / 穿甲。玩家位置 `PlayerLocation`：`IN_STORE` 或 `INVENTOR`（发明家/工坊场景）。`isShootingUnlocked` 控制射击是否解锁。

### 2.14 鉴定与对质

部分高价值物品有隐藏真伪（食品券、注射器、仿生手、等离子燃料匣、肋排堡、海明威香烟等）。需要对应指南 + 放大镜 / 专用扫描仪。鉴定公会交互：`AppraisalGuildInteractionEvent`；送评：`AppraisalSentEvent`（`ActualValue` vs `SentValue`）。对质：`ConfrontEvent`（`ConfrontType` / `Outcome`）。

### 2.15 失败与模式

`ExecuteGameOver(string ending)`，默认 `"rent"`。`GameOverEvent.Reason` 记录原因。

模式开关：

- `hardMode`：`StoreService.InitHardMode()` 调整服务费用等
- `endlessMode`：无尽模式
- `skipIntro`：跳过开场
- `devMode` / `isProduction`

### 2.16 区域势力事件

`StoreOperationManager` 每日按下层动荡、上层友好度、革命/治安/黑市力量排队区域行动（突袭、保护费、破坏等），通过 `NightLog` 与到店顾客体现。

---

## 3. 接口列表

MelonLoader 生成的游戏类型位于命名空间 `Il2Cpp`。下列为模组最常用的运行时入口。

### 3.1 物品创建与目录

```csharp
// 按 ID 创建物品（isOwned=true 表示玩家持有）
GameItem item = DirectoryMaster.Item("flashlight", true);

DirectoryMaster.Has<T>(identifier);
DirectoryMaster.Create<T>(identifier);
DirectoryMaster.CharacterItem(identifier);
DirectoryMaster.CombatAbility(identifier);
DirectoryMaster.GetIdentifierList<T>(dictionaryClassName);
DirectoryMaster.Reset();
```

过时 API：`GameItem.Create(...)`（标注 Obsolete，应改用 DirectoryMaster）。

### 3.2 店铺与存档

```csharp
PlayerStore store = PlayerStore.Instance;
int cash = store.playerCash;
store.playerCash += 500;

store.StartNewGame();
store.InitialSave();
store.SaveGame();
store.LoadGame();
PlayerStore.PreLoadStore();

store.BeginDay();
store.OpenShutter();
store.EndDay();
store.EndNight();
store.ExecuteGameOver("rent");

List<GameItem> all = store.FindAllItem(true);
bool owned = store.IsPlayerOwnThisItem("flashlight");
store.DismissCurrentClient(callNextWhenPossible: true);
```

开局：

```csharp
NewGameData.Instance.startType;          // StartType 枚举
NewGameData.HandleInitialItem();
NewGameData.GetStartDisplayName(startType);
NewGameData.HardReset();
PlayerStore.IsStartTypeInLimitedBuild(startType);
```

场景入口：

```csharp
EmporiumEntry emp = EmporiumEntry.Instance;
GameGridInventory inv = emp.invElement;           // 主库存 / 柜台
GameGridInventory showcase = emp.showcaseElement; // 展示柜
GameGridInventory hidden = emp.hiddenElement;     // 走私暗格等
```

`EmporiumEntry` 还持有垃圾桶、排水口、水龙头、磁带机、售货机、售水机、Afterhours 口袋、雇员栏、前后柜台等窗口。

### 3.3 库存与槽位

```csharp
SlotMarker slot = inv.TryFindOneValidInventorySlot(item, keepOrientation: false);
if (slot != null)
    slot.AcceptUnchecked();
else
{
    var list = new Il2CppSystem.Collections.Generic.List<GameItem>();
    list.Add(item);
    inv.UncheckedAcceptAll(list);
}

slot.TryAcceptOnce(amount: -1);
SlotMarker.StackItemUnchecked(src, dest, amount: -1);
inv.Expel(item);
inv.ExpelAll();
```

`GameInventory` 抽象接口要点：`UncheckedAccept`、`TryInventorySlot`、`childItems`、`GetTotalValue`。

实现类：`GameGridInventory`（网格）、`GameSlotInventory`（单槽，如口袋、机器输入）。

### 3.4 升级、声望、服务

```csharp
NetworkUpgrade.IsUnlocked("CHEMIST");
NetworkUpgrade.GetUpgradeById("GUN_PERMIT_I").Unlock();
NetworkUpgrade.IsLockedInDemo(id);

StoreReputation.ModReputation("FACTION_SECURITY", 5, notify: true);
StoreReputation.GetSecReputation();
StoreReputation.IsPerkUnlocked("SEC_VIP");

StoreService.FindServiceByID(id);
StoreService.GetPowerService().IsActive();
```

### 3.5 健康与夜间日志

```csharp
HealthData.ReceiveMinorWound();
HealthData.IsNicotineAddicted();
store.healthData.ConsumeAlcohol(value);

NightLog.BurglaryAlarmFailed(itemName);
NightLog.InspectionWarningTomorrow();
```

### 3.6 分析埋点（只写不读）

`EmporiumAnalytics` 把游戏内事件送到分析后端，模组一般不必调用，但与第 5 节事件一一对应：

`TrackNewGame`、`TrackWildUpgradePurchased`、`TrackInspectorArrived`、`TrackInspectionBribe`、`TrackOnInspected`、`TrackAppraisalSent`、`TrackConfront`、`TrackGameOver` 等。

### 3.7 Helper 一览（按系统）

这些静态 Helper 封装了物品行为，Hook 玩法时优先从这里找：

| Helper | 职责 |
|---|---|
| `WaterHelper` / `WaterFeatureHelper` / `WaterTestHelper` | 水质、杂质、检测 |
| `WineHelper` / `AgableHelper` | 酿酒与陈化 |
| `ChemicalHelper` / `ChemicalProductHelper` / `ChemicalCompositionHelper` | 化学合成 |
| `HydroponicHelper` | 水培 |
| `HusbandryHelper` / `GeneticHelper` | 畜牧与基因 |
| `GunHelper` / `GunModHelper` / `AmmoBoxHelper` | 枪械与配件 |
| `MachineHelper` / `MachineryHelper` / `ModuleHelper` / `ModuleEffectHelper` / `PowerHelper` | 机器与模组 |
| `CraftingHelper` | 工作台合成 |
| `ContrabandHelper` / `StolenHelper` | 违禁与赃物 |
| `AppraisalHelper` / `InspectableHelper` | 鉴定 |
| `MedicalHelper` / `InsInjectorHelper` | 医疗与注射器 |
| `BarterHelper` | 以物易物 |
| `ExpeditionHelper` / `ScavHelper` / `SalvageHelper` | 远征与拾荒 |
| `PermitHelper` | 许可证 |
| `LockHelper` | 钥匙卡锁 |
| `DurabilityHelper` / `UseCountHelper` | 耐久与使用次数 |
| `ContainerHelper` / `LiquidContainerHelper` | 容器与液体 |
| `FoodItemHelper` / `ConsumableHelper` | 食物与消耗品 |
| `LabelerHelper` | 标签重命名 |
| `LotteryHelper` / `ScratcherHelper` | 彩票 |
| `IntelHelper` | 情报 |
| `UniqueItemHelper` | 唯一物品 |

### 3.8 物品 Directory 类

每个 Directory 向 `DirectoryMaster` 注册一批 `identifier`：

| 类 | 内容 |
|---|---|
| `MiscItemDirectory` | 杂项大宗 |
| `ToolDirectory` | 工具 |
| `MedsItemDirectory` | 医疗 |
| `FoodItemDirectory` | 食物 |
| `WineDirectory` | 酒类 |
| `HydroponicDirectory` | 水培 |
| `HusbandryDirectory` | 畜牧 |
| `MaterialDirectory` | 材料 |
| `GunsItemDirectory` / `GunModDirectory` | 枪与配件 |
| `MeleeWeaponItemDirectory` | 近战 |
| `ExplosiveItemDirectory` | 爆炸物 |
| `ArmorItemDirectory` | 护甲 |
| `ContainerItemDirectory` | 容器 |
| `FurnitureItemDirectory` | 家具 |
| `ModuleDirectory` / `ModItemDirectory` | 模组 |
| `StationMachinery` | 站点机器 |
| `RuinedMachineDirectory` | 损坏机器 |
| `KeyItemDirectory` | 关键物品 |
| `OrganDirectory` | 器官 |
| `AmenitiesItemDirectory` | 日用品 |
| `ConstructionItemDirectory` | 建造 |
| `EquipmentDirectory` | 装备 |
| `ShipItemDirectory` / `ShipSystemDirectory` | 飞船系统 |
| `TechnicianBackpackDirectory` | 技师背包 |
| `PlayerAbilityItemDirectory` | 玩家能力物品 |
| `UnusedDirectory` | 未使用 |

### 3.9 模组注入参考（本仓库）

职业开局发物品的稳定写法见 `framework/Plugin.cs`：

1. Harmony 钩住 `NewGameData.HandleInitialItem` / `PlayerStore.InitialSave` 等。
2. `DirectoryMaster.Item(id, true)` 创建。
3. `EmporiumEntry.Instance.invElement.TryFindOneValidInventorySlot` 放入柜台。
4. 现金直接改 `PlayerStore.playerCash`。
5. 升级调用 `NetworkUpgrade.Unlock()`。

---

## 4. 物品模型

### 4.1 类型层次

```
GameItemFunc
  └── GameItem : GraphNodeStorage, DirectoryEntry, CombatAbility
        └── GameItemElement : PixelElement, TooltipListener
```

运行时物品几乎都是 `GameItemElement`。物品可再嵌套库存（容器、机器、背包），形成树：`parentInventory` / `children`。

### 4.2 `GameItem` 核心字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `identifier` | `string` | 原型 ID，如 `flashlight`。空字符串视为无效物品 |
| `uniqueId` | `int` | 存档内实例 ID，由 `PlayerStore.GetUniqueID()` 分配 |
| `name` | `string` | 显示名（可被标签机改写） |
| `shortDescription` / `longDescription` / `flavorText` | `string` | 描述与风味文本 |
| `unitCount` | `int` | 堆叠数量 |
| `unitValue` | `long` | 当前单位价值 |
| `unitBaseValue` | `long` | 基础价值 |
| `lateUnitValue` | `long` | 延迟计算价值 |
| `itemTypes` | `List<string>` | 类型标签（顾客过滤、市场修正用） |
| `itemFeatures` | `List<ItemFeature>` | 价值特征（见 4.4） |
| `state` / `modifiedState` | `TagSystem` | 动态标签状态（纯度、耐久、锁定……） |
| `shape` / `modifiedShape` | `GridShape` | 背包网格形状 |
| `spritePath` / `spriteAtlasPath` | `string` | 图标 |
| `parentInventory` | `GameInventory` | 所在容器 |
| `recipeManager` | `RecipeManager` | 合成配方 |
| `customText` | `string` | 自定义文本（便签、标签） |
| `effects` | `List<CombatAbilityEffect>` | 战斗效果 |
| `bonusAccuracy` | `int` | 精度加成 |
| `isCombatBackpack` | `bool` | 是否战斗背包 |

### 4.3 `TagState`（物品内部状态）

物品的可变属性存在 `TagSystem` 里的 `TagState`：

| 字段 | 用途 |
|---|---|
| `identifier` | 状态键 |
| `valueInt` / `valueFloat` / `valueLong` / `valueDouble` / `valueBool` / `valueString` | 值 |
| `valueEnabled` | 是否启用 |

常见用途：水质纯度、酒龄、模组插槽、耐久、电量、锁权限、种子生长阶段等。`ItemStateModifier` 可在放入/取出容器时改形状或状态。

### 4.4 `ItemFeature`（价值特征）

物品价格 = 基础价 × 各 Feature 修正。特征可对玩家隐藏，由顾客、放大镜或指南揭开。

**FeatureType**

| 值 | 名称 | 含义 |
|---|---|---|
| 0 | `Normale` | 固有（拼写如此） |
| 1 | `Event` | 事件 |
| 2 | `Special` | 特殊 |
| 3 | `Temporary` | 临时 |
| 4 | `TemporaryBuying` | 仅买入时 |
| 5 | `TemporarySelling` | 仅卖出时 |
| 6 | `ClientTemporary` | 仅当前顾客 |

**ValueStage**：`Innate`（先天）→ `Market`（市场）→ `Final`（成交）。

关键字段：`valueModifier`、`isFeatureExposed`、`isExposable`、`isPublicHidden`、`fakeCondition` / `realCondition`（真伪双条件）、`removedByTool`（可被某工具移除）。

`ItemFeatureList` 工厂示例：`RetailMarkUp()`、`StolenBonusBuyingHigh()`、`ContrabandCriticalMarkUp()`、`NeuroActivePerfumeSelling()`、`AddictionSellPenalty()`、`ConfrontSucessDiscount()`。

### 4.5 槽位 `SlotMarker`

| 字段 | 说明 |
|---|---|
| `item` | 待放入物品 |
| `inventory` | 目标库存 |
| `itemGridShape` | 放置形状 |
| `index` | 槽位索引 |
| `targetItem` | 堆叠目标 |
| `numTransfer` | 转移数量 |
| `priority` | 搜索优先级 |

`AcceptUnchecked()` 不跑完整校验，模组发物品时常用；正式交易应走 `TryAcceptOnce`。

### 4.6 存档形态

`PlayerStore` 把各库存序列化成 JSON 字符串：`mainInvJSON`、`backInvJSON`、`showcaseInvJSON`、`hiddenInvJSON`、`trashcanInvJSON`、`docInvJSON`、`vendingMachineInvJSON` 等。编解码：`EncodeItem` / `DecodeSaveItem`。

液体容器类物品用 `DirectoryMaster.Item` 创建后可能是空容器（酒、水瓶），这是原型默认状态，不是 API 错误。

### 4.7 物品 ID 约定

- 全小写 + 下划线：`bottled_water`、`permit_gun_2`
- 钥匙卡按部门：`cmd_keycard`、`eng_keycard`、`med_keycard`、`sec_keycard`、`ser_keycard`、`sup_keycard`、`sci_keycard`、`blank_keycard`
- 打印芯片带产量占位：`printer_chip_10_mag` 显示名含 `{0}`
- 无效 ID：`DirectoryMaster.Item` 可能返回 `identifier` 为空的占位对象，发放前必须检查

完整 ID 见第 6 节。自定义开局配置：`UserData/custom-start/{id}/profile.json`。

---

## 5. 事件系统

游戏内分析事件均继承 `Event`（Unity Gaming Services 风格）。它们在关键节点由 `EmporiumAnalytics.Track*` 发出。模组若要监听玩法，更稳妥的是 Harmony 钩对应的 `PlayerStore` / `StoreReputation` 方法，而不是订阅这些分析事件。

公共字段多数事件都有：`RunId`、`Spec`（开局职业）、`Day`、`RunNumber`、`CurrentCredit`、`RunPlayTimeSeconds`、`TotalPlayTimeSeconds`。

### 5.1 生命周期

| 事件 | 触发 | 特有字段 |
|---|---|---|
| `NewGameStartedEvent` | 新开一局 | `SkipIntro`、`HardMode`、`EndlessMode` |
| `StartingPerkSelectedEvent` | 选择开局天赋 | `PerkId` + 同上模式字段 |
| `LoadGameEvent` | 读档 | 检查损失/失窃间隔 |
| `LeaveToMainMenuEvent` | 回主菜单 | 检查损失、最近失窃 |
| `GameExitEvent` | 退出游戏 | 同上 |
| `GameOverEvent` | 失败 | `Reason` |
| `OnSleepEvent` | 睡觉跨天 | 财富估值、八派系声望、保险/警报、Afterhours 活动 |

`OnSleepEvent` 声望字段：`RepLowerLevel`、`RepUpperLevel`、`RepSecurity`、`RepBlackMarket`、`RepRevolution`、`RepTourist`、`RepChurch`、`RepCartel`。

### 5.2 经营与检查

| 事件 | 触发 | 特有字段 |
|---|---|---|
| `BusinessPermitBoughtEvent` | 买到营业许可 | — |
| `WildUIOpenedEvent` | 打开 Wilds Network UI | — |
| `WildUpgradePurchasedEvent` | 购买网络升级 | `UpgradeId` |
| `InspectorArrivedEvent` | 检查官到店 | `InspectorType`、`IsFromShowcase`、`HasSecurityGrace` |
| `InspectionBribeEvent` | 行贿 | `BribeAmount`、`HasSecurityGrace` |
| `OnInspectedEvent` | 检查结束 | `OutcomeType`、走私暗格、损失件数/价值、是否动用宽限 |
| `ItemOfInterestAcquisitionEvent` | 购得关注机器 | `MachineId`、`MachineryBoughtCount` |

### 5.3 鉴定、对质、通缉

| 事件 | 触发 | 特有字段 |
|---|---|---|
| `AppraisalGuildInteractionEvent` | 鉴定公会交互 | `Action` |
| `AppraisalSentEvent` | 送评一件物品 | `ItemId`、`ActualValue`、`SentValue` |
| `ConfrontEvent` | 对质 | `ItemId`、`ConfrontType`、`Outcome` |
| `CustomerReportedEvent` | 举报顾客 | `CustomerId`、`ReportType` |
| `WantedNotReportedEvent` | 通缉犯未举报 | `CustomerId` |

### 5.4 与玩法的对应关系（建议 Hook 点）

| 想拦截的行为 | 建议 Harmony 目标 |
|---|---|
| 新游戏发物品 | `NewGameData.HandleInitialItem`、`PlayerStore.InitialSave` |
| 开关门 / 跨天 | `PlayerStore.OpenShutter`、`EndDay`、`EndNight` |
| 现金变化 | 写 `playerCash` 或找成交回调 `StoreClient.onItemSold` |
| 声望 | `StoreReputation.ModReputation` |
| 检查结果 | `EmporiumAnalytics.TrackOnInspected` 或检查流程方法 |
| 升级解锁 | `NetworkUpgrade.Unlock` / `IsLockedInDemo` |
| 物品生成 | `DirectoryMaster.Item` |

UI Toolkit 的 `InputEvent`、`TooltipEvent` 等属于引擎层，与玩法事件无关。

---

## 6. 物品图鉴

分类来自本地化提取，与 Directory 类不完全一一对应（例如「杂项」涵盖多个 Directory）。带描述与风味文本的完整表：`output/items_full_list.md`。


### 杂项（132）

| ID | 英文名 | 中文名 |
|---|---|---|
| 100ml_cylinder | 100ml Graduated Cylinder | 100毫升量筒 |
| 1ml_dropper | 1ml Dropper | 1毫升滴管 |
| 25ml_cylinder | 25ml Graduated Cylinder | 25毫升量筒 |
| 50ml_cylinder | 50ml Graduated Cylinder | 50毫升量筒 |
| 5ml_dropper | 5ml Dropper | 5毫升滴管 |
| advanced_flux_agent | Flux Smelting Agent (Advanced) | 助熔剂（高级） |
| age_well | AgeWell | 催陈器 |
| alarm |  |  |
| ancient_alien_relics | "Ancient Alien Relics" | “远古外星遗物” |
| aquascan | AquaScan | 水质扫描仪 |
| bandage | Basic Bandage | 基础绷带 |
| black_lamp | Black Lamp | 暗灯 |
| blank_keycard | Disposable Keycard (Blank) | 一次性钥匙卡（空白） |
| blood_bag | Blood Bag | 血袋 |
| blue_blood_bag | Bag of "Blue Blood" | 一袋“蓝血” |
| c4 | Plastic Explosive | 塑性炸药 |
| c4_set | Plastic Explosive (Armed) | 塑性炸药（已激活） |
| canister_mbs | MBS Nerve Gas | MBS神经毒气 |
| card_chem | Business Card (Chemist) | 名片（化学家） |
| card_mining | Business Card (GP Mining Coop) | 名片（GP采矿合作社） |
| card_pharma | Business Card (Pharmacist) | 名片（药商） |
| card_rev | Business Card (Green) | 名片（绿） |
| cassette_player | Cassette Player | 磁带播放器 |
| cat_bar | Cat Chocolate Bar | 猫咪巧克力棒 |
| cert1 | Appraisal Board Junior Certificate | 鉴定委员会初级证书 |
| chem_finisher | Chem Finisher | 化学成品机 |
| cigarette_color | Hemingway Color Checker | 海明威色卡 |
| cmd_keycard | Disposable Keycard (Command) | 一次性钥匙卡（指挥） |
| combat_machete | Combat Machete | 战斗砍刀 |
| common_chemical | Chemical Supplies (Common) | 化学用品（普通） |
| common_electronic | Electronic Parts (Common) | 电子元件（普通） |
| common_medical | Medical Supplies (Common) | 医疗用品（普通） |
| crowbar | Crowbar | 撬棍 |
| cup_noodle | Instant Ramen | 速食拉面 |
| desequencer | Cryptographic Desequencer | 密码解序器 |
| dossier | Dossier | 档案箱 |
| drain | Water Drain | 排水口 |
| dream_dust | Vial of "Dream Dust" | 一小瓶“梦尘” |
| energy_credit | Energy Cell | 能量电池 |
| energy_credit_breeder | Self Charging Energy Cell | 自充电能量电池 |
| energy_credit_ext | Energy Cell (Mk. II) | 能量电池（2型） |
| energy_drink | Energy Drink | 能量饮料 |
| eng_keycard | Disposable Keycard (Engineering) | 一次性钥匙卡（工程） |
| exchange_directive | Underground Exchange Directive | 地下交易所清单 |
| fanny_pack | Fanny Pack | 腰包 |
| fat_meat | Animal Fat | 动物脂肪 |
| faucet | Water Faucet | 水龙头 |
| flashlight | Flashlight | 手电筒 |
| flux_agent | Flux Smelting Agent (Basic) | 助熔剂（基础） |
| furnace | Furnace | 熔炉 |
| galaxy_blend | Galaxy Blend | 繁星果糊 |
| gl | Underbarrel 25mm Grenade Launcher | 下挂式25毫米榴弹发射器 |
| glass_shard | Glass Shard | 碎玻璃 |
| glass_shard_shiv | Glass Shiv | 玻璃刀 |
| hand |  |  |
| handnote | Handnote | 手写便签 |
| hatchet | Hatchet | 短柄斧 |
| hemostatic_bandage | Hemostatic Bandage | 止血绷带 |
| joe_card | Business Card (Joe Wild) | 名片（乔·王尔德） |
| kitchen_cleaver | Meat Cleaver | 切肉刀 |
| labeler | Labeler | 标签打印机 |
| labeler_blue | Blue Labeler | 蓝色标签打印机 |
| li_eat_snackbar | Li-Eat Snack Bar | 轻食能量棒 |
| magnifier | Magnifying Glass | 放大镜 |
| mentor_contract | Lease Agreement | 租赁协议 |
| mirage_projector | Mirage Projector | 幻影投影仪 |
| modified_access_card | Modified Access Card | 篡改识别卡 |
| moisture_farm | Moisture Farm | 水分收集器 |
| mouse_trap | Mouse Trap | 捕鼠夹 |
| neuroactive_perfume | SYNC Neuroactive Perfume | “同步”神经活性香水 |
| newspaper | Newspaper | 报纸 |
| nightmare_dust | Vial of "Nightmare Dust" | 一小瓶“梦魇尘” |
| node |  |  |
| node_medium | Node (Medium) | 节点（中） |
| node_small | Node (Small) | 节点（小） |
| nuclear_waste | Radioactive Waste | 放射性废料 |
| nudka | Nudka | 努特加 |
| pack_condom | Box of REX Condoms | 一盒瑞克斯避孕套 |
| packet_red_cigarette | Pack of Hemingway Cigarettes | 一包海明威香烟 |
| paper_towel | Roll of Paper Towels | 一卷纸巾 |
| pheromone_perfume | L'ESSENCE Pheromone Perfume | “本源”费洛蒙香水 |
| pipe_weapon | Lead Pipe | 铅管 |
| plasma_fuel | Plasma Cartridge | 等离子燃料匣 |
| portable_water_purifier | HydraTech Micro Water Purifier | 海德拉科技微型净水器 |
| postit | Postit | 便利贴 |
| powerblock | PowerBloc | 能量阵列 |
| processed_cheese | Processed Cheese | 合成奶酪 |
| processed_juice | Puice | 代糖果汁 |
| processed_meat | Peat | “泥炭”合成肉 |
| processed_milk | Pilk | 碳酸代乳 |
| projector |  |  |
| rare_electronic | Electronic Parts (Rare) | 电子元件（稀有） |
| raw_meat | Raw Meat (Standard) | 生肉（标准） |
| recharger | Recharger | 充能器 |
| restricted_chemical | Chemical Supplies (Restricted) | 化学用品（管制） |
| restricted_medical | Medical Supplies (Restricted) | 医疗用品（管制） |
| rubbing_alcohol | Rubbing Alcohol | 医用酒精 |
| salve | Nightingale's Salve | 南丁格尔软膏 |
| satchel | Satchel (Small) | 挎包（小） |
| scav_token | Scavenger's Token | 拾荒者信物 |
| sci_keycard | Disposable Keycard (Research) | 一次性钥匙卡（研发） |
| screwdriver | Screwdriver | 螺丝刀 |
| sec_keycard | Disposable Keycard (Security) | 一次性钥匙卡（治安） |
| security_alarm | Alarm System | 警报系统 |
| ser_keycard | Disposable Keycard (Service) | 一次性钥匙卡（服务） |
| shampoo | Bottle of 4 In 1 Wash | 一瓶四合一洗涤剂 |
| skincare_cream | ETERNAL Rejuvenation Serum | “永恒”焕活精华 |
| small_raw_meat | Raw Meat (Small) | 生肉（小） |
| smelling_salt | Smelling Salts | 嗅盐 |
| soda_red | Soda | 汽水 |
| stun_baton | Stun Baton | 眩晕警棍 |
| sup_keycard | Disposable Keycard (Supply) | 一次性钥匙卡（补给） |
| tazer | Tazer | 电击枪 |
| toilet_paper | Roll of Toilet Paper | 一卷厕纸 |
| toothpaste | Tube of Toothpaste | 一支牙膏 |
| topical_bandage | Topical Medication Bandage | 外用药膏绷带 |
| turbo_booster | Disposable Turbo Booster | 一次性涡轮增压器 |
| turbo_booster_adv | Advanced Turbo Booster | 高级涡轮增压器 |
| used_water_testing_strip | Water Testing Strip (Used) | 水质检测试纸（已使用） |
| uv_filter | UV Lamp | 紫外线灯 |
| wanted_paper | Security Wanted List | 治安部通缉名单 |
| water_filter | Water Filter | 滤水器 |
| water_filter_adv | Advanced Water Filter | 高级滤水器 |
| water_jug | Jug of Water | 桶装水 |
| water_pitcher | Water Pitcher |  |
| water_purifier | Water Purifier | 净水器 |
| water_tablet | Water Purification Tablet | 净水药片 |
| water_test_strip | Water Testing Strip | 水质检测试纸 |
| welder | Plasma Cutter | 等离子切割机 |
| wire | Wire | 线缆 |
| wire_cutter | Wire Cutter | 剪线钳 |
| zerochew | ZeroChew Tab | 一板零嚼 |

### 机器（20）

| ID | 英文名 | 中文名 |
|---|---|---|
| 3d_printer | 3D Printer | 3D打印机 |
| blender | Blender | 搅拌机 |
| evaporator | Evaporator | 蒸发器 |
| evaporator_module_solvent_recovery | Evaporator Solvent Recovery Module | 蒸发器溶剂回收模块 |
| feed_dispenser | Livestock Feed Dispenser | 牲畜饲料分配器 |
| heating_plate | Heating Plate | 加热板 |
| printer_module_metal | Metal Printer Module | 金属打印模块 |
| printer_plastic | 3D Printing Filament | 3D打印耗材 |
| system_capped_neural_core | Neural Core Module (Capped) | 神经核心模组（受限） |
| system_module_corrupt | Corrupted Module | 损坏模组 |
| system_module_eco | Eco Module | 环保模组 |
| system_module_efficiancy | Efficiency Module | 效率模组 |
| system_module_fineness | Refinement Module | 精炼模组 |
| system_module_overclock | Overclock Module | 超频模组 |
| system_module_performance | Performance Module | 性能模组 |
| system_module_quality | Quality Module | 质量模组 |
| system_module_ruined | Ruined Module | 报废模组 |
| system_module_streamlining | Streamlining Module | 优化模组 |
| system_uncapped_neural_core | Neural Core Module (Uncapped) | 神经核心模组（无限制） |
| vacuum_robot | Cleaner Robot | 清洁机器人 |

### 模块（13）

| ID | 英文名 | 中文名 |
|---|---|---|
| alarm_module_transmitter | Alarm Transmitter Module | 警报传输模组 |
| blank_module | Blank Module | 空白模组 |
| chem_module | Chemical Equipment Module | 化学设备模块 |
| crypto_module_cmd | Cryptographic Desequencer Chip (Command) | 密码解序器芯片（指挥） |
| crypto_module_eng | Cryptographic Desequencer Chip (Engineering) | 密码解序器芯片（工程） |
| crypto_module_med | Cryptographic Desequencer Chip (Medical) | 密码解序器芯片（医疗） |
| crypto_module_sec | Cryptographic Desequencer Chip (Security) | 密码解序器芯片（治安） |
| crypto_module_ser | Cryptographic Desequencer Chip (Service) | 密码解序器芯片（服务） |
| crypto_module_sup | Cryptographic Desequencer Chip (Supply) | 密码解序器芯片（补给） |
| furnace_module_blast | Furnace Module (Blast) | 熔炉模组（高炉） |
| furnace_module_junk | Furnace Module (Junk Processing) | 熔炉模组（垃圾处理） |
| module_extractor | Module Extractor (Basic) | 模组提取器（基础） |
| module_extractor_advanced | Module Extractor (Advanced) | 模组提取器（高级） |

### 武器/配件（71）

| ID | 英文名 | 中文名 |
|---|---|---|
| ammo_display | Ammo Display | 弹药显示器 |
| armor_conditioner_system | Armor Conditioner System |  |
| armor_lining | Kotton Lining | 棉绒衬层 |
| armored_hull | Armored Hull |  |
| barrel | Attachable Extended Barrel | 可接式加长枪管 |
| bipod | Bipod | 两脚架 |
| compensator | Compensator | 枪口补偿器 |
| flashbang_grenade | Flashbang Grenade | 闪光弹 |
| glock_receiver | Sentinel Mk. III. | 哨兵3型。 |
| grip | Foregrip | 前握把 |
| grip_gel | Tactile Memory Grip Gel | 触觉记忆握把凝胶 |
| gun_part | Gun Parts | 枪械零件 |
| handmade_pistol | Nestfire Compact | “巢火”紧凑型手枪 |
| heavy_duty_hull | Heavy Duty Hull |  |
| heavy_handmade_pistol | Ironcraft 10 | “铁铸10”重型手枪 |
| heavy_pistol_ammo | 10mm Ammunition | 10毫米弹药 |
| heavy_pistol_ammo_nl | 10mm Ammunition (Non-Lethal) | 10毫米弹药（非致命） |
| heavy_pistol_ammo_p | 10mm Ammunition (AP) | 10毫米弹药（穿甲弹） |
| laser | Laser Sight | 激光瞄具 |
| laser2 | Target Acquisition Device | 目标捕获装置 |
| laser_toy | Toy Laser Pointer | 玩具激光笔 |
| m16_receiver | M16 Receiver |  |
| mag_10mm | 10mm Magazine | 10毫米弹匣 |
| mag_10mm_ext | Extended 10mm Magazine | 10毫米加长弹匣 |
| mag_10mm_high | High Capacity 10mm Magazine | 10毫米大容量弹匣 |
| mag_10mm_smg | 10mm SMG Magazine | 10毫米冲锋枪弹匣 |
| mag_10mm_smg_box | 10mm SMG Box Magazine | 10毫米冲锋枪弹鼓 |
| mag_10mm_smg_high | 10mm High Capacity SMG Magazine | 10毫米冲锋枪大容量弹匣 |
| mag_22 | .22 Magazine | .22弹匣 |
| mag_22_ext | Extended .22 Magazine | .22加长弹匣 |
| mag_22_high | High Capacity .22 Magazine | .22大容量弹匣 |
| makeshift_hull | Makeshift Hull |  |
| match_barrel | Match Grade Barrel | 比赛级枪管 |
| molotov_cocktail | Molotov Cocktail |  |
| permit_gun_1 | Class 1 Weapon Permit | 一级武器许可证 |
| permit_gun_2 | Class 2 Weapon Permit | 二级武器许可证 |
| permit_gun_3 | Class 3 Weapon Permit | 三级武器许可证 |
| pistol_switch | Pistol Auto Sear | 手枪全自动阻铁 |
| printed_gun | Liberator 3D Printed Pistol | “解放者”3D打印手枪 |
| printer_chip |  |  |
| printer_chip_10_mag | 3D Printer Chip (x{0} 10MM Magazine) | 3D打印芯片（x{0} 10毫米弹匣） |
| printer_chip_10_mag_ext | 3D Printer Chip (x{0} Ext. 10MM Mag.) | 3D打印芯片（x{0} 10毫米加长弹匣） |
| printer_chip_10_mag_high | 3D Printer Chip (x{0} High Cap. 10MM Mag.) | 3D打印芯片（x{0} 10毫米大容量弹匣） |
| printer_chip_22_mag | 3D Printer Chip (x{0} .22 Magazine) | 3D打印芯片（x{0} .22弹匣） |
| printer_chip_22_mag_ext | 3D Printer Chip (x{0} Ext. .22 Mag.) | 3D打印芯片（x{0} .22加长弹匣） |
| printer_chip_22_mag_high | 3D Printer Chip (x{0} High Cap. .22 Mag.) | 3D打印芯片（x{0} .22大容量弹匣） |
| printer_chip_laser_sight | 3D Printer Chip (x{0} Laser Sight) | 3D打印芯片（x{0} 激光瞄具） |
| printer_chip_makeshift_rds | 3D Printer Chip (x{0} Makeshift RDS) | 3D打印芯片（x{0} 简易红点瞄具） |
| printer_chip_makeshift_toy_laser | 3D Printer Chip (x{0} Toy Laser Pointer) | 3D打印芯片（x{0} 玩具激光笔） |
| printer_chip_pistol | .22 Pistol 3D Printer Chip | .22手枪3D打印芯片 |
| printer_chip_rds | 3D Printer Chip (x{0} RDS) | 3D打印芯片（x{0} 红点瞄具） |
| printer_chip_silencer | 3D Printer Chip (x{0} Silencer) | 3D打印芯片（x{0} 消音器） |
| printer_chip_small_bottle | 3D Printer Chip (x{0} Small Plastic Bottle) | 3D打印芯片（x{0} 小塑料瓶） |
| rds | Red Dot Sight | 红点瞄具 |
| rds_makeshift | Makeshift Red Dot Sight | 简易红点瞄具 |
| revolver | Lancewell Revolver | 兰斯韦尔左轮手枪 |
| short_stock | Buckler Stock | 圆盾短枪托 |
| shotgun | Rampart Dual-Action Shotgun | “壁垒”双动式霰弹枪 |
| shotgun_stock | Shotgun Stock |  |
| silencer | Suppressor | 消音器 |
| silencer2 | Night Owl Suppressor | 夜枭消音器 |
| silencer_makeshift | Makeshift Suppressor | 简易消音器 |
| small_pistol_ammo | .22 SR Ammunition | .22 SR弹药 |
| small_pistol_ammo_nl | .22 SR Ammunition (Non-Lethal) | .22 SR弹药（非致命） |
| small_pistol_ammo_p | .22 SR Ammunition (AP) | .22 SR弹药（穿甲） |
| smg | Peacemaker Heavy SMG | “维和者”重型冲锋枪 |
| smoke_grenade | Smoke Grenade | 烟雾弹 |
| stock | Guardian Stock | 守护者枪托 |
| storage_bay_gun | Gunsmith Storage Bay | 枪匠储物舱 |
| stun_gun | PulseGuard Stun Gun | “脉冲卫士”电击枪 |
| trigger_group | Tuned Trigger Group | 调校扳机组件 |

### 工具（11）

| ID | 英文名 | 中文名 |
|---|---|---|
| aug_scanner | Aug Scanner | 改造体扫描仪 |
| chem_scanner | Composition Spectrometer | 成分光谱仪 |
| combat_knife | Combat Knife | 战斗匕首 |
| genetic_scanner | Gene Scanner | 基因扫描仪 |
| kitchen_knife | Kitchen Knife | 厨刀 |
| metal_scanner | Scav Scanner | 拾荒扫描仪 |
| skinning_knife | Skinning Knife |  |
| spectral_analyser | Spectral Analyser |  |
| surgery_tool | Surgery Toolset | 外科手术工具套装 |
| wrench | Wrench |  |
| xray_scanner | Portable XRay Scanner | 便携式X射线扫描仪 |

### 背包（5）

| ID | 英文名 | 中文名 |
|---|---|---|
| backpack_large | Backpack (Large) | 背包（大） |
| backpack_large_military | Large Military Backpack | 大型军用背包 |
| backpack_medium | Backpack (Basic) | 背包（基础） |
| backpack_medium_military | Backpack (Army-Issue) | 背包（军用） |
| backpack_small | Backpack (Small) | 背包（小） |

### 材料（9）

| ID | 英文名 | 中文名 |
|---|---|---|
| battery | Battery |  |
| common_ore | Metal Ore | 金属矿石 |
| ingot_book | Metallurgy Manual | 冶金手册 |
| internal_springs | High Durability Internal Springs | 高耐久内部弹簧 |
| metal_ingot | Metal Ingot | 金属锭 |
| nuts_metal | Metal Screws | 金属螺丝 |
| rare_ore | Rare Metal Ore | 稀有金属矿石 |
| scrap_metal | Scrap Metal | 废金属 |
| sign_material | Material Neon Sign | 材料霓虹灯牌 |

### 酿酒（20）

| ID | 英文名 | 中文名 |
|---|---|---|
| beer_case | Red Imp Beer Case | 一箱红魔啤酒 |
| bottle_hot_sauce | Hot Sauce | 辣酱 |
| bottle_printer | Bottle Printer | 水瓶打印机 |
| bottled_water | Bottle of Water (Standard) | 瓶装水（标准） |
| bottled_water_premium | Bottle of Spring Water | 瓶装泉水 |
| card_brewer | Business Card (Red Imp Brewery) | 名片（红魔鬼酿酒厂） |
| empty_beer_bottle | Empty Beer Bottle | 空啤酒瓶 |
| fermentation_airlock | Fermentation Airlock |  |
| large_bottled_water | Bottle of Water (Large) | 瓶装水（大） |
| mini_bottle | Bottle of Water (Micro) | 瓶装水（微型） |
| red_beer | Red Imp Beer | 红魔鬼啤酒 |
| small_bottled_water | Bottle of Water (Small) | 瓶装水（小） |
| wine_berry | BloomBerry | 荧光莓 |
| wine_book | BloomBerry Wine Fermenting Guide | 荧光莓果酿发酵指南 |
| wine_bottle | Wine Bottle | 酒瓶 |
| wine_gloomberry | GloomBerry Wine | 阴光莓果酿 |
| wine_superyeast | Super Yeast | 超级酵母 |
| wine_yeast | Yeast | 酵母 |
| wine_yeast_infinite | Yeast Bioreactor | 酵母生物反应器 |
| wine_yeast_red | Synthetic Yeast | 合成酵母 |

### 医疗（27）

| ID | 英文名 | 中文名 |
|---|---|---|
| bicarsole_pill_bottle | Bicarsole Pill Bottle |  |
| birth_control_pill | Birth Control Pill | 避孕药 |
| black_injector | Synaprest Injector | 赛纳普斯注射器 |
| caffeine_pill | Caffeine Pill | 咖啡因药片 |
| fanta_pill | Fanta Pill | 芬太片 |
| fixalin_pill_bottle | Fixalin Pill Bottle |  |
| injector_guide | Immunivax Assessment Guide | 免疫宁检测指南 |
| injector_pouch | Injector Pouch |  |
| large_purple_injector | Immunivax Injector | 免疫宁注射器 |
| med_bottle_blue | Bottle of Basic Solution | 一瓶碱性溶液 |
| med_bottle_orange | Bottle of Reducing Agent | 一瓶还原剂 |
| med_bottle_red | Bottle of Acidic Solution | 一瓶酸性溶液 |
| med_bottle_small_pink | Bottle of Lipobond Agent | 一瓶脂键剂 |
| med_bottle_violet | Bottle of N-Methylol Base | 一瓶N-羟甲基碱 |
| med_box | Medical Bay Supply Crate | 医疗舱物资箱 |
| med_keycard | Disposable Keycard (Medical) | 一次性钥匙卡（医疗） |
| ocutol_pill_bottle | Ocutol Pill Bottle |  |
| oxycodone_pill_bottle | Oxycodone Pill Bottle |  |
| phagimycin_pill | Phagimycin Pill | 噬菌霉素药片 |
| pill_bottle | Pill Bottle |  |
| pink_alt_injector | Nomore Injector | 奥克莫吸注射器 |
| pink_injector | Oxymore Injector | 奥克西莫注射器 |
| pure_white_injector | Naloxgone Injector | 纳洛通注射器 |
| serum_green |  |  |
| serum_red |  |  |
| unlicensed_phagimycin_pill | Unlicensed Phagimycin Pill | 无证噬菌霉素药片 |
| zyanide_pill | Zyanide Pill | 氰化物药片 |

### 种植/水培（26）

| ID | 英文名 | 中文名 |
|---|---|---|
| bloomberry_seed | Bloomberry Seed | 花莓种子 |
| dream_cap | Dream Cap | 梦幻菌盖 |
| dream_cap_seed | Dream Cap Spores | 梦幻菌盖孢子 |
| farm_module_dream_cap | Dream Cap Neutralizer Hydroponic Module | 梦幻菌盖中和水培模块 |
| farm_module_fillerweed_production | Fillerweed Production Hydroponic Module | 填充草增产水培模块 |
| farm_module_hydroreed_filter | Hydroreed Filter Hydroponic Module | 水芦过滤器水培模块 |
| farm_module_kotton_loom | Kotton Auto Loom Hydroponic Module | 棉绒自动织机水培模块 |
| farm_module_nightmare_cap | Dream Cap Nightmare Hydroponic Module | 噩梦菌盖水培模块 |
| farm_module_nutrifruit | Nutrifruit Hydroponic Module | 营养果水培模块 |
| farm_module_smuggler | Hydroponic Smuggler Module | 水培走私模块 |
| fillerweed | Fillerweed | 填充草 |
| fillerweed_seed | Fillerweed Seed | 填料草种子 |
| hydroponic | Hydroponic System | 水培系统 |
| hydroponic_guide | Hydroponic Farming Manual | 水培种植手册 |
| hydroponic_nutrient_tablet | Hydroponic Nutrient Tablet | 水培营养片 |
| hydroreed_filter | Hydroreed Filter | 水芦过滤器 |
| hydroreed_seed | Hydroreed Seed | 水芦种子 |
| kotton_fabric | Kotton Fabric | 韧棉织物 |
| kotton_fiber | Kotton Fiber | 棉绒纤维 |
| kotton_seed | Kotton Seed | 韧棉种子 |
| nightmare_cap | Nightmare Cap | 噩梦菌盖 |
| nutrifruit | Nutrifruit | 营养果 |
| nutrifruit_seed | Nutrifruit Seed | 营养果种子 |
| nutrifruit_seed_packet | Packet of Nutrifruit Seeds | 一包营养果种子 |
| plant_analyser | Plant Analyser | 植物分析仪 |
| wine_bloomberry | BloomBerry Wine | 荧光莓果酿 |

### 容器/设施（29）

| ID | 英文名 | 中文名 |
|---|---|---|
| box_cutter | Box Cutter | 美工刀 |
| box_tampon | Box of PAX Tampons | 一盒帕克斯卫生棉条 |
| eng_box | Engineering Foundry Supply Crate | 工程铸造厂物资箱 |
| evidence_box | Security Department Evidence Locker | 治安部物证柜 |
| expedition_box | Expedition Supply Box | 远征补给箱 |
| large_storage_bay | Large Storage Bay |  |
| lunch_box | Lunch Box |  |
| machine_bay | Machine Bay | 机器区 |
| machine_bay_ext | Machine Bay (Expanded) | 机器区（扩建） |
| makeshift_storage_bay | Makeshift Storage Bay | 简易储物舱 |
| medical_pouch | Medical Pouch |  |
| module_bay_expansion_kit | Module Bay Expansion Kit | 模组舱扩建套件 |
| nutrient_tablet_container | Hydroponic Nutrient Tablet Bottle | 水培营养片药瓶 |
| safe | Safe |  |
| sec_box | Security Department Supply Crate | 治安部物资箱 |
| service_box | Service Department Supply Crate | 后勤服务部物资箱 |
| smuggler_bay | Smuggler's Bay | 走私者暗格 |
| smuggler_bay_mini | Mini Smuggler's Bay | 迷你走私舱 |
| smuggler_bay_mod | Smuggler's Bay (Modified) | 走私者暗格（改进） |
| storage_bay | Storage Bay | 储藏区 |
| storage_bay_chem | Chemist Storage Bay | 化学家储物舱 |
| storage_bay_large | Storage Bay (Extended) | 储藏区（扩建） |
| toolbox | Toolbox |  |
| vending_fountain | Vending Fountain | 自动售水机 |
| vending_fountain_core | Vending Fountain Core | 售水机核心 |
| vending_machine | Vending Machine | 自动售货机 |
| vending_machine_core | Vending Machine Core | 自动售货机核心 |
| water_tablet_container | Bottle of Water Purification Tablets | 一瓶净水药片 |
| water_test_container | Water Testing Kit | 水质检测试剂盒 |

### 文书/杂项（27）

| ID | 英文名 | 中文名 |
|---|---|---|
| business_permit | Business Permit | 营业许可证 |
| chemistry_guide | Chemistry Manual | 化学手册 |
| cigarette_guide | Hemingway Identification Guide | 海明威鉴定指南 |
| codebook | Codebook |  |
| deed | Deed | 产权契据 |
| expedition_log | Expedition Log | 远征日志 |
| fuel_guide | Plasma Cartridge Appraisal Guide | 等离子燃料匣鉴定指南 |
| hand_guide |  |  |
| intel | Intel |  |
| intel_sec | Security Record | 治安部档案 |
| logo_checker | Republic Logo Checker | 共和国标志校验卡 |
| lottery_info | Lower Levels Lottery Information | 下层区彩票说明 |
| lottery_ticket | Lottery Ticket | 彩票 |
| lottery_ticket_old | Old Lottery Ticket | 旧彩票 |
| procurement_slip | Procurement Slip | 采购单 |
| scav_journal | Scav's journal entry | 拾荒者的日志 |
| sec_slip | Incident Slip | 事件回执单 |
| sign_expedition | Expedition Sign | 远征招募牌 |
| sign_generic |  |  |
| sign_household | Household Item Neon Sign | 日用品霓虹灯牌 |
| sign_luxury | Luxury Item Neon Sign | 奢侈品霓虹灯牌 |
| sign_medical | Medical Neon Sign | 医疗霓虹灯牌 |
| sign_water | Water Neon Sign | 水霓虹灯牌 |
| slip | Slip | 单据 |
| stamp_guide | Food Stamp Identification Handbook | 食品券鉴定手册 |
| tutorial_book | Mentor's Handbook | 导师手册 |
| water_guide | Water Trading Manual | 水资源交易手册 |

### 食物（7）

| ID | 英文名 | 中文名 |
|---|---|---|
| coffee_bean | Coffee Beans | 咖啡豆 |
| food_stamp | Food Stamp | 食品券 |
| meal_cap | Meal Cap | 食用菌盖 |
| morsel | Morsel |  |
| ribwich | Packaged Rib Sandwich | 包装肋排三明治 |
| ribwich_guide | Ribwich Appraisal Guide | 肋排堡鉴定指南 |
| sign_food | Food Neon Sign | 食品霓虹灯牌 |

### 养殖/牲畜（9）

| ID | 英文名 | 中文名 |
|---|---|---|
| dehydrated_water | 100% Pure Dehydrated Water | 100%脱水纯水 |
| feces_large | Animal Feces (Large) | 动物粪便（大） |
| feces_medium | Animal Feces | 动物粪便 |
| feces_small | Animal Feces (Small) | 动物粪便（小） |
| rat | Rat | 老鼠 |
| scratcher | Scratcher Ticket | 刮刮乐彩票 |
| scratcher_stack | Stack of Scratcher Tickets (5) | 一叠刮刮乐彩票（5张） |
| water_ration | Sealed Water Ration (Standard) | 密封水配给包（标准） |
| water_ration_small | Sealed Water Ration (Small) | 密封水配给包（小） |

### 废品（4）

| ID | 英文名 | 中文名 |
|---|---|---|
| junk | Junk | 垃圾 |
| meat_scrap | Offal | 动物下水 |
| trash_pile | Trash Pile |  |
| trashcan | Trash Can | 垃圾桶 |

---

## 7. 附录

### 7.1 店铺空间（EmporiumEntry 库存）

| 字段 | 用途 |
|---|---|
| `invElement` | 主柜台 / 玩家库存 |
| `showcaseElement` | 展示柜（吸引顾客） |
| `frontInvinvElement` / `backInvinvElement` | 店前 / 店后 |
| `hiddenElement` | 隐藏 / 走私空间 |
| `trashInvElement` | 垃圾桶（付清洁费后夜间清空） |
| `drainInvElement` | 排水口 |
| `faucetElement` | 水龙头 |
| `docInvElement` | 文件栏 |
| `cassettePlayerElement` | 磁带机 |
| `vendingMachineElement` / `vendingFountainElement` | 售货机 / 售水机 |
| `afterhourInventory` 及口袋槽 | Afterhours 外出负重 |
| `hireling` 相关窗口 | 雇员装备 |

### 7.2 顾客意图速查

`UNDEFINED, BUY, SELL, SELLNBUY, INSPECTION, DIALOGUE, BARTER, RENT, LOAN_SHARK, SPECIAL, INFORMATION_DEALER, PROCUREMENT_OFFER, PROCUREMENT_COLLECT, WHOLESALE, APPRAISAL_SERVICE, GUNSMITH, EXPEDITION`

### 7.3 雇员特质

`Fighter, Coward, Survivor, Murderous, Butcher, Addict, Antisocial, Lucky, Junker, TreasureHunter, Friendly`

### 7.4 相关模组

| 模组 | 作用 |
|---|---|
| Custom Start Framework | 按职业发物品 / 现金 / 升级 |

配置文件：游戏目录 `UserData/custom-start/{id}/profile.json`（需 **CustomStartFramework**）。

模组能做 / 不能做的完整对照见 [MOD_CAPABILITIES.md](./MOD_CAPABILITIES.md)。

### 7.5 符号导出

更新游戏后需重新 dump：

- `tools/Il2CppDumper/dump.cs` — 类型与方法
- `tools/item_translations.json` — 物品中英对照
- `output/items_full_list.md` — 全物品表

Steam 更新会替换 `GameAssembly.dll`，本指南中的 RVA / 字段偏移会失效，但类型名与物品 ID 通常更稳定。
