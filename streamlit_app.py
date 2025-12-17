import streamlit as st
import json, os, time
import pandas as pd

# =============================
# CONFIG
# =============================
DB_FILE = "students_db.json"

USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "operator": {"password": "op123", "role": "OPERATOR"},
    "viewer": {"password": "view123", "role": "VIEWER"},
}

# =============================
# INIT STATE
# =============================
if "login" not in st.session_state:
    st.session_state.login = False
if "role" not in st.session_state:
    st.session_state.role = ""
if "theme" not in st.session_state:
    st.session_state.theme = "light"

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
# THEMES
# =============================
LIGHT = """
<style>
html, body, [data-testid="stApp"] {
background: linear-gradient(180deg,#fffdf5,#fff3c4);
color:#3a2f00;
}
h1,h2,h3{color:#b89000;}
.stButton>button{
background:linear-gradient(135deg,#ffe58a,#f1c232);
border-radius:16px;font-weight:700;
}
[data-testid="metric-container"]{
background:linear-gradient(145deg,#fff6d8,#ffeaa0);
border-radius:18px;
}
thead tr th{background:#ffe58a!important;}
</style>
"""

DARK = """
<style>
html, body, [data-testid="stApp"] {
background:linear-gradient(180deg,#1a1500,#000);
color:#ffe9a3;
}
h1,h2,h3{color:#ffd966;}
.stButton>button{
background:linear-gradient(135deg,#ffd966,#c9a300);
border-radius:16px;font-weight:700;
}
[data-testid="metric-container"]{
background:#151100;border-radius:18px;
}
thead tr th{background:#3a2f00!important;color:#ffe9a3!important;}
</style>
"""

st.markdown(LIGHT if st.session_state.theme=="light" else DARK, unsafe_allow_html=True)

# =============================
# LOGIN
# =============================
def login():
    st.title("🔐 Sistem Akademik")
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
# APP
# =============================
def app():
    with st.sidebar:
        st.markdown("## ⚙️ Control Center")
        if st.toggle("☼ / ☾ Mode"):
            st.session_state.theme = "dark" if st.session_state.theme=="light" else "light"
            st.rerun()
        st.caption(f"Role: **{st.session_state.role}**")

    st.title("🎓 Manajemen Data Mahasiswa")

    data = load_data()

    c1,c2 = st.columns(2)
    c1.metric("Total Mahasiswa", len(data))
    c2.metric("Rata-rata IPK", round(sum(d["ipk"] for d in data)/len(data),2) if data else 0)

    st.divider()

    # SEARCH & SORT
    s1,s2,s3 = st.columns(3)
    field = s1.selectbox("Cari", ["nim","name","major"])
    keyword = s1.text_input("Keyword")

    algo = s2.selectbox("Sorting", ["Bubble","Shell","Merge"])
    sort_field = s2.selectbox("Field", ["nim","name","major","ipk"])

    order = s3.radio("Urutan",["Ascending","Descending"],horizontal=True)

    filtered = data
    if keyword:
        filtered = [d for d in filtered if keyword.lower() in str(d[field]).lower()]

    min_ipk,max_ipk = st.slider("Filter IPK",0.0,4.0,(0.0,4.0),0.01)
    filtered = [d for d in filtered if min_ipk <= d["ipk"] <= max_ipk]

    reverse = order=="Descending"
    start=time.time()
    if algo=="Bubble":
        filtered=bubble_sort(filtered,sort_field,reverse)
    elif algo=="Shell":
        filtered=shell_sort(filtered,sort_field,reverse)
    else:
        filtered=merge_sort(filtered,sort_field,reverse)
    st.caption(f"⏱️ Sorting time: {round(time.time()-start,5)} s")

    st.divider()

    # FORM
    selected = st.selectbox("Pilih Mahasiswa", filtered, format_func=lambda x:f"{x['nim']} - {x['name']}") if filtered else None

    nim = st.text_input("NIM", selected["nim"] if selected else "")
    name = st.text_input("Nama", selected["name"] if selected else "")
    major = st.text_input("Jurusan", selected["major"] if selected else "")
    ipk = st.number_input("IPK",0.0,4.0,value=selected["ipk"] if selected else 0.0,step=0.01)

    if st.session_state.role!="VIEWER":
        b1,b2,b3 = st.columns(3)
        if b1.button("➕ Tambah"):
            if len(nim)!=12 or not nim.isdigit():
                st.error("NIM harus 12 digit")
            else:
                data.append({"nim":nim,"name":name,"major":major,"ipk":ipk})
                save_data(data); st.rerun()

        if b2.button("✏️ Edit") and selected:
            for d in data:
                if d["nim"]==selected["nim"]:
                    d.update({"nim":nim,"name":name,"major":major,"ipk":ipk})
            save_data(data); st.rerun()

        if b3.button("🗑️ Hapus") and selected:
            save_data([d for d in data if d["nim"]!=selected["nim"]])
            st.rerun()

    st.divider()
    df=pd.DataFrame(filtered)
    st.dataframe(df,use_container_width=True)

    st.download_button("⬇️ Export CSV",df.to_csv(index=False),"mahasiswa.csv","text/csv")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# =============================
# ROUTING
# =============================
login() if not st.session_state.login else app()
