import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# --- Streamlit Page Config ---
st.set_page_config(page_title="🌐 Simple Web Crawler", layout="wide")

# --- Helper Function: Crawl & Extract ---
def crawl_and_extract(url: str):
    result = {"url": url}
    html = None

    # Skip Playwright for Python 3.13 due to compatibility issues
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        html = r.text
        result["final_url"] = r.url
    except Exception as e:
        result["error"] = f"Failed to fetch page: {e}"
        return result

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    result["title"] = soup.title.string if soup.title else "No title found"
    result["headings"] = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])]
    result["paragraphs"] = [p.get_text(strip=True) for p in soup.find_all("p")][:10]
    result["links"] = [{"text": a.get_text(strip=True) or "(no text)", "url": urljoin(result["final_url"], a["href"])}
                       for a in soup.find_all("a", href=True)][:20]
    result["images"] = [urljoin(result["final_url"], img["src"]) for img in soup.find_all("img", src=True)][:10]

    return result

# --- Streamlit UI ---
st.title("🕵️ Web Crawler Agent")

st.markdown("""
Enter a website URL below and click **Crawl**.  
This app will fetch the page and extract:
- 🏷 Title  
- 📑 Headings (H1–H3)  
- 📝 Paragraphs  
- 🔗 Links  
- 🖼 Images  
""")

url = st.text_input("🌍 Enter a website URL:", "https://example.com")

if st.button("🚀 Crawl Website"):
    with st.spinner("🔎 Crawling the page... Please wait..."):
        data = crawl_and_extract(url)

    if "error" in data:
        st.error(data["error"])
    else:
        st.success(f"✅ Crawling complete for: {data['final_url']}")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["📌 Overview", "📑 Headings", "📝 Paragraphs", "🔗 Links", "🖼 Images", "💻 Raw JSON"]
        )

        with tab1:
            st.subheader("📌 Page Overview")
            st.write(f"**Title:** {data['title']}")
            st.write(f"**Final URL:** {data['final_url']}")

        with tab2:
            st.subheader("📑 Extracted Headings")
            if data["headings"]:
                for h in data["headings"]:
                    st.markdown(f"- {h}")
            else:
                st.info("No headings found.")

        with tab3:
            st.subheader("📝 Extracted Paragraphs")
            if data["paragraphs"]:
                for p in data["paragraphs"]:
                    st.markdown(f"- {p}")
            else:
                st.info("No paragraphs found.")

        with tab4:
            st.subheader("🔗 Extracted Links")
            if data["links"]:
                for link in data["links"]:
                    st.markdown(f"- [{link['text']}]({link['url']})")
            else:
                st.info("No links found.")

        with tab5:
            st.subheader("🖼 Extracted Images")
            if data["images"]:
                for img in data["images"]:
                    st.image(img, caption=img, use_container_width=True)  # ✅ updated parameter
            else:
                st.info("No images found.")

        with tab6:
            st.subheader("💻 Raw JSON Output")
            st.json(data)
