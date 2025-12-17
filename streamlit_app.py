st.set_page_config(
    page_title="Manajemen Mahasiswa",
    page_icon="🜂",
    layout="wide"
)

st.markdown("""
<style>
/* ===== GLOBAL ===== */
html, body, [class*="css"] {
    background: radial-gradient(circle at top, #2b2400, #0f0f0f);
    color: #f7e7a9;
    font-family: 'Segoe UI', sans-serif;
}

/* ===== TITLE ===== */
h1, h2, h3 {
    color: #ffd95a !important;
    letter-spacing: 0.5px;
}

/* ===== CARD EFFECT ===== */
.block-container {
    padding-top: 2rem;
}

/* ===== INPUT ===== */
input, textarea {
    background-color: #1b1b1b !important;
    color: #ffe58a !important;
    border-radius: 12px !important;
    border: 1px solid #5c4b00 !important;
}

/* ===== BUTTON ===== */
button {
    background: linear-gradient(135deg, #ffd95a, #c9a300) !important;
    color: #1b1b1b !important;
    border-radius: 14px !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: 0 0 18px rgba(255,217,90,0.4);
}
button:hover {
    transform: scale(1.03);
    box-shadow: 0 0 25px rgba(255,217,90,0.7);
}

/* ===== METRIC ===== */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #1c1c1c, #0e0e0e);
    border: 1px solid #7a6400;
    border-radius: 18px;
    padding: 15px;
    box-shadow: inset 0 0 10px rgba(255,217,90,0.15);
}

/* ===== TABLE ===== */
thead tr th {
    background-color: #3a2f00 !important;
    color: #ffe58a !important;
}
tbody tr td {
    background-color: #121212 !important;
    color: #f7e7a9 !important;
}

/* ===== DIVIDER ===== */
hr {
    border-top: 1px solid #5c4b00;
}
</style>
""", unsafe_allow_html=True)
