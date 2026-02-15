# ===================================================
# app.py - Tech0 Search v0.2
# Week 3 / 指令5・6
# 新機能: クローラー ・ 全文検索 ・ 一括クロール
# ===================================================
import streamlit as st
import json
from pathlib import Path
from datetime import date
from search_fulltext import search_fulltext
from crawler import crawl_url

st.set_page_config(page_title="Tech0 Search v0.2", page_icon="🔍", layout="wide")

DATA_PATH = Path("data/pages.json")

#共通：ID採番関数を追加
def next_id(pages: list) -> int:
    return (max([p.get("id", 0) for p in pages]) + 1) if pages else 1

def has_url(pages: list, url: str) -> bool:
    return any(p.get("url") == url for p in pages)


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


st.title("🔍 Tech0 Search v0.2")
st.caption("PROJECT ZERO ─ 社内ナレッジ検索エンジン【全文検索対応】")

tab_search, tab_crawl, tab_register, tab_list = st.tabs(
    ["🔍 検索", "🤖 クローラー", "📝 手動登録", "📋 一覧"]
)

pages = load_pages()


# ━━━ 検索タブ ━━━
with tab_search:
    query = st.text_input("🔍 キーワードを入力", placeholder="例: DX, IoT, 製造業")

    if query:
        results = search_fulltext(query, pages)

        st.markdown(f"**📊 検索結果: {len(results)}件**（マッチ数順）")
        st.divider()

        for page in results:
            with st.container():
                c_title, c_score = st.columns([4, 1])
                c_title.markdown(f"### 📄 {page['title']}")
                c_score.metric("マッチ", f"{page['match_count']}回")

                st.markdown(f"*{page.get('preview', page.get('description', ''))}*")

                if page.get("keywords"):
                    st.markdown("🏷️ " + " ".join(f"`{kw}`" for kw in page["keywords"][:5]))

                c1, c2, c3 = st.columns(3)
                c1.caption(f"👤 {page.get('author', '不明')}")
                c2.caption(f"📊 {page.get('word_count', 0)}語")
                c3.caption(f"📅 {page.get('created_at', '')[:10]}")

                st.markdown(f"🔗 [{page['url']}]({page['url']})")
                st.divider()

        if not results:
            st.info("該当するページが見つかりませんでした")


