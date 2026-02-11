# ===================================================
# scraping_example.py - Webスクレイピングサンプル
# Week 1 / 指令2
# ===================================================

import requests
from bs4 import BeautifulSoup

def scrape_page(url: str) -> dict:
    """
    Webページから情報を抽出する。

    Args:
        url: 対象URL

    Returns:
        抽出結果の辞書
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # タイトル
    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else "No Title"

    # meta description
    meta = soup.find("meta", attrs={"name": "description"})
    description = meta.get("content", "") if meta else ""

    # 段落テキスト
    paragraphs = soup.find_all("p")
    text = "\n".join(p.get_text().strip() for p in paragraphs)

    # リンク一覧
    links = [
        a["href"] for a in soup.find_all("a", href=True)
        if a["href"].startswith("http")
    ][:10]

    return {
        "url": url,
        "title": title,
        "description": description,
        "text": text,
        "links": links,
    }


# ─── 実行例 ───
if __name__ == "__main__":
    result = scrape_page("https://example.com")

    print(f"📄 タイトル: {result['title']}")
    print(f"📝 説明: {result['description'][:100]}...")
    print(f"🔗 リンク数: {len(result['links'])}件")