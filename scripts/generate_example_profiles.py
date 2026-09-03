#!/usr/bin/env python3
"""Generate profession-themed example custom-start profiles (excluding Rock Bottom / type 12)."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "example" / "custom-start"

FACTION_DEFAULTS = {
    "lower": 0,
    "upper": 0,
    "security": 0,
    "black_market": 0,
    "revolution": 0,
    "cartel": 0,
}

PROFILES = [
    {
        "id": "deep_well_supplier_1",
        "name": {"zh": "深井供应商", "en": "Deep Well Supplier"},
        "desc_zh": (
            "在下层区，干净的水比信用点还难找。你从小跟着水商网络跑管线，学会了用试纸和扫描仪辨纯度、估价格。"
            "如今盘下当铺，打算把「卖水」那套验货流程搬到杂货柜台——滤水器、检测试剂和霓虹水牌，都是你的老本行。\n\n"
            "【特性】\n"
            "· 水质检测与滤水工具\n"
            "· 瓶装水样本与交易手册\n"
            "· 开局现金 +150\n"
            "· 仅「水商」起始可选"
        ),
        "desc_en": (
            "In the Lower Levels, clean water is harder to find than credits. You grew up running pipelines "
            "for the water traders, learning to read purity with strips and scanners. Now you have a pawn shop—and "
            "plan to bring that inspection workflow to the counter: filters, test kits, and a neon water sign.\n\n"
            "【Features】\n"
            "· Water testing and filtration tools\n"
            "· Sample bottled water and trading manual\n"
            "· Begin with 150 extra cash\n"
            "· Water Merchant start only"
        ),
        "st": 1,
        "items": [
            "water_guide",
            "aquascan",
            "water_test_container",
            "water_test_strip",
            "water_filter",
            "bottled_water",
            "sign_water",
        ],
        "extraCash": 150,
        "faction": {"lower": 15},
    },
    {
        "id": "counter_apprentice_2",
        "name": {"zh": "柜台学徒", "en": "Counter Apprentice"},
        "desc_zh": (
            "你曾在老当铺师傅手下打了三年杂：贴标签、验成色、记金属价。师傅退休前塞给你一只小背包和一本成色指南，"
            "说「开自己的铺子吧，别把我教你的估价本事浪费了」。\n\n"
            "【特性】\n"
            "· 贴标机、放大镜与成色手册\n"
            "· 小背包\n"
            "· 仅「学徒」起始可选"
        ),
        "desc_en": (
            "You spent three years under an old pawnbroker: labeling, grading, logging metal prices. "
            'When he retired he handed you a small backpack and an ingot guide—"Open your own shop. '
            'Don\'t waste what I taught you about appraisal."\n\n'
            "【Features】\n"
            "· Labeler, magnifier, and ingot guide\n"
            "· Small backpack\n"
            "· Apprentice start only"
        ),
        "st": 2,
        "items": ["labeler", "magnifier", "ingot_book", "backpack_small"],
        "extraCash": 0,
        "faction": {},
    },
    {
        "id": "dump_diver_3",
        "name": {"zh": "垃圾场潜水员", "en": "Dump Diver"},
        "desc_zh": (
            "倾倒区是你的第二故乡。手电照路、扫描仪寻宝、剪线钳和焊枪拆废件——这套流程你闭着眼都能走。"
            "当铺只是换了个地方存货；战斗匕首和止血绷带，是垃圾场教给你的保险。\n\n"
            "【特性】\n"
            "· 完整拾荒工具链\n"
            "· 拾荒者信物与应急医疗\n"
            "· 开局现金 -100\n"
            "· 仅「拾荒者」起始可选"
        ),
        "desc_en": (
            "The Dumping Grounds are your second home. Flashlight, scanner, wire cutters, welder—you could run "
            "the salvage loop blindfolded. The pawn shop is just another stash; the knife and bandages are insurance "
            "the dump taught you.\n\n"
            "【Features】\n"
            "· Full scavenging toolkit\n"
            "· Scavenger token and emergency med\n"
            "· Begin with 100 less cash\n"
            "· Scavenger start only"
        ),
        "st": 3,
        "items": [
            "flashlight",
            "metal_scanner",
            "wire_cutter",
            "welder",
            "screwdriver",
            "scav_token",
            "combat_knife",
            "hemostatic_bandage",
        ],
        "extraCash": -100,
        "faction": {"lower": 20},
    },
    {
        "id": "gray_market_broker_4",
        "name": {"zh": "灰市中间人", "en": "Gray Market Broker"},
        "desc_zh": (
            "你不问货从哪来，只问值多少钱。销赃者的本事是快眼估价、快嘴压价，以及必要时用非致命手段让交易继续。"
            "放大镜、贴标机和电击枪，是你在灰市站稳脚跟的三件套。\n\n"
            "【特性】\n"
            "· 估价与经营工具\n"
            "· 电击枪（自卫）\n"
            "· 开局现金 +200\n"
            "· 仅「销赃者」起始可选"
        ),
        "desc_en": (
            "You never ask where goods come from—only what they are worth. A fence lives on quick appraisal, "
            "quick haggling, and when needed, a non-lethal nudge to close the deal. Magnifier, labeler, and stun gun: "
            "your gray-market trinity.\n\n"
            "【Features】\n"
            "· Appraisal and shop tools\n"
            "· Stun gun for self-defense\n"
            "· Begin with 200 extra cash\n"
            "· Fence start only"
        ),
        "st": 4,
        "items": ["magnifier", "labeler", "stun_gun", "ingot_book", "sign_generic"],
        "extraCash": 200,
        "faction": {"black_market": 25},
    },
    {
        "id": "cellar_brewer_5",
        "name": {"zh": "地窖酿师", "en": "Cellar Brewer"},
        "desc_zh": (
            "红鬼酒厂的名片还在钱包里——那是你还没被赶出来时的身份。地窖里藏着发酵锁、催陈器和一本酿酒笔记；"
            "廉价酒精和空酒瓶，是下一批私酿的起点。\n\n"
            "【特性】\n"
            "· 私酿发酵与催陈设备\n"
            "· 酿酒手册与酵母\n"
            "· 开局现金 -50\n"
            "· 仅「私酿酒师」起始可选"
        ),
        "desc_en": (
            "The Red Imp Brewery card is still in your wallet—from before they threw you out. The cellar holds "
            "an airlock, ager, and brewing notes; cheap alcohol and empty bottles are the seed of the next batch.\n\n"
            "【Features】\n"
            "· Homebrew fermentation and aging gear\n"
            "· Brewing manual and yeast\n"
            "· Begin with 50 less cash\n"
            "· Moonshiner start only"
        ),
        "st": 5,
        "items": [
            "card_brewer",
            "age_well",
            "fermentation_airlock",
            "wine_bottle",
            "wine_yeast",
            "wine_book",
            "rubbing_alcohol",
        ],
        "extraCash": -50,
        "faction": {"lower": 15},
    },
    {
        "id": "back_alley_chemist_6",
        "name": {"zh": "后巷化学家", "en": "Back-Alley Chemist"},
        "desc_zh": (
            "化学家的名片上印着假地址，量筒和滴管才是真话。你在后巷搭过小实验室，用扫描仪辨纯度、用储物舱藏原料。"
            "当铺柜台是新的掩护，配方笔记锁在抽屉里。\n\n"
            "【特性】\n"
            "· 化学指南与纯度扫描仪\n"
            "· 量筒、滴管与原料\n"
            "· 化学储物舱\n"
            "· 开局现金 -150\n"
            "· 仅「化学家」起始可选"
        ),
        "desc_en": (
            "The chemist card lists a fake address; cylinders and droppers tell the truth. You ran a back-alley lab—"
            "scanner for purity, storage bay for reagents. The pawn counter is cover; the recipe notes stay in the drawer.\n\n"
            "【Features】\n"
            "· Chemistry guide and purity scanner\n"
            "· Lab glassware and reagents\n"
            "· Chemical storage bay\n"
            "· Begin with 150 less cash\n"
            "· Drug Dealer start only"
        ),
        "st": 6,
        "items": [
            "card_chem",
            "chemistry_guide",
            "chem_scanner",
            "25ml_cylinder",
            "5ml_dropper",
            "common_chemical",
            "storage_bay_chem",
        ],
        "extraCash": -150,
        "faction": {"black_market": 15},
    },
    {
        "id": "cold_chain_courier_7",
        "name": {"zh": "冷链跑腿", "en": "Cold-Chain Courier"},
        "desc_zh": (
            "器官交易不靠吆喝，靠时效和保密。你做过冷链跑腿：医疗包、受限药品、止血与包扎耗材，哪一样都不能在路上出问题。"
            "医疗霓虹灯牌挂在当铺门口，是留给懂行人的暗号。\n\n"
            "【特性】\n"
            "· 医疗包与受限药品\n"
            "· 包扎与止血耗材\n"
            "· 医疗霓虹灯牌\n"
            "· 开局现金 +100\n"
            "· 仅「器官贩子」起始可选"
        ),
        "desc_en": (
            "Organ trade runs on timing and discretion. You were a cold-chain courier—medical pouch, restricted meds, "
            "bandages that cannot fail in transit. The medical neon sign outside the shop is a signal for those who know.\n\n"
            "【Features】\n"
            "· Medical pouch and restricted supplies\n"
            "· Bandaging and hemostatic kit\n"
            "· Medical neon sign\n"
            "· Begin with 100 extra cash\n"
            "· Organ Trader start only"
        ),
        "st": 7,
        "items": [
            "sign_medical",
            "medical_pouch",
            "restricted_medical",
            "hemostatic_bandage",
            "bandage",
            "topical_bandage",
        ],
        "extraCash": 100,
        "faction": {"upper": 10, "black_market": 10},
    },
    {
        "id": "corner_pharmacist_8",
        "name": {"zh": "街角药剂师", "en": "Corner Pharmacist"},
        "desc_zh": (
            "上层区吊销执照后，你在下层区街角续上了生意。名片、常见药瓶和几本常备药，加上医疗灯牌，足够让熟客认出你。"
            "当铺多一个合法外壳，柜台后仍是你熟悉的药架。\n\n"
            "【特性】\n"
            "· 药剂师名片与常备药\n"
            "· 常见医疗物资\n"
            "· 医疗霓虹灯牌\n"
            "· 开局现金 +50\n"
            "· 仅「药剂师」起始可选"
        ),
        "desc_en": (
            "After Upper Levels revoked your license, you kept going on a Lower Levels corner. Business card, "
            "pill bottles, common meds, and a medical sign—enough for regulars to find you. The pawn shop adds "
            "a legal front; behind the counter it is still your pharmacy.\n\n"
            "【Features】\n"
            "· Pharmacist card and staple medicines\n"
            "· Common medical supplies\n"
            "· Medical neon sign\n"
            "· Begin with 50 extra cash\n"
            "· Pharmacist start only"
        ),
        "st": 8,
        "items": [
            "card_pharma",
            "pill_bottle",
            "bicarsole_pill_bottle",
            "fixalin_pill_bottle",
            "common_medical",
            "sign_medical",
        ],
        "extraCash": 50,
        "faction": {"upper": 15},
    },
    {
        "id": "neon_noodle_stall_9",
        "name": {"zh": "霓虹面摊", "en": "Neon Noodle Stall"},
        "desc_zh": (
            "小吃摊的霓虹灯牌还在你手里。厨刀、剁骨刀和加工奶酪，是摊位关张后仅剩的家当。"
            "食物券识别手册帮你在当铺里分清哪些货能换口粮；能量棒和猫条，是你自己的晚饭。\n\n"
            "【特性】\n"
            "· 餐饮霓虹灯牌与厨具\n"
            "· 食物券与应急口粮\n"
            "· 开局现金 +100\n"
            "· 仅「街头小吃摊」起始可选"
        ),
        "desc_en": (
            "You still have the food stall neon sign. Cleavers and processed cheese are what is left after the stall closed. "
            "Food stamps help sort trade-ins at the counter; energy bars and cat treats are your own dinner.\n\n"
            "【Features】\n"
            "· Food neon sign and kitchen tools\n"
            "· Food stamps and emergency rations\n"
            "· Begin with 100 extra cash\n"
            "· Street Food Vendor start only"
        ),
        "st": 9,
        "items": [
            "sign_food",
            "food_stamp",
            "kitchen_knife",
            "kitchen_cleaver",
            "cat_bar",
            "energy_drink",
            "processed_cheese",
        ],
        "extraCash": 100,
        "faction": {"lower": 20},
    },
    {
        "id": "moisture_farmer_10",
        "name": {"zh": "湿气农夫", "en": "Moisture Farmer"},
        "desc_zh": (
            "农场主没地可种，只能向天花板要湿度。水分收集器、水培单元和营养片，加上梦幻浆果种子，"
            "是你从农庄带到当铺的全部家当。种植手册卷边处，还夹着当铺租约。\n\n"
            "【特性】\n"
            "· 水分收集与水培设备\n"
            "· 营养片与种子\n"
            "· 水培种植手册\n"
            "· 开局现金 -100\n"
            "· 仅「农场主」起始可选"
        ),
        "desc_en": (
            "With no soil left, you farm the humidity. Moisture collector, hydroponic unit, nutrient tablets, "
            "and bloomberry seeds—that is what you brought from the farm to the pawn shop. The growing manual "
            "still has the lease tucked in its pages.\n\n"
            "【Features】\n"
            "· Moisture and hydroponic gear\n"
            "· Nutrient tablets and seeds\n"
            "· Hydroponic farming manual\n"
            "· Begin with 100 less cash\n"
            "· Farmer start only"
        ),
        "st": 10,
        "items": [
            "hydroponic_guide",
            "hydroponic",
            "hydroponic_nutrient_tablet",
            "moisture_farm",
            "bloomberry_seed",
        ],
        "extraCash": -100,
        "faction": {"lower": 15},
    },
    {
        "id": "bench_gunsmith_11",
        "name": {"zh": "工位枪匠", "en": "Bench Gunsmith"},
        "desc_zh": (
            "枪匠铺子黄了，工位上的 3D 打印机和零件箱跟你到了当铺。一级枪证挂在墙上，储物舱专门留给枪件；"
            "打印手枪是样品，螺丝刀是日常。保安部门的人扫你一眼，就知道你懂规矩。\n\n"
            "【特性】\n"
            "· 3D 打印机与枪件\n"
            "· 一级枪证与枪匠储物舱\n"
            "· 开局现金 -200\n"
            "· 仅「枪匠」起始可选"
        ),
        "desc_en": (
            "The gunsmith shop folded; the 3D printer and parts crate moved with you. Tier-1 permit on the wall, "
            "storage bay for gun parts, printed pistol as a sample, screwdriver for daily work. Security knows "
            "you play by the rules.\n\n"
            "【Features】\n"
            "· 3D printer and gun parts\n"
            "· Tier-1 gun permit and gunsmith storage bay\n"
            "· Begin with 200 less cash\n"
            "· Gunsmith start only"
        ),
        "st": 11,
        "items": [
            "gun_part",
            "3d_printer",
            "printed_gun",
            "permit_gun_1",
            "storage_bay_gun",
            "screwdriver",
        ],
        "extraCash": -200,
        "faction": {"security": 10},
    },
    {
        "id": "rat_ranch_starter_13",
        "name": {"zh": "养鼠起步", "en": "Rat Ranch Starter"},
        "desc_zh": (
            "养鼠人在下层区不算稀奇，稀奇的是把鼠场开进当铺。你带着种鼠、投喂器和捕鼠夹——还有一块加工奶酪当诱饵。"
            "熟客知道，柜台后面那扇门后，总有窸窸窣窣的动静。\n\n"
            "【特性】\n"
            "· 种鼠与投喂设备\n"
            "· 捕鼠夹与诱饵\n"
            "· 小背包\n"
            "· 开局现金 -50\n"
            "· 仅「养鼠人」起始可选"
        ),
        "desc_en": (
            "Ranchers are common in the Lower Levels; what is rare is running the ranch inside a pawn shop. "
            "You brought breeding stock, a feeder, traps, and processed cheese for bait. Regulars know something "
            "always rustles behind that back door.\n\n"
            "【Features】\n"
            "· Breeding rat and feeder\n"
            "· Traps and bait\n"
            "· Small backpack\n"
            "· Begin with 50 less cash\n"
            "· Rancher start only"
        ),
        "st": 13,
        "items": ["rat", "feed_dispenser", "mouse_trap", "processed_cheese", "backpack_small"],
        "extraCash": -50,
        "faction": {"lower": 25},
    },
]


def main() -> None:
    for folder in ROOT.iterdir():
        if folder.is_dir() and folder.name.startswith("the_cyber_bear_") and folder.name != "the_cyber_bear_12":
            shutil.rmtree(folder)
            print(f"removed {folder.name}")

    for spec in PROFILES:
        profile = {
            "version": 1,
            "id": spec["id"],
            "name": spec["name"],
            "description": {"zh": spec["desc_zh"], "en": spec["desc_en"]},
            "cost": 0,
            "type": 0,
            "allowedStartTypes": [spec["st"]],
            "items": spec["items"],
            "removeItems": [],
            "extraCash": spec["extraCash"],
            "extraRent": 0,
            "unlockedUpgrades": [],
            "factionReputationDelta": {**FACTION_DEFAULTS, **spec.get("faction", {})},
        }
        out_dir = ROOT / profile["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "profile.json").write_text(
            json.dumps(profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"created {profile['id']}")

    total = sum(1 for p in ROOT.iterdir() if p.is_dir())
    print(f"done ({total} profile folders under {ROOT})")


if __name__ == "__main__":
    main()
