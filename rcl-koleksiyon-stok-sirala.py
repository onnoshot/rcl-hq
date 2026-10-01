#!/usr/bin/env python3
"""Move sold-out products to the end of every manually sorted collection.

Idempotent: keeps the existing relative order inside the in-stock and sold-out
groups, and does nothing when a collection is already in that shape.
Usage: python3 rcl-koleksiyon-stok-sirala.py [--dry-run]
"""
import json
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from retrocameraland_api import SHOPIFY_TOKEN

SHOP = "6w0ejb-4b.myshopify.com"
API = f"https://{SHOP}/admin/api/2025-10/graphql.json"
SKIP_PREFIXES = ("gsc-",)  # app-managed collections
BACKUP_DIR = Path(__file__).parent / "outputs" / "rcl-koleksiyon-sira-yedek"


def gql(query, variables=None):
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"},
    )
    out = json.load(urllib.request.urlopen(req, timeout=60))
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]


def collection_products(cid):
    items, after = [], None
    while True:
        data = gql(
            """query($id:ID!,$a:String){collection(id:$id){products(first:100,after:$a,sortKey:COLLECTION_DEFAULT){
                 pageInfo{hasNextPage endCursor}
                 nodes{id title status variants(first:20){nodes{availableForSale}}}}}}""",
            {"id": cid, "a": after},
        )["collection"]["products"]
        for p in data["nodes"]:
            in_stock = p["status"] == "ACTIVE" and any(v["availableForSale"] for v in p["variants"]["nodes"])
            items.append({"id": p["id"], "title": p["title"], "in_stock": in_stock})
        if not data["pageInfo"]["hasNextPage"]:
            return items
        after = data["pageInfo"]["endCursor"]


def main():
    dry = "--dry-run" in sys.argv
    cols = gql("{collections(first:100){nodes{id handle sortOrder productsCount{count}}}}")["collections"]["nodes"]
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    for c in cols:
        if c["sortOrder"] != "MANUAL" or c["handle"].startswith(SKIP_PREFIXES) or c["productsCount"]["count"] < 2:
            continue
        items = collection_products(c["id"])
        wanted = [p for p in items if p["in_stock"]] + [p for p in items if not p["in_stock"]]
        n_in = sum(p["in_stock"] for p in items)
        if [p["id"] for p in wanted] == [p["id"] for p in items]:
            print(f"{c['handle']}: already ordered ({n_in} in stock / {len(items)})")
            continue
        print(f"{c['handle']}: reordering ({n_in} in stock / {len(items)})")
        if dry:
            continue
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        (BACKUP_DIR / f"{stamp}_{c['handle']}.json").write_text(
            json.dumps([p["id"] for p in items], indent=1), encoding="utf-8"
        )
        moves = [{"id": p["id"], "newPosition": str(i)} for i, p in enumerate(wanted)]
        for i in range(0, len(moves), 250):
            res = gql(
                """mutation($id:ID!,$m:[MoveInput!]!){collectionReorderProducts(id:$id,moves:$m){
                     job{id} userErrors{field message}}}""",
                {"id": c["id"], "m": moves[i : i + 250]},
            )["collectionReorderProducts"]
            if res["userErrors"]:
                raise RuntimeError(res["userErrors"])
            time.sleep(1)


if __name__ == "__main__":
    main()
