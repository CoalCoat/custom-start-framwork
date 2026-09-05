#!/usr/bin/env python3
"""Custom Start Framework — profile editor for UserData/custom-start/{id}/."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tkinter as tk
from collections import deque
from copy import deepcopy
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = SCRIPT_DIR / "catalog.json"
DEFAULT_START_TYPES = SCRIPT_DIR / "start_types.json"
SETTINGS_FILE = SCRIPT_DIR / "editor_settings.json"
CATALOG_PREVIEW_LIMIT = 150
DESC_MAX_LEN_ZH = 150
DESC_MAX_LEN_EN = 250
ICON_SIZE = 32
ICON_ALPHA_CUTOFF = 32
ICON_BG_TOLERANCE = 36

# Matches WagesPerks / ExtraPerks embedded starting-perk icons (32x32, white glyph, transparent bg).
ICON_SYSTEM_PROMPT = """32x32 pixel art game perk icon for Probably Stolen (MelonLoader starting perk).
Style reference: WagesPerks and ExtraPerks perk icons — single white (#FFFFFF) silhouette glyph on a fully transparent background.
Monochrome 1-bit icon: no color, no grayscale shading, no gradients, no drop shadow, no glow.
Crisp point-filter pixels (no anti-aliasing), thick 2-4px lines, minimalist symbolic single subject centered.
Use negative space cutouts for internal detail; icon body fills about 30-45% of the canvas with generous transparent padding.
Flat 2D front view, no border, no frame, no badge, no text, no watermark.
Export: 32×32 PNG, RGBA, only pure white glyph + alpha transparency. Background color is NOT drawn in the icon; the game tints the perk slot by type (positive=green, negative=red, neutral=orange)."""

ICON_NEGATIVE_PROMPT = """color, multicolor, grayscale shading, gradient, drop shadow, glow, bevel, 3D, photorealistic,
anti-aliased smooth edges, background color, solid background, black background, white background fill,
border, frame, rounded badge, circle badge, text, letters, watermark, logo, noisy texture, detailed scenery"""



def resolve_default_root(script_dir: Path) -> Path:
    if not (script_dir / "catalog.json").is_file():
        return script_dir.parent.parent / "UserData" / "custom-start"
    for candidate in (
        script_dir.parent / "custom-start",
        script_dir.parent.parent / "example" / "custom-start",
        script_dir.parent.parent / "dist" / "example" / "custom-start",
    ):
        if candidate.is_dir():
            return candidate
    return script_dir.parent / "custom-start"


DEFAULT_ROOT = resolve_default_root(SCRIPT_DIR)

WATER_TYPES = ["", "pure", "high_quality", "base", "ghost", "rust", "gutterflow"]
PROFILE_FILE = "profile.json"
ICON_FILE = "icon.png"

FACTION_KEYS = [
    ("lower", {"zh": "下层区", "en": "Lower District"}),
    ("upper", {"zh": "上层区", "en": "Upper District"}),
    ("security", {"zh": "治安部", "en": "Security"}),
    ("black_market", {"zh": "黑市", "en": "Black Market"}),
    ("revolution", {"zh": "革命", "en": "Revolution"}),
    ("cartel", {"zh": "卡特尔", "en": "Cartel"}),
]

CONTRABAND_MARKUP_KEYS = [
    ("low", {"zh": "低", "en": "Low"}),
    ("mid", {"zh": "中", "en": "Mid"}),
    ("high", {"zh": "高", "en": "High"}),
    ("critical", {"zh": "严重", "en": "Critical"}),
]

UPGRADES = {
    "BREWER": {"zh": "酿酒师", "en": "Brewer"},
    "CHEMIST": {"zh": "化学家", "en": "Chemist"},
    "PHARMA": {"zh": "药剂", "en": "Pharma"},
    "MINER": {"zh": "矿工", "en": "Miner"},
    "LANDLORD_GRACE": {"zh": "房东宽限", "en": "Landlord Grace"},
    "SEC_GRACE": {"zh": "安保/监狱宽限", "en": "Security/Prison Grace"},
    "INSPECTION_INFORMANT": {"zh": "检查内线", "en": "Inspection Informant"},
    "WILD_FIXER": {"zh": "荒野销赃人/修理工", "en": "Wild Fixer"},
    "EVIDENCE_REMOVAL": {"zh": "清除证据", "en": "Evidence Removal"},
    "BUY_REFERAL": {"zh": "购买介绍", "en": "Buy Referral"},
    "SELL_REFERAL": {"zh": "销售介绍", "en": "Sell Referral"},
    "CRIMINEL_NETWORK": {"zh": "犯罪网络", "en": "Criminal Network"},
    "POWER_HIJACK": {"zh": "偷电", "en": "Power Hijack"},
    "COMMERCIAL_POWER": {"zh": "商业电力", "en": "Commercial Power"},
    "SHOWCASE_I": {"zh": "展柜 I", "en": "Showcase I"},
    "SHOWCASE_II": {"zh": "展柜 II", "en": "Showcase II"},
    "GUTTERFLOW_TAP": {"zh": "排水管接水", "en": "Gutterflow Tap"},
    "RUSTWATER_TAP": {"zh": "锈水接水", "en": "Rustwater Tap"},
    "RUINED_MACHINE_UNLOCK": {"zh": "破旧机器解锁", "en": "Ruined Machine Unlock"},
    "RETIRED_FARMER": {"zh": "退休农夫", "en": "Retired Farmer"},
    "RETIRED_GUNSMITH": {"zh": "退休枪匠", "en": "Retired Gunsmith"},
    "GUN_PERMIT_I": {"zh": "枪证 I", "en": "Gun Permit I"},
    "GUN_PERMIT_II": {"zh": "枪证 II", "en": "Gun Permit II"},
    "GUN_PERMIT_III": {"zh": "枪证 III", "en": "Gun Permit III"},
    "RETIRED_CHEMIST": {"zh": "退休化学家", "en": "Retired Chemist"},
    "RETIRED_RANCHER": {"zh": "退休牧场主", "en": "Retired Rancher"},
    "WATER_TRADER": {"zh": "水商", "en": "Water Trader"},
    "WINEMAKER": {"zh": "葡萄酒酿酒师", "en": "Winemaker"},
    "MARKETPLACE_REQUESTS": {"zh": "市场请求", "en": "Marketplace Requests"},
    "JACKSON1": {"zh": "Jackson 投资 I", "en": "Jackson Investment I"},
    "JACKSON2": {"zh": "Jackson 投资 II", "en": "Jackson Investment II"},
    "RENOVATION1": {"zh": "翻新 I", "en": "Renovation I"},
    "RENOVATION2": {"zh": "翻新 II", "en": "Renovation II"},
    "RENOVATION3": {"zh": "翻新 III", "en": "Renovation III"},
}

UI: dict[str, dict[str, str]] = {
    "app_title": {"zh": "自定义开局编辑器", "en": "Custom Start Editor"},
    "menu_file": {"zh": "文件", "en": "File"},
    "menu_language": {"zh": "语言", "en": "Language"},
    "menu_open_root": {"zh": "打开 custom-start 目录…", "en": "Open custom-start Folder…"},
    "menu_save": {"zh": "保存当前", "en": "Save Current"},
    "btn_save": {"zh": "保存", "en": "Save"},
    "btn_browse": {"zh": "浏览…", "en": "Browse…"},
    "menu_save_all": {"zh": "保存全部", "en": "Save All"},
    "menu_reload": {"zh": "重新扫描", "en": "Rescan"},
    "menu_exit": {"zh": "退出", "en": "Exit"},
    "lang_zh": {"zh": "中文", "en": "中文"},
    "lang_en": {"zh": "English", "en": "English"},
    "lang_pick_title": {"zh": "选择语言", "en": "Choose Language"},
    "lang_pick_prompt": {
        "zh": "请选择编辑器界面语言",
        "en": "Choose the editor interface language",
    },
    "profiles": {"zh": "自定义开局", "en": "Custom Starts"},
    "btn_new": {"zh": "新建", "en": "New"},
    "btn_delete": {"zh": "删除", "en": "Delete"},
    "btn_duplicate": {"zh": "复制", "en": "Duplicate"},
    "tab_meta": {"zh": "Perk 信息", "en": "Perk Info"},
    "tab_items": {"zh": "物品清单", "en": "Loadout"},
    "tab_cash": {"zh": "经济/店铺", "en": "Economy / Store"},
    "tab_upgrades": {"zh": "网络升级", "en": "Upgrades"},
    "tab_reputation": {"zh": "阵营声望 Δ", "en": "Faction Rep Δ"},
    "label_id": {"zh": "ID（自动生成）", "en": "ID (auto-generated)"},
    "label_name_zh": {"zh": "名称（中文）", "en": "Name (Chinese)"},
    "label_name_en": {"zh": "名称（英文）", "en": "Name (English)"},
    "label_desc_zh": {"zh": "描述（中文，最多150字）", "en": "Description (Chinese, max 150 chars)"},
    "label_desc_en": {"zh": "描述（英文，最多250字）", "en": "Description (English, max 250 chars)"},
    "label_cost": {"zh": "Perk 点数消耗", "en": "Perk point cost"},
    "label_type": {"zh": "类型 (0=正面 1=负面 2=中性)", "en": "Type (0=positive 1=negative 2=neutral)"},
    "label_allowed": {"zh": "可用起始职业", "en": "Allowed start types"},
    "allowed_hint": {
        "zh": "从右侧清单添加；留空 = 全部职业可见。ID 由英文名 + 起始职业自动生成。",
        "en": "Add from the picker on the right; empty = all start types. ID auto-generated from English name + start types.",
    },
    "start_type_unlisted": {"zh": "（未登记）", "en": "(unlisted)"},
    "btn_add": {"zh": "添加", "en": "Add"},
    "btn_delete": {"zh": "删除", "en": "Delete"},
    "label_icon": {"zh": "Perk 图标", "en": "Perk icon"},
    "btn_upload_icon": {"zh": "上传图标…", "en": "Upload icon…"},
    "icon_status_none": {"zh": "当前：未设置 icon.png", "en": "Current: no icon.png"},
    "icon_status_set": {"zh": "当前：已设置 icon.png（32×32 白剪影，底色由类型决定）", "en": "Current: icon.png set (32×32 white glyph; bg color from type)"},
    "icon_prompt_title": {"zh": "图标提示词（可复制到 AI 绘图）", "en": "Icon system prompt (copy to AI tools)"},
    "btn_copy_prompt": {"zh": "复制提示词", "en": "Copy prompt"},
    "prompt_copied": {"zh": "已复制到剪贴板", "en": "Copied to clipboard"},
    "catalog_title": {"zh": "物品库", "en": "Item Catalog"},
    "picker_title_start_types": {"zh": "起始职业清单", "en": "Start Types"},
    "picker_title_upgrades": {"zh": "网络升级清单", "en": "Network Upgrades"},
    "picker_title_none": {"zh": "清单", "en": "Picker"},
    "picker_hint_none": {
        "zh": "请切换到 Perk 信息 / 物品清单 / 网络升级 页使用右侧清单",
        "en": "Switch to Perk Info / Loadout / Upgrades tab to use the picker",
    },
    "allowed_list_title": {"zh": "已选起始职业", "en": "Selected start types"},
    "btn_remove_from_allowed": {"zh": "从列表移除", "en": "Remove from list"},
    "btn_clear_allowed": {"zh": "清空（=全部职业）", "en": "Clear (= all types)"},
    "picker_btn_add_allowed": {"zh": "添加到起始职业", "en": "Add start type"},
    "picker_btn_add_upgrade": {"zh": "添加到升级列表", "en": "Add upgrade"},
    "upgrades_list_title": {"zh": "已解锁升级", "en": "Unlocked upgrades"},
    "btn_remove_from_upgrades": {"zh": "从列表移除", "en": "Remove from list"},
    "search": {"zh": "搜索", "en": "Search"},
    "btn_add_simple": {"zh": "添加到新增列表", "en": "Add to Add List"},
    "btn_add_remove": {"zh": "添加到删除列表", "en": "Add to Remove List"},
    "items_add_title": {"zh": "新增物品", "en": "Items to add"},
    "items_remove_title": {"zh": "删除物品", "en": "Items to remove"},
    "btn_remove_from_add": {"zh": "从新增列表移除", "en": "Remove from add list"},
    "btn_remove_from_remove": {"zh": "从删除列表移除", "en": "Remove from remove list"},
    "label_extra_cash": {"zh": "额外现金 Δ", "en": "Extra cash Δ"},
    "label_extra_rent": {"zh": "额外租金 Δ", "en": "Extra rent Δ"},
    "label_attractiveness_delta": {"zh": "店铺吸引力 Δ", "en": "Store attractiveness Δ"},
    "label_contraband_markup_delta": {"zh": "违禁品加价 Δ（百分点）", "en": "Contraband markup Δ (percent points)"},
    "economy_tab_hint": {
        "zh": "以下数值均为「在起始职业默认值上的增减」，不是存档最终绝对值。0 = 不改动。一贫如洗参考：租金 200、吸引力 250、违禁品加价 35/70/100/200。",
        "en": "All values are deltas on the start-type baseline, not final save absolutes. 0 = no change. Penniless baseline: rent 200, attractiveness 250, contraband markup 35/70/100/200.",
    },
    "status_unsaved": {"zh": "未保存", "en": "Unsaved"},
    "status_loading": {"zh": "加载中…", "en": "Loading…"},
    "status_loading_catalog": {"zh": "加载物品库…", "en": "Loading item catalog…"},
    "catalog_search_hint": {
        "zh": "… 更多物品请输入上方搜索框",
        "en": "… type in the search box above for more items",
    },
    "confirm_delete": {"zh": "删除此自定义开局？", "en": "Delete this custom start?"},
    "invalid_id": {"zh": "无法生成有效 ID，请填写英文名称", "en": "Could not generate a valid ID; enter an English name"},
    "id_exists": {"zh": "目标 ID 已存在", "en": "Target ID already exists"},
    "error_numeric": {"zh": "数值字段无效", "en": "Invalid numeric field"},
    "error_title": {"zh": "错误", "en": "Error"},
    "confirm_title": {"zh": "确认", "en": "Confirm"},
}


class I18n:
    _lang = "zh"

    @classmethod
    def set_language(cls, lang: str) -> None:
        cls._lang = "en" if lang == "en" else "zh"

    @classmethod
    def t(cls, key: str) -> str:
        entry = UI.get(key, {})
        return entry.get(cls._lang) or entry.get("zh") or key


def t(key: str) -> str:
    return I18n.t(key)


def load_saved_language() -> str | None:
    if not SETTINGS_FILE.is_file():
        return None
    try:
        data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        lang = data.get("lang")
        return lang if lang in ("zh", "en") else None
    except Exception:
        return None


def save_saved_language(lang: str) -> None:
    if lang not in ("zh", "en"):
        return
    SETTINGS_FILE.write_text(json.dumps({"lang": lang}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def resolve_startup_language(cli_lang: str | None) -> str:
    if cli_lang in ("zh", "en"):
        save_saved_language(cli_lang)
        return cli_lang
    saved = load_saved_language()
    if saved:
        return saved
    I18n.set_language("zh")
    picked = ask_language()
    save_saved_language(picked)
    return picked


def slugify(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def generate_profile_id(name_en: str, allowed_start_types: list[int]) -> str:
    base = slugify(name_en) or "custom_start"
    if not allowed_start_types:
        return base
    suffix = "_".join(str(x) for x in sorted(set(allowed_start_types)))
    return f"{base}_{suffix}"


def empty_profile(profile_id: str) -> dict:
    return {
        "version": 1,
        "id": profile_id,
        "name": {"zh": "", "en": ""},
        "description": {"zh": "", "en": ""},
        "cost": 0,
        "type": 0,
        "allowedStartTypes": [],
        "items": [],
        "removeItems": [],
        "extraCash": 0,
        "extraRent": 0,
        "retailMarkupDelta": 0,
        "contrabandMarkupDelta": {k: 0 for k, _ in CONTRABAND_MARKUP_KEYS},
        "baseStoreAttractivenessDelta": 0,
        "unlockedUpgrades": [],
        "factionReputationDelta": {k: 0 for k, _ in FACTION_KEYS},
    }


def slug_ok(profile_id: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_-]+", profile_id or ""))


def load_start_types(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        print(f"start types file not found: {path}")
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {str(k): v for k, v in sorted(raw.items(), key=lambda item: int(item[0]))}


def sort_start_type_keys(keys: list[str]) -> list[str]:
    return sorted(keys, key=lambda k: int(k) if k.isdigit() else 0)


def scan_profiles(root: Path) -> dict[str, dict]:
    profiles: dict[str, dict] = {}
    if not root.is_dir():
        return profiles
    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        path = folder / PROFILE_FILE
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data.setdefault("id", folder.name)
            profiles[folder.name] = {"folder": folder, "data": data, "dirty": False}
        except Exception as e:
            print(f"skip {folder}: {e}")
    return profiles


def catalog_names(meta: dict) -> tuple[str, str]:
    en = meta.get("en") or meta.get("name_en") or ""
    zh = meta.get("zh") or meta.get("name_zh") or ""
    return en, zh


def bilingual_label(en: str, zh: str, item_id: str = "") -> str:
    if I18n._lang == "zh":
        first, second = zh, en
    else:
        first, second = en, zh
    if first and second and first != second:
        return f"{first} / {second}"
    return first or second or item_id


def clamp_text(text: str, max_len: int = DESC_MAX_LEN_ZH) -> str:
    text = text or ""
    return text if len(text) <= max_len else text[:max_len]


def _sample_corner_background(pixels, size: int) -> list[tuple[int, int, int]]:
    corners = ((0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1))
    samples: list[tuple[int, int, int]] = []
    for x, y in corners:
        r, g, b, a = pixels[x, y]
        if a >= ICON_ALPHA_CUTOFF:
            samples.append((r, g, b))
    return samples or [(255, 255, 255)]


def _is_opaque_background(r: int, g: int, b: int, bg_colors: list[tuple[int, int, int]], tolerance: int) -> bool:
    for br, bg, bb in bg_colors:
        if max(abs(r - br), abs(g - bg), abs(b - bb)) <= tolerance:
            return True
    return False


def _build_foreground_mask(pixels, size: int) -> list[list[bool]]:
    if _pixel_grid_has_transparency(pixels, size):
        return [[pixels[x, y][3] >= ICON_ALPHA_CUTOFF for x in range(size)] for y in range(size)]

    bg_colors = _sample_corner_background(pixels, size)
    is_background = [[False] * size for _ in range(size)]
    queue: deque[tuple[int, int]] = deque()

    def try_add(x: int, y: int) -> None:
        if x < 0 or x >= size or y < 0 or y >= size or is_background[y][x]:
            return
        r, g, b, a = pixels[x, y]
        if a < ICON_ALPHA_CUTOFF or _is_opaque_background(r, g, b, bg_colors, ICON_BG_TOLERANCE):
            is_background[y][x] = True
            queue.append((x, y))

    for x in range(size):
        try_add(x, 0)
        try_add(x, size - 1)
    for y in range(size):
        try_add(0, y)
        try_add(size - 1, y)

    while queue:
        x, y = queue.popleft()
        try_add(x + 1, y)
        try_add(x - 1, y)
        try_add(x, y + 1)
        try_add(x, y - 1)

    return [[not is_background[y][x] for x in range(size)] for y in range(size)]


def _pixel_grid_has_transparency(pixels, size: int) -> bool:
    transparent = 0
    for y in range(size):
        for x in range(size):
            if pixels[x, y][3] < ICON_ALPHA_CUTOFF:
                transparent += 1
    return transparent >= size * size * 0.05


def _apply_white_silhouette(resized, foreground: list[list[bool]]) -> None:
    pixels = resized.load()
    for y in range(ICON_SIZE):
        for x in range(ICON_SIZE):
            pixels[x, y] = (255, 255, 255, 255) if foreground[y][x] else (255, 255, 255, 0)


def process_icon_file(src: Path, dest: Path) -> None:
    from PIL import Image

    with Image.open(src) as img:
        img = img.convert("RGBA")
        width, height = img.size
        side = min(width, height)
        left = (width - side) // 2
        top = (height - side) // 2
        cropped = img.crop((left, top, left + side, top + side))
        resized = cropped.resize((ICON_SIZE, ICON_SIZE), Image.Resampling.NEAREST)
        pixels = resized.load()
        foreground = _build_foreground_mask(pixels, ICON_SIZE)
        _apply_white_silhouette(resized, foreground)
        resized.save(dest, format="PNG")


def build_icon_prompt(data: dict) -> str:
    name_en = data.get("name", {}).get("en", "").strip() or "Custom Start Perk"
    name_zh = data.get("name", {}).get("zh", "").strip()
    desc_en = clamp_text((data.get("description", {}).get("en", "") or "").strip(), DESC_MAX_LEN_EN)
    desc_zh = clamp_text((data.get("description", {}).get("zh", "") or "").strip(), DESC_MAX_LEN_ZH)

    subject_lines = [f'Subject perk: "{name_en}".']
    if name_zh:
        subject_lines.append(f'Chinese name: "{name_zh}".')
    if desc_en:
        subject_lines.append(f"Meaning (en): {desc_en}")
    if desc_zh:
        subject_lines.append(f"Meaning (zh): {desc_zh}")
    if not desc_en and not desc_zh:
        subject_lines.append("Concept: one simple symbolic object or silhouette that represents this custom starting loadout perk.")

    return "\n\n".join(
        [
            ICON_SYSTEM_PROMPT,
            "\n".join(subject_lines),
            f"Negative prompt:\n{ICON_NEGATIVE_PROMPT}",
        ]
    )


def ask_language() -> str:
    root = tk.Tk()
    root.title("选择语言 / Choose Language")
    root.resizable(False, False)
    choice: dict[str, str | None] = {"lang": None}

    frame = ttk.Frame(root, padding=16)
    frame.pack()
    ttk.Label(
        frame,
        text="请选择编辑器界面语言\nChoose the editor interface language",
        justify="center",
    ).pack(pady=(0, 12))
    btn_row = ttk.Frame(frame)
    btn_row.pack()

    def pick(lang: str) -> None:
        choice["lang"] = lang
        root.quit()

    ttk.Button(btn_row, text="中文", width=12, command=lambda: pick("zh")).pack(side="left", padx=6)
    ttk.Button(btn_row, text="English", width=12, command=lambda: pick("en")).pack(side="left", padx=6)

    def on_close() -> None:
        root.quit()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.update_idletasks()
    width, height = 360, 160
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    root.focus_force()
    root.mainloop()
    picked = choice["lang"] or "zh"
    root.destroy()
    return picked


class ProfileEditor(tk.Tk):
    def __init__(self, root_dir: Path, catalog_path: Path, start_types_path: Path, lang: str = "zh"):
        super().__init__()
        I18n.set_language(lang)
        self.title(t("app_title"))
        self.geometry("1240x820")
        self.root_dir = root_dir
        self.catalog_path = catalog_path
        self.start_types_path = start_types_path
        self.catalog: dict[str, dict] = {}
        self.start_types: dict[str, dict[str, str]] = {}
        self.start_type_keys: list[str] = []
        self.upgrade_keys: list[str] = list(UPGRADES.keys())
        self.profiles: dict[str, dict] = {}
        self.current_id: str | None = None
        self.picker_mode = "start_types"
        self._loading = False
        self._lang_busy = False
        self._i18n_labels: list[tuple[ttk.Label, str]] = []
        self._i18n_buttons: list[tuple[ttk.Button, str]] = []
        self._rep_labels: dict[str, ttk.Label] = {}
        self._contraband_labels: dict[str, ttk.Label] = {}
        self._preserved_retail_markup_delta = 0

        self._build_menu()
        self._build_layout()
        self._load_start_types()
        self.name_en_var.trace_add("write", lambda *_: self._refresh_id_preview())
        self.status_label.config(text=t("status_loading"))
        self.update_idletasks()
        self.after(10, self._startup)

    def _startup(self) -> None:
        self.rescan_profiles()
        self._on_tab_changed()
        self.status_label.config(text=t("status_loading_catalog"))
        self.update_idletasks()
        self.after(10, self._load_catalog)

    def _build_menu(self):
        self._menu_bar = tk.Menu(self)
        self._file_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._file_menu.add_command(label=t("menu_open_root"), command=self.open_root)
        self._file_menu.add_command(label=t("menu_save"), command=self.save_current, accelerator="Ctrl+S")
        self._file_menu.add_command(label=t("menu_save_all"), command=self.save_all)
        self._file_menu.add_separator()
        self._file_menu.add_command(label=t("menu_reload"), command=self.rescan_profiles)
        self._file_menu.add_separator()
        self._file_menu.add_command(label=t("menu_exit"), command=self.destroy)
        self._menu_bar.add_cascade(label=t("menu_file"), menu=self._file_menu)
        self._file_cascade_idx = self._menu_bar.index("end")

        self._lang_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._lang_menu.add_command(label=self._lang_menu_label("zh"), command=lambda: self.set_language("zh"))
        self._lang_menu.add_command(label=self._lang_menu_label("en"), command=lambda: self.set_language("en"))
        self._menu_bar.add_cascade(label=t("menu_language"), menu=self._lang_menu)
        self._lang_cascade_idx = self._menu_bar.index("end")

        self.config(menu=self._menu_bar)
        self.bind("<Control-s>", lambda _e: self.save_current())

    @staticmethod
    def _lang_menu_label(lang: str) -> str:
        mark = "* " if lang == I18n._lang else "  "
        return mark + t("lang_zh" if lang == "zh" else "lang_en")

    def set_language(self, lang: str) -> None:
        if lang not in ("zh", "en") or lang == I18n._lang or self._lang_busy:
            return
        self._lang_busy = True
        try:
            I18n.set_language(lang)
            save_saved_language(lang)
            self._apply_language()
        finally:
            self._lang_busy = False

    def _apply_language(self) -> None:
        self.title(t("app_title"))
        self._menu_bar.entryconfigure(self._file_cascade_idx, label=t("menu_file"))
        self._menu_bar.entryconfigure(self._lang_cascade_idx, label=t("menu_language"))
        self._file_menu.entryconfigure(0, label=t("menu_open_root"))
        self._file_menu.entryconfigure(1, label=t("menu_save"))
        self._file_menu.entryconfigure(2, label=t("menu_save_all"))
        self._file_menu.entryconfigure(4, label=t("menu_reload"))
        self._file_menu.entryconfigure(6, label=t("menu_exit"))
        self._lang_menu.entryconfigure(0, label=self._lang_menu_label("zh"))
        self._lang_menu.entryconfigure(1, label=self._lang_menu_label("en"))

        for widget, key in self._i18n_labels:
            widget.config(text=t(key))
        for widget, key in self._i18n_buttons:
            widget.config(text=t(key))

        self.notebook.tab(self.meta_tab, text=t("tab_meta"))
        self.notebook.tab(self.items_tab, text=t("tab_items"))
        self.notebook.tab(self.cash_tab, text=t("tab_cash"))
        self.notebook.tab(self.upgrades_tab, text=t("tab_upgrades"))
        self.notebook.tab(self.rep_tab, text=t("tab_reputation"))

        for key, widget in self._rep_labels.items():
            names = dict(FACTION_KEYS).get(key, {})
            widget.config(text=names.get(I18n._lang, key))

        for key, widget in self._contraband_labels.items():
            names = dict(CONTRABAND_MARKUP_KEYS).get(key, {})
            widget.config(text=names.get(I18n._lang, key))

        self._save_ui_to_current(silent=True)
        if self.current_id:
            data = self.profiles[self.current_id]["data"]
            self._reload_item_lists(data)
            self._reload_allowed_list(data)
            self._reload_upgrades_list(data)
        self._refresh_profile_list_labels()
        self._refresh_icon_status()
        self._refresh_icon_prompt()
        self._sync_picker_panel()
        self._update_status()

    def _label(self, parent, key: str, **kwargs) -> ttk.Label:
        widget = ttk.Label(parent, text=t(key), **kwargs)
        self._i18n_labels.append((widget, key))
        return widget

    def _button(self, parent, key: str, command, **kwargs) -> ttk.Button:
        widget = ttk.Button(parent, text=t(key), command=command, **kwargs)
        self._i18n_buttons.append((widget, key))
        return widget

    def _build_layout(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        path_row = ttk.Frame(top)
        path_row.pack(side="left", fill="x", expand=True)
        self.path_label = ttk.Label(path_row, text=str(self.root_dir))
        self.path_label.pack(side="left", fill="x", expand=True)
        self._button(path_row, "btn_browse", self.open_root).pack(side="left", padx=(8, 0))
        top_actions = ttk.Frame(top)
        top_actions.pack(side="right")
        self.save_btn = self._button(top_actions, "btn_save", self.save_current)
        self.save_btn.pack(side="left", padx=(0, 8))
        lang_frame = ttk.Frame(top_actions)
        lang_frame.pack(side="left", padx=(0, 8))
        self._lang_zh_btn = ttk.Button(lang_frame, text=t("lang_zh"), width=6, command=lambda: self.set_language("zh"))
        self._lang_zh_btn.pack(side="left", padx=(0, 2))
        self._lang_en_btn = ttk.Button(lang_frame, text=t("lang_en"), width=6, command=lambda: self.set_language("en"))
        self._lang_en_btn.pack(side="left")
        self.status_label = ttk.Label(top_actions, text="")
        self.status_label.pack(side="left")

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=4)

        left = ttk.Frame(paned, padding=4)
        paned.add(left, weight=1)
        self._label(left, "profiles").pack(anchor="w")
        self.profile_list = tk.Listbox(left, exportselection=False)
        self.profile_list.pack(fill="both", expand=True, pady=4)
        self.profile_list.bind("<<ListboxSelect>>", self._on_profile_selected)
        btns = ttk.Frame(left)
        btns.pack(fill="x")
        self._button(btns, "btn_new", self.new_profile).pack(side="left", padx=2)
        self._button(btns, "btn_duplicate", self.duplicate_profile).pack(side="left", padx=2)
        self._button(btns, "btn_delete", self.delete_profile).pack(side="left", padx=2)

        center = ttk.Frame(paned, padding=4)
        paned.add(center, weight=3)
        self.notebook = ttk.Notebook(center)
        self.notebook.pack(fill="both", expand=True)
        self._build_meta_tab()
        self._build_items_tab()
        self._build_cash_tab()
        self._build_upgrades_tab()
        self._build_rep_tab()

        right = ttk.Frame(paned, padding=4)
        paned.add(right, weight=2)
        self.picker_title_label = self._label(right, "catalog_title")
        self.picker_title_label.pack(anchor="w")
        self.search_row = ttk.Frame(right)
        self.search_row.pack(fill="x", pady=4)
        self._label(self.search_row, "search").pack(side="left")
        self.search_var = tk.StringVar()
        ent = ttk.Entry(self.search_row, textvariable=self.search_var)
        ent.pack(side="left", fill="x", expand=True, padx=4)
        ent.bind("<KeyRelease>", lambda _e: self._refresh_picker_list())
        self.picker_hint_label = ttk.Label(right, text="", foreground="#666")
        self.catalog_list = tk.Listbox(right, exportselection=False)
        self.catalog_list.bind("<Double-1>", lambda _e: self._picker_primary_action())
        self.picker_btn_row = ttk.Frame(right)
        self.picker_primary_btn = self._button(
            self.picker_btn_row, "btn_add_simple", self._picker_primary_action
        )
        self.picker_primary_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        self.picker_secondary_btn = self._button(
            self.picker_btn_row, "btn_add_remove", self._picker_secondary_action
        )
        self.picker_secondary_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _build_meta_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_meta"))
        self.meta_tab = tab
        self.name_zh_var = tk.StringVar()
        self.name_en_var = tk.StringVar()
        self.cost_var = tk.StringVar(value="0")
        self.type_var = tk.StringVar(value="0")

        row = 0
        self._label(tab, "label_id").grid(row=row, column=0, sticky="w", pady=2)
        self.id_display = ttk.Label(tab, text="—", foreground="#444")
        self.id_display.grid(row=row, column=1, sticky="w", pady=2)
        row += 1

        fields = [
            ("label_name_zh", self.name_zh_var),
            ("label_name_en", self.name_en_var),
            ("label_cost", self.cost_var),
            ("label_type", self.type_var),
        ]
        for key, var in fields:
            self._label(tab, key).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(tab, textvariable=var, width=60).grid(row=row, column=1, sticky="ew", pady=2)
            row += 1

        self._label(tab, "label_desc_zh").grid(row=row, column=0, sticky="nw")
        self.desc_zh = tk.Text(tab, height=8, width=60)
        self.desc_zh.grid(row=row, column=1, sticky="ew", pady=2)
        self.desc_zh.bind("<KeyRelease>", lambda _e: self._on_desc_changed(self.desc_zh))
        row += 1
        self._label(tab, "label_desc_en").grid(row=row, column=0, sticky="nw")
        self.desc_en = tk.Text(tab, height=8, width=60)
        self.desc_en.grid(row=row, column=1, sticky="ew", pady=2)
        self.desc_en.bind("<KeyRelease>", lambda _e: self._on_desc_changed(self.desc_en))
        row += 1

        self._label(tab, "label_allowed").grid(row=row, column=0, sticky="nw")
        allowed_col = ttk.Frame(tab)
        allowed_col.grid(row=row, column=1, sticky="ew", pady=2)
        self._label(allowed_col, "allowed_list_title").pack(anchor="w")
        self.allowed_types_list = tk.Listbox(allowed_col, height=3, exportselection=False)
        self.allowed_types_list.pack(fill="x", pady=(2, 4))
        allowed_btns = ttk.Frame(allowed_col)
        allowed_btns.pack(anchor="w")
        self._button(allowed_btns, "btn_remove_from_allowed", self.remove_selected_allowed).pack(side="left", padx=(0, 4))
        self._button(allowed_btns, "btn_clear_allowed", self._clear_allowed_types).pack(side="left")
        row += 1

        hint = self._label(tab, "allowed_hint", foreground="#666")
        hint.grid(row=row, column=1, sticky="w")
        row += 1

        self._label(tab, "label_icon").grid(row=row, column=0, sticky="nw", pady=(8, 2))
        icon_frame = ttk.Frame(tab)
        icon_frame.grid(row=row, column=1, sticky="ew", pady=(8, 2))
        self.icon_status_label = ttk.Label(icon_frame, text=t("icon_status_none"))
        self.icon_status_label.pack(anchor="w")
        self._button(icon_frame, "btn_upload_icon", self.upload_icon).pack(anchor="w", pady=4)
        row += 1

        self._label(tab, "icon_prompt_title").grid(row=row, column=0, sticky="nw")
        prompt_frame = ttk.Frame(tab)
        prompt_frame.grid(row=row, column=1, sticky="ew")
        self.icon_prompt_text = tk.Text(prompt_frame, height=12, width=60, wrap="word")
        self.icon_prompt_text.pack(fill="x")
        self.icon_prompt_text.config(state="disabled")
        self._button(prompt_frame, "btn_copy_prompt", self.copy_icon_prompt).pack(anchor="w", pady=4)
        tab.columnconfigure(1, weight=1)

    def _build_items_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_items"))
        self.items_tab = tab
        tab.rowconfigure(1, weight=1)
        tab.rowconfigure(4, weight=1)
        tab.columnconfigure(0, weight=1)

        self._label(tab, "items_add_title").grid(row=0, column=0, sticky="w")
        self.items_list = tk.Listbox(tab, height=10, exportselection=False)
        self.items_list.grid(row=1, column=0, sticky="nsew", pady=(2, 4))
        self._button(tab, "btn_remove_from_add", self.remove_selected_add_item).grid(row=2, column=0, sticky="w", pady=(0, 8))

        self._label(tab, "items_remove_title").grid(row=3, column=0, sticky="w")
        self.remove_list = tk.Listbox(tab, height=8, exportselection=False)
        self.remove_list.grid(row=4, column=0, sticky="nsew", pady=(2, 4))
        self._button(tab, "btn_remove_from_remove", self.remove_selected_remove_item).grid(row=5, column=0, sticky="w")

    def _build_cash_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_cash"))
        self.cash_tab = tab
        self.cash_var = tk.StringVar(value="0")
        self.rent_var = tk.StringVar(value="0")
        self.attractiveness_var = tk.StringVar(value="0")
        self.contraband_vars: dict[str, tk.StringVar] = {}
        self._contraband_labels: dict[str, ttk.Label] = {}

        hint = ttk.Label(
            tab,
            text=t("economy_tab_hint"),
            wraplength=420,
            justify="left",
            foreground="#666",
        )
        hint.pack(anchor="w", pady=(0, 10))

        self._label(tab, "label_extra_cash").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.cash_var, width=16).pack(anchor="w", pady=4)
        self._label(tab, "label_extra_rent").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.rent_var, width=16).pack(anchor="w", pady=4)
        self._label(tab, "label_attractiveness_delta").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.attractiveness_var, width=16).pack(anchor="w", pady=(4, 8))

        self._label(tab, "label_contraband_markup_delta").pack(anchor="w")
        contraband_frame = ttk.Frame(tab)
        contraband_frame.pack(fill="x", pady=4)
        for key, names in CONTRABAND_MARKUP_KEYS:
            row = ttk.Frame(contraband_frame)
            row.pack(fill="x", pady=2)
            label = ttk.Label(row, text=names[I18n._lang], width=16)
            label.pack(side="left")
            self._contraband_labels[key] = label
            var = tk.StringVar(value="0")
            self.contraband_vars[key] = var
            ttk.Entry(row, textvariable=var, width=10).pack(side="left")

    def _build_upgrades_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_upgrades"))
        self.upgrades_tab = tab
        self._label(tab, "upgrades_list_title").pack(anchor="w", pady=(0, 4))
        self.upgrades_list = tk.Listbox(tab, height=14, exportselection=False)
        self.upgrades_list.pack(fill="both", expand=True, pady=(0, 4))
        self._button(tab, "btn_remove_from_upgrades", self.remove_selected_upgrade).pack(anchor="w")

    def _build_rep_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_reputation"))
        self.rep_tab = tab
        self.rep_vars: dict[str, tk.StringVar] = {}
        for key, names in FACTION_KEYS:
            row = ttk.Frame(tab)
            row.pack(fill="x", pady=2)
            label = ttk.Label(row, text=names[I18n._lang], width=16)
            label.pack(side="left")
            self._rep_labels[key] = label
            var = tk.StringVar(value="0")
            self.rep_vars[key] = var
            ttk.Entry(row, textvariable=var, width=10).pack(side="left")

    def _load_start_types(self):
        self.start_types = load_start_types(self.start_types_path)
        self.start_type_keys = sort_start_type_keys(list(self.start_types.keys()))

    def _on_tab_changed(self, _event=None) -> None:
        tab_id = self.notebook.select()
        if tab_id == str(self.meta_tab):
            self.picker_mode = "start_types"
        elif tab_id == str(self.items_tab):
            self.picker_mode = "items"
        elif tab_id == str(self.upgrades_tab):
            self.picker_mode = "upgrades"
        else:
            self.picker_mode = "none"
        self._sync_picker_panel()

    def _sync_picker_panel(self) -> None:
        title_key = {
            "items": "catalog_title",
            "start_types": "picker_title_start_types",
            "upgrades": "picker_title_upgrades",
            "none": "picker_title_none",
        }.get(self.picker_mode, "picker_title_none")
        self.picker_title_label.config(text=t(title_key))

        if self.picker_mode == "none":
            self.search_row.pack_forget()
            self.catalog_list.pack_forget()
            self.picker_btn_row.pack_forget()
            self.picker_hint_label.config(text=t("picker_hint_none"))
            self.picker_hint_label.pack(fill="x", pady=4)
            return

        self.picker_hint_label.pack_forget()
        self.search_row.pack(fill="x", pady=4)
        self.catalog_list.pack(fill="both", expand=True)
        self.picker_btn_row.pack(fill="x", pady=4)

        if self.picker_mode == "items":
            self.picker_primary_btn.config(text=t("btn_add_simple"))
            self.picker_secondary_btn.config(text=t("btn_add_remove"))
            self.picker_secondary_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
        elif self.picker_mode == "start_types":
            self.picker_primary_btn.config(text=t("picker_btn_add_allowed"))
            self.picker_secondary_btn.pack_forget()
        elif self.picker_mode == "upgrades":
            self.picker_primary_btn.config(text=t("picker_btn_add_upgrade"))
            self.picker_secondary_btn.pack_forget()

        self._refresh_picker_list()

    def _picker_primary_action(self) -> None:
        if self.picker_mode == "items":
            self.add_catalog_item()
        elif self.picker_mode == "start_types":
            self.add_picker_start_type()
        elif self.picker_mode == "upgrades":
            self.add_picker_upgrade()

    def _picker_secondary_action(self) -> None:
        if self.picker_mode == "items":
            self.add_catalog_to_remove()

    def _upgrade_label(self, key: str) -> str:
        meta = UPGRADES.get(key, {})
        en = meta.get("en", key)
        zh = meta.get("zh", key)
        return f"{key} — {bilingual_label(en, zh, key)}"

    def _start_type_label(self, key: str) -> str:
        meta = self.start_types.get(key, {})
        en = meta.get("en") or key
        zh = meta.get("zh") or key
        return f"{key} — {bilingual_label(en, zh, key)}"

    def _ensure_start_types_for_allowed(self, allowed: set[str]) -> None:
        unlisted = t("start_type_unlisted")
        changed = False
        for key in sort_start_type_keys(list(allowed)):
            if key in self.start_types:
                continue
            self.start_types[key] = {"zh": f"{key} {unlisted}", "en": f"{key} {unlisted}"}
            changed = True
        if changed:
            self.start_type_keys = sort_start_type_keys(list(self.start_types.keys()))

    def _reload_allowed_list(self, data: dict) -> None:
        self.allowed_types_list.delete(0, "end")
        for key in data.get("allowedStartTypes", []):
            self.allowed_types_list.insert("end", self._start_type_label(str(key)))

    def _reload_upgrades_list(self, data: dict) -> None:
        self.upgrades_list.delete(0, "end")
        for up in data.get("unlockedUpgrades", []):
            self.upgrades_list.insert("end", self._upgrade_label(str(up)))

    def _catalog_display(self, item_id: str, meta: dict) -> str:
        en, zh = catalog_names(meta)
        return f"{item_id} — {bilingual_label(en, zh, item_id)}"

    def _load_catalog(self):
        if self.catalog_path.is_file():
            self.catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        self._refresh_picker_list()
        self._update_status()

    def _refresh_picker_list(self):
        q = self.search_var.get().strip().lower()
        self.catalog_list.delete(0, "end")
        self._picker_ids: list[str] = []

        if self.picker_mode == "none":
            return

        if self.picker_mode == "start_types":
            for key in self.start_type_keys:
                meta = self.start_types.get(key, {})
                en = meta.get("en") or key
                zh = meta.get("zh") or key
                hay = f"{key} {en} {zh}".lower()
                if q and q not in hay:
                    continue
                self.catalog_list.insert("end", self._start_type_label(key))
                self._picker_ids.append(key)
            return

        if self.picker_mode == "upgrades":
            for key in self.upgrade_keys:
                hay = f"{key} {UPGRADES[key].get('en', '')} {UPGRADES[key].get('zh', '')}".lower()
                if q and q not in hay:
                    continue
                self.catalog_list.insert("end", self._upgrade_label(key))
                self._picker_ids.append(key)
            return

        shown = 0
        truncated = False
        for item_id, meta in sorted(self.catalog.items()):
            en, zh = catalog_names(meta)
            hay = f"{item_id} {en} {zh}".lower()
            if q and q not in hay:
                continue
            if not q and shown >= CATALOG_PREVIEW_LIMIT:
                truncated = True
                continue
            self.catalog_list.insert("end", self._catalog_display(item_id, meta))
            self._picker_ids.append(item_id)
            shown += 1
        if truncated:
            self.catalog_list.insert("end", t("catalog_search_hint"))

    def _collect_allowed_start_types(self) -> list[int]:
        ids: list[int] = []
        for i in range(self.allowed_types_list.size()):
            key = self._item_id_from_display(self.allowed_types_list.get(i))
            if key.isdigit():
                ids.append(int(key))
        ids = sorted(set(ids))
        if self.start_type_keys and len(ids) >= len(self.start_type_keys):
            return []
        return ids

    def _selected_allowed_types(self) -> list[int]:
        return self._collect_allowed_start_types()

    def _preview_id(self) -> str:
        return generate_profile_id(self.name_en_var.get().strip(), self._selected_allowed_types())

    def _refresh_id_preview(self) -> None:
        preview = self._preview_id()
        self.id_display.config(text=preview or "—")
        self._refresh_icon_prompt()

    def _on_allowed_list_changed(self) -> None:
        self._refresh_id_preview()
        if self.current_id and not self._loading:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def _desc_max_len(self, widget: tk.Text) -> int:
        return DESC_MAX_LEN_EN if widget is self.desc_en else DESC_MAX_LEN_ZH

    def _on_desc_changed(self, widget: tk.Text) -> None:
        if self._loading:
            return
        max_len = self._desc_max_len(widget)
        text = widget.get("1.0", "end-1c")
        if len(text) > max_len:
            widget.delete(f"1.0+{max_len}c", "end-1c")
        self._refresh_icon_prompt()
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def _read_desc(self, widget: tk.Text) -> str:
        return clamp_text(widget.get("1.0", "end").strip(), self._desc_max_len(widget))

    def _set_desc(self, widget: tk.Text, text: str) -> None:
        widget.delete("1.0", "end")
        widget.insert("1.0", clamp_text(text or "", self._desc_max_len(widget)))

    def _collect_ui_data(self) -> dict:
        data = {
            "version": 1,
            "id": self._preview_id(),
            "name": {"zh": self.name_zh_var.get(), "en": self.name_en_var.get()},
            "description": {
                "zh": self._read_desc(self.desc_zh),
                "en": self._read_desc(self.desc_en),
            },
            "cost": int(self.cost_var.get() or "0"),
            "type": int(self.type_var.get() or "0"),
            "allowedStartTypes": self._collect_allowed_start_types(),
            "items": [self._parse_item_line(self._item_id_from_display(self.items_list.get(i))) for i in range(self.items_list.size())],
            "removeItems": [self._item_id_from_display(self.remove_list.get(i)) for i in range(self.remove_list.size())],
            "extraCash": int(self.cash_var.get() or "0"),
            "extraRent": int(self.rent_var.get() or "0"),
            "retailMarkupDelta": self._preserved_retail_markup_delta,
            "contrabandMarkupDelta": {
                k: int(v.get() or "0") for k, v in self.contraband_vars.items()
            },
            "baseStoreAttractivenessDelta": int(self.attractiveness_var.get() or "0"),
            "unlockedUpgrades": [
                self._item_id_from_display(self.upgrades_list.get(i)) for i in range(self.upgrades_list.size())
            ],
            "factionReputationDelta": {k: int(v.get() or "0") for k, v in self.rep_vars.items()},
        }
        return data

    @staticmethod
    def _item_id_from_display(line: str) -> str:
        line = line.strip()
        if " — " in line:
            return line.split(" — ", 1)[0].strip()
        return line

    def _format_item_display(self, item) -> str:
        if isinstance(item, str):
            meta = self.catalog.get(item, {})
            if meta:
                return self._catalog_display(item, meta)
            return item
        return json.dumps(item, ensure_ascii=False)

    def _reload_item_lists(self, data: dict) -> None:
        self.items_list.delete(0, "end")
        for item in data.get("items", []):
            self.items_list.insert("end", self._format_item_display(item))
        self.remove_list.delete(0, "end")
        for rid in data.get("removeItems", []):
            self.remove_list.insert("end", self._format_item_display(rid))

    def _refresh_icon_status(self) -> None:
        if not self.current_id:
            self.icon_status_label.config(text=t("icon_status_none"))
            return
        icon_path = self.profiles[self.current_id]["folder"] / ICON_FILE
        self.icon_status_label.config(text=t("icon_status_set") if icon_path.is_file() else t("icon_status_none"))

    def _refresh_icon_prompt(self) -> None:
        data = {
            "name": {"zh": self.name_zh_var.get(), "en": self.name_en_var.get()},
            "description": {
                "zh": self._read_desc(self.desc_zh),
                "en": self._read_desc(self.desc_en),
            },
        }
        prompt = build_icon_prompt(data)
        self.icon_prompt_text.config(state="normal")
        self.icon_prompt_text.delete("1.0", "end")
        self.icon_prompt_text.insert("1.0", prompt)
        self.icon_prompt_text.config(state="disabled")

    def _refresh_profile_list_labels(self) -> None:
        keep = self.current_id
        keys = list(self.profiles.keys())
        sel_idx = keys.index(keep) if keep in keys else None
        self.profile_list.delete(0, "end")
        for folder_name in keys:
            data = self.profiles[folder_name]["data"]
            lang = I18n._lang
            display = data.get("name", {}).get(lang) or data.get("name", {}).get("en") or folder_name
            self.profile_list.insert("end", f"{display} ({folder_name})")
        if sel_idx is not None:
            self.profile_list.selection_clear(0, "end")
            self.profile_list.selection_set(sel_idx)

    def _select_profile(self, folder_name: str) -> None:
        keys = list(self.profiles.keys())
        if folder_name not in keys:
            return
        idx = keys.index(folder_name)
        self.profile_list.unbind("<<ListboxSelect>>")
        try:
            self.profile_list.selection_clear(0, "end")
            self.profile_list.selection_set(idx)
        finally:
            self.profile_list.bind("<<ListboxSelect>>", self._on_profile_selected)
        self.current_id = folder_name
        self._load_profile_to_ui(self.profiles[folder_name]["data"])

    def rescan_profiles(self, select_current: bool = False):
        keep = self.current_id if select_current else None
        self._save_ui_to_current(silent=True)
        self.profiles = scan_profiles(self.root_dir)
        self._refresh_profile_list_labels()
        keys = list(self.profiles.keys())
        if keys:
            target = keep if keep in keys else keys[0]
            self._select_profile(target)
        else:
            self.current_id = None
        self.path_label.config(text=str(self.root_dir))

    def open_root(self):
        chosen = filedialog.askdirectory(initialdir=str(self.root_dir))
        if not chosen:
            return
        self.root_dir = Path(chosen)
        self.rescan_profiles()

    def _clear_allowed_types(self) -> None:
        self.allowed_types_list.delete(0, "end")
        self._on_allowed_list_changed()

    def remove_selected_allowed(self) -> None:
        sel = list(self.allowed_types_list.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            self.allowed_types_list.delete(idx)
        self._on_allowed_list_changed()

    def add_picker_start_type(self) -> None:
        sel = self.catalog_list.curselection()
        if not sel or sel[0] >= len(self._picker_ids):
            return
        key = self._picker_ids[sel[0]]
        existing = {
            self._item_id_from_display(self.allowed_types_list.get(i))
            for i in range(self.allowed_types_list.size())
        }
        if key in existing:
            return
        self.allowed_types_list.insert("end", self._start_type_label(key))
        self._on_allowed_list_changed()

    def remove_selected_upgrade(self) -> None:
        sel = list(self.upgrades_list.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            self.upgrades_list.delete(idx)
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def add_picker_upgrade(self) -> None:
        sel = self.catalog_list.curselection()
        if not sel or sel[0] >= len(self._picker_ids):
            return
        key = self._picker_ids[sel[0]]
        existing = {
            self._item_id_from_display(self.upgrades_list.get(i)) for i in range(self.upgrades_list.size())
        }
        if key in existing:
            return
        self.upgrades_list.insert("end", self._upgrade_label(key))
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def _on_profile_selected(self, _event=None):
        self._save_ui_to_current(silent=True)
        sel = self.profile_list.curselection()
        if not sel:
            self.current_id = None
            return
        folder_name = list(self.profiles.keys())[sel[0]]
        self.current_id = folder_name
        self._load_profile_to_ui(self.profiles[folder_name]["data"])

    def _load_profile_to_ui(self, data: dict):
        self._loading = True
        name = data.get("name", {})
        self.name_zh_var.set(name.get("zh", ""))
        self.name_en_var.set(name.get("en", ""))
        desc = data.get("description", {})
        self._set_desc(self.desc_zh, desc.get("zh", ""))
        self._set_desc(self.desc_en, desc.get("en", ""))
        self.cost_var.set(str(data.get("cost", 0)))
        self.type_var.set(str(data.get("type", 0)))
        allowed = {str(x) for x in data.get("allowedStartTypes", [])}
        self._ensure_start_types_for_allowed(allowed)
        self._reload_allowed_list(data)
        self._reload_item_lists(data)
        self.cash_var.set(str(data.get("extraCash", 0)))
        self.rent_var.set(str(data.get("extraRent", 0)))
        self._preserved_retail_markup_delta = int(data.get("retailMarkupDelta", 0) or 0)
        self.attractiveness_var.set(str(data.get("baseStoreAttractivenessDelta", 0)))
        contraband = data.get("contrabandMarkupDelta", {})
        if isinstance(contraband, int):
            for key, var in self.contraband_vars.items():
                var.set(str(contraband))
        else:
            for key, var in self.contraband_vars.items():
                var.set(str(contraband.get(key, 0)))
        self._reload_upgrades_list(data)
        rep = data.get("factionReputationDelta", {})
        for key, var in self.rep_vars.items():
            var.set(str(rep.get(key, 0)))
        self._loading = False
        self._refresh_id_preview()
        self._refresh_icon_status()
        self._refresh_icon_prompt()
        self._update_status()

    def _unique_profile_id(self, base_id: str, exclude: str | None = None) -> str:
        if not slug_ok(base_id):
            base_id = "custom_start"
        candidate = base_id
        n = 2
        while True:
            folder = self.root_dir / candidate
            if candidate == exclude or not folder.exists():
                return candidate
            candidate = f"{base_id}_{n}"
            n += 1

    def _save_ui_to_current(self, silent: bool = False) -> bool:
        if self._loading or not self.current_id or self.current_id not in self.profiles:
            return True
        try:
            data = self._collect_ui_data()
            new_id = data["id"]
            if not new_id or not slug_ok(new_id):
                if not silent:
                    messagebox.showerror(t("error_title"), t("invalid_id"))
                return False
            data["id"] = self._unique_profile_id(new_id, exclude=self.current_id)
            self.profiles[self.current_id]["data"] = data
            self.profiles[self.current_id]["dirty"] = True
            self._refresh_id_preview()
            self._refresh_icon_prompt()
            self._update_status()
            return True
        except ValueError:
            if not silent:
                messagebox.showerror(t("error_title"), t("error_numeric"))
            return False

    def _sync_folder_name(self) -> bool:
        if not self.current_id:
            return True
        entry = self.profiles[self.current_id]
        data = entry["data"]
        new_id = data["id"]
        old_folder: Path = entry["folder"]
        if old_folder.name == new_id:
            return True
        new_folder = self.root_dir / new_id
        if new_folder.exists():
            messagebox.showerror(t("error_title"), t("id_exists"))
            return False
        old_folder.rename(new_folder)
        old_key = self.current_id
        entry["folder"] = new_folder
        self.profiles[new_id] = entry
        if old_key != new_id:
            del self.profiles[old_key]
        self.current_id = new_id
        return True

    @staticmethod
    def _parse_item_line(line: str):
        line = line.strip()
        if line.startswith("{"):
            return json.loads(line)
        return line

    def save_current(self):
        if not self.current_id:
            return
        if not self._save_ui_to_current():
            return
        if not self._sync_folder_name():
            return
        entry = self.profiles[self.current_id]
        folder = entry["folder"]
        (folder / PROFILE_FILE).write_text(
            json.dumps(entry["data"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        entry["dirty"] = False
        self._refresh_profile_list_labels()
        self._update_status()

    def save_all(self):
        sel = self.current_id
        for key in list(self.profiles.keys()):
            self.current_id = key
            self._load_profile_to_ui(self.profiles[key]["data"])
            self.save_current()
        self.current_id = sel
        self.rescan_profiles(select_current=True)

    def new_profile(self):
        base = "new_start"
        n = 1
        while (self.root_dir / f"{base}_{n}").exists():
            n += 1
        profile_id = f"{base}_{n}"
        folder = self.root_dir / profile_id
        folder.mkdir(parents=True, exist_ok=True)
        data = empty_profile(profile_id)
        (folder / PROFILE_FILE).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.rescan_profiles()
        if profile_id in self.profiles:
            self._select_profile(profile_id)

    def duplicate_profile(self):
        if not self.current_id:
            return
        if not self._save_ui_to_current():
            return
        src = deepcopy(self.profiles[self.current_id]["data"])
        src["name"]["en"] = (src.get("name", {}).get("en") or src["id"]) + " Copy"
        src["name"]["zh"] = (src.get("name", {}).get("zh") or src["id"]) + " 副本"
        new_id = self._unique_profile_id(generate_profile_id(src["name"]["en"], src.get("allowedStartTypes", [])))
        src["id"] = new_id
        folder = self.root_dir / new_id
        folder.mkdir(parents=True)
        (folder / PROFILE_FILE).write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        icon_src = self.profiles[self.current_id]["folder"] / ICON_FILE
        if icon_src.is_file():
            shutil.copy2(icon_src, folder / ICON_FILE)
        self.rescan_profiles()
        if new_id in self.profiles:
            self._select_profile(new_id)

    def delete_profile(self):
        if not self.current_id:
            return
        if not messagebox.askyesno(t("confirm_title"), t("confirm_delete")):
            return
        folder = self.profiles[self.current_id]["folder"]
        shutil.rmtree(folder)
        self.current_id = None
        self.rescan_profiles()

    def upload_icon(self):
        if not self.current_id:
            return
        path = filedialog.askopenfilename(
            title=t("btn_upload_icon"),
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.webp *.gif *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        folder = self.profiles[self.current_id]["folder"]
        dest = folder / ICON_FILE
        src = Path(path)
        try:
            process_icon_file(src, dest)
        except ImportError:
            messagebox.showwarning(
                t("error_title"),
                "Install Pillow (pip install Pillow) to convert and crop icons to icon.png.",
            )
            return
        except Exception as exc:
            messagebox.showerror(t("error_title"), f"Failed to save icon: {exc}")
            return
        for old in folder.iterdir():
            if old.is_file() and old.name.lower().startswith("icon.") and old.name != ICON_FILE:
                try:
                    old.unlink()
                except OSError:
                    pass
        self._refresh_icon_status()
        self.profiles[self.current_id]["dirty"] = True
        self._update_status()

    def copy_icon_prompt(self):
        prompt = self.icon_prompt_text.get("1.0", "end").strip()
        self.clipboard_clear()
        self.clipboard_append(prompt)
        messagebox.showinfo(t("icon_prompt_title"), t("prompt_copied"))

    def add_catalog_item(self):
        sel = self.catalog_list.curselection()
        if not sel or sel[0] >= len(self._picker_ids):
            return
        item_id = self._picker_ids[sel[0]]
        meta = self.catalog.get(item_id, {})
        self.items_list.insert("end", self._catalog_display(item_id, meta))
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def add_catalog_to_remove(self):
        sel = self.catalog_list.curselection()
        if not sel or sel[0] >= len(self._picker_ids):
            return
        item_id = self._picker_ids[sel[0]]
        meta = self.catalog.get(item_id, {})
        self.remove_list.insert("end", self._catalog_display(item_id, meta))
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def remove_selected_add_item(self):
        sel = list(self.items_list.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            self.items_list.delete(idx)
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def remove_selected_remove_item(self):
        sel = list(self.remove_list.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            self.remove_list.delete(idx)
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def _update_status(self):
        dirty = any(p["dirty"] for p in self.profiles.values())
        self.status_label.config(text=t("status_unsaved") if dirty else "")


def main():
    parser = argparse.ArgumentParser(description="Custom Start Framework profile editor")
    parser.add_argument("-r", "--root", type=Path, default=DEFAULT_ROOT, help="custom-start root directory")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--start-types", type=Path, default=DEFAULT_START_TYPES)
    parser.add_argument("--lang", choices=["zh", "en"], default=None, help="UI language (overrides saved preference)")
    args = parser.parse_args()
    try:
        args.root.mkdir(parents=True, exist_ok=True)
        lang = resolve_startup_language(args.lang)
        app = ProfileEditor(
            args.root.resolve(),
            args.catalog.resolve(),
            args.start_types.resolve(),
            lang=lang,
        )
        app.mainloop()
    except Exception as exc:
        import traceback

        traceback.print_exc()
        try:
            err = tk.Tk()
            err.withdraw()
            messagebox.showerror("Editor Error", str(exc))
            err.destroy()
        except Exception:
            pass
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
