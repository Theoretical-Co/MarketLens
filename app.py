import streamlit as st
import pandas as pd
import plotly.express as px

from news import get_financial_news
from market_data import get_price_history, get_default_market_snapshot, DEFAULT_TICKERS
from ai_analysis import analyze_article

# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="MacroLens - AI Market Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# THEME TOGGLE (MANUAL CONTROL FOR RELIABILITY)
# =========================================================
theme = st.sidebar.radio(
    "🌓 Theme",
    ["Light", "Dark"],
    index=0
)

# Apply theme attribute to HTML root (used by CSS below)
if theme == "Dark":
    st.markdown('<html data-theme="dark">', unsafe_allow_html=True)
else:
    st.markdown('<html data-theme="light">', unsafe_allow_html=True)

# =========================================================
# CUSTOM CSS STYLING (GLASSMORPHISM + DARK MODE FIX)
# =========================================================
st.markdown("""
<style>

/* =========================================================
   THEME VARIABLES (LIGHT + DARK)
   These define reusable colors across the app
========================================================= */

html[data-theme="light"] {
    --bg-color: #f5f7fb;
    --card-bg: rgba(255, 255, 255, 0.75);
    --text-color: #1a1a1a;
    --border-color: rgba(0, 0, 0, 0.08);
    --accent-color: #1f77b4;
}

html[data-theme="dark"] {
    --bg-color: #0e1117;
    --card-bg: rgba(22, 27, 34, 0.75);
    --text-color: #e6edf3;
    --border-color: rgba(255, 255, 255, 0.08);
    --accent-color: #58a6ff;
}

/* =========================================================
   BASE APP STYLING
========================================================= */

/* Main app background */
.stApp {
    background-color: var(--bg-color);
    color: var(--text-color);
}

/* Headings styling */
h1, h2, h3 {
    font-weight: 600;
}

/* Main title styling */
h1 {
    text-align: center;
    border-bottom: 2px solid var(--accent-color);
    padding-bottom: 10px;
}

/* =========================================================
   GLASSMORPHISM CARD DESIGN
========================================================= */

.article-card {
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    margin: 12px 0;
    transition: all 0.2s ease-in-out;
}

/* Hover animation */
.article-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

/* =========================================================
   SIDEBAR STYLING (STABLE SELECTOR)
========================================================= */

section[data-testid="stSidebar"] {
    background: var(--card-bg);
    border-right: 1px solid var(--border-color);
}

/* =========================================================
   DATAFRAME FIXES (DARK MODE COMPATIBILITY)
========================================================= */

.stDataFrame {
    background: var(--card-bg);
    border-radius: 10px;
    border: 1px solid var(--border-color);
}

/* Ensure text is readable in dark mode */
html[data-theme="dark"] .stDataFrame div {
    color: #e6edf3 !important;
}

/* =========================================================
   SENTIMENT BADGES
========================================================= */

.sentiment-bullish {
    background-color: #d4edda;
    color: #155724;
    padding: 6px 10px;
    border-radius: 6px;
    font-weight: 600;
}

.sentiment-bearish {
    background-color: #f8d7da;
    color: #721c24;
    padding: 6px 10px;
    border-radius: 6px;
    font-weight: 600;
}

.sentiment-neutral {
    background-color: #e2e3e5;
    color: #383d41;
    padding: 6px 10px;
    border-radius: 6px;
    font-weight: 600;
}

/* Dark mode overrides */
html[data-theme="dark"] .sentiment-bullish {
    background-color: #238636;
    color: white;
}

html[data-theme="dark"] .sentiment-bearish {
    background-color: #da3633;
    color: white;
}

html[data-theme="dark"] .sentiment-neutral {
    background-color: #656c76;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER SECTION
# =========================================================
st.title("🔍 MacroLens")
st.markdown("### AI-Powered Market Intelligence Dashboard")

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
query = st.sidebar.text_input("📰 News Query", value="general")

page_size = st.sidebar.slider("📊 Articles", 5, 20, 10)

selected_asset_label = st.sidebar.selectbox(
    "📈 Chart Asset",
    list(DEFAULT_TICKERS.keys())
)

run_news = st.sidebar.button("🔄 Refresh News")

# =========================================================
# FETCH NEWS DATA
# =========================================================
if run_news or "articles" not in st.session_state:
    try:
        if not query.strip():
            query = "markets"
        st.session_state.articles = get_financial_news(query=query, page_size=page_size)
    except Exception as e:
        st.error(f"Error loading news: {e}")
        st.session_state.articles = []

articles = st.session_state.get("articles", [])

# =========================================================
# MAIN LAYOUT
# =========================================================
col1, col2 = st.columns([1.2, 0.8])

# =========================================================
# LEFT COLUMN: NEWS + AI ANALYSIS
# =========================================================
with col1:
    st.header("📰 Financial News")

    if articles:
        titles = [a["title"][:60] for a in articles]

        idx = st.selectbox("Select article", range(len(titles)), format_func=lambda i: titles[i])
        article = articles[idx]

        st.markdown(f"### {article['title']}")
        st.markdown(f"*{article.get('description', '')}*")

        if st.button("🤖 Analyze"):
            result = analyze_article(
                article["title"],
                article.get("description", ""),
                article.get("source", {}).get("name", "")
            )
            st.session_state.analysis = result

        if "analysis" in st.session_state:
            st.markdown(st.session_state.analysis)

# =========================================================
# RIGHT COLUMN: MARKET SNAPSHOT
# =========================================================
with col2:
    st.header("📊 Market Snapshot")

    df = get_default_market_snapshot()

    if not df.empty:
        df["Latest"] = df["Latest"].map(lambda x: f"${x:.2f}")
        df["Daily % Change"] = df["Daily % Change"].map(lambda x: f"{x:+.2f}%")
        st.dataframe(df, use_container_width=True, hide_index=True)

# =========================================================
# CHART SECTION (IMPROVED STYLING)
# =========================================================
st.header("📈 Market Chart")

ticker = DEFAULT_TICKERS[selected_asset_label]
price_df = get_price_history(ticker)

if not price_df.empty:
    fig = px.line(price_df, x="Date", y="Close")

    # Apply theme-aware chart styling
    fig.update_layout(
        template="plotly_dark" if theme == "Dark" else "plotly_white",
        height=420,
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("### 📧 Contact")
    st.markdown("**Creator:** Mohamed Ahmed")
    st.markdown("[📧 Email](mailto:mohamedahmed@bennington.edu)")
    st.markdown("[💼 LinkedIn](https://www.linkedin.com/in/mohamed-ahmed-4794b6158/)")
    st.markdown("[🐙 GitHub](https://github.com/maxamedjaamac34)")

with col2:
    st.markdown("### 🎯 Mission")
    st.markdown("""
    **MacroLens** democratizes market intelligence by combining:
    
    📰 **Real-time news aggregation** from trusted sources  
    🤖 **AI-powered analysis** using GPT-4o for market insights  
    📊 **Interactive visualizations** for better decision-making  
    🚀 **Open-source accessibility** for traders and analysts
    
    Built to help professionals stay ahead of market-moving events without the noise.
    """)

with col3:
    st.markdown("### ⚠️ Disclaimer")
    st.markdown("""
    **Not financial advice.**  
    This tool provides market intelligence and event interpretation only.  
    Always conduct your own research and consult financial professionals.
    """)

st.markdown("---")
st.markdown(
    "<p style='text-align: center; font-size: 11px; color: #aaa;'>"
    "MacroLens v1.0 • Built with Streamlit, OpenAI, and yfinance • "
    "<a href='https://github.com/maxamedjaamac34/ai-market-intelligence' target='_blank'>View Source</a>"
    "</p>",
    unsafe_allow_html=True
)
