# manajemen_data_mahasiswa_glossy_final.py
"""
Final — Manajemen Data Mahasiswa (Glossy Dark Navy)
Features:
- Login (glossy card)
- CRUD (Tambah / Edit / Hapus)
- IPK (0.00 - 4.00), NIM 12 digit
- File I/O (students_db.json)
- Search: Linear, Binary, Sequential (supports field:value)
- Sorting: Bubble, Insertion, Selection, Merge, Shell
- Stats (total, avg IPK, by major)
- Export CSV
- Edit/Delete fixed (match by NIM on object)
No external libs required (pure Tkinter + stdlib)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, re, os, csv
from copy import deepcopy
from typing import List, Optional, Any, Tuple

# ---------------------------
# Config & Regex
# ---------------------------
DB_FILE = "students_db.json"
NIM_RE = re.compile(r"^\d{12}$")
NAME_RE = re.compile(r"^[A-Za-z\s\.\'\-]{2,80}$")
IPK_RE = re.compile(r"^[0-4](?:\.\d{1,2})?$")

# Demo credentials
USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "operator": {"password": "op123", "role": "OPERATOR"},
    "viewer": {"password": "view123", "role": "VIEWER"}
}

# ---------------------------
# Models (OOP)
# ---------------------------
class Person:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Student(Person):
    def __init__(self, nim: str, name: str, major: str, ipk: float):
        super().__init__(name)
        self._nim = nim
        self._major = major
        self._ipk = float(ipk)

    @property
    def nim(self) -> str:
        return self._nim

    @property
    def major(self) -> str:
        return self._major

    @property
    def ipk(self) -> float:
        return float(self._ipk)

    @nim.setter
    def nim(self, v: str):
        self._nim = v

    @major.setter
    def major(self, v: str):
        self._major = v

    @ipk.setter
    def ipk(self, v: float):
        self._ipk = float(v)

    def to_dict(self) -> dict:
        return {"nim": self._nim, "name": self._name, "major": self._major, "ipk": float(self._ipk)}

    @staticmethod
    def from_dict(d: dict) -> "Student":
        return Student(d["nim"], d["name"], d.get("major", ""), d.get("ipk", 0.0))


# ---------------------------
# Storage manager
# ---------------------------
class StudentManager:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.students: List[Student] = []
        self.load()

    def load(self):
        if not os.path.exists(self.db_file):
            self.students = []
            return
        try:
            with open(self.db_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.students = [Student.from_dict(d) for d in raw]
        except Exception:
            self.students = []

    def save(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.students], f, indent=2, ensure_ascii=False)

    def add(self, s: Student):
        if self.get_by_nim(s.nim):
            raise ValueError("NIM sudah terdaftar.")
        self.students.append(s)
        self.save()

    def get_by_nim(self, nim: str) -> Optional[Student]:
        for s in self.students:
            if s.nim == nim:
                return s
        return None

    def update(self, old_nim: str, new_s: Student):
        s = self.get_by_nim(old_nim)
        if not s:
            raise LookupError("Mahasiswa tidak ditemukan.")
        # if nim changed, ensure unique
        if new_s.nim != old_nim and self.get_by_nim(new_s.nim):
            raise ValueError("NIM baru sudah dipakai.")
        s._nim = new_s.nim
        s._name = new_s.name
        s._major = new_s.major
        s._ipk = float(new_s.ipk)
        self.save()

    def delete(self, nim: str):
        before = len(self.students)
        self.students = [x for x in self.students if x.nim != nim]
        if len(self.students) == before:
            raise LookupError("NIM tidak ditemukan.")
        self.save()

    def list_all(self) -> List[Student]:
        return deepcopy(self.students)


# ---------------------------
# Search strategies
# ---------------------------
class SearchStrategy:
    def search(self, arr: List[Student], key: Any) -> List[Tuple[int, Student]]:
        raise NotImplementedError


class LinearSearch(SearchStrategy):
    def search(self, arr: List[Student], key: Any):
        res = []
        for i, s in enumerate(arr):
            if isinstance(key, tuple):
                field, val = key
                if hasattr(s, field) and val.lower() in str(getattr(s, field)).lower():
                    res.append((i, s))
            else:
                if key.lower() in s.name.lower() or key == s.nim:
                    res.append((i, s))
        return res


class BinarySearch(SearchStrategy):
    def search(self, arr: List[Student], key: Any):
        # assumes arr sorted by nim
        if isinstance(key, tuple):
            field, val = key
            if field != "nim":
                return []
            target = val
        else:
            target = key
        left, right = 0, len(arr) - 1
        while left <= right:
            mid = (left + right) // 2
            if arr[mid].nim == target:
                return [(mid, arr[mid])]
            elif arr[mid].nim < target:
                left = mid + 1
            else:
                right = mid - 1
        return []


class SequentialSearch(SearchStrategy):
    def search(self, arr: List[Student], key: Any):
        if isinstance(key, tuple):
            field, val = key
            res = []
            for i, s in enumerate(arr):
                if hasattr(s, field) and val.lower() in str(getattr(s, field)).lower():
                    res.append((i, s))
            return res
        else:
            return LinearSearch().search(arr, key)


# ---------------------------
# Sorting functions
# ---------------------------
def insertion_sort(arr: List[Student], key='nim'):
    a = arr[:]
    for i in range(1, len(a)):
        cur = a[i]
        j = i - 1
        while j >= 0 and getattr(a[j], key) > getattr(cur, key):
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = cur
    return a


def selection_sort(arr: List[Student], key='nim'):
    a = arr[:]
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if getattr(a[j], key) < getattr(a[min_idx], key):
                min_idx = j
        a[i], a[min_idx] = a[min_idx], a[i]
    return a


def bubble_sort(arr: List[Student], key='nim'):
    a = arr[:]
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if getattr(a[j], key) > getattr(a[j + 1], key):
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    return a


def merge_sort(arr: List[Student], key='nim'):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    L = merge_sort(arr[:mid], key)
    R = merge_sort(arr[mid:], key)
    merged = []
    i = j = 0
    while i < len(L) and j < len(R):
        if getattr(L[i], key) <= getattr(R[j], key):
            merged.append(L[i]); i += 1
        else:
            merged.append(R[j]); j += 1
    merged.extend(L[i:]); merged.extend(R[j:])
    return merged


def shell_sort(arr: List[Student], key='nim'):
    a = arr[:]
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and getattr(a[j - gap], key) > getattr(temp, key):
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
        gap //= 2
    return a


# ---------------------------
# Utilities: validation & stats
# ---------------------------
def validate_nim(nim: str) -> bool:
    return bool(NIM_RE.match(nim))


def validate_name(name: str) -> bool:
    return bool(NAME_RE.match(name))


def validate_ipk(ipk: str) -> bool:
    if not IPK_RE.match(ipk):
        return False
    try:
        v = float(ipk)
        return 0.0 <= v <= 4.0
    except:
        return False


def calc_stats(students: List[Student]) -> dict:
    total = len(students)
    avg_ipk = round(sum([s.ipk for s in students]) / total, 2) if total else 0.0
    majors = {}
    for s in students:
        majors[s.major] = majors.get(s.major, 0) + 1
    return {"total": total, "avg_ipk": avg_ipk, "by_major": majors}


# ---------------------------
# UI helpers (glossy style)
# ---------------------------
class GlossyFrame(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg="#0f1724", **kw)
        self.config(highlightthickness=1, highlightbackground="#1f2a44")


def nice_button(master, text, command, bg="#29486a", fg="white", width=None):
    b = tk.Button(master, text=text, command=command, bg=bg, fg=fg, relief="flat", activebackground="#2b547a")
    b.config(font=("Segoe UI", 10, "bold"))
    if width:
        b.config(width=width)
    return b


# ---------------------------
# Main App GUI
# ---------------------------
class App:
    def __init__(self, root, user_role="ADMIN"):
        self.root = root
        self.root.title("Manajemen Data Mahasiswa — Glossy Dark Navy")
        self.root.geometry("1100x700")
        self.root.configure(bg="#071124")
        self.user_role = user_role
        self.mgr = StudentManager()

        # header
        header = tk.Frame(root, bg="#071124")
        header.pack(fill="x", pady=8)
        tk.Label(header, text="Manajemen Data Mahasiswa", fg="#cfe8ff", bg="#071124",
                 font=("Segoe UI", 20, "bold")).pack(side="left", padx=20)

        # stats card in header
        self.stats_card = GlossyFrame(header)
        self.stats_card.pack(side="right", padx=20)
        self.stats_label = tk.Label(self.stats_card, text="", bg="#0f1724", fg="#d6e9ff", font=("Segoe UI", 10))
        self.stats_label.pack(padx=12, pady=8)

        main = tk.Frame(root, bg="#071124")
        main.pack(fill="both", expand=True, padx=18, pady=(6, 18))

        # left form
        left = GlossyFrame(main)
        left.place(x=18, y=10, width=380, height=560)
        tk.Label(left, text="Form Mahasiswa", bg="#0f1724", fg="#e7f5ff", font=("Segoe UI", 14, "bold")).pack(pady=12)

        form = tk.Frame(left, bg="#0f1724")
        form.pack(padx=16, pady=6, anchor="w")

        tk.Label(form, text="NIM (12 digit)", bg="#0f1724", fg="#bcd7ff").grid(row=0, column=0, sticky="w", pady=8)
        self.entry_nim = tk.Entry(form, width=28, bg="#0c2036", fg="#eaf6ff", insertbackground="white")
        self.entry_nim.grid(row=0, column=1, padx=8)

        tk.Label(form, text="Nama", bg="#0f1724", fg="#bcd7ff").grid(row=1, column=0, sticky="w", pady=8)
        self.entry_name = tk.Entry(form, width=28, bg="#0c2036", fg="#eaf6ff", insertbackground="white")
        self.entry_name.grid(row=1, column=1, padx=8)

        tk.Label(form, text="Jurusan", bg="#0f1724", fg="#bcd7ff").grid(row=2, column=0, sticky="w", pady=8)
        self.entry_major = tk.Entry(form, width=28, bg="#0c2036", fg="#eaf6ff", insertbackground="white")
        self.entry_major.grid(row=2, column=1, padx=8)

        tk.Label(form, text="IPK (0.00-4.00)", bg="#0f1724", fg="#bcd7ff").grid(row=3, column=0, sticky="w", pady=8)
        self.entry_ipk = tk.Entry(form, width=28, bg="#0c2036", fg="#eaf6ff", insertbackground="white")
        self.entry_ipk.grid(row=3, column=1, padx=8)

        btns = tk.Frame(left, bg="#0f1724")
        btns.pack(pady=12)
        self.add_btn = nice_button(btns, "Tambah", self.add_student, bg="#29486a")
        self.add_btn.grid(row=0, column=0, padx=6)
        self.edit_btn = nice_button(btns, "Edit", self.edit_student, bg="#375c9b")
        self.edit_btn.grid(row=0, column=1, padx=6)
        self.del_btn = nice_button(btns, "Hapus", self.delete_student, bg="#8b3b3b")
        self.del_btn.grid(row=0, column=2, padx=6)

        self.clear_btn = nice_button(left, "Clear", self.clear_form, bg="#233049", width=36)
        self.clear_btn.pack(pady=8)

        # right area
        right = GlossyFrame(main)
        right.place(x=420, y=10, width=650, height=560)

        control = tk.Frame(right, bg="#0f1724")
        control.pack(fill="x", padx=10, pady=8)

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(control, textvariable=self.search_var, width=34, bg="#0c2036", fg="#eaf6ff", insertbackground="white")
        self.search_entry.pack(side="left", padx=(2,6))

        self.search_method = tk.StringVar(value="linear")
        ttk.Combobox(control, textvariable=self.search_method, values=["linear","binary","sequential"], width=12).pack(side="left", padx=6)

        tk.Button(control, text="Cari", bg="#2f6a97", fg="white", command=self.do_search).pack(side="left", padx=6)
        tk.Button(control, text="Reload", bg="#6c6df6", fg="white", command=self.load_table).pack(side="left", padx=6)

        tk.Label(control, text="Urutkan:", bg="#0f1724", fg="#cfe8ff").pack(side="left", padx=(12,4))
        self.sort_method = tk.StringVar(value="merge")
        ttk.Combobox(control, textvariable=self.sort_method, values=["bubble","insertion","selection","merge","shell"], width=12).pack(side="left")
        tk.Button(control, text="Apply", bg="#2f6a97", fg="white", command=self.do_sort).pack(side="left", padx=6)

        # treeview style
        cols = ("nim","name","major","ipk")
        style = ttk.Style()
        style.theme_use('default')
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Segoe UI', 10), background="#071124",
                        fieldbackground="#071124", foreground="#eaf6ff")
        style.configure("mystyle.Treeview.Heading", font=('Segoe UI', 10, 'bold'), background="#0f1724", foreground="#cfe8ff")
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

        self.tree = ttk.Treeview(right, columns=cols, show="headings", style="mystyle.Treeview", height=18)
        for c in cols:
            self.tree.heading(c, text=c.upper())
            if c == "name":
                self.tree.column(c, width=200)
            elif c == "major":
                self.tree.column(c, width=140)
            else:
                self.tree.column(c, width=110)

        self.tree.pack(fill="both", expand=True, padx=8, pady=(6,10))
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        bottom = tk.Frame(right, bg="#0f1724")
        bottom.pack(fill="x", padx=10, pady=(4,8))
        tk.Button(bottom, text="Export CSV", bg="#2fbf8f", fg="white", command=self.export_csv).pack(side="right")

        self.update_stats()
        self.load_table()

    # CRUD operations
    def clear_form(self):
        self.entry_nim.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.entry_major.delete(0, "end")
        self.entry_ipk.delete(0, "end")
        try:
            self.tree.selection_remove(self.tree.selection())
        except Exception:
            pass

    def add_student(self):
        nim = self.entry_nim.get().strip()
        name = self.entry_name.get().strip()
        major = self.entry_major.get().strip()
        ipk = self.entry_ipk.get().strip()
        try:
            if not validate_nim(nim):
                raise ValueError("NIM harus 12 digit angka")
            if not validate_name(name):
                raise ValueError("Nama tidak valid")
            if not validate_ipk(ipk):
                raise ValueError("IPK harus 0.00 - 4.00")
            s = Student(nim, name, major, float(ipk))
            self.mgr.add(s)
            messagebox.showinfo("Sukses", "Mahasiswa ditambahkan")
            self.load_table()
            self.clear_form()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_tree_select(self, ev):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        values = self.tree.item(item, "values")
        nim = str(values[0]).strip()
        s = self.mgr.get_by_nim(nim)
        if s:
            self.entry_nim.delete(0, "end"); self.entry_nim.insert(0, s.nim)
            self.entry_name.delete(0, "end"); self.entry_name.insert(0, s.name)
            self.entry_major.delete(0, "end"); self.entry_major.insert(0, s.major)
            self.entry_ipk.delete(0, "end"); self.entry_ipk.insert(0, f"{s.ipk:.2f}")

    def edit_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Pilih", "Pilih baris di tabel dahulu")
            return
        item = sel[0]
        values = self.tree.item(item, "values")
        old_nim = str(values[0]).strip()

        nim = self.entry_nim.get().strip()
        name = self.entry_name.get().strip()
        major = self.entry_major.get().strip()
        ipk = self.entry_ipk.get().strip()
        try:
            if not validate_nim(nim):
                raise ValueError("NIM harus 12 digit angka")
            if not validate_name(name):
                raise ValueError("Nama tidak valid")
            if not validate_ipk(ipk):
                raise ValueError("IPK harus 0.00 - 4.00")
            new_s = Student(nim, name, major, float(ipk))
            self.mgr.update(old_nim, new_s)   # match by old_nim on objects
            messagebox.showinfo("Sukses", "Data diperbarui")
            self.load_table()
            self.clear_form()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Pilih", "Pilih baris di tabel dahulu")
            return
        item = sel[0]
        values = self.tree.item(item, "values")
        nim = str(values[0]).strip()
        if not messagebox.askyesno("Konfirmasi", f"Hapus mahasiswa NIM {nim}?"):
            return
        try:
            self.mgr.delete(nim)
            messagebox.showinfo("Sukses", "Data dihapus")
            self.load_table()
            self.clear_form()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # load table
    def load_table(self, data: Optional[List[Student]] = None):
        for r in self.tree.get_children():
            self.tree.delete(r)
        source = data if data is not None else self.mgr.list_all()
        for s in source:
            # insert using nim as iid if possible (unique)
            try:
                self.tree.insert("", "end", iid=s.nim, values=(s.nim, s.name, s.major, f"{s.ipk:.2f}"))
            except Exception:
                self.tree.insert("", "end", values=(s.nim, s.name, s.major, f"{s.ipk:.2f}"))

    # search / parse key
    def parse_search_key(self, raw: str):
        raw = raw.strip()
        if ":" in raw:
            fld, val = raw.split(":", 1)
            fld = fld.strip().lower()
            val = val.strip()
            allowed = {"name": "name", "nim": "nim", "major": "major", "ipk": "ipk"}
            if fld in allowed:
                return (allowed[fld], val)
        return raw

    def do_search(self):
        method = self.search_method.get()
        raw = self.search_var.get().strip()
        if raw == "":
            messagebox.showwarning("Input", "Masukkan kata kunci pencarian (nama atau nim atau field:value)")
            return
        key = self.parse_search_key(raw)
        arr = self.mgr.list_all()
        if method == "binary":
            # must sort by nim first
            arr = merge_sort(arr, key="nim")
            param = key[1] if isinstance(key, tuple) else key
            res = BinarySearch().search(arr, param)
            if res:
                students = [s for _, s in res]
                self.load_table(students)
            else:
                messagebox.showinfo("Hasil", "Tidak ditemukan")
            return
        elif method == "linear":
            res = LinearSearch().search(arr, key)
        else:
            res = SequentialSearch().search(arr, key)
        if res:
            students = [s for _, s in res]
            self.load_table(students)
        else:
            messagebox.showinfo("Hasil", "Tidak ditemukan")

    def do_sort(self):
        method = self.sort_method.get()
        arr = self.mgr.list_all()
        try:
            if method == "bubble":
                arr = bubble_sort(arr, key="name")
            elif method == "insertion":
                arr = insertion_sort(arr, key="name")
            elif method == "selection":
                arr = selection_sort(arr, key="name")
            elif method == "merge":
                arr = merge_sort(arr, key="name")
            elif method == "shell":
                arr = shell_sort(arr, key="name")
            else:
                messagebox.showwarning("Sort", "Metode sort tidak dikenal")
                return
            self.load_table(arr)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengurutkan: {e}")

    def export_csv(self):
        fname = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not fname:
            return
        try:
            with open(fname, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["nim", "name", "major", "ipk"])
                for s in self.mgr.list_all():
                    w.writerow([s.nim, s.name, s.major, f"{s.ipk:.2f}"])
            messagebox.showinfo("Export", f"Berhasil export ke {fname}")
        except Exception as e:
            messagebox.showerror("Export error", str(e))

    def update_stats(self):
        stats = calc_stats(self.mgr.list_all())
        text = f"Total: {stats['total']}   Avg IPK: {stats['avg_ipk']:.2f}"
        majors = stats["by_major"]
        if majors:
            parts = [f"{k}:{v}" for k, v in list(majors.items())[:3]]
            text += "   |   " + "  ".join(parts)
        self.stats_label.config(text=text)


# ---------------------------
# Login window (glossy)
# ---------------------------
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login — Manajemen Data Mahasiswa")
        self.geometry("420x300")
        self.configure(bg="#071124")
        self.resizable(False, False)

        card = tk.Frame(self, bg="#071731")
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=220)
        card.config(highlightthickness=1, highlightbackground="#2b3b66")

        tk.Label(card, text="Selamat datang", bg="#071731", fg="#d9eefc", font=("Segoe UI", 14, "bold")).pack(pady=(18,6))
        tk.Label(card, text="Masuk dulu untuk melanjutkan", bg="#071731", fg="#bcd7ff").pack()

        frm = tk.Frame(card, bg="#071731")
        frm.pack(pady=12)

        tk.Label(frm, text="Username", bg="#071731", fg="#cfe8ff").grid(row=0, column=0, sticky="w")
        self.ent_user = tk.Entry(frm, width=28, bg="#0c2036", fg="#eaf6ff", insertbackground="white")
        self.ent_user.grid(row=0, column=1, pady=6, padx=6)

        tk.Label(frm, text="Password", bg="#071731", fg="#cfe8ff").grid(row=1, column=0, sticky="w")
        self.ent_pass = tk.Entry(frm, width=28, bg="#0c2036", fg="#eaf6ff", insertbackground="white", show="*")
        self.ent_pass.grid(row=1, column=1, pady=6, padx=6)

        tk.Button(card, text="Masuk", bg="#2f6a97", fg="white", width=24, command=self.do_login).pack(pady=(8,10))
        self.bind("<Return>", lambda e: self.do_login())

    def do_login(self):
        user = self.ent_user.get().strip()
        pwd = self.ent_pass.get()
        if user in USERS and USERS[user]["password"] == pwd:
            role = USERS[user]["role"]
            self.destroy()
            root = tk.Tk()
            app = App(root, user_role=role)
            root.mainloop()
        else:
            messagebox.showerror("Login failed", "Username atau password salah")


# ---------------------------
# Ensure DB exists and launch
# ---------------------------
if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    login = LoginWindow()
    login.mainloop()
