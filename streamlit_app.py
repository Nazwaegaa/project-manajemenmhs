import streamlit as st
import json
import os
from copy import deepcopy

# =============================
# CONFIG
# =============================
DB_FILE = "students_db.json"

USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "operator": {"password": "op123", "role": "OPERATOR"},
    "viewer": {"password": "view123", "role": "VIEWER"}
}

# =============================
# DATA UTILITIES
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
# SORTING ALGORITHMS
# =============================
def bubble_sort(data, key):
    arr = data[:]
    for i in range(len(arr)):
        for j in range(len(arr)-i-1):
            if arr[j][key] > arr[j+1][key]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def insertion_sort(data, key):
    arr = data[:]
    for i in range(1, len(arr)):
        cur = arr[i]
        j = i-1
        while j >= 0 and arr[j][key] > cur[key]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = cur
    return arr

def selection_sort(data, key):
    arr = data[:]
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[j][key] < arr[min_idx][key]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr

def merge_sort(data, key):
    if len(data) <= 1:
        return data
    mid = len(data)//2
    left = merge_sort(data[:mid], key)
    right = merge_sort(data[mid:], key)
    return merge(left, right, key)

def merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def shell_sort(data, key):
    arr = data[:]
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j-gap][key] > temp[key]:
                arr[j] = arr[j-gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr

# =============================
# LOGIN PAGE
# =============================
def login_page():
    st.title("🔐 Login Manajemen Mahasiswa")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Masuk"):
        if user in USERS and USERS[user]["password"] == pwd:
            st.session_state.login = True
            st.session_state.role = USERS[user]["role"]
            st.success("Login berhasil")
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

    # ---------- STATS ----------
    total = len(data)
    avg_ipk = round(sum(d["ipk"] for d in data) / total, 2) if total else 0
    c1, c2 = st.columns(2)
    c1.metric("Total Mahasiswa", total)
    c2.metric("Rata-rata IPK", avg_ipk)

    st.divider()

    # ---------- FORM ----------
    st.subheader("📝 Form Mahasiswa")

    old_nim = st.text_input("NIM Lama (untuk EDIT)")
    nim = st.text_input("NIM Baru")
    name = st.text_input("Nama")
    major = st.text_input("Jurusan")
    ipk = st.number_input("IPK", 0.0, 4.0, step=0.01)

    b1, b2, b3 = st.columns(3)

    # ---- TAMBAH ----
    with b1:
        if st.button("➕ Tambah"):
            if any(d["nim"] == nim for d in data):
                st.error("NIM sudah ada")
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

    # ---- EDIT ----
    with b2:
        if st.button("✏️ Edit"):
            found = False
            for d in data:
                if d["nim"] == old_nim:
                    d["nim"] = nim
                    d["name"] = name
                    d["major"] = major
                    d["ipk"] = ipk
                    found = True
                    break
            if found:
                save_data(data)
                st.success("Data berhasil diupdate")
                st.rerun()
            else:
                st.error("NIM lama tidak ditemukan")

    # ---- HAPUS ----
    with b3:
        if st.button("🗑️ Hapus"):
            new_data = [d for d in data if d["nim"] != nim]
            if len(new_data) == len(data):
                st.error("NIM tidak ditemukan")
            else:
                save_data(new_data)
                st.warning("Data berhasil dihapus")
                st.rerun()

    st.divider()

    # ---------- SEARCH ----------
    st.subheader("🔍 Pencarian")
    keyword = st.text_input("Cari (NIM / Nama / Jurusan)")

    filtered = deepcopy(data)
    if keyword:
        filtered = [
            d for d in filtered
            if keyword.lower() in d["nim"].lower()
            or keyword.lower() in d["name"].lower()
            or keyword.lower() in d["major"].lower()
        ]

    # ---------- SORT ----------
    st.subheader("↕ Sorting")
    method = st.selectbox("Metode", ["Bubble", "Insertion", "Selection", "Merge", "Shell"])

    if st.button("Apply Sorting"):
        if method == "Bubble":
            filtered = bubble_sort(filtered, "name")
        elif method == "Insertion":
            filtered = insertion_sort(filtered, "name")
        elif method == "Selection":
            filtered = selection_sort(filtered, "name")
        elif method == "Merge":
            filtered = merge_sort(filtered, "name")
        elif method == "Shell":
            filtered = shell_sort(filtered, "name")

    # ---------- TABLE ----------
    st.subheader("📋 Data Mahasiswa")
    st.dataframe(filtered, use_container_width=True)

    # ---------- LOGOUT ----------
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
