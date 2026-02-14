# ===================================================
# app.py - Tech0 Search v0.1
# Week 2 / 指令3
# 機能: キーワード検索 ・ 手動登録 ・ 一覧表示
# ===================================================
import streamlit as st
import json
from pathlib import Path
from datetime import date
from search import search_pages, highlight_match

# ── ページ設定 ──
st.set_page_config(page_title="Tech0 Search v0.1", page_icon="🔍", layout="wide")

DATA_PATH = Path("data/pages.json")


# ── データ I/O ──
@st.cache_data
def load_pages() -> list:
    if DATA_PATH.exists():
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_pages(pages: list):
    DATA_PATH.parent.mkdir(exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)


# ── メインレイアウト ──
st.title("🔍 Tech0 Search v0.1")
st.caption("PROJECT ZERO ─ 社内ナレッジ検索エンジン")

tab_search, tab_register, tab_list = st.tabs(["🔍 検索", "📝 登録", "📋 一覧"])

pages = load_pages()


# ━━━ 検索タブ ━━━
with tab_search:
    st.subheader("キーワードで検索")

    query = st.text_input("🔍 キーワードを入力", placeholder="例: DX, IoT, 製造業")

    if query:
        results = search_pages(query, pages)
        st.markdown(f"**📊 検索結果: {len(results)}件**")
        st.divider()

        if results:
            for page in results:
                with st.container():
                    st.markdown(f"### 📄 {page['title']}")
                    st.markdown(highlight_match(page["description"], query))

                    tags = " ".join(f"`{kw}`" for kw in page["keywords"])
                    st.markdown(f"🏷️ {tags}")

                    c1, c2 = st.columns(2)
                    c1.caption(f"👤 {page['author']}")
                    c2.caption(f"📅 {page['created_at']}")

                    st.markdown(f"🔗 [{page['url']}]({page['url']})")
                    st.divider()
        else:
            st.info("該当するページが見つかりませんでした")


# ━━━ 登録タブ ━━━
with tab_register:
    st.subheader("新規ページ登録")

    with st.form("register_form"):
        url         = st.text_input("URL *", placeholder="https://...")
        title       = st.text_input("タイトル *", placeholder="ページタイトル")
        description = st.text_area("説明 *", placeholder="ページの説明文")
        keywords_in = st.text_input("キーワード（カンマ区切り）", placeholder="DX, IoT")
        author      = st.text_input("作成者", placeholder="田中太郎")
        category    = st.selectbox("カテゴリ", ["自己紹介", "プロダクト", "事例", "その他"])
        submitted   = st.form_submit_button("📝 登録", type="primary")

    if submitted:
        if url and title and description:
            new_page = {
                "id": len(pages) + 1,
                "url": url,
                "title": title,
                "description": description,
                "keywords": [kw.strip() for kw in keywords_in.split(",") if kw.strip()],
                "author": author,
                "created_at": str(date.today()),
                "category": category,
            }
            pages.append(new_page)
            save_pages(pages)
            st.success(f"✅ 「{title}」を登録しました！")
            st.cache_data.clear()
        else:
            st.error("URL・タイトル・説明は必須です")


# ━━━ 一覧タブ ━━━
with tab_list:
    st.subheader(f"📋 登録済みページ一覧（{len(pages)}件）")

    if pages:
        for page in pages:
            with st.expander(f"📄 {page['title']}"):
                st.markdown(f"**URL:** {page['url']}")
                st.markdown(f"**説明:** {page['description']}")
                st.markdown(f"**キーワード:** {', '.join(page['keywords'])}")
                st.markdown(f"**作成者:** {page['author']} ／ **カテゴリ:** {page['category']}")
    else:
        st.info("まだページが登録されていません")


# ── フッター ──
st.divider()
st.caption("© 2025 PROJECT ZERO ─ Tech0 Search v0.1")