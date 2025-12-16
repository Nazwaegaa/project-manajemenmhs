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
# DATA UTILS
# =============================
def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# =============================
# LOGIN
# =============================
def login_page():
    st.title("🔐 Login Manajemen Mahasiswa")

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

    data = load_data()

    # ===== STATS =====
    total = len(data)
    avg = round(sum(d["ipk"] for d in data) / total, 2) if total else 0
    c1, c2 = st.columns(2)
    c1.metric("Total Mahasiswa", total)
    c2.metric("Rata-rata IPK", avg)

    st.divider()

    # ===== PILIH DATA =====
    st.subheader("📋 Data Mahasiswa")

    if data:
        selected = st.selectbox(
            "Klik untuk pilih mahasiswa (edit / hapus)",
            options=data,
            format_func=lambda x: f"{x['nim']} - {x['name']}"
        )
    else:
        selected = None
        st.info("Belum ada data mahasiswa")

    # ===== FORM =====
    st.subheader("📝 Form Mahasiswa")

    nim = st.text_input("NIM", value=selected["nim"] if selected else "")
    name = st.text_input("Nama", value=selected["name"] if selected else "")
    major = st.text_input("Jurusan", value=selected["major"] if selected else "")
    ipk = st.number_input(
        "IPK", 0.0, 4.0, step=0.01,
        value=selected["ipk"] if selected else 0.0
    )

    b1, b2, b3 = st.columns(3)

    # ===== TAMBAH =====
    with b1:
        if st.button("➕ Tambah"):
            if not nim or not name:
                st.error("NIM dan Nama wajib diisi")
            elif any(d["nim"] == nim for d in data):
                st.error("NIM sudah ada")
            else:
                data.append({
                    "nim": nim,
                    "name": name,
                    "major": major,
                    "ipk": ipk
                })
                save_data(data)
                st.success("Data ditambahkan")
                st.rerun()

    # ===== EDIT =====
    with b2:
        if st.button("✏️ Edit"):
            if not selected:
                st.error("Pilih data dari tabel dulu")
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

    # ===== HAPUS =====
    with b3:
        if st.button("🗑️ Hapus"):
            if not selected:
                st.error("Pilih data dulu")
            else:
                data = [d for d in data if d["nim"] != selected["nim"]]
                save_data(data)
                st.warning("Data dihapus")
                st.rerun()

    # ===== TABLE VIEW =====
    st.divider()
    st.dataframe(data, use_container_width=True)

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =============================
# ROUTER
# =============================
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    login_page()
else:
    main_app()
