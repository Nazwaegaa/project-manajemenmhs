import streamlit as st
import json
import os

# =============================
# PAGE CONFIG (AMAN)
# =============================
st.set_page_config(
    page_title="Arsip Mahasiswa",
    page_icon="🜂",
    layout="wide"
)

# =============================
# SAFE GLOSSY GOLD STYLE
# =============================
st.markdown("""
<style>
body {
    background: linear-gradient(180deg,#1a1500,#0b0b0b);
    color: #ffe9a3;
}
h1,h2,h3 {
    color: #ffd966;
}
[data-testid="metric-container"] {
    background: #151100;
    border: 1px solid #6f5b00;
    border-radius: 14px;
    padding: 12px;
}
.stButton>button {
    background: linear-gradient(135deg,#ffd966,#c9a300);
    color: black;
    border-radius: 12px;
    font-weight: 600;
}
.stButton>button:hover {
    box-shadow: 0 0 15px rgba(255,217,102,0.6);
}
.stDataFrame {
    background-color: #0e0e0e;
}
</style>
""", unsafe_allow_html=True)

# =============================
# DATABASE
# =============================
DB_FILE = "students_db.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def clean_data(data):
    return [d for d in data if d.get("nim") and d.get("name")]

if not os.path.exists(DB_FILE):
    save_data([])

# =============================
# SORTING
# =============================
def bubble_sort(data, key, reverse=False):
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if (arr[j][key] > arr[j+1][key]) ^ reverse:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def shell_sort(data, key, reverse=False):
    arr = data[:]
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
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
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if (left[i][key] <= right[j][key]) ^ reverse:
            result.append(left[i]); i+=1
        else:
            result.append(right[j]); j+=1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# =============================
# LOGIN
# =============================
USERS = {
    "admin": "admin123",
    "operator": "op123",
    "viewer": "view123"
}

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🜂 Portal Akademika")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("⟡ Autentikasi"):
        if u in USERS and USERS[u] == p:
            st.session_state.login = True
            st.rerun()
        else:
            st.error("Akses ditolak")
    st.stop()

# =============================
# MAIN APP
# =============================
st.title("🜁 Arsip Mahasiswa Akademika")

data = clean_data(load_data())

total = len(data)
avg_ipk = round(sum(d["ipk"] for d in data) / total, 2) if total else 0

c1, c2 = st.columns(2)
c1.metric("Total Entitas", total)
c2.metric("Rata-rata IPK", avg_ipk)

st.divider()

# =============================
# SEARCH & SORT
# =============================
st.subheader("🜃 Seleksi Dataset")

c1, c2, c3 = st.columns(3)

with c1:
    search_field = st.selectbox("Field", ["nim","name","major","ipk"])
    keyword = st.text_input("Kata kunci")

with c2:
    algo = st.selectbox("Algoritma", ["Bubble","Shell","Merge"])
    sort_field = st.selectbox("Urutkan berdasarkan", ["nim","name","major","ipk"])

with c3:
    order = st.radio("Arah", ["Ascending","Descending"], horizontal=True)

filtered = data
if keyword:
    if search_field == "ipk":
        try:
            filtered = [d for d in filtered if d["ipk"] == float(keyword)]
        except:
            filtered = []
    else:
        filtered = [d for d in filtered if keyword.lower() in d[search_field].lower()]

reverse = order == "Descending"

if algo == "Bubble":
    filtered = bubble_sort(filtered, sort_field, reverse)
elif algo == "Shell":
    filtered = shell_sort(filtered, sort_field, reverse)
else:
    filtered = merge_sort(filtered, sort_field, reverse)

st.divider()

# =============================
# SELECT ROW (AMAN)
# =============================
selected_nim = st.selectbox(
    "Pilih Mahasiswa",
    [""] + [d["nim"] for d in filtered]
)

selected = next((d for d in data if d["nim"] == selected_nim), None)

# =============================
# FORM
# =============================
st.subheader("🜄 Form Entri")

nim = st.text_input("NIM", value=selected["nim"] if selected else "")
name = st.text_input("Nama", value=selected["name"] if selected else "")
major = st.text_input("Jurusan", value=selected["major"] if selected else "")
ipk = st.number_input("IPK", 0.0, 4.0, value=selected["ipk"] if selected else 0.0)

b1, b2, b3 = st.columns(3)

with b1:
    if st.button("⟡ Tambah"):
        if not nim or not name:
            st.error("NIM & Nama wajib")
        elif any(d["nim"] == nim for d in data):
            st.error("NIM sudah ada")
        else:
            data.append({"nim":nim,"name":name,"major":major,"ipk":ipk})
            save_data(data)
            st.success("Data masuk")
            st.rerun()

with b2:
    if st.button("⟡ Edit"):
        if not selected:
            st.error("Pilih data")
        else:
            for d in data:
                if d["nim"] == selected["nim"]:
                    d.update({"nim":nim,"name":name,"major":major,"ipk":ipk})
            save_data(data)
            st.success("Data diubah")
            st.rerun()

with b3:
    if st.button("⟡ Hapus"):
        if selected:
            data = [d for d in data if d["nim"] != selected["nim"]]
            save_data(data)
            st.warning("Data dihapus")
            st.rerun()

st.divider()
st.subheader("🜏 Tabel Dataset")
st.dataframe(filtered, use_container_width=True)

if st.button("⟡ Terminasi Sesi"):
    st.session_state.clear()
    st.rerun()
