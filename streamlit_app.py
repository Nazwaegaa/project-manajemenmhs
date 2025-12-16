import streamlit as st
import json
import os

DB_FILE = "students_db.json"

# =============================
# LOGIN DATA
# =============================
USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "operator": {"password": "op123", "role": "OPERATOR"},
    "viewer": {"password": "view123", "role": "VIEWER"}
}

# =============================
# DATABASE
# =============================
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def clean_data(data):
    return [
        d for d in data
        if d.get("nim") and d.get("name")
    ]

# reset database pertama kali
if not os.path.exists(DB_FILE):
    save_data([])

# =============================
# SORTING ALGORITHMS
# =============================
def bubble_sort(data, key, reverse=False):
    arr = data[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if (arr[j][key] > arr[j + 1][key]) ^ reverse:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
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

    mid = len(data) // 2
    left = merge_sort(data[:mid], key, reverse)
    right = merge_sort(data[mid:], key, reverse)

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if (left[i][key] <= right[j][key]) ^ reverse:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result

# =============================
# LOGIN PAGE
# =============================
def login_page():
    st.title("🔐 Login Sistem")

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
    st.title("🎓 Manajemen Data Mahasiswa")
    st.caption(f"Role: {st.session_state.role}")

    data = clean_data(load_data())

    total = len(data)
    avg = round(sum(d["ipk"] for d in data) / total, 2) if total else 0

    c1, c2 = st.columns(2)
    c1.metric("Total Mahasiswa", total)
    c2.metric("Rata-rata IPK", avg)

    st.divider()

    # =============================
    # SEARCH & SORT
    # =============================
    st.subheader("🔍 Pencarian & Sorting")

    c1, c2, c3 = st.columns(3)

    with c1:
        search_field = st.selectbox("Cari berdasarkan", ["nim", "name", "major", "ipk"])
        search_value = st.text_input("Keyword")

    with c2:
        sort_algo = st.selectbox("Metode Sorting", ["Bubble Sort", "Shell Sort", "Merge Sort"])
        sort_field = st.selectbox("Field", ["nim", "name", "major", "ipk"])

    with c3:
        order = st.radio("Urutan", ["Ascending", "Descending"], horizontal=True)

    # SEARCH
    filtered = data
    if search_value:
        if search_field == "ipk":
            try:
                filtered = [d for d in filtered if d["ipk"] == float(search_value)]
            except:
                filtered = []
        else:
            filtered = [d for d in filtered if search_value.lower() in d[search_field].lower()]

    reverse = order == "Descending"

    # SORT
    if sort_algo == "Bubble Sort":
        filtered = bubble_sort(filtered, sort_field, reverse)
    elif sort_algo == "Shell Sort":
        filtered = shell_sort(filtered, sort_field, reverse)
    else:
        filtered = merge_sort(filtered, sort_field, reverse)

    st.divider()

    # =============================
    # SELECT DATA
    # =============================
    selected = None
    if filtered:
        selected = st.selectbox(
            "Klik mahasiswa untuk Edit/Hapus",
            filtered,
            format_func=lambda x: f"{x['nim']} - {x['name']}"
        )
    else:
        st.info("Data tidak ditemukan")

    # =============================
    # FORM
    # =============================
    st.subheader("📝 Form Mahasiswa")

    nim = st.text_input("NIM", value=selected["nim"] if selected else "")
    name = st.text_input("Nama", value=selected["name"] if selected else "")
    major = st.text_input("Jurusan", value=selected["major"] if selected else "")
    ipk = st.number_input("IPK", 0.0, 4.0, step=0.01,
                          value=selected["ipk"] if selected else 0.0)

    b1, b2, b3 = st.columns(3)

    # TAMBAH
    with b1:
        if st.button("➕ Tambah"):
            if not nim.strip() or not name.strip():
                st.error("NIM & Nama wajib diisi")
            elif any(d["nim"] == nim for d in data):
                st.error("NIM sudah ada")
            else:
                data.append({"nim": nim, "name": name, "major": major, "ipk": ipk})
                save_data(data)
                st.success("Data ditambahkan")
                st.rerun()

    # EDIT
    with b2:
        if st.button("✏️ Edit"):
            if not selected:
                st.error("Pilih data dulu")
            else:
                for d in data:
                    if d["nim"] == selected["nim"]:
                        d.update({"nim": nim, "name": name, "major": major, "ipk": ipk})
                        break
                save_data(data)
                st.success("Data diperbarui")
                st.rerun()

    # HAPUS
    with b3:
        if st.button("🗑️ Hapus"):
            if not selected:
                st.error("Pilih data dulu")
            else:
                data = [d for d in data if d["nim"] != selected["nim"]]
                save_data(data)
                st.warning("Data dihapus")
                st.rerun()

    st.divider()
    st.subheader("📊 Tabel Mahasiswa")
    st.dataframe(filtered, use_container_width=True)

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =============================
# ROUTING
# =============================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    login_page()
else:
    main_app()
