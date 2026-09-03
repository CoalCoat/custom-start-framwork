# Examples / 示例

本目录与 **Custom Start Framework** 独立发布，不参与框架默认打包。  
游戏内需已安装 **CustomStartFramework.dll**。

## 职业示例 Perk

每个 profile 仅对对应起始职业可见（`allowedStartTypes` 绑定）。  
**一贫如洗 (12)** 单独保留「赛博贝爷」示例；其余 12 个职业各一套主题 loadout。

| Profile ID | 名称 | 职业 | 现金 |
|---|---|---|---|
| `the_cyber_bear_12` | 赛博贝爷 | 一贫如洗 (12) | -400 |

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
