#!/usr/bin/env python3
"""Custom Start Framework — profile editor for UserData/custom-start/{id}/."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tkinter as tk
from copy import deepcopy
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = SCRIPT_DIR / "catalog.json"
DEFAULT_START_TYPES = SCRIPT_DIR / "start_types.json"
if (SCRIPT_DIR / "catalog.json").is_file():
    DEFAULT_ROOT = SCRIPT_DIR.parent / "custom-start"
else:
    DEFAULT_ROOT = SCRIPT_DIR.parent.parent / "UserData" / "custom-start"

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

UPGRADES = {
    "BREWER": {"zh": "酿酒师", "en": "Brewer"},
    "CHEMIST": {"zh": "化学家", "en": "Chemist"},
    "PHARMA": {"zh": "药剂", "en": "Pharma"},
    "MINER": {"zh": "矿工", "en": "Miner"},
    "RETIRED_GUNSMITH": {"zh": "退休枪匠", "en": "Retired Gunsmith"},
    "WATER_TRADER": {"zh": "水商", "en": "Water Trader"},
}

UI: dict[str, dict[str, str]] = {
    "app_title": {"zh": "自定义开局编辑器", "en": "Custom Start Editor"},
    "menu_file": {"zh": "文件", "en": "File"},
    "menu_open_root": {"zh": "打开 custom-start 目录…", "en": "Open custom-start Folder…"},
    "menu_save": {"zh": "保存当前", "en": "Save Current"},
    "menu_save_all": {"zh": "保存全部", "en": "Save All"},
    "menu_reload": {"zh": "重新扫描", "en": "Rescan"},
    "menu_exit": {"zh": "退出", "en": "Exit"},
    "profiles": {"zh": "自定义开局", "en": "Custom Starts"},
    "btn_new": {"zh": "新建", "en": "New"},
    "btn_delete": {"zh": "删除", "en": "Delete"},
    "btn_duplicate": {"zh": "复制", "en": "Duplicate"},
    "tab_meta": {"zh": "Perk 信息", "en": "Perk Info"},
    "tab_items": {"zh": "物品清单", "en": "Loadout"},
    "tab_cash": {"zh": "现金/租金", "en": "Cash / Rent"},
    "tab_upgrades": {"zh": "网络升级", "en": "Upgrades"},
    "tab_reputation": {"zh": "阵营声望 Δ", "en": "Faction Rep Δ"},
    "label_id": {"zh": "ID（ASCII，文件夹名）", "en": "ID (ASCII, folder name)"},
    "label_name_zh": {"zh": "名称（中文）", "en": "Name (Chinese)"},
    "label_name_en": {"zh": "名称（英文）", "en": "Name (English)"},
    "label_desc_zh": {"zh": "描述（中文）", "en": "Description (Chinese)"},
    "label_desc_en": {"zh": "描述（英文）", "en": "Description (English)"},
    "label_cost": {"zh": "Perk 点数消耗", "en": "Perk point cost"},
    "label_type": {"zh": "类型 (0=正面 1=负面 2=中性)", "en": "Type (0=positive 1=negative 2=neutral)"},
    "label_allowed": {"zh": "可用起始职业", "en": "Allowed start types"},
    "allowed_hint": {
        "zh": "可多选任意职业；留空 = 全部职业均可见。职业列表见 start_types.json，可追加新编号。",
        "en": "Multi-select roles; empty = visible for all start types. Edit start_types.json to add new IDs.",
    },
    "start_type_unlisted": {"zh": "（未登记）", "en": "(unlisted)"},
    "btn_select_all_types": {"zh": "全选职业", "en": "Select all types"},
    "btn_clear_types": {"zh": "清空（=全部）", "en": "Clear (= all types)"},
    "catalog_title": {"zh": "物品库", "en": "Item Catalog"},
    "search": {"zh": "搜索", "en": "Search"},
    "btn_add_simple": {"zh": "添加物品", "en": "Add Item"},
    "btn_add_remove": {"zh": "添加到移除列表", "en": "Add to Remove List"},
    "status_unsaved": {"zh": "未保存", "en": "Unsaved"},
    "confirm_delete": {"zh": "删除此自定义开局？", "en": "Delete this custom start?"},
    "prompt_new_id": {"zh": "新开局 ID", "en": "New start ID"},
    "invalid_id": {"zh": "ID 只能包含字母、数字、下划线和连字符", "en": "ID may only contain letters, digits, underscore, hyphen"},
    "id_exists": {"zh": "该 ID 已存在", "en": "That ID already exists"},
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


def empty_profile(profile_id: str) -> dict:
    return {
        "version": 1,
        "id": profile_id,
        "name": {"zh": profile_id, "en": profile_id},
        "description": {"zh": "", "en": ""},
        "cost": 1,
        "type": 0,
        "allowedStartTypes": [],
        "items": [],
        "removeItems": [],
        "extraCash": 0,
        "extraRent": 0,
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


class ProfileEditor(tk.Tk):
    def __init__(self, root_dir: Path, catalog_path: Path, start_types_path: Path, lang: str = "zh"):
        super().__init__()
        I18n.set_language(lang)
        self.title(t("app_title"))
        self.geometry("1200x780")
        self.root_dir = root_dir
        self.catalog_path = catalog_path
        self.start_types_path = start_types_path
        self.catalog: dict[str, dict] = {}
        self.start_types: dict[str, dict[str, str]] = {}
        self.start_type_keys: list[str] = []
        self.profiles: dict[str, dict] = {}
        self.current_id: str | None = None
        self._loading = False

        self._build_menu()
        self._build_layout()
        self._load_catalog()
        self._load_start_types()
        self.rescan_profiles()

    def _build_menu(self):
        bar = tk.Menu(self)
        file_menu = tk.Menu(bar, tearoff=0)
        file_menu.add_command(label=t("menu_open_root"), command=self.open_root)
        file_menu.add_command(label=t("menu_save"), command=self.save_current, accelerator="Ctrl+S")
        file_menu.add_command(label=t("menu_save_all"), command=self.save_all)
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_reload"), command=self.rescan_profiles)
        file_menu.add_separator()
        file_menu.add_command(label=t("menu_exit"), command=self.destroy)
        bar.add_cascade(label=t("menu_file"), menu=file_menu)
        self.config(menu=bar)
        self.bind("<Control-s>", lambda _e: self.save_current())

    def _build_layout(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        self.path_label = ttk.Label(top, text=str(self.root_dir))
        self.path_label.pack(side="left", fill="x", expand=True)
        self.status_label = ttk.Label(top, text="")
        self.status_label.pack(side="right")

        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=4)

        left = ttk.Frame(paned, padding=4)
        paned.add(left, weight=1)
        ttk.Label(left, text=t("profiles")).pack(anchor="w")
        self.profile_list = tk.Listbox(left, exportselection=False)
        self.profile_list.pack(fill="both", expand=True, pady=4)
        self.profile_list.bind("<<ListboxSelect>>", self._on_profile_selected)
        btns = ttk.Frame(left)
        btns.pack(fill="x")
        ttk.Button(btns, text=t("btn_new"), command=self.new_profile).pack(side="left", padx=2)
        ttk.Button(btns, text=t("btn_duplicate"), command=self.duplicate_profile).pack(side="left", padx=2)
        ttk.Button(btns, text=t("btn_delete"), command=self.delete_profile).pack(side="left", padx=2)

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
        ttk.Label(right, text=t("catalog_title")).pack(anchor="w")
        self.search_var = tk.StringVar()
        search_row = ttk.Frame(right)
        search_row.pack(fill="x", pady=4)
        ttk.Label(search_row, text=t("search")).pack(side="left")
        ent = ttk.Entry(search_row, textvariable=self.search_var)
        ent.pack(side="left", fill="x", expand=True, padx=4)
        ent.bind("<KeyRelease>", lambda _e: self._refresh_catalog())
        self.catalog_list = tk.Listbox(right, exportselection=False)
        self.catalog_list.pack(fill="both", expand=True)
        ttk.Button(right, text=t("btn_add_simple"), command=self.add_catalog_item).pack(fill="x", pady=2)
        ttk.Button(right, text=t("btn_add_remove"), command=self.add_catalog_to_remove).pack(fill="x", pady=2)

    def _build_meta_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_meta"))
        self.id_var = tk.StringVar()
        self.name_zh_var = tk.StringVar()
        self.name_en_var = tk.StringVar()
        self.cost_var = tk.StringVar(value="1")
        self.type_var = tk.StringVar(value="0")
        rows = [
            (t("label_id"), self.id_var),
            (t("label_name_zh"), self.name_zh_var),
            (t("label_name_en"), self.name_en_var),
            (t("label_cost"), self.cost_var),
            (t("label_type"), self.type_var),
        ]
        for i, (label, var) in enumerate(rows):
            ttk.Label(tab, text=label).grid(row=i, column=0, sticky="w", pady=2)
            ttk.Entry(tab, textvariable=var, width=60).grid(row=i, column=1, sticky="ew", pady=2)
        ttk.Label(tab, text=t("label_desc_zh")).grid(row=len(rows), column=0, sticky="nw")
        self.desc_zh = tk.Text(tab, height=3, width=60)
        self.desc_zh.grid(row=len(rows), column=1, sticky="ew", pady=2)
        ttk.Label(tab, text=t("label_desc_en")).grid(row=len(rows) + 1, column=0, sticky="nw")
        self.desc_en = tk.Text(tab, height=3, width=60)
        self.desc_en.grid(row=len(rows) + 1, column=1, sticky="ew", pady=2)
        ttk.Label(tab, text=t("label_allowed")).grid(row=len(rows) + 2, column=0, sticky="nw")
        ttk.Label(tab, text=t("allowed_hint"), foreground="#666").grid(row=len(rows) + 3, column=1, sticky="w")
        allowed_frame = ttk.Frame(tab)
        allowed_frame.grid(row=len(rows) + 2, column=1, sticky="nsew", pady=2, rowspan=2)
        allowed_scroll = ttk.Scrollbar(allowed_frame, orient="vertical")
        self.allowed_list = tk.Listbox(
            allowed_frame,
            selectmode="extended",
            height=12,
            exportselection=False,
            yscrollcommand=allowed_scroll.set,
        )
        allowed_scroll.config(command=self.allowed_list.yview)
        self.allowed_list.pack(side="left", fill="both", expand=True)
        allowed_scroll.pack(side="right", fill="y")
        allowed_btns = ttk.Frame(tab)
        allowed_btns.grid(row=len(rows) + 4, column=1, sticky="w", pady=4)
        ttk.Button(allowed_btns, text=t("btn_select_all_types"), command=self._select_all_start_types).pack(side="left", padx=2)
        ttk.Button(allowed_btns, text=t("btn_clear_types"), command=self._clear_start_types).pack(side="left", padx=2)
        tab.columnconfigure(1, weight=1)

    def _build_items_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_items"))
        self.items_list = tk.Listbox(tab, height=12)
        self.items_list.pack(fill="both", expand=True)
        self.remove_list = tk.Listbox(tab, height=6)
        self.remove_list.pack(fill="both", expand=True, pady=8)

    def _build_cash_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_cash"))
        self.cash_var = tk.StringVar(value="0")
        self.rent_var = tk.StringVar(value="0")
        ttk.Label(tab, text="extraCash").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.cash_var, width=16).pack(anchor="w", pady=4)
        ttk.Label(tab, text="extraRent").pack(anchor="w")
        ttk.Entry(tab, textvariable=self.rent_var, width=16).pack(anchor="w", pady=4)

    def _build_upgrades_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_upgrades"))
        self.upgrades_list = tk.Listbox(tab, height=16)
        self.upgrades_list.pack(fill="both", expand=True)

    def _build_rep_tab(self):
        tab = ttk.Frame(self.notebook, padding=8)
        self.notebook.add(tab, text=t("tab_reputation"))
        self.rep_vars: dict[str, tk.StringVar] = {}
        for key, names in FACTION_KEYS:
            row = ttk.Frame(tab)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=names[I18n._lang], width=16).pack(side="left")
            var = tk.StringVar(value="0")
            self.rep_vars[key] = var
            ttk.Entry(row, textvariable=var, width=10).pack(side="left")

    def _load_start_types(self):
        self.start_types = load_start_types(self.start_types_path)
        self.start_type_keys = sort_start_type_keys(list(self.start_types.keys()))
        self._populate_allowed_list()

    def _start_type_label(self, key: str) -> str:
        meta = self.start_types.get(key, {})
        lang = I18n._lang
        name = meta.get(lang) or meta.get("zh") or meta.get("en") or key
        return f"{key} — {name}"

    def _populate_allowed_list(self) -> None:
        self.allowed_list.delete(0, "end")
        for key in self.start_type_keys:
            self.allowed_list.insert("end", self._start_type_label(key))

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
            self._populate_allowed_list()

    def _load_catalog(self):
        if self.catalog_path.is_file():
            self.catalog = json.loads(self.catalog_path.read_text(encoding="utf-8"))
        self._refresh_catalog()

    def _refresh_catalog(self):
        q = self.search_var.get().strip().lower()
        self.catalog_list.delete(0, "end")
        self._catalog_ids: list[str] = []
        for item_id, meta in sorted(self.catalog.items()):
            hay = f"{item_id} {meta.get('name_en','')} {meta.get('name_zh','')}".lower()
            if q and q not in hay:
                continue
            lang = I18n._lang
            name = meta.get("name_zh" if lang == "zh" else "name_en", item_id)
            self.catalog_list.insert("end", f"{item_id} — {name}")
            self._catalog_ids.append(item_id)

    def rescan_profiles(self):
        self._save_ui_to_current(silent=True)
        self.profiles = scan_profiles(self.root_dir)
        self.profile_list.delete(0, "end")
        for folder_name, entry in self.profiles.items():
            data = entry["data"]
            lang = I18n._lang
            display = data.get("name", {}).get(lang) or data.get("id", folder_name)
            self.profile_list.insert("end", f"{display} ({folder_name})")
        if self.profiles:
            self.profile_list.selection_set(0)
            self._on_profile_selected()
        self.path_label.config(text=str(self.root_dir))

    def open_root(self):
        chosen = filedialog.askdirectory(initialdir=str(self.root_dir))
        if not chosen:
            return
        self.root_dir = Path(chosen)
        self.rescan_profiles()

    def _select_all_start_types(self) -> None:
        self.allowed_list.selection_set(0, "end")
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def _clear_start_types(self) -> None:
        self.allowed_list.selection_clear(0, "end")
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
        self.id_var.set(data.get("id", ""))
        name = data.get("name", {})
        self.name_zh_var.set(name.get("zh", ""))
        self.name_en_var.set(name.get("en", ""))
        desc = data.get("description", {})
        self.desc_zh.delete("1.0", "end")
        self.desc_zh.insert("1.0", desc.get("zh", ""))
        self.desc_en.delete("1.0", "end")
        self.desc_en.insert("1.0", desc.get("en", ""))
        self.cost_var.set(str(data.get("cost", 1)))
        self.type_var.set(str(data.get("type", 0)))
        allowed = {str(x) for x in data.get("allowedStartTypes", [])}
        self._ensure_start_types_for_allowed(allowed)
        self.allowed_list.selection_clear(0, "end")
        for i, key in enumerate(self.start_type_keys):
            if key in allowed:
                self.allowed_list.selection_set(i)
        self.items_list.delete(0, "end")
        for item in data.get("items", []):
            self.items_list.insert("end", item if isinstance(item, str) else json.dumps(item, ensure_ascii=False))
        self.remove_list.delete(0, "end")
        for rid in data.get("removeItems", []):
            self.remove_list.insert("end", rid)
        self.cash_var.set(str(data.get("extraCash", 0)))
        self.rent_var.set(str(data.get("extraRent", 0)))
        self.upgrades_list.delete(0, "end")
        for up in data.get("unlockedUpgrades", []):
            self.upgrades_list.insert("end", up)
        rep = data.get("factionReputationDelta", {})
        for key, var in self.rep_vars.items():
            var.set(str(rep.get(key, 0)))
        self._loading = False
        self._update_status()

    def _save_ui_to_current(self, silent: bool = False) -> bool:
        if self._loading or not self.current_id or self.current_id not in self.profiles:
            return True
        try:
            data = self.profiles[self.current_id]["data"]
            data["id"] = self.id_var.get().strip()
            data["name"] = {"zh": self.name_zh_var.get(), "en": self.name_en_var.get()}
            data["description"] = {
                "zh": self.desc_zh.get("1.0", "end").strip(),
                "en": self.desc_en.get("1.0", "end").strip(),
            }
            data["cost"] = int(self.cost_var.get() or "0")
            data["type"] = int(self.type_var.get() or "0")
            keys = self.start_type_keys
            selected = [int(keys[i]) for i in self.allowed_list.curselection()]
            if keys and len(selected) >= len(keys):
                selected = []
            data["allowedStartTypes"] = selected
            data["items"] = [self._parse_item_line(self.items_list.get(i)) for i in range(self.items_list.size())]
            data["removeItems"] = [self.remove_list.get(i) for i in range(self.remove_list.size())]
            data["extraCash"] = int(self.cash_var.get() or "0")
            data["extraRent"] = int(self.rent_var.get() or "0")
            data["unlockedUpgrades"] = [self.upgrades_list.get(i) for i in range(self.upgrades_list.size())]
            data["factionReputationDelta"] = {k: int(v.get() or "0") for k, v in self.rep_vars.items()}
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()
            return True
        except ValueError:
            if not silent:
                messagebox.showerror("Error", "Invalid numeric field")
            return False

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
        entry = self.profiles[self.current_id]
        folder = entry["folder"]
        (folder / PROFILE_FILE).write_text(json.dumps(entry["data"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        entry["dirty"] = False
        self._update_status()

    def save_all(self):
        sel = self.current_id
        for key in list(self.profiles.keys()):
            self.current_id = key
            self._load_profile_to_ui(self.profiles[key]["data"])
            self.save_current()
        self.current_id = sel
        self.rescan_profiles()

    def new_profile(self):
        profile_id = simpledialog.askstring(t("prompt_new_id"), t("prompt_new_id"), parent=self)
        if not profile_id:
            return
        profile_id = profile_id.strip()
        if not slug_ok(profile_id):
            messagebox.showerror("Error", t("invalid_id"))
            return
        folder = self.root_dir / profile_id
        if folder.exists():
            messagebox.showerror("Error", t("id_exists"))
            return
        folder.mkdir(parents=True, exist_ok=True)
        data = empty_profile(profile_id)
        (folder / PROFILE_FILE).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.rescan_profiles()
        keys = list(self.profiles.keys())
        if profile_id in keys:
            self.profile_list.selection_clear(0, "end")
            self.profile_list.selection_set(keys.index(profile_id))

    def duplicate_profile(self):
        if not self.current_id:
            return
        self._save_ui_to_current()
        src = deepcopy(self.profiles[self.current_id]["data"])
        new_id = src["id"] + "_copy"
        i = 2
        while (self.root_dir / new_id).exists():
            new_id = f"{src['id']}_copy{i}"
            i += 1
        src["id"] = new_id
        folder = self.root_dir / new_id
        folder.mkdir(parents=True)
        (folder / PROFILE_FILE).write_text(json.dumps(src, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        icon_src = self.profiles[self.current_id]["folder"] / ICON_FILE
        if icon_src.is_file():
            shutil.copy2(icon_src, folder / ICON_FILE)
        self.rescan_profiles()

    def delete_profile(self):
        if not self.current_id:
            return
        if not messagebox.askyesno("Confirm", t("confirm_delete")):
            return
        folder = self.profiles[self.current_id]["folder"]
        shutil.rmtree(folder)
        self.current_id = None
        self.rescan_profiles()

    def add_catalog_item(self):
        sel = self.catalog_list.curselection()
        if not sel:
            return
        item_id = self._catalog_ids[sel[0]]
        self.items_list.insert("end", item_id)
        if self.current_id:
            self.profiles[self.current_id]["dirty"] = True
            self._update_status()

    def add_catalog_to_remove(self):
        sel = self.catalog_list.curselection()
        if not sel:
            return
        item_id = self._catalog_ids[sel[0]]
        self.remove_list.insert("end", item_id)
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
    parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    args = parser.parse_args()
    args.root.mkdir(parents=True, exist_ok=True)
    app = ProfileEditor(
        args.root.resolve(),
        args.catalog.resolve(),
        args.start_types.resolve(),
        lang=args.lang,
    )
    app.mainloop()


if __name__ == "__main__":
    main()
