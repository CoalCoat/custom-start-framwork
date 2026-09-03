# Examples / 示例

本目录与 **Custom Start Framework** 独立发布，不参与框架默认打包。  
游戏内需已安装 **CustomStartFramework.dll**。

## 拾荒开局（Scavenger Start）

| 项 | 值 |
|---|---|
| Profile ID | `nico_scavenger_start` |
| 可见职业 | 一贫如洗 (12) |
| Perk 消耗 | 2 |
| 效果 | 拾荒装备包，现金 -400 |

### 安装

将 `custom-start/nico_scavenger_start/` 复制到 `UserData/custom-start/nico_scavenger_start/`。

也可用框架自带的编辑器新建或修改 profile：

```bash
python framework/editor/edit_profiles.py -r "UserData/custom-start"
```

### 打包

```powershell
.\scripts\Pack-Example.ps1
```

---

## English

Independent from the **Custom Start Framework** release.

Copy `custom-start/nico_scavenger_start/` to `UserData/custom-start/`, or use the bundled profile editor.
