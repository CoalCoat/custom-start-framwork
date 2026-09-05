#!/usr/bin/env python3
"""Analyze Probably Stolen ES3 save for custom-start profile opportunities."""
import json
import re
import sys
from pathlib import Path

SAVE = Path(r"c:\Users\49479\AppData\LocalLow\Questing Goose Studio\Probably Stolen\save_19.es3")

SCALAR_FIELDS = [
    "playerCash", "wildFavor", "saveSlotId", "runNumber", "dayUntilRent", "rentValue",
    "dayUntilLoan", "loanValue", "startingRent", "temporaryRent", "retailMarkup",
    "contrabandMarkupLow", "contrabandMarkupMid", "contrabandMarkupHigh", "contrabandMarkupCritial",
    "baseStoreAttractiveness", "projectorAttractivenessBonus", "garbageLevel", "isPowerOn",
    "dayWithoutInsurance", "foreclosePercentage", "contrabandFinePercentage",
    "machineryBoughtCount", "startType", "hardMode", "endlessMode", "skipIntro",
    "hasBusinessPermit", "odinBudget", "isPayingMortgage", "mortgageWeekLeft",
    "mortgageWeeklyPayment", "dealMakerBargainBonus", "lastInspectionLossDay",
    "lastInspectionLossValue", "lastTheftDay", "lastTheftValue",
]

INV_JSON_KEYS = [
    "mainInvJSON", "backInvJSON", "showcaseInvJSON", "hiddenInvJSON",
    "trashcanInvJSON", "docInvJSON", "vendingMachineInvJSON",
]


def extract_scalars(text: str) -> dict:
    out = {}
    for f in SCALAR_FIELDS:
        m = re.search(r'"' + re.escape(f) + r'"\s*:\s*([^,}\]]+)', text)
        if m:
            raw = m.group(1).strip()
            if raw in ("true", "false"):
                out[f] = raw == "true"
            elif raw.startswith('"'):
                out[f] = raw.strip('"')
            else:
                try:
                    out[f] = int(raw) if "." not in raw else float(raw)
                except ValueError:
                    out[f] = raw
    return out


def extract_faction_reps(text: str) -> list:
    reps = []
    for m in re.finditer(
        r'"amount"\s*:\s*(-?\d+)\s*,\s*"factionDisplay"[^}]*?"factionId"\s*:\s*"([^"]+)"',
        text,
    ):
        reps.append({"factionId": m.group(2), "amount": int(m.group(1))})
    return reps


def extract_store_services(text: str) -> list:
    services = []
    for m in re.finditer(
        r'"serviceId"\s*:\s*"([^"]+)"[^}]*?"isActive"\s*:\s*(true|false)',
        text,
    ):
        if m.group(2) == "true":
            services.append(m.group(1))
    return sorted(set(services))


def extract_all_playerstore_keys(text: str) -> list:
    """Keys directly under playerStore.value object (first ~30k chars)."""
    m = re.search(r'"playerStore"\s*:\s*\{[^}]*"value"\s*:\s*\{', text)
    if not m:
        return []
    start = m.end()
    chunk = text[start : start + 80000]
    return sorted(set(re.findall(r'"([a-zA-Z][a-zA-Z0-9_]*)"\s*:', chunk)))


def extract_unlocked_upgrades(text: str) -> list:
    upgrades = []
    # networkUpgrade is a dict keyed by upgrade id
    block = re.search(r'"networkUpgrade"\s*:\s*\{', text)
    if not block:
        return upgrades
    start = block.end() - 1
    depth = 0
    end = start
    for i in range(start, min(start + 50000, len(text))):
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    chunk = text[start:end]
    for m in re.finditer(r'"([A-Z0-9_]+)"\s*:\s*\{[^}]*?"isUnlocked"\s*:\s*true', chunk):
        upgrades.append(m.group(1))
    return sorted(set(upgrades))


def extract_starting_perks(text: str) -> list:
    perks = []
    for m in re.finditer(r'"startingPerk[^"]*"\s*:\s*"([^"]+)"', text):
        perks.append(m.group(1))
    for m in re.finditer(r'"id"\s*:\s*"([a-z0-9_]+)"[^}]*?"isSelected"\s*:\s*true', text):
        pid = m.group(1)
        if pid not in perks:
            perks.append(pid)
    return perks


def extract_items_from_inv_json(inv_text: str) -> list:
    """Parse nested JSON string inside mainInvJSON etc."""
    items = []
    try:
        inv = json.loads(inv_text)
    except json.JSONDecodeError:
        # fallback: identifier fields
        for m in re.finditer(r'"identifier"\s*:\s*"([^"]+)"', inv_text):
            items.append({"id": m.group(1)})
        return items

    def walk(node):
        if isinstance(node, dict):
            ident = node.get("identifier") or node.get("id")
            if ident:
                entry = {"id": ident}
                if "charge" in node:
                    entry["charge"] = node["charge"]
                if "waterType" in node or "water" in node:
                    entry["water"] = node.get("waterType") or node.get("water")
                if "volumeMl" in node:
                    entry["volumeMl"] = node["volumeMl"]
                items.append(entry)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(inv)
    return items


