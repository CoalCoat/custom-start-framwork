# Examples / 示例

本目录与 **Custom Start Framework** 独立发布，不参与框架默认打包。  
游戏内需已安装 **CustomStartFramework.dll**。

## 赛博贝爷（The Cyber Bear）

| 项 | 值 |
|---|---|
| Profile ID | `the_cyber_bear_12` |
| 可见职业 | 一贫如洗 (12) |
| Perk 消耗 | 0 |
| 效果 | 拾荒当铺装备包，现金 -400 |

### 安装

将 `custom-start/the_cyber_bear_12/` 复制到 `UserData/custom-start/the_cyber_bear_12/`。

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

Copy `custom-start/the_cyber_bear_12/` to `UserData/custom-start/`, or use the bundled profile editor.
