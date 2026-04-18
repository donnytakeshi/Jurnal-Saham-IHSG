st.markdown("""
<style>
/* QUANT EDGE DESIGN SYSTEM - STOCKBIT STYLE */
:root {
    --sb-bg: #101419;
    --sb-surface: #181c21;
    --sb-surface-2: #1c2127;
    --sb-border: rgba(103, 217, 203, 0.1);
    --sb-text: #bcc9c6;
    --sb-text-bright: #ffffff;
    --sb-accent: #159D91; /* Primary Teal */
    --sb-green: #67d9cb;
    --sb-red: #ff5e5e;
    --sb-yellow: #f2d18f;
}

/* Global Background */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--sb-bg) !important;
    color: var(--sb-text) !important;
    font-family: 'Manrope', sans-serif !important;
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background: var(--sb-surface) !important;
    border-right: 1px solid var(--sb-border) !important;
}

/* Card Styling (Modular) */
div[data-testid="stVerticalBlock"] > div:has(div.metric-card),
div[data-testid="column"] {
    background: var(--sb-surface) !important;
    border-radius: 12px !important;
    border: 1px solid var(--sb-border) !important;
    padding: 16px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
}

/* Metric Overrides */
[data-testid="stMetric"] {
    background: transparent !important;
    border: none !important;
}

[data-testid="stMetricValue"] {
    color: var(--sb-green) !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: var(--sb-text) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-size: 0.7rem !important;
}

/* Tab Overrides */
button[data-baseweb="tab"] {
    color: var(--sb-text) !important;
    font-weight: 600 !important;
}

button[aria-selected="true"] {
    color: var(--sb-green) !important;
    border-bottom-color: var(--sb-green) !important;
}

/* Table Styling */
.stDataFrame, table {
    border: none !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

thead th {
    background-color: var(--sb-surface-2) !important;
    color: var(--sb-green) !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
}

tbody td {
    background-color: var(--sb-surface) !important;
    border-bottom: 1px solid rgba(255,255,255,0.03) !important;
}

/* Button Styling */
button[kind="primary"] {
    background: var(--sb-accent) !important;
    border: none !important;
    border-radius: 8px !important;
    color: white !important;
    font-weight: 700 !important;
}

button[kind="secondary"] {
    background: var(--sb-surface-2) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 8px !important;
}

/* Main Header */
.main-header {
    background: linear-gradient(135deg, #159D91 0%, #101419 100%) !important;
    border: 1px solid var(--sb-border) !important;
    border-radius: 16px !important;
    padding: 30px !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""<style>
    .block-container {
        padding-top: 0.35rem !important;
    }
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        background: transparent;
    }
    [data-testid="stExpander"],
    [data-testid="stContainer"],
    div[data-testid="stMetric"] {
        border-color: var(--sb-border) !important;
    }
    
    /* Elements spacing ultra-tight */
    .stMetric, .metric {
        margin: 0 !important;
        padding: 2px 0 !important;
    }
    [data-testid="stCaptionContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Headings - minimal spacing */
    h1 {
        margin: 0 0 3px 0 !important;
        padding: 0 !important;
        font-size: 1.55rem !important;
        line-height: 1.2 !important;
    }
    h2 {
        margin: 2px 0 2px 0 !important;
        padding: 0 !important;
        font-size: 1.25rem !important;
        line-height: 1.1 !important;
    }
    h3 {
        margin: 2px 0 1px 0 !important;
        padding: 0 !important;
        font-size: 1.0rem !important;
    }

    /* Link + accent */
    a, a:visited {
        color: var(--sb-accent) !important;
    }
    
    /* Divider ultra-compact */
    hr {
        margin: 2px 0 !important;
        padding: 0 !important;
    }
    
    /* Column gap - medium (match metric cards spacing) */
    .stColumns {
        gap: 0.46rem !important;
    }

    /* Streamlit layout gaps: target real flex wrappers */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.46rem !important;
    }
    div[data-testid="column"] {
        padding-left: 0.14rem !important;
        padding-right: 0.14rem !important;
    }

    /* Vertical spacing: consistent & dense */
    div[data-testid="stVerticalBlock"] {
        gap: 0.25rem !important;
    }
    div[data-testid="element-container"],
    div.element-container {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stMarkdown"],
    [data-testid="stHeading"],
    [data-testid="stText"],
    [data-testid="stCaptionContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stDivider"] {
        margin: 0.25rem 0 !important;
        padding: 0 !important;
    }
    [data-testid="stDivider"] hr {
        margin: 0 !important;
    }

    /* Headings wrapper spacing (Streamlit adds extra padding sometimes) */
    div[data-testid="stMarkdownContainer"] > h1,
    div[data-testid="stMarkdownContainer"] > h2,
    div[data-testid="stMarkdownContainer"] > h3 {
        margin-top: 0 !important;
        margin-bottom: 0.25rem !important;
    }

    /* Mobile density tweaks: keep look closer to desktop */
    @media (max-width: 600px) {
        html { font-size: 12.5px !important; }

        /* Hide the right-side vertical scrollbar in mobile WebView (keep scrolling) */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main, .block-container {
            -ms-overflow-style: none;
            scrollbar-width: none;
        }
        /* Also hide scrollbars from nested scrollable containers (dataframes/table wrappers/etc). */
        * {
            scrollbar-width: none;
            -ms-overflow-style: none;
        }
        *::-webkit-scrollbar {
            width: 0px;
            height: 0px;
            background: transparent;
        }

        .main { padding: 0.25rem !important; }
        .block-container { padding-top: 0.25rem !important; }

        h1 { font-size: 1.25rem !important; }
        h2 { font-size: 1.02rem !important; }
        h3 { font-size: 0.92rem !important; }

        [data-testid="stTabs"] button {
            padding: 2px 6px !important;
            margin: 0 1px !important;
            font-size: 0.74rem !important;
        }

        button {
            padding: 2px 8px !important;
            font-size: 0.74rem !important;
            height: 26px !important;
        }

        /* Slightly narrower minimum table width to reduce horizontal scrolling */
        table.compact-table, .table-wrap table.dataframe { min-width: 640px; }
    }
    
    /* Tab styling - compact */
    [data-testid="stTabs"] {
        margin: 1px 0 !important;
        padding: 0 !important;
    }
    [data-testid="stTabs"] button {
        padding: 3px 7px !important;
        margin: 0 2px !important;
        font-size: 0.82rem !important;
    }
    
    /* Forms - compact */
    .stTextInput, .stNumberInput, .stSelectbox, .stMultiSelect {
        margin: 0 !important;
    }
    [data-testid="stNumberInput"], [data-testid="stSelectbox"] {
        margin: 0 !important;
    }

    /* P/L color helpers */
    .pl-card {
        background: linear-gradient(180deg, var(--sb-surface) 0%, var(--sb-surface-2) 100%);
        border-radius: 9px;
        padding: 10px 12px;
        border-left: 3px solid var(--sb-accent);
        border: 1px solid var(--sb-border);
    }
    .pl-title {
        color: var(--sb-text-dim);
        font-size: 0.88rem;
        opacity: 0.9;
        margin-bottom: 4px;
    }
    .pl-value {
        font-size: clamp(1.20rem, 2.7vw, 1.85rem);
        font-weight: 650;
        line-height: 1.05;
        margin: 0;
        padding: 0;
        white-space: nowrap;
        word-break: keep-all;
        overflow: hidden;
        text-overflow: ellipsis;
        font-variant-numeric: tabular-nums;
    }
    .pl-card.align-right { text-align: right; }
    .pl-pos { color: var(--sb-green); }
    .pl-neg { color: var(--sb-red); }
    .pl-neu { color: var(--sb-text); }
    .pl-pill {
        display: inline-block;
        margin-top: 7px;
        padding: 4px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    .pl-pill-pos { background: rgba(26, 163, 114, 0.14); color: var(--sb-green); }
    .pl-pill-neg { background: rgba(238, 90, 82, 0.14); color: #ee5a52; }
    .pl-pill-neu { background: rgba(225, 232, 237, 0.10); color: #E1E8ED; }

    /* Small animation helpers (used mainly on dashboard charts) */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-up { animation: fadeUp 0.35s ease both; }

    /* Compact table styles (used across tabs) */
    .table-wrap {
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border-radius: 8px;
    }

    table.compact-table {
        background: var(--sb-surface) !important;
        border: 1px solid var(--sb-border) !important;
        border-radius: 10px;
        overflow: hidden;
    }
    table.compact-table thead th {
        background: rgba(21, 157, 145, 0.18) !important;
        color: var(--sb-text) !important;
        border-bottom: 1px solid var(--sb-border) !important;
        letter-spacing: 0.02em;
    }
    table.compact-table tbody td {
        color: var(--sb-text) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    table.compact-table tbody tr:hover td {
        background: rgba(21, 157, 145, 0.06) !important;
    }

    /* Inputs */
    input, textarea, select {
        color: var(--sb-text) !important;
    }
    [data-baseweb="input"], [data-baseweb="select"], [data-baseweb="textarea"] {
        background: var(--sb-surface) !important;
        border-color: var(--sb-border) !important;
    }

    /* Portfolio table tweaks: make P/L and Return% narrower so the delete panel can fit */
    table.portfolio-table th:nth-child(6),
    table.portfolio-table td:nth-child(6) {
        width: 150px;
        max-width: 150px;
    }
    table.portfolio-table th:nth-child(7),
    table.portfolio-table td:nth-child(7) {
        width: 120px;
        max-width: 120px;
    }
    table.portfolio-table th:nth-child(6),
    table.portfolio-table td:nth-child(6),
    table.portfolio-table th:nth-child(7),
    table.portfolio-table td:nth-child(7) {
        white-space: nowrap;
    }
    table.compact-table {
        width: 100%;
        border-collapse: collapse;
        min-width: 860px;
    }
    table.compact-table thead th {
        background-color: #4A8FA8;
        color: white;
        font-weight: 800;
        padding: 6px 8px;
        text-align: left;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
        white-space: nowrap;
    }
    table.compact-table tbody td {
        padding: 5px 8px;
        border-bottom: 1px solid rgba(225, 232, 237, 0.18);
        font-size: 0.86rem;
        line-height: 1.2;
        white-space: nowrap;
        color: #E1E8ED;
    }
    table.compact-table tbody tr:hover {
        background-color: rgba(74, 143, 168, 0.10);
    }

    /* Make pandas default dataframe HTML (class=dataframe) match compact style */
    .table-wrap table.dataframe {
        width: 100%;
        border-collapse: collapse;
        min-width: 860px;
    }
    .table-wrap table.dataframe th {
        background-color: #4A8FA8 !important;
        color: white !important;
        font-weight: 800 !important;
        padding: 6px 8px !important;
        text-align: left !important;
        font-size: 0.85rem !important;
        white-space: nowrap;
    }
    .table-wrap table.dataframe td {
        padding: 5px 8px !important;
        border-bottom: 1px solid rgba(225, 232, 237, 0.18) !important;
        font-size: 0.86rem !important;
        line-height: 1.2;
        white-space: nowrap;
        color: #E1E8ED !important;
    }

    /* Narrow screens: reduce min width so it doesn't feel too wide */
    @media (max-width: 900px) {
        table.compact-table, .table-wrap table.dataframe { min-width: 720px; }
    }
    
    /* Buttons - compact */
    button {
        padding: 3px 10px !important;
        margin: 1px 1px !important;
        font-size: 0.78rem !important;
        height: 28px !important;
    }
    div.stButton {
        margin: 0 !important;
        padding: 0 !important;
    }
    div.stButton > button {
        margin: 0 !important;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 8px 12px;
        border-radius: 6px;
        color: white;
        margin: 2px 0;
        line-height: 1.2;
    }
    
    /* Table styling - tight */
    .stDataFrame {
        border: 1px solid #4A8FA8 !important;
        margin: 2px 0 !important;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid #4A8FA8 !important;
        margin: 2px 0 !important;
    }
    [data-testid="stDataFrame"] tbody tr {
        border-bottom: 1px solid #ddd !important;
        height: 24px !important;
    }
    [data-testid="stDataFrame"] td {
        padding: 2px 3px !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stDataFrame"] thead th {
        border: 1px solid #4A8FA8 !important;
        padding: 2px 3px !important;
        font-weight: bold;
        font-size: 0.80rem !important;
        background-color: #4A8FA8 !important;
        color: white !important;
    }
    
    /* Signal boxes - compact */
    .buy-signal {
        background-color: #d4f3d4;
        border: 1px solid #28a745;
        padding: 6px 8px;
        border-radius: 4px;
        margin: 2px 0;
        font-size: 0.9rem;
    }
    .sell-signal {
        background-color: #f8d7da;
        border: 1px solid #dc3545;
        padding: 6px 8px;
        border-radius: 4px;
        margin: 2px 0;
        font-size: 0.9rem;
    }
    .hold-signal {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        padding: 6px 8px;
        border-radius: 4px;
        margin: 2px 0;
        font-size: 0.9rem;
    }
    
    /* Status badges - compact */
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-weight: bold;
        margin: 1px;
        border: 1px solid #4A8FA8;
        font-size: 0.8rem;
    }
    .badge-green {
        background-color: #d4f3d4;
        color: #155724;
        border: 1px solid #28a745;
    }
    .badge-red {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #dc3545;
    }
    .badge-yellow {
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffc107;
    }
    
    /* Alerts - ultra tight */
    .stAlert {
        margin: 2px 0 !important;
        padding: 5px 7px !important;
        font-size: 0.82rem !important;
    }
    
    /* Container spacing - compact */
    .stContainer {
        padding: 1px !important;
        margin: 0 !important;
    }
    
    /* Sidebar - compact */
    [data-testid="stSidebar"] {
        padding: 0.6rem 0.45rem !important;
    }
    
    /* Expander - compact */
    [data-testid="stExpander"] {
        margin: 1px 0 !important;
    }
    
    /* GLOBAL TABLE STYLING - KONSISTEN DI SEMUA TAB */
    .table-header {
        background-color: #4A8FA8 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 8px !important;
        text-align: left !important;
    }
    .table-cell {
        padding: 5px !important;
        border-bottom: 1px solid #333 !important;
        font-size: 0.88rem !important;
    }
    .table-row:hover {
        background-color: #1a2332 !important;
    }
    
    /* Color scheme - HIJAU untuk positif, MERAH untuk negatif */
    .positive-value {
        color: #00c77a !important;
        font-weight: bold !important;
    }
    .negative-value {
        color: #ee5a52 !important;
        font-weight: bold !important;
    }
    .neutral-value {
        color: #E1E8ED !important;
    }
    
    /* TABLE HTML STYLING */
    table {
        width: 100% !important;
        border-collapse: collapse !important;
        background-color: #0F1419 !important;
        border: 1px solid #4A8FA8 !important;
        border-radius: 6px !important;
        overflow: hidden !important;
    }
    table th {
        background-color: #4A8FA8 !important;
        color: white !important;
        font-weight: bold !important;
        padding: 6px 8px !important;
        text-align: left !important;
        border-bottom: 2px solid #2d5a75 !important;
        font-size: 0.85rem !important;
    }
    table td {
        padding: 5px 8px !important;
        border-bottom: 1px solid #333 !important;
        color: #E1E8ED !important;
        font-size: 0.86rem !important;
        line-height: 1.2;
    }
    table tr:hover {
        background-color: #1a2332 !important;
    }
    table tr:last-child td {
        border-bottom: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Preview popup for local HTML preview (opens `top10_nav_preview.html`) ---
try:
        preview_path = Path(__file__).parent / "top10_nav_preview.html"
        if preview_path.exists():
                _preview_html = preview_path.read_text(encoding="utf-8")
                # Embed safely as a JS string using JSON encoding. Avoid f-string
                # so that literal JS braces don't confuse Python's f-string parser.
                js_header = """
<div style='margin:6px 0'>
    <button onclick="openPreview()" style='padding:6px 10px; font-size:0.9rem'>Preview Top10 (popup)</button>
</div>
<script>
"""
                js_footer = """

function openPreview(){
    const w = window.open('', '_blank', 'width=1100,height=800');
    if(!w) { alert('Popup blocked. Allow popups for this site.'); return; }
    w.document.open();
    w.document.write(_preview_content);
    w.document.close();
}
</script>
"""
                popup_js = js_header + "  const _preview_content = " + json.dumps(_preview_html) + ";\n" + js_footer
                components.html(popup_js, height=48)
        else:
                components.html('<div style="color:#E1E8ED">Preview file not found: top10_nav_preview.html</div>', height=32)
except Exception as _e:
        try:
                components.html(f'<div style="color:#ee5a52">Preview error: {_e}</div>', height=32)
        except Exception:
                pass


def _pl_class(value: float) -> str:
    if value > 0:
        return "pl-pos"
    if value < 0:
        return "pl-neg"
    return "pl-neu"


def _pl_pill_class(value: float) -> str:
    if value > 0:
        return "pl-pill pl-pill-pos"
    if value < 0:
        return "pl-pill pl-pill-neg"
    return "pl-pill pl-pill-neu"


def render_pl_card(title: str, value_text: str, delta_pct: float) -> None:
    arrow = "↑" if delta_pct > 0 else "↓" if delta_pct < 0 else "→"
    pl_cls = _pl_class(delta_pct)
    pill_cls = _pl_pill_class(delta_pct)
    st.markdown(
        f"""
        <div class="pl-card fade-up">
            <div class="pl-title">{title}</div>
            <div class="pl-value {pl_cls}">{value_text}</div>
            <div class="{pill_cls}">{arrow} {delta_pct:+.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pl_value_card(title: str, value_text: str, value_for_color: float) -> None:
    pl_cls = _pl_class(value_for_color)
    st.markdown(
        f"""
        <div class="pl-card fade-up">
            <div class="pl-title">{title}</div>
            <div class="pl-value {pl_cls}">{value_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_card(title: str, value_text: str, align_right: bool = False) -> None:
    align_cls = " align-right" if align_right else ""
    st.markdown(
        f"""
        <div class="pl-card fade-up{align_cls}">
            <div class="pl-title">{title}</div>
            <div class="pl-value pl-neu">{value_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pct_value_card(title: str, pct_value: float, suffix: str = "%") -> None:
    render_pl_value_card(title, f"{pct_value:+.2f}{suffix}", float(pct_value))


def st_plotly_chart_stretch(fig, **kwargs):
    """Compat wrapper: Streamlit >= 2026 uses width='stretch' instead of use_container_width."""
    try:
        return st.plotly_chart(fig, width="stretch", **kwargs)
    except TypeError:
        return st.plotly_chart(fig, use_container_width=True, **kwargs)


def st_dataframe_stretch(df, **kwargs):
    """Compat wrapper for st.dataframe container sizing."""
    try:
        return st.dataframe(df, width="stretch", **kwargs)
    except TypeError:
        return st.dataframe(df, use_container_width=True, **kwargs)


def st_button_stretch(label: str, **kwargs):
    """Compat wrapper for st.button full width."""
    try:
        return st.button(label, width="stretch", **kwargs)
    except TypeError:
        return st.button(label, use_container_width=True, **kwargs)


def st_download_button_stretch(label: str, data, file_name: str, mime: str, **kwargs):
    """Compat wrapper for st.download_button full width."""
    try:
        return st.download_button(label, data, file_name, mime, width="stretch", **kwargs)
    except TypeError:
        return st.download_button(label, data, file_name, mime, use_container_width=True, **kwargs)


def _cloud_payload_from_state() -> dict:
    portfolio_df = st.session_state.get("portfolio")
    journal_df = st.session_state.get("monthly_journal")

    portfolio_rows = []
    if isinstance(portfolio_df, pd.DataFrame):
        portfolio_rows = portfolio_df.replace({np.nan: None}).to_dict(orient="records")

    journal_rows = []
    if isinstance(journal_df, pd.DataFrame):
        df = journal_df.copy()
        if "Tanggal" in df.columns:
            df["Tanggal"] = df["Tanggal"].astype(str)
        journal_rows = df.replace({np.nan: None}).to_dict(orient="records")

    return {
        "schema": "jurnal-saham-ihsg:user_blob:v1",
        "saved_at": datetime.now().isoformat(),
        "portfolio": portfolio_rows,
        "monthly_journal": journal_rows,
    }


def _restore_state_from_cloud_row(row: dict) -> bool:
    """Row shape: {data: {...}, updated_at: ...}."""
    try:
        payload = (row or {}).get("data")
        if not isinstance(payload, dict):
            return False

        portfolio_rows = payload.get("portfolio") or []
        journal_rows = payload.get("monthly_journal") or []

        if isinstance(portfolio_rows, list):
            st.session_state.portfolio = pd.DataFrame(portfolio_rows)

        if isinstance(journal_rows, list):
            dfj = pd.DataFrame(journal_rows)
            # Keep dates user-friendly; Streamlit tables can handle strings.
            st.session_state.monthly_journal = dfj
            st.session_state.current_journal_month = datetime.now().strftime("%Y-%m")

        return True
    except Exception:
        return False


def _cloud_autosync(reason: str = "") -> None:
    try:
        auth = st.session_state.get("auth") or {}
        if not auth.get("logged_in") or auth.get("mode") != "cloud":
            return
        if not bool(st.session_state.get("cloud_auto_sync", True)):
            return

        cloud = st.session_state.get("cloud_sync")
        uid = auth.get("user_id")
        if not cloud or not uid:
            return

        cloud.save_user_blob(str(uid), _cloud_payload_from_state())
    except Exception:
        # Never block the UX on cloud errors
        return


def _save_local_checkpoint() -> None:
    """Save a local sync checkpoint unconditionally (safeguard for local mode).

    Uses `LocalSync` (if available) and stores the current `_cloud_payload_from_state()`
    under the current user id (or 'local' when no user id exists).
    """
    try:
        if 'LocalSync' not in globals() or LocalSync is None:
            return
        auth = st.session_state.get("auth") or {}
        uid = auth.get("user_id") or "local"
        # LocalSync will create the sync directory if missing
        LocalSync().save_sync_checkpoint(uid, _cloud_payload_from_state())
    except Exception:
        # Do not raise or block UI on local save errors
        return


def require_login() -> bool:
    if "auth" not in st.session_state:
        st.session_state.auth = {
            "logged_in": False,
            "user_id": None,
            "username": None,
            "mode": "local",  # local | cloud
        }

    st.sidebar.markdown("### Login")

    supabase_url, supabase_key = get_supabase_config()
    cloud_available = bool(create_client) and bool(CloudSync) and bool(supabase_url and supabase_key)

    # Auto-restore Supabase session if available
    if cloud_available and not st.session_state.auth.get("logged_in") and supabase_load_session is not None:
        if "_cloud_auto_checked" not in st.session_state:
            st.session_state._cloud_auto_checked = True
            ps = supabase_load_session()
            if ps and ps.access_token and ps.refresh_token:
                try:
                    client = create_client(supabase_url, supabase_key)
                    auth_resp = client.auth.set_session(ps.access_token, ps.refresh_token)
                    # Persist refreshed tokens best-effort
                    if supabase_save_session is not None:
                        supabase_save_session(auth_resp, email=ps.email)
                    user_resp = client.auth.get_user()
                    user = getattr(user_resp, "user", None)
                    if user is not None:
                        st.session_state.supabase_client = client
                        st.session_state.cloud_sync = CloudSync(client=client)
                        st.session_state.auth = {
                            "logged_in": True,
                            "user_id": getattr(user, "id", None),
                            "username": getattr(user, "email", None) or ps.email,
                            "mode": "cloud",
                        }
                        st.rerun()
                except Exception:
                    # If tokens are invalid, clear persisted session to avoid loops
                    if supabase_clear_session is not None:
                        supabase_clear_session()

    # Already logged in
    if st.session_state.auth.get("logged_in"):
        st.sidebar.success(f"Masuk sebagai: {st.session_state.auth.get('username')}")

        if st.session_state.auth.get("mode") == "cloud":
            st.session_state.cloud_auto_sync = st.sidebar.toggle(
                "Auto-sync ke cloud",
                value=bool(st.session_state.get("cloud_auto_sync", True)),
            )

            if st.sidebar.button("☁️ Sync sekarang"):
                try:
                    cloud = st.session_state.get("cloud_sync")
                    uid = st.session_state.auth.get("user_id")
                    if cloud and uid:
                        ok = cloud.save_user_blob(str(uid), _cloud_payload_from_state())
                        if ok:
                            st.sidebar.success("✅ Tersimpan ke cloud")
                        else:
                            st.sidebar.error("❌ Gagal sync ke cloud")
                    else:
                        st.sidebar.error("❌ Cloud belum siap")
                except Exception as e:
                    st.sidebar.error(f"❌ Sync error: {e}")

            if st.sidebar.button("↻ Restore dari cloud"):
                try:
                    cloud = st.session_state.get("cloud_sync")
                    uid = st.session_state.auth.get("user_id")
                    if cloud and uid:
                        row = cloud.load_user_blob(str(uid))
                        if row and _restore_state_from_cloud_row(row):
                            st.sidebar.success("✅ Data cloud dimuat")
                            st.rerun()
                        else:
                            st.sidebar.info("ℹ️ Belum ada data di cloud")
                    else:
                        st.sidebar.error("❌ Cloud belum siap")
                except Exception as e:
                    st.sidebar.error(f"❌ Restore error: {e}")

        if st.sidebar.button("🚪 Logout"):
            if st.session_state.auth.get("mode") == "cloud":
                try:
                    client = st.session_state.get("supabase_client")
                    if client is not None:
                        client.auth.sign_out()
                except Exception:
                    pass
                if supabase_clear_session is not None:
                    supabase_clear_session()

            st.session_state.auth = {"logged_in": False, "user_id": None, "username": None, "mode": "local"}
            st.rerun()

        return True

    # Login mode selection
    if cloud_available:
        mode = st.sidebar.radio("Mode Login", ["Cloud (Email)", "Local (Device)"], index=0)
    else:
        mode = "Local (Device)"
        if create_client and CloudSync:
            st.sidebar.caption("Cloud login: set env SUPABASE_URL & SUPABASE_ANON_KEY untuk aktifkan.")

    # Cloud login (works without hosting via email+password)
    if mode == "Cloud (Email)":
        st.sidebar.info("Login cloud via email+password bisa dipakai walau app hanya jalan di localhost.")
        tab_login, tab_signup = st.sidebar.tabs(["Masuk", "Daftar"])

        with tab_login:
            with st.form("cloud_login_form"):
                email = st.text_input("Email", key="cloud_login_email")
                password = st.text_input("Password", type="password", key="cloud_login_pw")
                remember = st.checkbox("Ingat saya (30 hari)", value=True)
                submitted = st.form_submit_button("🔓 Login Cloud")
            if submitted:
                try:
                    client = create_client(supabase_url, supabase_key)
                    resp = client.auth.sign_in_with_password({"email": email.strip(), "password": password})
                    user = getattr(resp, "user", None) or getattr(getattr(resp, "session", None), "user", None)
                    if user is None:
                        st.sidebar.error("❌ Login gagal")
                    else:
                        if remember and supabase_save_session is not None:
                            supabase_save_session(resp, email=email.strip())

                        st.session_state.supabase_client = client
                        st.session_state.cloud_sync = CloudSync(client=client)
                        st.session_state.auth = {
                            "logged_in": True,
                            "user_id": getattr(user, "id", None),
                            "username": getattr(user, "email", None) or email.strip(),
                            "mode": "cloud",
                        }

                        # Restore cloud data once on login (if exists)
                        try:
                            row = st.session_state.cloud_sync.load_user_blob(str(st.session_state.auth["user_id"]))
                            if row:
                                _restore_state_from_cloud_row(row)
                        except Exception:
                            pass

                        st.rerun()
                except Exception as e:
                    st.sidebar.error(f"❌ Login error: {e}")

            with st.expander("Opsional: Passwordless (OTP) tanpa hosting"):
                st.caption("Butuh Supabase Email OTP aktif. Jika email yang kamu terima berupa link, mode ini mungkin tidak jalan tanpa domain.")
                otp_email = st.text_input("Email", key="cloud_otp_email")
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("📨 Kirim OTP", key="cloud_send_otp"):
                        try:
                            client = create_client(supabase_url, supabase_key)
                            client.auth.sign_in_with_otp({"email": otp_email.strip()})
                            st.success("✅ OTP dikirim. Cek email.")
                        except Exception as e:
                            st.error(f"❌ Gagal kirim OTP: {e}")
                with c2:
                    otp_token = st.text_input("Kode OTP", key="cloud_otp_token")
                    if st.button("✅ Verifikasi OTP", key="cloud_verify_otp"):
                        try:
                            client = create_client(supabase_url, supabase_key)
                            resp = client.auth.verify_otp({"email": otp_email.strip(), "token": otp_token.strip(), "type": "email"})
                            user = getattr(resp, "user", None) or getattr(getattr(resp, "session", None), "user", None)
                            if user is None:
                                st.error("❌ OTP tidak valid")
                            else:
                                if supabase_save_session is not None:
                                    supabase_save_session(resp, email=otp_email.strip())
                                st.session_state.supabase_client = client
                                st.session_state.cloud_sync = CloudSync(client=client)
                                st.session_state.auth = {
                                    "logged_in": True,
                                    "user_id": getattr(user, "id", None),
                                    "username": getattr(user, "email", None) or otp_email.strip(),
                                    "mode": "cloud",
                                }
                                try:
                                    row = st.session_state.cloud_sync.load_user_blob(str(st.session_state.auth["user_id"]))
                                    if row:
                                        _restore_state_from_cloud_row(row)
                                except Exception:
                                    pass
                                _cloud_autosync("transaction")
                                _save_local_checkpoint()
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ Verify error: {e}")

        with tab_signup:
            with st.form("cloud_signup_form"):
                email = st.text_input("Email", key="cloud_signup_email")
                password = st.text_input("Password", type="password", key="cloud_signup_pw")
                submitted2 = st.form_submit_button("✍️ Daftar Cloud")
            if submitted2:
                try:
                    client = create_client(supabase_url, supabase_key)
                    client.auth.sign_up({"email": email.strip(), "password": password})
                    st.sidebar.success("✅ Daftar berhasil. Silakan login.")
                except Exception as e:
                    st.sidebar.error(f"❌ Daftar error: {e}")

        return False

    # Local auth fallback
    if AuthManager is None:
        st.sidebar.warning("Auth lokal belum siap. Akses dilanjutkan tanpa login.")
        return True

    tab_login, tab_signup = st.sidebar.tabs(["Login", "Daftar"])
    auth = AuthManager()

    with tab_login:
        with st.form("login_form"):
            u = st.text_input("Username / Email", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            submitted = st.form_submit_button("🔓 Login")
        if submitted:
            ok, res = auth.login(u.strip(), p)
            if ok:
                st.session_state.auth = {
                    "logged_in": True,
                    "user_id": res["user_id"],
                    "username": res["username"],
                }
                st.rerun()
            else:
                st.sidebar.error(str(res))

    with tab_signup:
        with st.form("signup_form"):
            su = st.text_input("Username", key="signup_u")
            se = st.text_input("Email", key="signup_e")
            sp = st.text_input("Password", type="password", key="signup_p")
            submitted2 = st.form_submit_button("✍️ Daftar")
        if submitted2:
            ok, msg = auth.signup(su.strip(), se.strip(), sp)
            if ok:
                st.sidebar.success(str(msg))
                st.sidebar.info("Silakan login di tab Login")
            else:
                st.sidebar.error(str(msg))

    st.sidebar.caption("Tip: akun ini tersimpan lokal (device ini).")
    return False

# ============= HELPER FUNCTIONS =============
@st.cache_data
def load_screening_results():
    """Load hasil screening terbaru"""
    screening_dir = Path("data/screening_results")
    if not screening_dir.exists():
        return None
    files = sorted(list(screening_dir.glob("scan_*.csv")), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None

    # Prefer the newest readable CSV; skip empty or malformed files
    for candidate in files:
        try:
            # skip zero-byte files quickly
            if candidate.stat().st_size == 0:
                continue
            df = pd.read_csv(candidate)
            return df, candidate
        except Exception:
            # ignore parse errors and try the next file
            continue

    # If none valid, return an empty DataFrame and None path
    return pd.DataFrame(), None

def get_file_age(filepath):
    """Get waktu file dibuat"""
    timestamp = filepath.stem.split('_')[1:3]  # scan_YYYYMMDD_HHMMSS
    if len(timestamp) >= 2:
        date_str = timestamp[0]
        time_str = timestamp[1]
        return f"{date_str[4:6]}/{date_str[6:]} {time_str[0:2]}:{time_str[2:4]}"
    return "Unknown"

def create_signal_badge(signal):
    """Create HTML badge for signal"""
    if 'BUY' in signal:
        return f'<span class="status-badge badge-green">{signal}</span>'
    elif 'SELL' in signal:
        return f'<span class="status-badge badge-red">{signal}</span>'
    else:
        return f'<span class="status-badge badge-yellow">{signal}</span>'

def format_table_with_colors(display_df, numeric_data):
    """Format dataframe dengan color coding hijau/merah konsisten di semua tab"""
    styled_data = []
    for idx, (i, row) in enumerate(display_df.iterrows()):
        styled_row = {}
        for col_name in display_df.columns:
            value = row[col_name]
            
            # SAHAM/Symbol - Bold
            if col_name in ['SAHAM', 'symbol', 'Kode']:
                styled_row[col_name] = f'<span style="font-weight: bold; font-size: 1.05em;">{value}</span>'
            
            # HARGA/Price & KEMARIN/Prev - Color coding
            elif col_name in ['HARGA', 'current_price']:
                if idx < len(numeric_data.get('current_price', [])):
                    curr_price = numeric_data.get('current_price', [None])[idx]
                    prev_price = numeric_data.get('prev_price', [None])[idx]
                    if curr_price and prev_price:
                        if curr_price > prev_price:
                            styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{value}</span>'
                        elif curr_price < prev_price:
                            styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{value}</span>'
                        else:
                            styled_row[col_name] = f'<span>{value}</span>'
                    else:
                        styled_row[col_name] = f'<span>{value}</span>'
                else:
                    styled_row[col_name] = f'<span>{value}</span>'
            
            # PERUBAHAN % / change_pct - Green if positive, Red if negative
            elif col_name in ['PERUBAHAN %', 'change_pct']:
                if idx < len(numeric_data.get('change_pct', [])):
                    change_val = numeric_data.get('change_pct', [None])[idx]
                    if change_val:
                        if change_val > 0:
                            styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{value}</span>'
                        elif change_val < 0:
                            styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{value}</span>'
                        else:
                            styled_row[col_name] = f'<span>{value}</span>'
                    else:
                        styled_row[col_name] = f'<span>{value}</span>'
                else:
                    styled_row[col_name] = f'<span>{value}</span>'
            
            # NET BUY - Green if larger than NET SELL
            elif col_name in ['NET BUY', 'broker_buy']:
                if idx < len(numeric_data.get('broker_buy', [])):
                    net_buy_val = numeric_data.get('broker_buy', [None])[idx]
                    net_sell_val = numeric_data.get('broker_sell', [None])[idx]
                    if net_buy_val and net_sell_val:
                        if net_buy_val > net_sell_val:
                            styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{value}</span>'
                        elif net_buy_val < net_sell_val:
                            styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{value}</span>'
                        else:
                            styled_row[col_name] = f'<span>{value}</span>'
                    else:
                        styled_row[col_name] = f'<span>{value}</span>'
                else:
                    styled_row[col_name] = f'<span>{value}</span>'
            
            # NET SELL - Green if larger than NET BUY
            elif col_name in ['NET SELL', 'broker_sell']:
                if idx < len(numeric_data.get('broker_sell', [])):
                    net_sell_val = numeric_data.get('broker_sell', [None])[idx]
                    net_buy_val = numeric_data.get('broker_buy', [None])[idx]
                    if net_sell_val and net_buy_val:
                        if net_sell_val > net_buy_val:
                            styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{value}</span>'
                        elif net_sell_val < net_buy_val:
                            styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{value}</span>'
                        else:
                            styled_row[col_name] = f'<span>{value}</span>'
                    else:
                        styled_row[col_name] = f'<span>{value}</span>'
                else:
                    styled_row[col_name] = f'<span>{value}</span>'
            
            else:
                styled_row[col_name] = f'<span>{value}</span>'
        
        styled_data.append(styled_row)
    
    return pd.DataFrame(styled_data)

def format_journal_with_colors(journal_df):
    """Format journal dengan calculation P/L dan percentage dengan color coding"""
    styled_data = []
    for idx, (i, row) in enumerate(journal_df.iterrows()):
        styled_row = {}
        
        # Convert Qty from lembar to lot for display
        qty_lot = row['Qty'] / 100 if row['Qty'] > 0 else 0
        price = row['Price']
        current_price = row['Current Price']
        action = row['Action']
        
        # Calculate unrealized P/L: (Current Price - Price) × Qty (in lembar)
        pl_value = (current_price - price) * row['Qty'] if action in ['BUY', 'HOLD'] else row['Profit/Loss']
        
        # Calculate percentage: ((Current Price - Price) / Price) × 100
        pct_value = ((current_price - price) / price * 100) if price > 0 and action in ['BUY', 'HOLD'] else (row['Profit/Loss'] / (row['Price'] * row['Qty']) * 100 if row['Price'] * row['Qty'] > 0 and action == 'SELL' else 0)
        
        for col_name in ['Tanggal', 'Saham', 'Action', 'Qty', 'Price', 'Current Price', 'Total', 'Profit/Loss', 'Return %']:
            if col_name == 'Tanggal':
                styled_row[col_name] = str(row['Tanggal'])
            
            elif col_name == 'Saham':
                styled_row[col_name] = f'<span style="font-weight: bold; font-size: 1.05em;">{row["Saham"]}</span>'
            
            elif col_name == 'Action':
                action_text = row['Action']
                action_color = '#00c77a' if action_text == 'BUY' else '#ee5a52' if action_text == 'SELL' else '#4A8FA8'
                styled_row[col_name] = f'<span style="color: {action_color}; font-weight: bold;">{action_text}</span>'
            
            elif col_name == 'Qty':
                # Display Qty in lots
                styled_row[col_name] = f"{int(qty_lot)}"
            
            elif col_name == 'Price':
                styled_row[col_name] = f"Rp {int(price):,}"
            
            elif col_name == 'Current Price':
                styled_row[col_name] = f"Rp {int(current_price):,}"
            
            elif col_name == 'Total':
                styled_row[col_name] = f"Rp {int(row['Total']):,}"
            
            elif col_name == 'Profit/Loss':
                pl_text = f"Rp {int(pl_value):+,}"
                if pl_value > 0:
                    styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{pl_text}</span>'
                elif pl_value < 0:
                    styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{pl_text}</span>'
                else:
                    styled_row[col_name] = f'<span>{pl_text}</span>'
            
            elif col_name == 'Return %':
                pct_text = f"{pct_value:+.2f}%"
                if pct_value > 0:
                    styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{pct_text}</span>'
                elif pct_value < 0:
                    styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{pct_text}</span>'
                else:
                    styled_row[col_name] = f'<span>{pct_text}</span>'
        
        styled_data.append(styled_row)
    
    return pd.DataFrame(styled_data)

def fetch_single_stock(stock_code):
    """Fetch data single stock (without cache to ensure fresh data)"""
    try:
        fetcher = DataFetcher()
        hist = fetcher.fetch_stock_data(stock_code, period='3mo')
        return hist
    except Exception as e:
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_all_stocks_yfinance():
    """
    Fetch data realtime semua saham IHSG dengan timeout fallback
    - First try: Stockbit Order Book API untuk bid/offer real
    - Second: yFinance dengan timeout protection
    - Fallback: Return empty DataFrame jika terlalu lambat
    TTL: 5 menit (auto refresh)
    """
    import yfinance as yf
    import random
    
    # Compact IHSG stock list (30 saham utama saja untuk kecepatan)
    sample_stocks = [
        'BBCA', 'BBNI', 'BBRI', 'BDMN', 'BMRI', 'BSDE', 'BSIM', 'BTPN', 'CPIN',
        'CTBN', 'ENRG', 'GGRM', 'HMSP', 'INCO', 'INTP', 'ITMG', 'JSMR', 'KLBF',
        'MEDC', 'MIKA', 'MNCN', 'PGAS', 'PJAA', 'SMGR', 'TINS', 'TLKM', 'UNTR',
        'UNVR', 'WIKA', 'WSKT'
    ]
    
    # Try Stockbit fetcher first (dengan timeout)
    if StockbitFetcher:
        try:
            print("🔄 Fetching dari Stockbit...")
            fetcher = StockbitFetcher(use_cache=True)
            fetcher.sample_stocks = sample_stocks
            
            df = fetcher.fetch_all_stocks_hybrid()
            
            if not df.empty:
                print(f"✅ Stockbit: {len(df)} saham")
                required_cols = ['symbol', 'current_price', 'prev_price', 'change_pct',
                               'open_price', 'low_price', 'high_price', 'open_is_low',
                               'volume', 'bid_volume', 'offer_volume', 'broker_buy', 
                               'broker_sell', 'buy_greater_sell']
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = df['broker_buy'] > df['broker_sell' ] if col == 'buy_greater_sell' else 0
                return df[required_cols]
        except Exception as e:
            print(f"⚠️ Stockbit gagal: {str(e)[:50]}")
    
    # Fallback fast: Return empty DataFrame instead of hanging on yfinance
    print("⚠️ Using fast fallback mode (no real data)")
    return pd.DataFrame({
        'symbol': [],
        'current_price': [],
        'prev_price': [],
        'change_pct': [],
        'open_price': [],
        'low_price': [],
        'high_price': [],
        'open_is_low': [],
        'volume': [],
        'bid_volume': [],
        'offer_volume': [],
        'broker_buy': [],
        'broker_sell': [],
        'buy_greater_sell': []
    })

def run_screening():
    """Run screening process"""
    # Validasi modul tersedia
    if not DataFetcher or not BandarmologyAnalyzer:
        st.error("❌ Modul yang diperlukan tidak tersedia")
        return
    
    try:
        # Step 1: Initialize
        st.info("📍 Step 1: Initializing DataFetcher...")
        fetcher = DataFetcher()
        st.success("✅ DataFetcher ready")
        
        # Step 2: Fetch data
        st.info("📍 Step 2: Fetching stock data from yFinance...")
        stock_data = fetcher.fetch_all_data()
        
        if not stock_data:
            st.error("❌ Gagal mengambil data. Periksa koneksi internet.")
            return
            
        st.success(f"✅ Retrieved {len(stock_data)} stocks")
        
        # Step 3: Analyze stocks
        st.info("📍 Step 3: Analyzing stocks with Bandarmology...")
        progress_bar = st.progress(0)
        progress_text = st.empty()
        results = []
        
        for i, stock in enumerate(stock_data):
            try:
                analyzer = BandarmologyAnalyzer(stock['data'])
                phase = analyzer.detect_phase()
                divergence = analyzer.detect_divergence()
                
                open_is_low = False
                try:
                    last_row = stock['data'].iloc[-1]
                    open_is_low = (last_row['Open'] == last_row['Low'])
                except:
                    pass
                
                if phase:
                    results.append({
                        'symbol': stock['symbol'],
                        'company': stock['company_name'],
                        'price': phase['current_price'],
                        'vwap': phase['vwap'],
                        'distance': phase['distance_pct'],
                        'phase': phase['phase'],
                        'signal': phase['signal'],
                        'divergence': divergence,
                        'strength': phase['strength'],
                        'open_is_low': open_is_low
                    })
                
                progress = (i + 1) / len(stock_data)
                progress_bar.progress(progress)
                progress_text.text(f"Progress: {i + 1}/{len(stock_data)} stocks")
                
            except Exception as e:
                continue
        
        progress_text.empty()
        st.success(f"✅ Analyzed {len(results)} stocks")
        
        # Step 4: Save
        st.info("📍 Step 4: Saving results...")
        df = pd.DataFrame(results)
        Path("data/screening_results").mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/screening_results/scan_{timestamp}.csv"
        df.to_csv(filename, index=False)
        st.success(f"✅ Saved to: {filename}")
        
        # Final summary
        st.success("✅ ✅ ✅ SCREENING SELESAI! ✅ ✅ ✅")
        st.balloons()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", len(df))
        with col2:
            acc = len(df[df['phase'] == 'ACCUMULATION']) if 'phase' in df.columns else 0
            st.metric("Akumulasi", acc)
        with col3:
            dis = len(df[df['phase'] == 'DISTRIBUTION']) if 'phase' in df.columns else 0
            st.metric("Distribusi", dis)
        with col4:
            sb = len(df[df['signal'] == 'STRONG_BUY']) if 'signal' in df.columns else 0
            st.metric("Strong Buy", sb)
        
        st.write("✅ Hasil tersimpan! Buka Tab 1 untuk lihat Dashboard Utama")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        with st.expander("Error Details"):
            st.code(str(e))

# ============= MAIN APP =============
def main():
    if not require_login():
        st.markdown(
            """
            <div style="padding: 14px 16px; background: #161B22; border-radius: 10px; border-left: 3px solid #4A8FA8;">
                <div style="color:#E1E8ED; font-weight: 800; font-size: 1.2rem; margin-bottom: 6px;">Login dibutuhkan</div>
                <div style="color:#E1E8ED; opacity: 0.9;">Silakan login / daftar lewat sidebar untuk membuka dashboard.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    # HEADER dengan styling lebih menarik
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #4A8FA8 0%, #5A9FB8 50%, #4A8FA8 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(74, 143, 168, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.15em;
        font-weight: bold;
    }
    .main-header p {
        margin: 5px 0 0 0;
        font-size: 1.0em;
        opacity: 0.95;
    }

    /* Mobile: make header less tall/large */
    @media (max-width: 600px) {
        .main-header {
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 10px;
        }
        .main-header h1 {
            font-size: 1.45em;
            line-height: 1.15;
        }
        .main-header p {
            font-size: 0.85em;
            margin-top: 4px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>Jurnal Screening Saham IHSG</h1>
        <p>Intelligent Stock Analysis Powered by Bandarmology</p>
    </div>
    """, unsafe_allow_html=True)
    # Render compact profile / login panel (top-left)
    def render_profile_panel():
        if 'auth' not in st.session_state:
            st.session_state.auth = {"logged_in": False, "user_id": None, "username": None, "mode": "local"}

        cols = st.columns([1, 6, 1])
        # Left: tappable logo (use a visible emoji button for reliable mobile taps)
        with cols[0]:
            # Fallback to a simple emoji button so touch events register on mobile
            if st.button('👤', key='header_logo_btn'):
                st.session_state.show_header_login = not st.session_state.get('show_header_login', False)

        # Center: profile / login button
        with cols[1]:
            if st.session_state.auth.get('logged_in'):
                user = st.session_state.auth.get('username') or 'User'
                st.markdown(f"**👤 {user}**")
                if st.button('🚪 Logout', key='header_logout'):
                    client = st.session_state.get('supabase_client')
                    try:
                        if client is not None:
                            client.auth.sign_out()
                    except Exception:
                        pass
                    st.session_state.auth = {"logged_in": False, "user_id": None, "username": None, "mode": "local"}
                    st.rerun()
            else:
                st.markdown("**🔓 Belum login**")
                if st.button('🔓 Login / Daftar', key='header_show_login'):
                    st.session_state.show_header_login = True

        # Inline login form
        if st.session_state.get('show_header_login'):
            with st.form('header_cloud_login'):
                he = st.text_input('Email', key='header_cloud_email')
                hp = st.text_input('Password', type='password', key='header_cloud_pw')
                hsub = st.form_submit_button('🔓 Login Cloud')
            if hsub:
                try:
                    client = create_client(supabase_url, supabase_key)
                    resp = client.auth.sign_in_with_password({"email": he.strip(), "password": hp})
                    user = getattr(resp, 'user', None) or getattr(getattr(resp, 'session', None), 'user', None)
                    if user is None:
                        st.error('❌ Login gagal')
                        return
                    st.session_state.supabase_client = client
                    st.session_state.cloud_sync = CloudSync(client=client)
                    st.session_state.auth = {
                        'logged_in': True,
                        'user_id': getattr(user, 'id', None),
                        'username': getattr(user, 'email', None) or he.strip(),
                        'mode': 'cloud'
                    }
                    try:
                        row = st.session_state.cloud_sync.load_user_blob(str(st.session_state.auth['user_id']))
                        if row:
                            _restore_state_from_cloud_row(row)
                    except Exception:
                        pass
                    st.session_state.show_header_login = False
                    st.rerun()
                except Exception:
                    pass

    # Render panel (safe to call)
    render_profile_panel()
    
    # MVP quick-switch in sidebar
    try:
        mode_choice = st.sidebar.selectbox("Mode Tampilan", ["Full App", "MVP (Light)"], index=0)
    except Exception:
        mode_choice = "Full App"

    

    # TAB NAVIGATION
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Dashboard Utama",
        "Cek Saham",
        "Hasil Screening",
        "Action",
        "Tutorial",
        "Investasi Saya"
    ])
    
    # ============= TAB 1: DASHBOARD UTAMA =============
    with tab1:
        st.markdown("""
        <style>
        /* Dark mode multi-block layout - minimal borders */
        .metric-card {
            background: #161B22;
            border-radius: 8px;
            padding: 10px 14px;
            border: none;
            border-left: 3px solid #4A8FA8;
            box-shadow: none;
            margin: 0;
        }
        .metric-card-green {
            border-left-color: #4A8FA8;
        }
        .metric-card-red {
            border-left-color: #E85D75;
        }
        .metric-card-yellow {
            border-left-color: #D4A942;
        }
        /* Minimal styling */
        [data-testid="stPlotlyChart"] {
            border: none;
            border-radius: 8px;
            padding: 4px;
            margin: 3px 0;
            animation: fadeUp 0.35s ease both;
        }
        [data-testid="stDataFrame"] {
            border: none;
            border-radius: 8px;
            overflow: hidden;
            animation: fadeUp 0.35s ease both;
        }
        .metric {
            border: none;
            border-radius: 8px;
            padding: 4px;
            background: transparent;
        }
        .header-title {
            background: linear-gradient(90deg, #4A8FA8, #5A9FB8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
            font-size: 1.9em;
            margin: 10px 0;
        }

        @media (max-width: 600px) {
            .header-title {
                font-size: 1.35em;
                margin: 6px 0;
            }
        }
        /* Reduce spacing */
        h2, h3 {
            margin: 3px 0 6px 0 !important;
            font-size: 1.1em !important;
            color: #E1E8ED !important;
        }
        p {
            margin: 1px 0 !important;
            line-height: 1.2 !important;
            color: #E1E8ED !important;
        }

        /* Light animation */
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.75rem !important;
        }
        /* Minimal column styling */
        [data-testid="column"] {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 4px !important;
            margin: 2px !important;
        }
        [data-testid="stVerticalBlock"] > div {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 4px;
            margin: 2px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<h1 class="header-title">Analisis Saham</h1>', unsafe_allow_html=True)
        
        result = load_screening_results()
        
        if result is None:
            st.warning("Belum ada hasil screening")
            st.info("**Klik tab Action → Jalankan Screening** untuk mulai")
        else:
            df, filepath = result
            
            age = get_file_age(filepath)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.caption(f"Updated: {age}")
            with col2:
                if st.button("🔄", key="refresh_btn", help="Refresh"):
                    st.cache_data.clear()
                    st.rerun()
            
            # Compact metrics in single row
            metric_cols = st.columns([1.5, 1.5, 1.5, 1.5])
            with metric_cols[0]:
                st.metric("Total", f"{len(df)}")
            accumulation_count = len(df[df['phase'] == 'ACCUMULATION'])
            with metric_cols[1]:
                st.metric("Akumulasi", f"{accumulation_count}")
            distribution_count = len(df[df['phase'] == 'DISTRIBUTION'])
            with metric_cols[2]:
                st.metric("Distribusi", f"{distribution_count}")
            absorbing_count = len(df[df['phase'] == 'ABSORBING'])
            with metric_cols[3]:
                st.metric("Absorbing", f"{absorbing_count}")
            
            # CHARTS - Compact block layout with minimal styling
            col1, col2 = st.columns(2)
            
            with col1:
                st.caption("Fase Pasar")
                phase_counts = df['phase'].value_counts()
                colors = {'ACCUMULATION': '#28a745', 'DISTRIBUTION': '#dc3545', 'ABSORBING': '#ffc107'}
                fig = go.Figure(data=[go.Pie(
                    labels=phase_counts.index,
                    values=phase_counts.values,
                    hole=0.35,
                    textposition="auto",
                    hovertemplate="<b>%{label}</b><br>Jumlah: %{value}<br>Persentase: %{percent}<extra></extra>",
                    marker=dict(
                        colors=[colors.get(p, '#999') for p in phase_counts.index],
                        line=dict(color='#FFFFFF', width=2)
                    )
                )])
                fig.update_layout(
                    height=280,
                    showlegend=False,
                    font=dict(size=9, color='#E1E8ED'),
                    plot_bgcolor='#0F1419',
                    paper_bgcolor='#1A1F2E',
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(showgrid=False, color='#E1E8ED'),
                    yaxis=dict(showgrid=False, color='#E1E8ED')
                )
                st_plotly_chart_stretch(fig)
            
            with col2:
                st.caption("Signal Trading")
                signal_counts = df['signal'].value_counts()
                signal_colors = {
                    'STRONG_BUY': '#FF6B6B',
                    'BUY': '#28a745',
                    'SELL': '#dc3545',
                    'STRONG_SELL': '#8B0000'
                }
                fig = go.Figure(data=[go.Bar(
                    x=signal_counts.index,
                    y=signal_counts.values,
                    text=signal_counts.values,
                    textposition='auto',
                    hovertemplate="<b>%{x}</b><br>%{y}<extra></extra>",
                    marker_color=[signal_colors.get(x, '#999') for x in signal_counts.index]
                )])
                fig.update_layout(
                    height=280,
                    showlegend=False,
                    font=dict(size=9, color='#E1E8ED'),
                    plot_bgcolor='#0F1419',
                    paper_bgcolor='#1A1F2E',
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(showgrid=False, color='#E1E8ED'),
                    yaxis=dict(showgrid=False, color='#E1E8ED'),
                    xaxis_title="",
                    yaxis_title=""
                )
                st_plotly_chart_stretch(fig)
            
            # TOP AKUMULASI
            st.markdown("<h3 style='margin: 6px 0 6px 0; color: #E1E8ED;'>Top 10 Akumulasi</h3>", unsafe_allow_html=True)
            accumulation = df[df['phase'] == 'ACCUMULATION'].nlargest(10, 'distance')
            
            if not accumulation.empty:
                try:
                    display_df = accumulation[[
                        'symbol', 'company', 'price', 'vwap', 'distance', 'signal', 'strength'
                    ]].copy()
                    
                    # Simpan numeric values untuk coloring
                    numeric_data = {
                        'price': accumulation['price'].values,
                        'vwap': accumulation['vwap'].values,
                        'distance': accumulation['distance'].values,
                        'strength': accumulation['strength'].values,
                    }
                    
                    # Format kolom dengan safe handling
                    display_df['price'] = display_df['price'].apply(lambda x: f"{float(x):,.0f}")
                    display_df['vwap'] = display_df['vwap'].apply(lambda x: f"{float(x):,.0f}")
                    display_df['distance'] = display_df['distance'].apply(lambda x: f"{float(x):+.2f}%")
                    display_df['strength'] = display_df['strength'].apply(lambda x: f"{float(x):.0f}%")
                    
                    # Rename untuk tampilan lebih baik
                    display_df = display_df.rename(columns={
                        'symbol': 'SAHAM',
                        'company': 'PERUSAHAAN',
                        'price': 'HARGA',
                        'vwap': 'VWAP',
                        'distance': 'JARAK',
                        'signal': 'SIGNAL',
                        'strength': 'STRENGTH'
                    })
                    
                    # Render HTML dengan color coding konsisten
                    styled_data = []
                    for idx, (i, row) in enumerate(display_df.iterrows()):
                        styled_row = {}
                        for col_name in display_df.columns:
                            value = row[col_name]
                            
                            if col_name == 'SAHAM':
                                styled_row[col_name] = f'<span style="font-weight: bold; font-size: 1.05em;">{value}</span>'
                            elif col_name == 'JARAK':
                                distance = numeric_data['distance'][idx]
                                if distance > 0:
                                    styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{value}</span>'
                                elif distance < 0:
                                    styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{value}</span>'
                                else:
                                    styled_row[col_name] = f'<span>{value}</span>'
                            elif col_name == 'STRENGTH':
                                strength = numeric_data['strength'][idx]
                                if strength > 0:
                                    styled_row[col_name] = f'<span style="color: #00c77a; font-weight: bold;">{value}</span>'
                                elif strength < 0:
                                    styled_row[col_name] = f'<span style="color: #ee5a52; font-weight: bold;">{value}</span>'
                                else:
                                    styled_row[col_name] = f'<span>{value}</span>'
                            else:
                                styled_row[col_name] = f'<span>{value}</span>'
                        
                        styled_data.append(styled_row)
                    
                    styled_df = pd.DataFrame(styled_data)
                    st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                    
                    # Download button
                    csv = accumulation.to_csv(index=False)
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        st_download_button_stretch(
                            "📥 Download CSV",
                            csv,
                            "akumulasi_stocks.csv",
                            "text/csv",
                        )
                except Exception as e:
                    st.error(f"Error formatting table: {str(e)}")
                    # Fallback: show raw dataframe
                    st_dataframe_stretch(accumulation)
            else:
                st.info("Tidak ada saham dalam fase akumulasi")
    
    # ============= TAB 2: CEK SAHAM =============
    with tab2:
        st.header("Analisis Saham Individual")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stock_code = st.text_input(
                "Masukkan kode saham",
                "BBCA",
                help="Contoh: BBCA, BBNI, UNTR (tanpa .JK)"
            ).upper().strip()
        
        with col2:
            source = st.selectbox("Sumber data:", ["Stockbit", "yFinance"], index=0)
        
        st.info("Tekan tombol untuk menganalisis saham yang dipilih")
        
        if st_button_stretch("🔎 Cek Sekarang", key="cek_saham_btn"):
            if not stock_code:
                st.error("❌ Masukkan kode saham!")
            else:
                try:
                    if source == "yFinance":
                        st.subheader(f"Analisis {stock_code} (yFinance)")
                        
                        with st.spinner(f"Mengambil data {stock_code} dari yFinance..."):
                            hist = fetch_single_stock(stock_code)
                            
                            if hist is None or hist.empty:
                                st.error(f"❌ Data {stock_code} tidak ditemukan di yFinance")
                                st.info("Pastikan kode saham benar (format: BBCA, bukan BBCA.JK)")
                                st.stop()
                            
                            st.success(f"✅ Data {stock_code} berhasil diambil ({len(hist)} candlestick)")
                            
                            # Layout: Left = Bandarmology, Right = Chart
                            try:
                                # Get Bandarmology data first
                                analyzer = BandarmologyAnalyzer(hist)
                                phase_info = analyzer.detect_phase()
                                trend_info = analyzer.analyze_trend()
                                sr_info = analyzer.calculate_support_resistance()
                                
                                col_left, col_right = st.columns([1.2, 1])
                                
                                # LEFT: Bandarmology Analysis
                                with col_left:
                                    st.subheader("📊 Analisis Bandarmology")
                                    
                                    if phase_info:
                                        # Key Metrics - Bandarmology
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.metric("Harga", f"Rp {phase_info['current_price']:,.0f}")
                                        with col2:
                                            distance = phase_info['distance_pct']
                                            render_pct_value_card("Jarak VWAP", float(distance))
                                        
                                        # Signal & Strength
                                        st.write("**🎯 SIGNAL & STRENGTH**")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            st.write(f"{phase_info['signal']}")
                                        with col2:
                                            strength = float(phase_info['strength'])
                                            strength_cls = _pl_class(strength)
                                            st.markdown(
                                                f"<div class='fade-up'><span class='{strength_cls}' style='font-weight:800;'>{strength:.0f}%</span></div>",
                                                unsafe_allow_html=True,
                                            )
                                        
                                        # Trend
                                        st.write("**📈 TREND**")
                                        if trend_info:
                                            st.write(f"{trend_info['trend']}")
                                        
                                        # Support & Resistance  
                                        st.write("**🧱 SUPPORT & RESISTANCE**")
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if sr_info:
                                                st.write(f"S: {sr_info['support']:,.0f}")
                                        with col2:
                                            if sr_info:
                                                st.write(f"R: {sr_info['resistance']:,.0f}")
                                        
                                        st.markdown("---")
                                        
                                        # Recommendation
                                        phase = phase_info['phase']
                                        st.write("**💡 REKOMENDASI**")
                                        if phase == "ACCUMULATION":
                                            st.write("**BUY - Akumulasi**")
                                        elif phase == "DISTRIBUTION":
                                            st.write("**SELL - Distribusi**")
                                        else:
                                            st.write("**HOLD - Konsolidasi**")
                                    else:
                                        st.warning("⚠️ Data tidak cukup")
                                
                                # RIGHT: Chart
                                with col_right:
                                    st.subheader("Chart (3 Bulan)")
                                    try:
                                        fig = go.Figure(data=[go.Candlestick(
                                            x=hist.index,
                                            open=hist['Open'],
                                            high=hist['High'],
                                            low=hist['Low'],
                                            close=hist['Close'],
                                            name=stock_code
                                        )])
                                        
                                        if 'SMA20' in hist.columns:
                                            fig.add_trace(go.Scatter(
                                                x=hist.index,
                                                y=hist['SMA20'],
                                                name='SMA20',
                                                line=dict(color='#4A8FA8', width=1),
                                                visible='legendonly'
                                            ))
                                        
                                        if 'SMA50' in hist.columns:
                                            fig.add_trace(go.Scatter(
                                                x=hist.index,
                                                y=hist['SMA50'],
                                                name='SMA50',
                                                line=dict(color='#E85D75', width=1),
                                                visible='legendonly'
                                            ))
                                        
                                        fig.update_layout(
                                            title=None,
                                            yaxis_title=None,
                                            xaxis_title=None,
                                            height=350,
                                            hovermode='x unified',
                                            margin=dict(l=0, r=0, t=0, b=0),
                                            showlegend=True
                                        )
                                        st_plotly_chart_stretch(fig, key="chart_tab2")
                                    except Exception as e:
                                        st.error(f"Error chart: {str(e)}")
                            
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                    
                    else:  # Stockbit
                        st.subheader(f"Data Stockbit - {stock_code}")
                        
                        with st.spinner(f"Mengambil data Stockbit {stock_code}..."):
                            try:
                                if not StockbitFetcher:
                                    st.error("❌ StockbitFetcher tidak tersedia")
                                    st.stop()
                                
                                stockbit = StockbitFetcher(use_cache=False)
                                # Ambil semua data sentiment (realtime)
                                all_data = stockbit.fetch_all_stocks_sentiment()
                                
                                if all_data.empty:
                                    st.error(f"❌ Gagal mengambil data dari Stockbit")
                                    st.stop()
                                
                                # Filter untuk saham pilihan user
                                stock_data = all_data[all_data['symbol'].str.upper() == stock_code.upper()]
                                
                                if stock_data.empty:
                                    st.error(f"❌ Data {stock_code} tidak ditemukan di Stockbit")
                                    st.stop()
                                
                                st.success(f"✅ Data {stock_code} berhasil diambil dari Stockbit (Realtime)")
                                
                                # Extract single row
                                row = stock_data.iloc[0]
                                
                                # Key Metrics dengan styling
                                st.markdown("""
                                <style>
                                .metric-stockbit { font-size: 0.95em; margin: 5px 0; }
                                </style>
                                """, unsafe_allow_html=True)
                                
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    price = row.get('current_price', 0)
                                    st.metric("Harga", f"Rp {float(price):,.0f}" if price > 0 else "-")
                                with col2:
                                    change = row.get('change_pct', 0)
                                    if change is None or change == 0:
                                        render_stat_card("Change %", "-")
                                    else:
                                        render_pct_value_card("Change %", float(change))
                                with col3:
                                    rec = row.get('recommendation', 'N/A')
                                    st.metric("Rekomendasi", str(rec) if rec else "-")
                                with col4:
                                    tech = row.get('technical_rating', 'N/A')
                                    st.metric("Technical", str(tech) if tech else "-")
                                
                                st.divider()
                                
                                # Detail signals
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    buy = row.get('buy', 0)
                                    st.metric("BUY Signals", int(buy) if buy else 0)
                                with col2:
                                    sell = row.get('sell', 0)
                                    st.metric("SELL Signals", int(sell) if sell else 0)
                                with col3:
                                    fund = row.get('fundamental_rating', 'N/A')
                                    st.metric("Fundamental", str(fund) if fund else "-")
                                
                                st.divider()
                                st.info("✅ Data realtime dari Stockbit sentiment analysis")
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                
                except Exception as e:
                    st.error(f"❌ Error tidak terduga: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # ============= TAB 3: HASIL SCREENING =============
    with tab3:
        st.header("Hasil Screening Lengkap")
        
        st.write("**Data Sumber:** IHSG & Listed Stocks | **Provider:** yFinance (Realtime)")
        
        # Pilih sumber screening (default yFinance, reliable)
        screening_source = st.radio("Sumber Screening:", ["yFinance", "Stockbit"], horizontal=True, index=0)
        
        # Filter options
        col_filter1, col_filter2, col_filter3, col_filter4 = st.columns([1.5, 1.5, 1.5, 1.5])
        with col_filter1:
            show_open_low_only = st.checkbox("Open=Low", value=False)
        with col_filter2:
            show_buy_greater_sell = st.checkbox("Net Buy > Net Sell", value=False)
        with col_filter3:
            show_mover_only = st.checkbox("Mover (>2%)", value=False)
        with col_filter4:
            show_bid_greater_offer = st.checkbox("Bid > Offer", value=False)
        
        # Sorting options
        col_sort1, col_sort2, col_sort3 = st.columns([2, 2, 2])
        with col_sort1:
            sort_by = st.selectbox("Urutkan Berdasarkan:", 
                ["Default", "Mover Tertinggi ↑", "Mover Terendah ↓", "Volume Tertinggi", "Bid Volume", "Net Buy"])
        with col_sort2:
            st.write("")  # Spacer
        with col_sort3:
            st.write("")  # Spacer
        
        if screening_source == "yFinance":
            # Inject custom CSS untuk table styling
            st.markdown("""
            <style>
            .bold-saham { font-weight: bold !important; font-size: 1.05em !important; }
            .small-font { font-size: 0.93em !important; }
            .green-text { color: #00ff00 !important; }
            .red-text { color: #ff4444 !important; }
            table { width: 100%; border-collapse: collapse; }
            th { background-color: #4A8FA8 !important; color: white !important; font-weight: bold !important; padding: 10px !important; text-align: left !important; }
            td { padding: 8px !important; border-bottom: 1px solid #ddd !important; }
            tr:hover { background-color: #f5f5f5 !important; }
            </style>
            """, unsafe_allow_html=True)
            
            try:
                # Ambil data realtime dari yFinance dengan open=low calculation
                yf_df = fetch_all_stocks_yfinance()
                
                if not yf_df.empty:
                    # Apply filters
                    display_df = yf_df.copy()
                    
                    if show_open_low_only:
                        display_df = display_df[display_df['open_is_low'] == True]
                    
                    if show_buy_greater_sell:
                        display_df = display_df[display_df['buy_greater_sell'] == True]
                    
                    if show_mover_only:
                        display_df = display_df[(display_df['change_pct'] >= 2.0)]
                    
                    if show_bid_greater_offer:
                        display_df = display_df[display_df['bid_volume'] > display_df['offer_volume']]
                    
                    if len(display_df) > 0:
                        filter_desc = []
                        if show_open_low_only:
                            filter_desc.append("Open=Low")
                        if show_buy_greater_sell:
                            filter_desc.append("Net Buy > Net Sell")
                        if show_mover_only:
                            filter_desc.append("Mover (>2%)")
                        if show_bid_greater_offer:
                            filter_desc.append("Bid > Offer")
                        
                        if filter_desc:
                            st.info(f"Screening otomatis: {len(display_df)} saham dengan filter {' & '.join(filter_desc)}")
                        else:
                            st.info(f"Data realtime dari yFinance ({len(display_df)} saham)")
                        
                        # Add data source info about bid/offer accuracy
                        st.warning(
                            "⚠️ **Data Bid/Offer**: Karena Stockbit API saat ini tidak accessible, "
                            "nilai BID/OFFER dan NET BUY/NET SELL adalah *estimasi* berdasarkan volume total. "
                            "Untuk data real-time bid/offer yang akurat, gunakan aplikasi broker langsung. "
                            "[Lihat issue →](https://github.com/donnytakeshi/jurnal-saham-ihsg/issues)"
                        )
                        
                        # Apply sorting based on selection
                        if sort_by == "Mover Tertinggi ↑":
                            display_df = display_df.sort_values('change_pct', ascending=False)
                        elif sort_by == "Mover Terendah ↓":
                            display_df = display_df.sort_values('change_pct', ascending=True)
                        elif sort_by == "Volume Tertinggi":
                            display_df = display_df.sort_values('volume', ascending=False)
                        elif sort_by == "Bid Volume":
                            display_df = display_df.sort_values('bid_volume', ascending=False)
                        elif sort_by == "Net Buy":
                            display_df = display_df.sort_values('broker_buy', ascending=False)
                        
                        # Siapkan display columns dengan data termasuk broker dan harga kemarin
                        display_cols = display_df[['symbol', 'current_price', 'prev_price', 'change_pct', 'bid_volume', 'offer_volume', 'broker_buy', 'broker_sell', 'open_is_low']].copy()
                        
                        # Simpan numeric values untuk coloring sebelum formatting
                        numeric_data = {
                            'current_price': display_df['current_price'].values,
                            'prev_price': display_df['prev_price'].values,
                            'change_pct': display_df['change_pct'].values,
                            'bid_volume': display_df['bid_volume'].values,
                            'offer_volume': display_df['offer_volume'].values,
                            'broker_buy': display_df['broker_buy'].values,
                            'broker_sell': display_df['broker_sell'].values,
                            'volume': display_df['volume'].values,
                        }
                        
                        display_cols = display_cols.rename(columns={
                            'symbol': 'SAHAM',
                            'current_price': 'HARGA',
                            'prev_price': 'KEMARIN',
                            'change_pct': 'PERUBAHAN %',
                            'bid_volume': 'BID',
                            'offer_volume': 'OFFER',
                            'broker_buy': 'NET BUY',
                            'broker_sell': 'NET SELL',
                            'open_is_low': 'OPEN=LOW'
                        })
                        
                        # Format harga dan volume
                        display_cols['HARGA'] = display_cols['HARGA'].apply(lambda x: f"{float(x):,.0f}")
                        display_cols['KEMARIN'] = display_cols['KEMARIN'].apply(lambda x: f"{float(x):,.0f}")
                        display_cols['PERUBAHAN %'] = display_cols['PERUBAHAN %'].apply(lambda x: f"{float(x):+.2f}%")
                        display_cols['BID'] = display_cols['BID'].apply(lambda x: f"{int(x):,}")
                        display_cols['OFFER'] = display_cols['OFFER'].apply(lambda x: f"{int(x):,}")
                        display_cols['NET BUY'] = display_cols['NET BUY'].apply(lambda x: f"{int(x):,}")
                        display_cols['NET SELL'] = display_cols['NET SELL'].apply(lambda x: f"{int(x):,}")
                        display_cols['OPEN=LOW'] = display_cols['OPEN=LOW'].apply(lambda x: "YA" if x else "TIDAK")
                        
                        # Render HTML dengan color coding konsisten menggunakan helper function
                        styled_df = format_table_with_colors(display_cols, numeric_data)
                        st.write(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.warning("❌ Tidak ada saham yang sesuai dengan filter yang Anda pilih")
                else:
                    st.error("Gagal mengambil data yFinance")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        elif screening_source == "Stockbit":
            # Stockbit fallback (may have issues)
            st.markdown("""
            <style>
            .stockbit-bold { font-weight: bold !important; font-size: 1.05em !important; }
            .stockbit-small { font-size: 0.93em !important; }
            </style>
            """, unsafe_allow_html=True)
            
            try:
                stockbit = StockbitFetcher(use_cache=False)
                st.info("⚠️ Menampilkan dari Stockbit (mungkin ada data 0 atau tidak lengkap)")
                sb_df = stockbit.fetch_all_stocks_sentiment()
                
                if not sb_df.empty and sb_df['current_price'].sum() > 0:
                    sb_df = sb_df.rename(columns={
                        'symbol': 'SAHAM',
                        'current_price': 'HARGA',
                        'change_pct': 'PERUBAHAN %',
                        'recommendation': 'REKOMENDASI'
                    })
                    
                    sb_df['HARGA'] = sb_df['HARGA'].apply(lambda x: f"Rp {float(x):,.0f}" if x and float(x) > 0 else "-")
                    sb_df['PERUBAHAN %'] = sb_df['PERUBAHAN %'].apply(lambda x: f"{float(x):.2f}%" if x else "-")
                    
                    # Hanya ambil kolom utama
                    display_cols = ['SAHAM', 'HARGA', 'PERUBAHAN %', 'REKOMENDASI']
                    sb_df = sb_df[display_cols]
                    
                    def style_row(row):
                        out = [f'<span class="stockbit-bold">{row["SAHAM"]}</span>']
                        for col in row.index[1:]:
                            v = row[col]
                            if col == 'PERUBAHAN %':
                                try:
                                    s = str(v).strip()
                                    if s == '-' or s == '':
                                        out.append(f'<span class="stockbit-small">{v}</span>')
                                    else:
                                        num = float(s.replace('%', '').replace('+', '').strip())
                                        if str(v).strip().startswith('-'):
                                            num = -abs(num)
                                        pct_color = "#00c77a" if num > 0 else "#ee5a52" if num < 0 else "#E1E8ED"
                                        out.append(f'<span class="stockbit-small" style="color:{pct_color}; font-weight:800;">{v}</span>')
                                except Exception:
                                    out.append(f'<span class="stockbit-small">{v}</span>')
                            else:
                                out.append(f'<span class="stockbit-small">{v}</span>')
                        return out
                    
                    styled = sb_df.apply(style_row, axis=1, result_type='expand')
                    styled.columns = sb_df.columns
                    st.write(styled.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Data Stockbit tidak tersedia atau semua bernilai 0. Gunakan yFinance untuk data yang lebih akurat dan lengkap.")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # ============= TAB 4: ACTION =============
    with tab4:
        st.header("Action & Tools")
        
        # Debug info
        st.markdown("""
        <div style="background-color: #161B22; padding: 12px; border-left: 3px solid #4A8FA8; border-radius: 4px; margin-bottom: 12px;">
        <small>Di tab ini Anda dapat menjalankan screening saham dan generate report</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("Jalankan Screening")
        st.write("Analisis 30+ saham IHSG dan deteksi fase akumulasi/distribusi")
        st.info("Screening memakan waktu 3-5 menit tergantung koneksi internet")
        
        # Initialize session state for screening
        if 'screening_running' not in st.session_state:
            st.session_state.screening_running = False
        
        col1, col2 = st.columns([3, 1])
        with col1:
            start_btn = st_button_stretch("Mulai Screening Sekarang")
            if start_btn:
                st.session_state.screening_running = True
        
        # If button was clicked, run screening
        if st.session_state.screening_running:
            st.warning("**Screening dimulai!** Mohon tunggu, jangan tutup tab ini...")
            run_screening()
            st.session_state.screening_running = False
        
        st.divider()
        
        st.subheader("Generate Report")
        if st_button_stretch("Generate PDF Report"):
            st.info("Feature coming soon! 🔜")
        
        st.divider()
        
        st.subheader("Settings")
        col1, col2 = st.columns(2)
        
        with col1:
            if st_button_stretch("Refresh Data"):
                st.cache_data.clear()
                st.success("✅ Cache cleared! Refresh page untuk melihat hasil terbaru")
                time.sleep(1)
                st.rerun()
        
        with col2:
            if st_button_stretch("Open Data Folder"):
                st.info("✅ Hasil disimpan di: `data/screening_results/`")
    
    # ============= TAB 5: TUTORIAL =============
    with tab5:
        st.header("Tutorial & Bantuan")
        
        st.subheader("Cara Menggunakan Dashboard")
        
        st.markdown("""
        ### Tab 1: Dashboard Utama
        - Lihat ringkasan hasil screening
        - Distribusi fase saham
        - Top 10 saham akumulasi
        - Download hasil
        
        ### Tab 2: Cek Saham
        - Analisis detail 1 saham
        - Chart candlestick 3 bulan
        - Data yFinance atau Stockbit
        - Technical analysis otomatis
        
        ### Tab 3: Hasil Screening
        - Tabel lengkap semua saham
        - Filter per fase & signal
        - Urutkan sesuai kebutuhan
        - Download CSV
        
        ### Tab 4: Action
        - Jalankan screening baru
        - Generate report
        - Refresh data
        - Settings
        
        ### Tab 5: Tutorial
        - Panduan ini
        - FAQ
        - Tips trading
        """)
        
        st.divider()
        
        st.subheader("Interpretasi Hasil")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Akumulasi**
            - Bandar besar membeli
            - Harga < VWAP
            - Volume tinggi
            - **Action**: BUY
            """)
        
        with col2:
            st.markdown("""
            **Distribusi**
            - Bandar besar jual
            - Harga > VWAP
            - Volume tinggi
            - **Action**: SELL/HOLD
            """)
        
        with col3:
            st.markdown("""
            **Absorbing**
            - Pasar konsolidasi
            - Harga ≈ VWAP
            - Volume normal
            - **Action**: WAIT
            """)
        
        st.divider()
        
        st.subheader("Tips Trading")
        
        tips = [
            "Selalu gunakan STOP LOSS untuk manage risiko",
            "Cross-check dengan fundamental analysis",
            "Jangan all-in 1 saham - diversifikasi",
            "Trade dengan money management yang baik",
            "Update data minimal 1x sehari",
            "Jangan blind trust automated system",
            "Hindari trading saat berita besar",
            "Jangan trading dengan capital yang tidak bisa ditanggung",
        ]
        
        for tip in tips:
            st.write(tip)
        
        st.divider()
        
        st.subheader("FAQ")
        
        with st.expander("Berapa lama screening memakan waktu?"):
            st.write("Screening 30+ saham biasanya memakan waktu 2-3 menit tergantung koneksi internet.")
        
        with st.expander("Data dari mana?"):
            st.write("Data diambil dari yFinance (data publik) dan Stockbit API (optional).")
        
        with st.expander("Accuracy berapa persen?"):
            st.write("Ini adalah tools analisis, bukan prediksi 100% akurat. Gunakan sebagai reference saja.")
        
        with st.expander("Bisa trade langsung dari sini?"):
            st.write("Belum bisa. Tools ini hanya untuk analisis. Port ke broker API bisa ditambahkan nanti.")
        
        with st.expander("Data disimpan di mana?"):
            st.write("Semua hasil screening disimpan di folder `data/screening_results/` dalam format CSV.")
    
    with tab6:
        # Initialize session state for portfolio
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = pd.DataFrame({
                'Saham': ['BBCA', 'BBRI', 'BMRI', 'ASII', 'TLKM'],
                'Qty': [100, 250, 150, 300, 200],
                'Avg Price': [9800, 4200, 7500, 4100, 2850],
                'Current Price': [10200, 4350, 7800, 4250, 3050],
                'Invested': [980000, 1050000, 1125000, 1230000, 570000]
            })
        
        # Initialize monthly journal with current year-month
        from datetime import datetime
        current_year_month = datetime.now().strftime("%Y-%m")
        
        if 'current_journal_month' not in st.session_state:
            st.session_state.current_journal_month = current_year_month
        
        # Reset journal if month has changed
        if st.session_state.current_journal_month != current_year_month:
            st.session_state.current_journal_month = current_year_month
            st.session_state.monthly_journal = pd.DataFrame({
                'Tanggal': [],
                'Saham': [],
                'Action': [],
                'Qty': [],
                'Price': [],
                'Current Price': [],
                'Total': [],
                'Profit/Loss': [],
                'Notes': []
            })
        
        if 'monthly_journal' not in st.session_state:
            st.session_state.monthly_journal = pd.DataFrame({
                'Tanggal': [],
                'Saham': [],
                'Action': [],
                'Qty': [],
                'Price': [],
                'Current Price': [],
                'Total': [],
                'Profit/Loss': [],
                'Notes': []
            })
        
        # ===== PORTFOLIO SECTION =====
        st.subheader("Portfolio Saham")
        
        portfolio_df = st.session_state.portfolio.copy()
        portfolio_df['Profit/Loss'] = (portfolio_df['Current Price'] - portfolio_df['Avg Price']) * portfolio_df['Qty'] * 100
        portfolio_df['Return %'] = ((portfolio_df['Current Price'] - portfolio_df['Avg Price']) / portfolio_df['Avg Price'] * 100).round(2)
        
        # Display portfolio table with colors
        portfolio_display = portfolio_df.copy()
        
        # Simpan numeric values untuk coloring
        numeric_data = {
            'Profit/Loss': portfolio_df['Profit/Loss'].values,
            'Return %': portfolio_df['Return %'].values,
        }
        
        portfolio_display['Invested'] = portfolio_display['Invested'].apply(lambda x: f"Rp {x:,.2f}")
        portfolio_display['Profit/Loss'] = portfolio_display['Profit/Loss'].apply(lambda x: f"Rp {x:,.2f}")
        portfolio_display['Return %'] = portfolio_display['Return %'].apply(lambda x: f"{x:+.2f}%")
        
        # Style portfolio table dengan color coding (copy pattern from format_table_with_colors)
        styled_portfolio = portfolio_display.copy()
        for idx, (i, row) in enumerate(styled_portfolio.iterrows()):
            # Bold stock name
            styled_portfolio.at[i, 'Saham'] = f'<span style="font-weight: bold; font-size: 1.05em;">{row["Saham"]}</span>'
            
            # Color code P/L and Return %
            pl = numeric_data['Profit/Loss'][idx]
            ret = numeric_data['Return %'][idx]
            
            pl_color = "#00c77a" if pl > 0 else "#ee5a52" if pl < 0 else "#E1E8ED"
            ret_color = "#00c77a" if ret > 0 else "#ee5a52" if ret < 0 else "#E1E8ED"
            
            styled_portfolio.at[i, 'Profit/Loss'] = f'<span style="color: {pl_color}; font-weight: bold;">{row["Profit/Loss"]}</span>'
            styled_portfolio.at[i, 'Return %'] = f'<span style="color: {ret_color}; font-weight: bold;">{row["Return %"]}</span>'
        
        # Table + Delete panel (right side)
        table_col, delete_col = st.columns([4.6, 1.4])

        with table_col:
            # Render portfolio as compact HTML table (consistent density with Hasil Screening)
            try:
                html_table = "<div class='table-wrap'><table class='compact-table portfolio-table'><thead><tr>" \
                             "<th>SAHAM</th><th>QTY (LOT)</th><th>AVG PRICE</th><th>CURRENT</th><th>INVESTED</th><th>P/L</th><th>RETURN %</th>" \
                             "</tr></thead><tbody>"

                for idx, (i, row) in enumerate(styled_portfolio.iterrows()):
                    saham_code = portfolio_df.iloc[idx]['Saham']
                    avg_price = float(portfolio_df.iloc[idx]['Avg Price'])
                    cur_price = float(portfolio_df.iloc[idx]['Current Price'])
                    pl = float(numeric_data['Profit/Loss'][idx])
                    ret = float(numeric_data['Return %'][idx])

                    pl_color = "#00c77a" if pl > 0 else "#ee5a52" if pl < 0 else "#E1E8ED"
                    ret_color = "#00c77a" if ret > 0 else "#ee5a52" if ret < 0 else "#E1E8ED"

                    html_table += "<tr>" \
                                  f"<td><span style='font-weight:800;'>{saham_code}</span></td>" \
                                  f"<td>{int(row['Qty'])}</td>" \
                                  f"<td>Rp {avg_price:,.2f}</td>" \
                                  f"<td>Rp {cur_price:,.2f}</td>" \
                                  f"<td>{row['Invested']}</td>" \
                                  f"<td><span style='color:{pl_color}; font-weight:800;'>{row['Profit/Loss']}</span></td>" \
                                  f"<td><span style='color:{ret_color}; font-weight:800;'>{row['Return %']}</span></td>" \
                                  "</tr>"

                html_table += "</tbody></table></div>"
                st.markdown(html_table, unsafe_allow_html=True)
            except Exception as e:
                st.warning(f"⚠️ Gagal render tabel compact, fallback ke dataframe. ({e})")
                st_dataframe_stretch(portfolio_display)

        with delete_col:
            st.caption("🗑️ Hapus saham")
            delete_symbol = st.selectbox(
                "Pilih",
                options=list(portfolio_df['Saham'].astype(str).values) if len(portfolio_df) > 0 else [],
                key="delete_symbol_select",
            )
            if delete_symbol and st_button_stretch("Hapus", key="delete_symbol_btn"):
                st.session_state.portfolio = st.session_state.portfolio[
                    st.session_state.portfolio['Saham'] != delete_symbol
                ].reset_index(drop=True)
                st.success(f"✅ {delete_symbol} dihapus!")
                _cloud_autosync("delete")
                _save_local_checkpoint()
                st.rerun()
        
        st.divider()
        
        # Portfolio Summary
        col1, col2, col3 = st.columns([1.2, 2.0, 1.2])
        
        total_invested = portfolio_df['Invested'].sum()
        total_profit_loss = portfolio_df['Profit/Loss'].sum()
        total_return_pct = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        with col1:
            render_stat_card("Total Invested", f"Rp&nbsp;{total_invested:,.0f}")
        
        with col2:
            render_pl_card(
                "Total P/L",
                f"Rp&nbsp;{total_profit_loss:,.2f}",
                float(total_return_pct),
            )
        
        with col3:
            render_stat_card("Num Stocks", f"{len(portfolio_df):,}", align_right=True)
        
        st.divider()
        
        # ===== ADD/EDIT PORTFOLIO =====
        st.subheader("Tambah/Edit Saham (BUY/SELL/HOLD)")

        # Row 1 (more mobile friendly)
        r1c1, r1c2, r1c3 = st.columns([1.6, 1.2, 1.2])
        with r1c1:
            new_saham = st.text_input("Kode Saham", placeholder="e.g., BBCA").upper()
        with r1c2:
            action = st.selectbox("Action", ["BUY", "SELL", "HOLD"])
        with r1c3:
            new_qty = st.number_input("Qty (lot)", step=1, value=1, min_value=1)

        # Row 2 (bottom aligned: Price + buttons inline)
        try:
            r2c1, r2c2, r2c3 = st.columns([1.6, 1.2, 1.2], vertical_alignment="bottom")
        except TypeError:
            r2c1, r2c2, r2c3 = st.columns([1.6, 1.2, 1.2])
        with r2c1:
            if 'fetched_price' not in st.session_state:
                st.session_state.fetched_price = None
            current_display_price = st.session_state.fetched_price if st.session_state.fetched_price else 1000
            new_price = st.number_input("Price (per lembar)", min_value=0, step=100, value=int(current_display_price))
        with r2c2:
            if st_button_stretch("🔄 Fetch Current Price", key="fetch_current_price_btn"):
                if new_saham:
                    try:
                        import yfinance as yf
                        ticker = yf.Ticker(f"{new_saham}.JK")
                        try:
                            fetched = ticker.info.get('currentPrice') or ticker.history(period='1d')['Close'].iloc[-1]
                            st.session_state.fetched_price = int(fetched)
                            st.success(f"✅ Harga {new_saham}: Rp {int(fetched):,.0f}")
                        except:
                            st.warning(f"⚠️ Tidak bisa fetch harga {new_saham}")
                    except:
                        st.error("❌ Error fetching price")
                else:
                    st.warning("⚠️ Masukkan kode saham terlebih dahulu")
        with r2c3:
            if 'transaction_history' not in st.session_state:
                st.session_state.transaction_history = []

            try:
                action_btn1, action_btn2 = st.columns(2, vertical_alignment="bottom")
            except TypeError:
                action_btn1, action_btn2 = st.columns(2)
            with action_btn1:
                if st_button_stretch("✅ Proses", key="add_stock_btn"):
                    if new_saham and new_qty > 0:
                        with st.spinner(f"Processing {action} {new_saham}..."):
                            try:
                                # Fetch current price from API
                                try:
                                    import yfinance as yf
                                    ticker = yf.Ticker(f"{new_saham}.JK")
                                    current_price = ticker.info.get('currentPrice') or ticker.history(period='1d')['Close'].iloc[-1]
                                except:
                                    current_price = None

                                if current_price is None:
                                    st.warning(f"⚠️ Tidak bisa fetch current price untuk {new_saham}, gunakan input manual")
                                    current_price = st.number_input(
                                        f"Masukkan Current Price untuk {new_saham}",
                                        min_value=0,
                                        step=100,
                                        value=1000,
                                        key="manual_current_price",
                                    )

                                # Save state before transaction
                                st.session_state.transaction_history.append({
                                    'portfolio': st.session_state.portfolio.copy(),
                                    'journal': st.session_state.monthly_journal.copy()
                                })

                                # Process berdasarkan action
                                if action == "BUY":
                                    existing_idx = st.session_state.portfolio[st.session_state.portfolio['Saham'] == new_saham].index

                                    # Calculate total cost: qty (lot) x 100 x price
                                    lembar_count = int(new_qty * 100)
                                    transaction_cost = lembar_count * int(new_price)

                                    if len(existing_idx) > 0:
                                        # Top-up existing stock
                                        idx = existing_idx[0]
                                        old_qty = st.session_state.portfolio.at[idx, 'Qty']
                                        old_invested = st.session_state.portfolio.at[idx, 'Invested']

                                        new_total_invested = old_invested + transaction_cost
                                        combined_qty = old_qty + new_qty
                                        new_avg_price = new_total_invested / (combined_qty * 100)

                                        st.session_state.portfolio.at[idx, 'Qty'] = combined_qty
                                        st.session_state.portfolio.at[idx, 'Avg Price'] = int(new_avg_price)
                                        st.session_state.portfolio.at[idx, 'Current Price'] = int(current_price)
                                        st.session_state.portfolio.at[idx, 'Invested'] = new_total_invested

                                        st.success(
                                            f"✅ {new_saham} di-top-up! Qty: {combined_qty} lot ({combined_qty*100} lembar), Avg Price: Rp {new_avg_price:,.2f}"
                                        )
                                    else:
                                        # Add new stock
                                        new_row = pd.DataFrame({
                                            'Saham': [new_saham],
                                            'Qty': [int(new_qty)],
                                            'Avg Price': [int(new_price)],
                                            'Current Price': [int(current_price)],
                                            'Invested': [transaction_cost]
                                        })
                                        st.session_state.portfolio = pd.concat([st.session_state.portfolio, new_row], ignore_index=True)
                                        st.success(f"✅ {new_saham} ditambahkan ke portfolio! ({lembar_count} lembar)")

                                    # Log ke trading journal (qty is in lembar)
                                    new_journal = pd.DataFrame({
                                        'Tanggal': [datetime.now().date()],
                                        'Saham': [new_saham],
                                        'Action': ['BUY'],
                                        'Qty': [lembar_count],
                                        'Price': [int(new_price)],
                                        'Current Price': [int(current_price)],
                                        'Total': [transaction_cost],
                                        'Profit/Loss': [0],
                                        'Notes': ['']
                                    })
                                    st.session_state.monthly_journal = pd.concat([st.session_state.monthly_journal, new_journal], ignore_index=True)

                                elif action == "SELL":
                                    existing_idx = st.session_state.portfolio[st.session_state.portfolio['Saham'] == new_saham].index

                                    # Calculate total cost: qty (lot) x 100 x price
                                    lembar_count = int(new_qty * 100)

                                    if len(existing_idx) == 0:
                                        st.error(f"❌ {new_saham} tidak ada di portfolio!")
                                    else:
                                        idx = existing_idx[0]
                                        old_qty = st.session_state.portfolio.at[idx, 'Qty']
                                        old_avg_price = st.session_state.portfolio.at[idx, 'Avg Price']
                                        old_invested = st.session_state.portfolio.at[idx, 'Invested']

                                        if new_qty > old_qty:
                                            st.error(f"❌ Qty jual ({new_qty} lot = {lembar_count} lembar) melebihi stok ({old_qty} lot)!")
                                        else:
                                            # Calculate P/L for sold quantity
                                            sell_proceeds = lembar_count * int(new_price)
                                            cost_of_sold = lembar_count * old_avg_price
                                            pl = sell_proceeds - cost_of_sold

                                            # Update portfolio
                                            remaining_qty = old_qty - new_qty

                                            if remaining_qty > 0:
                                                st.session_state.portfolio.at[idx, 'Qty'] = remaining_qty
                                                st.session_state.portfolio.at[idx, 'Current Price'] = int(new_price)
                                                st.session_state.portfolio.at[idx, 'Invested'] = old_invested - cost_of_sold
                                                st.success(
                                                    f"✅ {new_saham} dijual sebagian {new_qty} lot ({lembar_count} lembar)! Sisa: {remaining_qty} lot, P/L: Rp {pl:+,.0f}"
                                                )
                                            else:
                                                st.session_state.portfolio = st.session_state.portfolio.drop(idx).reset_index(drop=True)
                                                st.success(f"✅ {new_saham} terjual HABIS! P/L: Rp {pl:+,.0f}")

                                            # Log ke trading journal
                                            new_journal = pd.DataFrame({
                                                'Tanggal': [datetime.now().date()],
                                                'Saham': [new_saham],
                                                'Action': ['SELL'],
                                                'Qty': [lembar_count],
                                                'Price': [int(new_price)],
                                                'Current Price': [int(new_price)],
                                                'Total': [sell_proceeds],
                                                'Profit/Loss': [int(pl)],
                                                'Notes': [f'Avg Beli: Rp {old_avg_price:,.0f}']
                                            })
                                            st.session_state.monthly_journal = pd.concat([st.session_state.monthly_journal, new_journal], ignore_index=True)

                                elif action == "HOLD":
                                    st.info(f"📌 {new_saham} ditandai sebagai HOLD - tidak ada perubahan portfolio")

                                    # Log ke trading journal
                                    new_journal = pd.DataFrame({
                                        'Tanggal': [datetime.now().date()],
                                        'Saham': [new_saham],
                                        'Action': ['HOLD'],
                                        'Qty': [0],
                                        'Price': [int(new_price)],
                                        'Current Price': [int(current_price)],
                                        'Total': [0],
                                        'Profit/Loss': [0],
                                        'Notes': [f'Current Price: Rp {current_price:,.0f}']
                                    })
                                    st.session_state.monthly_journal = pd.concat([st.session_state.monthly_journal, new_journal], ignore_index=True)

                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                                import traceback
                                st.code(traceback.format_exc())
                    else:
                        st.warning("⚠️ Masukkan kode saham dan qty")

            with action_btn2:
                if st_button_stretch("↶ Undo", key="undo_btn", help="Cancel last transaction"):
                    if 'transaction_history' in st.session_state and len(st.session_state.transaction_history) > 0:
                        last_state = st.session_state.transaction_history.pop()
                        st.session_state.portfolio = last_state['portfolio']
                        st.session_state.monthly_journal = last_state['journal']
                        st.success("✅ Transaction undone!")
                        _cloud_autosync("undo")
                        _save_local_checkpoint()
                        st.rerun()
                    else:
                        st.warning("⚠️ Tidak ada transaksi untuk di-undo")
        
        st.divider()
        
        # Display Monthly Journal
        current_month_display = datetime.now().strftime("%B %Y")

        title_col, print_col = st.columns([8, 1.2])
        with title_col:
            st.subheader(f"Daftar Trade - {current_month_display}")
        with print_col:
            if st.button("🖨️ Print", key="print_journal_btn"):
                st.success("✅ Siap untuk print - Gunakan Ctrl+P atau Cmd+P")
        
        if not st.session_state.monthly_journal.empty:
            # Format journal dengan P/L dan percentage calculation
            journal_display = format_journal_with_colors(st.session_state.monthly_journal.copy())
            
            # Display as HTML untuk styling yang lebih baik
            html_table = "<div class='table-wrap'><table class='compact-table'><thead><tr>"
            for col in journal_display.columns:
                html_table += f"<th>{col}</th>"
            html_table += "</tr></thead><tbody>"
            
            for _, row in journal_display.iterrows():
                html_table += "<tr>"
                for col in journal_display.columns:
                    html_table += f"<td>{row[col]}</td>"
                html_table += "</tr>"
            
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            
            # Monthly Summary - Calculated from journal transactions
            st.markdown("---")
            st.markdown("**Monthly Trading Performance**")
            
            # Calculate from journal with proper P/L and Return % calculation
            journal_data = st.session_state.monthly_journal.copy()
            
            # Calculate Monthly P/L (sum of unrealized P/L for open positions and realized P/L for closed)
            monthly_pnl = 0
            total_return_pct = 0.0
            
            for _, row in journal_data.iterrows():
                price = row['Price']
                current_price = row['Current Price']
                qty_lembar = row['Qty']  # Qty is in lembar
                action = row['Action']
                
                if action in ['BUY', 'HOLD']:
                    # Unrealized P/L: (Current Price - Price) × Qty
                    pl_value = (current_price - price) * qty_lembar
                    return_pct = ((current_price - price) / price * 100) if price > 0 else 0.00
                else:  # SELL
                    # Realized P/L from Profit/Loss column
                    pl_value = row['Profit/Loss']
                    return_pct = (row['Profit/Loss'] / (row['Price'] * qty_lembar) * 100) if (row['Price'] * qty_lembar) > 0 else 0.00
                
                monthly_pnl += pl_value
                total_return_pct += return_pct
            
            total_trades = len(journal_data)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Holdings", len(portfolio_df), "stocks")
            with col2:
                per_trade_return = (total_return_pct)/total_trades if total_trades > 0 else 0
                render_pl_card(
                    "Winning (per trade)",
                    f"{per_trade_return:+.2f}%",
                    float(total_return_pct),
                )
            with col3:
                render_pl_value_card(
                    "Monthly P/L",
                    f"Rp&nbsp;{monthly_pnl:+,.2f}",
                    float(monthly_pnl),
                )
        else:
            st.info("Belum ada trade tercatat bulan ini. Mulai catat trade Anda!")

if __name__ == "__main__":
    main()
    
    # Footer
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; color: #888; font-size: 0.85rem; margin-top: 20px;'>
        <p>Developed by <strong>Donny Takeshi</strong></p>
        <p>© 2026 - All Rights Reserved</p>
        <p style='font-size: 0.75rem; margin-top: 10px;'>
        ⚠️ Disclaimer: Tools ini untuk educational & analysis purposes saja. 
        Bukan financial advice. Trade with caution!
        </p>
        </div>
        """, unsafe_allow_html=True)

