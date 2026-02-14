# ===================================================
# search.py - 部分一致検索モジュール（Level 1）
# Week 2 / 指令3
# ===================================================
import re

def search_pages(query: str, pages: list) -> list:
    """
    部分一致検索を実行する。

    Args:
        query: 検索キーワード（例: "DX"）
        pages: ページリスト

    Returns:
        マッチしたページのリスト
    """
    if not query.strip():
        return []

    results = []
    query_lower = query.lower()

    for page in pages:
        # title, description, keywords を検索対象とする
        search_text = " ".join([
            page["title"],
            page["description"],
            " ".join(page["keywords"]),
        ])

        if query_lower in search_text.lower():
            results.append(page)

    return results


def highlight_match(text: str, query: str) -> str:
    """
    マッチ箇所を **太字** でハイライトする。

    Args:
        text:  元テキスト
        query: 検索キーワード

    Returns:
        ハイライト済みテキスト
    """
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(f"**{query}**", text)