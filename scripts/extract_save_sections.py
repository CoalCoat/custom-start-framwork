import re, json
from pathlib import Path

def show(path, patterns):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    for pat in patterns:
        m = re.search(pat, text, re.DOTALL)
        print(f"\n=== {pat[:40]}... ===")
        if m:
            s = m.group(0)
            print(s[:2000] + ("..." if len(s) > 2000 else ""))
        else:
            print("NOT FOUND")

save2 = r"c:\Users\49479\AppData\LocalLow\Questing Goose Studio\Probably Stolen\save_2.es3"
save19 = r"c:\Users\49479\AppData\LocalLow\Questing Goose Studio\Probably Stolen\save_19.es3"

for label, p in [("save_2", save2), ("save_19", save19)]:
    print("\n" + "=" * 60)
    print(label)
    show(p, [
        r'"storeReputations"\s*:\s*\[.*?\]',
        r'"networkUpgrade"\s*:\s*\{.*?\}',
        r'"storeService"\s*:\s*\{.*?\}',
        r'"futurStoreClientIdQueue"\s*:\s*\[[^\]]*\]',
        r'"healthData"\s*:\s*\{.*?\}',
        r'"ActivePermits"\s*:\s*\[[^\]]*\]',
    ])
