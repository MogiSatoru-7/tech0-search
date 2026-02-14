# ===================================================
# search_fulltext.py - 全文検索モジュール（Level 2）
# Week 3 / 指令6
# ===================================================

import re


def search_fulltext(query: str, pages: list) -> list:
    """
    全文検索（本文含む）を実行し、マッチ数でスコアリングする。

    Args:
        query: 検索キーワード
        pages: ページリスト

    Returns:
        マッチしたページのリスト（スコア降順）
    """
    if not query.strip():
        return []

    results = []
    # クエリ正規化：空白を1つに、大小無視
    q = re.sub(r"\s+", " ", query.strip().lower())
    # q = query.lower()   #元コード

    for page in pages:
        text = " ".join([
            page.get("title", ""),
            page.get("description", ""),
            page.get("full_text", ""),
            " ".join(page.get("keywords", [])),
        ]).lower()

        count = text.count(q)
        if count > 0:
            r = page.copy()
            r["match_count"] = count
            r["preview"] = _make_preview(page.get("full_text", page.get("description", "")), query)
            results.append(r)

    results.sort(key=lambda x: x["match_count"], reverse=True)
    return results


def _make_preview(text: str, query: str, ctx: int = 80) -> str:
    """マッチ箇所周辺のプレビューを生成する。"""
    if not text or not query:
        return ""

    pos = text.lower().find(query.lower())
    if pos == -1:
        return (text[:200] + "...") if len(text) > 200 else text

    start = max(0, pos - ctx)
    end = min(len(text), pos + len(query) + ctx)

    preview = ""
    if start > 0:
        preview += "..."
    preview += text[start:end]
    if end < len(text):
        preview += "..."
    return preview


#テストコード#######
if __name__ == "__main__":
    import json
    from pathlib import Path

    DATA_PATH = Path("data/pages.json")
    pages = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    query = "DX"   # ← ここ変えて色々試す
    results = search_fulltext(query, pages)

    print(f"🔎 Query: {query}")
    print(f"📄 Hit件数: {len(results)}")

    for r in results[:3]:
        print("-" * 40)
        print("Title:", r.get("title"))
        print("Match:", r.get("match_count"))
        print("Preview:", r.get("preview"))
