import streamlit as st
import json
import os

DB_FILE = "students_db.json"

USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "operator": {"password": "op123", "role": "OPERATOR"},
    "viewer": {"password": "view123", "role": "VIEWER"}
}

# =============================
# DATABASE UTILS
# =============================
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# PAKSA DATABASE KOSONG SAAT PERTAMA
if not os.path.exists(DB_FILE):
    save_data([])

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
            st.error("Login gagal")

# =============================
# MAIN APP
# =============================
def main_app():
    st.title("🎓 Manajemen Data Mahasiswa")
    st.caption(f"Role: {st.session_state.role}")

    data = load_data()

    # ===== STAT =====
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

    s_col1, s_col2, s_col3 = st.columns(3)

    with s_col1:
        search_field = st.selectbox(
            "Cari berdasarkan",
            ["nim", "name", "major", "ipk"]
        )

    with s_col2:
        search_value = st.text_input("Kata kunci")

    with s_col3:
        sort_field = st.selectbox(
            "Urutkan berdasarkan",
            ["nim", "name", "major", "ipk"]
        )

    asc = st.radio("Urutan", ["Ascending", "Descending"], horizontal=True)

    # ===== FILTER DATA =====
    filtered = data
    if search_value:
        if search_field == "ipk":
            try:
                filtered = [
                    d for d in filtered
                    if float(search_value) == d["ipk"]
                ]
            except:
                filtered = []
        else:
            filtered = [
                d for d in filtered
                if search_value.lower() in d[search_field].lower()
            ]

    # ===== SORT DATA =====
    reverse = asc == "Descending"
    filtered = sorted(filtered, key=lambda x: x[sort_field], reverse=reverse)

    st.divider()

    # =============================
    # SELECT DATA (EDIT VIA KLIK)
    # =============================
    st.subheader("📋 Pilih Data")

    selected = None
    if filtered:
        selected = st.selectbox(
            "Klik mahasiswa",
            filtered,
            format_func=lambda x: f"{x['nim']} - {x['name']}"
        )
    else:
        st.info("Data tidak ditemukan")

    # =============================
    # FORM INPUT
    # =============================
    st.subheader("📝 Form Mahasiswa")

    nim = st.text_input("NIM", value=selected["nim"] if selected else "")
    name = st.text_input("Nama", value=selected["name"] if selected else "")
    major = st.text_input("Jurusan", value=selected["major"] if selected else "")
    ipk = st.number_input(
        "IPK", 0.0, 4.0, step=0.01,
        value=selected["ipk"] if selected else 0.0
    )

    b1, b2, b3 = st.columns(3)

    # =============================
    # TAMBAH
    # =============================
    with b1:
        if st.button("➕ Tambah"):
            if not nim or not name:
                st.error("NIM & Nama wajib diisi")
            elif any(d["nim"] == nim for d in data):
                st.error("NIM sudah terdaftar")
            else:
                data.append({
                    "nim": nim,
                    "name": name,
                    "major": major,
                    "ipk": ipk
                })
                save_data(data)
                st.success("Data berhasil ditambahkan")
                st.rerun()

    # =============================
    # EDIT
    # =============================
    with b2:
        if st.button("✏️ Edit"):
            if not selected:
                st.error("Pilih data dulu")
            else:
                for d in data:
                    if d["nim"] == selected["nim"]:
                        d["nim"] = nim
                        d["name"] = name
                        d["major"] = major
                        d["ipk"] = ipk
                        break
                save_data(data)
                st.success("Data berhasil diupdate")
                st.rerun()

    # =============================
    # HAPUS
    # =============================
    with b3:
        if st.button("🗑️ Hapus"):
            if not selected:
                st.error("Pilih data dulu")
            else:
                data = [d for d in data if d["nim"] != selected["nim"]]
                save_data(data)
                st.warning("Data dihapus")
                st.rerun()

    # =============================
    # TABLE VIEW
    # =============================
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