def extract_inventory_items(text: str) -> dict:
    result = {}
    for key in INV_JSON_KEYS:
        m = re.search(r'"' + re.escape(key) + r'"\s*:\s*"((?:\\.|[^"\\])*)"', text)
        if not m:
            continue
        raw = m.group(1)
        try:
            decoded = json.loads('"' + raw + '"')  # unescape
        except json.JSONDecodeError:
            decoded = raw.replace('\\"', '"').replace('\\\\', '\\')
        result[key] = extract_items_from_inv_json(decoded)
    return result


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SAVE
    text = path.read_text(encoding="utf-8", errors="replace")
    print(f"=== Save analysis: {path.name} ({len(text)} chars) ===\n")

    scalars = extract_scalars(text)
    print("--- PlayerStore scalars (start-relevant) ---")
    for k in SCALAR_FIELDS:
        if k in scalars:
            print(f"  {k}: {scalars[k]}")

    reps = extract_faction_reps(text)
    print("\n--- Faction reputations ---")
    for r in reps:
        print(f"  {r['factionId']}: {r['amount']}")

    services = extract_store_services(text)
    if services:
        print(f"\n--- Active store services ({len(services)}) ---")
        for s in services:
            print(f"  {s}")

    ps_keys = extract_all_playerstore_keys(text)
    print(f"\n--- All PlayerStore.value keys ({len(ps_keys)}) ---")
    print("  " + ", ".join(ps_keys))

    upgrades = extract_unlocked_upgrades(text)
    print(f"\n--- Unlocked network upgrades ({len(upgrades)}) ---")
    for u in upgrades:
        print(f"  {u}")

    inv = extract_inventory_items(text)
    print("\n--- Inventory items by zone ---")
    for zone, items in inv.items():
        ids = [i["id"] for i in items]
        print(f"  {zone}: {len(ids)} items")
        if ids:
            print(f"    {', '.join(ids[:30])}" + (" ..." if len(ids) > 30 else ""))

    # Compare to framework profile fields
    print("\n--- Framework mapping ---")
    framework_supported = {
        "items": "mainInvJSON + backInvJSON (counter + backpack)",
        "removeItems": "N/A in save (manual)",
        "extraCash": "playerCash (delta from startType baseline)",
        "extraRent": "startingRent / rentValue delta",
        "unlockedUpgrades": "networkUpgrade[*].isUnlocked",
        "factionReputationDelta": "storeReputations[*].amount",
    }
    for field, source in framework_supported.items():
        print(f"  profile.{field} <- {source}")

    # Candidate new fields NOT in framework yet
    framework_fields = {
        "items", "removeItems", "extraCash", "extraRent",
        "unlockedUpgrades", "factionReputationDelta",
        "compensateWildFavorForLowerRep",
    }
    interesting_keys = [
        k for k in ps_keys
        if k not in {
            "storeClientManager", "storeReputations", "networkUpgrade",
            "storeServices", "nightLogs", "dialogHistory", "storeUIZoomLevels",
            "futurStoreClientIdQueue", "futurStoreClientDayQueue",
            "mainInvJSON", "backInvJSON", "showcaseInvJSON", "hiddenInvJSON",
            "trashcanInvJSON", "docInvJSON", "vendingMachineInvJSON",
            "runID", "lastSaveTime", "wealthHistory", "runPlayTimeSeconds",
            "totalPlayTimeSeconds", "saveSlotId",
        }
        and not k.endswith("JSON")
    ]

    candidates = {
        "wildFavor (extraWildFavor?)": scalars.get("wildFavor"),
        "loanValue / dayUntilLoan": (scalars.get("loanValue"), scalars.get("dayUntilLoan")),
        "retailMarkup": scalars.get("retailMarkup"),
        "contrabandMarkup*": {k: scalars.get(k) for k in SCALAR_FIELDS if "contrabandMarkup" in k and k in scalars},
        "hasBusinessPermit": scalars.get("hasBusinessPermit"),
        "baseStoreAttractiveness (+bonus)": (scalars.get("baseStoreAttractiveness"), scalars.get("projectorAttractivenessBonus")),
        "showcaseInv / hiddenInv": (len(inv.get("showcaseInvJSON", [])), len(inv.get("hiddenInvJSON", []))),
        "hardMode/endlessMode/skipIntro": (scalars.get("hardMode"), scalars.get("endlessMode"), scalars.get("skipIntro")),
        "startType": scalars.get("startType"),
        "odinBudget": scalars.get("odinBudget"),
        "mortgage fields": (scalars.get("isPayingMortgage"), scalars.get("mortgageWeekLeft"), scalars.get("mortgageWeeklyPayment")),
        "store services active": services,
        "other scalar keys to consider": interesting_keys,
    }
    print("\n--- Candidate NEW profile fields (not in framework v1) ---")
    for k, v in candidates.items():
        if v is not None and v != (None, None) and v != {}:
            print(f"  {k}: {v}")


def compare_saves(root: Path, limit: int = 30):
    files = sorted(root.glob("save_*.es3")) + sorted((root / "backups").rglob("*.es3"))
    rows = []
    for p in files:
        t = p.read_text(encoding="utf-8", errors="replace")
        cash_m = re.search(r'"playerCash"\s*:\s*(-?\d+)', t)
        run_m = re.search(r'"runNumber"\s*:\s*(\d+)', t)
        st_m = re.search(r'"startType"\s*:\s*(\d+)', t)
        unlocked = len(re.findall(r'"isUnlocked"\s*:\s*true', t))
        rows.append((
            p.name,
            p.parent.name,
            int(cash_m.group(1)) if cash_m else -1,
            int(run_m.group(1)) if run_m else -1,
            int(st_m.group(1)) if st_m else -1,
            unlocked,
            len(t),
        ))
    rows.sort(key=lambda r: (r[2], r[5], r[6]), reverse=True)
    print("\n=== Save comparison (top by cash / unlocks) ===")
    print("file | folder | cash | run# | startType | unlocked | size")
    for r in rows[:limit]:
        print(" | ".join(map(str, r)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--compare":
        compare_saves(Path(sys.argv[2]) if len(sys.argv) > 2 else SAVE.parent)
    else:
        path = Path(sys.argv[1]) if len(sys.argv) > 1 else SAVE
        # temporarily override SAVE for main()
        globals()["SAVE"] = path
        main()