# ━━━ クローラータブ ━━━
with tab_crawl:
    st.subheader("🤖 自動クローラー")
    st.info("URLを入力すると、自動でページ情報を取得します")

    # ── 単体クロール ──
    target_url = st.text_input("クロール対象URL", placeholder="https://example.com")
    
    #クローラータブ：SSLスキップ追加＆ID採番修正
    skip_ssl = st.checkbox("SSL検証をスキップ（検証用）", value=False)

    #session_state対応
    if "crawl_result" not in st.session_state:
        st.session_state.crawl_result = None

    if st.button("🤖 クロール実行", type="primary", key="btn_crawl_single"):
        if target_url:
            with st.spinner("クロール中..."):
                st.session_state.crawl_result = crawl_url(target_url, verify_ssl=not skip_ssl)
        else:
            st.warning("URLを入力してください")

    result = st.session_state.crawl_result

    if result and result.get("crawl_status") == "success":
        st.success("✅ クロール成功！")

        c1, c2 = st.columns(2)
        c1.metric("📄 タイトル", (result["title"][:30] + "...") if len(result["title"]) > 30 else result["title"])
        c1.metric("📊 文字数", f"{result.get('word_count', 0)}語")
        c2.metric("🔗 リンク数", f"{len(result.get('links', []))}件")
        c2.metric("🏷️ キーワード", f"{len(result.get('keywords', []))}個")

        st.markdown("**📖 本文プレビュー:**")
        ft = result.get("full_text", "")
        st.write(ft[:500] + ("..." if len(ft) > 500 else ""))

        if st.button("💾 インデックスに登録", key="btn_register_single"):
            if has_url(pages, result["url"]):
                st.warning("同じURLが既に登録されています（スキップしました）")
            else:
                r = result.copy()
                r["id"] = next_id(pages)
                r["author"] = "クローラー"
                r["category"] = "自動取得"
                r["created_at"] = r["crawled_at"][:10]
                pages.append(r)
                save_pages(pages)
                st.success(f"✅ 「{r['title']}」を登録しました！")
                st.cache_data.clear()
                st.session_state.crawl_result = None
                st.rerun()

    elif result and result.get("crawl_status") != "success":
        st.error(f"❌ クロール失敗: {result.get('error', 'Unknown')}")

    #session_state前
    # if st.button("🤖 クロール実行", type="primary", key="btn_crawl_single"):
    #     if target_url:
    #         with st.spinner("クロール中..."):
    #             # result = crawl_url(target_url)
    #             result = crawl_url(target_url, verify_ssl=not skip_ssl)

    #         if result.get("crawl_status") == "success":
    #             st.success("✅ クロール成功！")

    #             c1, c2 = st.columns(2)
    #             c1.metric("📄 タイトル", result["title"][:30] + "...")
    #             c1.metric("📊 文字数", f"{result['word_count']}語")
    #             c2.metric("🔗 リンク数", f"{len(result.get('links', []))}件")
    #             c2.metric("🏷️ キーワード", f"{len(result.get('keywords', []))}個")

    #             st.markdown("**📖 本文プレビュー:**")
    #             preview = result.get("full_text", "")[:500]
    #             st.write(preview + ("..." if len(result.get("full_text", "")) > 500 else ""))

    #             if st.button("💾 インデックスに登録"):
    #                 if has_url(pages, result["url"]):
    #                     st.warning("同じURLが既に登録されています（スキップしました）")  #if追加
    #                 else:
    #                     result["id"] = next_id(pages)
    #                     # result["id"] = len(pages) + 1
    #                     result["author"] = "クローラー"
    #                     result["category"] = "自動取得"
    #                     result["created_at"] = result["crawled_at"][:10]
    #                     pages.append(result)
    #                     save_pages(pages)
    #                     st.success(f"✅ 「{result['title']}」を登録しました！")
    #                     st.cache_data.clear()
    #                     st.rerun()
    #         else:
    #             st.error(f"❌ クロール失敗: {result.get('error', 'Unknown')}")

    # ── 一括クロール ──
    st.divider()
    st.subheader("📋 一括クロール")

    urls_text = st.text_area("URLリスト（1行に1URL）", height=150,
                             placeholder="https://example1.com\\nhttps://example2.com")

    if st.button("🚀 一括クロール実行"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if urls:
            bar = st.progress(0)
            ok = 0
            for i, u in enumerate(urls):
                if has_url(pages, u):
                    bar.progress((i + 1) / len(urls))
                    continue

                r = crawl_url(u, verify_ssl=not skip_ssl)
                if r.get("crawl_status") == "success":
                    r["id"] = next_id(pages)
                    r["author"] = "クローラー"
                    r["category"] = "自動取得"
                    r["created_at"] = r["crawled_at"][:10]
                    pages.append(r)
                    ok += 1
                bar.progress((i + 1) / len(urls))

            # for i, u in enumerate(urls):
            #     r = crawl_url(u)
            #     if r.get("crawl_status") == "success":
            #         r["id"] = len(pages) + 1
            #         r["author"] = "クローラー"
            #         r["category"] = "自動取得"
            #         r["created_at"] = r["crawled_at"][:10]
            #         pages.append(r)
            #         ok += 1
            #     bar.progress((i + 1) / len(urls))

            save_pages(pages)
            st.cache_data.clear()
            st.success(f"✅ {ok}/{len(urls)}件 クロール完了！")


# ━━━ 手動登録タブ ━━━
with tab_register:
    st.subheader("新規ページ登録（手動）")
    with st.form("reg"):
        url   = st.text_input("URL *")
        title = st.text_input("タイトル *")
        desc  = st.text_area("説明 *")
        kws   = st.text_input("キーワード（カンマ区切り）")
        auth  = st.text_input("作成者")
        cat   = st.selectbox("カテゴリ", ["自己紹介", "プロダクト", "事例", "その他"])
        go    = st.form_submit_button("📝 登録", type="primary")

    if go and url and title and desc:
        pages.append({
            "id": next_id(pages),
            "url": url,
            "title": title,
            "description": desc,
            "full_text": desc,
            "word_count": len(desc.split()),
            "keywords": [k.strip() for k in kws.split(",") if k.strip()],
            "author": auth,
            "created_at": str(date.today()),
            "category": cat,
            "crawl_status": "manual",
            "crawled_at": None,
        })

        # pages.append({
        #     "id": len(pages) + 1, "url": url, "title": title,
        #     "description": desc,
        #     "keywords": [k.strip() for k in kws.split(",") if k.strip()],
        #     "author": auth, "created_at": str(date.today()), "category": cat,
        # })
        save_pages(pages)
        st.success(f"✅ 「{title}」を登録しました！")
        st.cache_data.clear()


# ━━━ 一覧タブ ━━━
with tab_list:
    st.subheader(f"📋 登録済みページ（{len(pages)}件）")
    for p in pages:
        with st.expander(f"📄 {p['title']}"):
            st.write(f"**URL:** {p['url']}")
            st.write(f"**文字数:** {p.get('word_count', 0)}語")
            st.write(f"**ステータス:** {p.get('crawl_status', '手動登録')}")


st.divider()
st.caption("© 2025 PROJECT ZERO ─ Tech0 Search v0.2")