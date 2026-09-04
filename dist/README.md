# Custom Start Framework — release

Build with `scripts/Build.ps1` or pack with `scripts/Pack.ps1`.

| Output | Description |
|---|---|
| `CustomStartFramework-X.Y.Z.dll` | Single build; rename to `CustomStartFramework.dll` |
| `editor/` | Profile editor (`edit_profiles.py`) |
| `README.md` / `change.log` | Documentation |

The mod follows the game locale at runtime. Profile `name` / `description` use zh/en fields in `profile.json`.

Zip: `dist/custom-start-framework.zip`

Examples ship separately — see [`../example/`](../example/) and `scripts/Pack-Example.ps1`.
