#!/usr/bin/env python3
"""Build a small, attributed Penny Scout lead feed from Penny Recon's public JSON.

Personal-use lead aggregator, not a Home Depot price/stock service.
Only the public URL below is fetched; no authentication, scraping, or retailer calls.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "leads.json"
SOURCE = "https://www.pennyrecon.com/data/items.json"
AL = "AL"
ADJACENT = {"TN", "GA", "MS"}
MAX_ITEMS = 175
MAX_DAYS = 42
UTC = dt.timezone.utc


def digits(value):
    if value is None or str(value).startswith("$undefined"):
        return ""
    return re.sub(r"\D", "", str(value))


def iso_date(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        return None


def category_for(name):
    t = name.lower()
    groups = [
        ("Lighting", "light", "lamp", "bulb", "led", "lantern", "fixture"),
        ("Garden", "cooler", "grill", "hose", "sprinkler", "lawn", "mower", "patio", "outdoor", "rake"),
        ("Flooring", "floor", "vinyl plank", "tile", "laminate"),
        ("Tools", "drill", "vacuum", "tool", "driver", "welder", "saw", "wrench", "work light", "clamp fan"),
        ("Hardware", "nail", "bolt", "screw", "lock", "hinge", "adhesive", "stripper", "hand truck"),
        ("Home", "toilet", "shower", "faucet", "fan", "storage", "bath", "sink"),
    ]
    for row in groups:
        if any(k in t for k in row[1:]):
            return row[0]
    return "Other"


def normalize(items, now=None):
    now = now or dt.datetime.now(UTC)
    if not isinstance(items, list) or len(items) < 10:
        raise ValueError("Unexpected upstream JSON structure")
    cleaned = {}
    for raw in items:
        if not isinstance(raw, dict):
            continue
        sku = digits(raw.get("sku"))
        name = raw.get("name")
        when = iso_date(raw.get("lastSeenAt"))
        if not (5 <= len(sku) <= 14 and isinstance(name, str) and 4 <= len(name) <= 200 and when):
            continue
        days = (now - when).total_seconds() / 86400
        if days > MAX_DAYS or days < -2:
            continue
        if raw.get("tier") not in ("hot", "active", "fading"):
            continue
        states = raw.get("states") or {}
        states = {str(k).upper(): int(v) for k, v in states.items() if isinstance(k, str) and k.isalpha() and len(k) == 2 and isinstance(v, int) and v > 0} if isinstance(states, dict) else {}
        region = "alabama" if states.get(AL) else "regional" if any(states.get(k) for k in ADJACENT) else "national"
        internet = digits(raw.get("internetNumber"))
        upc = digits(raw.get("upc"))
        if len(upc) not in (11, 12, 13, 14):
            upc = ""
        retail = raw.get("retail")
        retail = round(float(retail), 2) if isinstance(retail, (int, float)) and 0 <= retail <= 100000 else None
        score = raw.get("score")
        score = round(float(score), 1) if isinstance(score, (int, float)) else 0.0
        source_count = max(0, int(raw.get("sourceCount") or 0))
        reports = max(0, int(raw.get("reports") or 0))
        entry = {
            "id": "pr-" + sku, "name": name.strip()[:180], "brand": str(raw.get("brand") or "").replace("$undefined", "")[:60],
            "sku": sku, "upc": upc, "internet": internet,
            "retail": retail, "category": category_for(name),
            "lastSeenAt": when.isoformat().replace("+00:00", "Z"),
            "reports": reports, "sourceCount": source_count, "stateCounts": states,
            "region": region, "tier": raw.get("tier"),
            "likelihood": raw.get("likelihood") if raw.get("likelihood") in ("high", "medium", "low") else "unknown",
            "score": score, "source": "Penny Recon", "reportUrl": "https://www.pennyrecon.com/item/" + sku + "/",
            "productUrl": "https://www.homedepot.com/p/" + internet if len(internet) == 9 else "",
        }
        old = cleaned.get(sku)
        if old is None or (when, reports) > (iso_date(old["lastSeenAt"]), old["reports"]):
            cleaned[sku] = entry
    if len(cleaned) < 10:
        raise ValueError("Too few valid reports; refusing to overwrite existing data")
    order = {"alabama": 0, "regional": 1, "national": 2}
    sorted_items = sorted(cleaned.values(), key=lambda x: (order[x["region"]], {"hot":0,"active":1,"fading":2}.get(x["tier"], 3), -x["score"], x["lastSeenAt"]), reverse=False)
    return sorted_items[:MAX_ITEMS]


def refresh():
    request = urllib.request.Request(SOURCE, headers={"User-Agent": "PennyScoutPersonal/2.0 (daily community lead reader)", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=25) as response:
        raw = response.read(2_500_001)
        if len(raw) > 2_500_000:
            raise ValueError("Source unexpectedly large")
        incoming = json.loads(raw)
    now = dt.datetime.now(UTC)
    items = normalize(incoming, now)
    payload = {
        "schema": 2, "feedStatus": "updated", "generatedAt": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "sourceName": "Penny Recon", "sourceUrl": SOURCE,
        "storeId": "0887", "storeConfirmed": False,
        "description": "Community penny reports. Alabama is a state-wide signal, NOT a confirmed Trussville price or inventory check.",
        "items": items,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    temp = DEST.with_suffix('.tmp')
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding="utf-8")
    temp.replace(DEST)
    print(f"Refreshed {len(items)} reported leads; Alabama: {sum(x['region'] == 'alabama' for x in items)}")


if __name__ == "__main__":
    try:
        refresh()
    except Exception as e:
        print(f"Warning: Could not refresh source ({e}). Keeping bundled data, clearly dated.", file=sys.stderr)
        if not DEST.exists():
            sys.exit(1)
