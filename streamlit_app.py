import streamlit as st
import json, os, time
import pandas as pd

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Manajemen Data Mahasiswa", layout="wide")
DB_FILE = "students_db.json"

USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "operator": {"password": "op123", "role": "OPERATOR"},
    "viewer": {"password": "view123", "role": "VIEWER"},
}

# =============================
# CSS – YELLOW THEME, BLACK FONT
# =============================
st.markdown("""
<style>
html, body, [data-testid="stApp"] {
    background: linear-gradient(180deg, #fffef8, #fff2b3);
    color: #000000 !important;
    font-family: "Segoe UI", "Inter", sans-serif;
}
h1,h2,h3,h4,h5,h6,p,span,label,div {
    color: #000000 !important;
}
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #fff9d6, #ffe88a);
    border-radius: 18px;
    border: 1px solid #e6c94a;
    box-shadow: 0 8px 20px rgba(255,204,0,0.35);
}
input, textarea {
    background-color: #fffdf5 !important;
    border-radius: 12px !important;
    border: 1px solid #e6c94a !important;
    color: #000000 !important;
}
[data-baseweb="select"] > div,
[data-baseweb="input"] > div {
    background-color: #fffdf5 !important;
    border-radius: 12px;
    border: 1px solid #e6c94a;
    color: #000000 !important;
}
.stButton>button {
    background: linear-gradient(135deg, #ffe066, #ffcc00);
    color: #000000 !important;
    border-radius: 16px;
    font-weight: 700;
    border: none;
    box-shadow: 0 6px 14px rgba(255,193,7,0.45);
}
.stButton>button:hover {
    transform: scale(1.03);
}
[data-testid="stDataFrame"] {
    background-color: #fffdf5;
    border-radius: 16px;
    border: 1px solid #e6c94a;
}
thead tr th {
    background-color: #ffe066 !important;
    color: #000000 !important;
    font-weight: 800;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff9d6, #ffe88a);
    border-right: 1px solid #e6c94a;
}
hr {
    border: 1px solid #e6c94a;
}
</style>
""", unsafe_allow_html=True)

# =============================
# SESSION STATE
# =============================
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = ""

# =============================
# DATABASE
# =============================
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    return [d for d in data if d.get("nim")]

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

if not os.path.exists(DB_FILE):
    save_data([])

# =============================
# SORTING
# =============================
def bubble_sort(data, key, reverse=False):
    arr = data[:]
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if (arr[j][key] > arr[j+1][key]) ^ reverse:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def shell_sort(data, key, reverse=False):
    arr = data[:]
    gap = len(arr)//2
    while gap > 0:
        for i in range(gap, len(arr)):
            temp = arr[i]
            j = i
            while j >= gap and ((arr[j-gap][key] > temp[key]) ^ reverse):
                arr[j] = arr[j-gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr

def merge_sort(data, key, reverse=False):
    if len(data) <= 1:
        return data
    mid = len(data)//2
    left = merge_sort(data[:mid], key, reverse)
    right = merge_sort(data[mid:], key, reverse)
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if (left[i][key] <= right[j][key]) ^ reverse:
            res.append(left[i]); i+=1
        else:
            res.append(right[j]); j+=1
    res.extend(left[i:])
    res.extend(right[j:])
    return res

# =============================
# LOGIN PAGE
# =============================
def login_page():
    st.title("🔐 Login Sistem Akademik")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Masuk"):
        if u in USERS and USERS[u]["password"] == p:
            st.session_state.login = True
            st.session_state.role = USERS[u]["role"]
            st.rerun()
        else:
            st.error("Username atau password salah")

# =============================
# MAIN APP
# =============================
def main_app():
    with st.sidebar:
        st.markdown("## ⚙️ Control Panel")
        st.caption(f"Role: **{st.session_state.role}**")

    st.title("🎓 Manajemen Data Mahasiswa")

    data = load_data()

    c1, c2 = st.columns(2)
    c1.metric("Total Mahasiswa", len(data))
    c2.metric("Rata-rata IPK", round(sum(d["ipk"] for d in data)/len(data),2) if data else 0)

    st.divider()

    # SEARCH & SORT
    s1, s2, s3 = st.columns(3)
    search_field = s1.selectbox("Cari berdasarkan", ["nim","name","major"])
    keyword = s1.text_input("Keyword")

    sort_algo = s2.selectbox("Metode Sorting", ["Bubble","Shell","Merge"])
    sort_field = s2.selectbox("Field", ["nim","name","major","ipk"])

    order = s3.radio("Urutan", ["Ascending","Descending"], horizontal=True)

    filtered = data
    if keyword:
        filtered = [d for d in filtered if keyword.lower() in str(d[search_field]).lower()]

    min_ipk, max_ipk = st.slider("Filter IPK", 0.0, 4.0, (0.0,4.0), 0.01)
    filtered = [d for d in filtered if min_ipk <= d["ipk"] <= max_ipk]

    reverse = order == "Descending"
    start = time.time()
    if sort_algo == "Bubble":
        filtered = bubble_sort(filtered, sort_field, reverse)
    elif sort_algo == "Shell":
        filtered = shell_sort(filtered, sort_field, reverse)
    else:
        filtered = merge_sort(filtered, sort_field, reverse)
    st.caption(f"⏱️ Waktu sorting: {round(time.time()-start,5)} detik")

    st.divider()

    # FORM
    selected = st.selectbox(
        "Pilih Mahasiswa (untuk Edit / Hapus)",
        filtered,
        format_func=lambda x: f"{x['nim']} - {x['name']}"
    ) if filtered else None

    nim = st.text_input("NIM", selected["nim"] if selected else "")
    name = st.text_input("Nama", selected["name"] if selected else "")
    major = st.text_input("Jurusan", selected["major"] if selected else "")
    ipk = st.number_input("IPK", 0.0, 4.0, step=0.01,
                          value=selected["ipk"] if selected else 0.0)

    if st.session_state.role != "VIEWER":
        b1, b2, b3 = st.columns(3)

        if b1.button("➕ Tambah"):
            if len(nim) != 12 or not nim.isdigit():
                st.error("NIM harus 12 digit angka")
            elif any(d["nim"] == nim for d in data):
                st.error("NIM sudah terdaftar")
            else:
                data.append({"nim":nim,"name":name,"major":major,"ipk":ipk})
                save_data(data)
                st.rerun()

        if b2.button("✏️ Edit") and selected:
            for d in data:
                if d["nim"] == selected["nim"]:
                    d.update({"nim":nim,"name":name,"major":major,"ipk":ipk})
            save_data(data)
            st.rerun()

        if b3.button("🗑️ Hapus") and selected:
            save_data([d for d in data if d["nim"] != selected["nim"]])
            st.rerun()

    st.divider()

    df = pd.DataFrame(filtered)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "⬇️ Export CSV",
        df.to_csv(index=False),
        "mahasiswa.csv",
        "text/csv"
    )

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =============================
# ROUTING
# =============================
if not st.session_state.login:
    login_page()
else:
    main_app()
