import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Logbook Digital Praktikum Titrimetri", layout="wide")

INVENTORY = [
    "labu takar 100 mL",
    "buret",
    "klamp",
    "erlenmeyer 250 mL",
    "corong kaca",
    "batang pengaduk",
    "pipet tetes",
    "kaca arloji",
    "tutup kaca",
]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username_login" not in st.session_state:
    st.session_state.username_login = ""
if "inventory" not in st.session_state:
    st.session_state.inventory = {a: {"total": 5, "available": 5} for a in INVENTORY}
if "loans" not in st.session_state:
    st.session_state.loans = []
if "returns" not in st.session_state:
    st.session_state.returns = []
if "damages" not in st.session_state:
    st.session_state.damages = []
if "next_loan_id" not in st.session_state:
    st.session_state.next_loan_id = 1
if "next_damage_id" not in st.session_state:
    st.session_state.next_damage_id = 1

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def login_form():
    st.sidebar.subheader("Login Admin")
    with st.sidebar.form("login_form"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if user == "admin" and pwd == "1234":
                st.session_state.logged_in = True
                st.session_state.username_login = user
                st.success("Login berhasil.")
            else:
                st.error("Username atau password salah.")

def check_availability(requested):
    for alat, qty in requested.items():
        if qty <= 0:
            return False, f"Jumlah untuk '{alat}' harus > 0."
        if alat not in st.session_state.inventory:
            return False, f"Alat '{alat}' tidak dikenal."
        if qty > st.session_state.inventory[alat]["available"]:
            return False, f"Stok '{alat}' tidak cukup (tersedia {st.session_state.inventory[alat]['available']})."
    return True, "Ok"

def loans_df():
    if not st.session_state.loans:
        return pd.DataFrame(columns=["loan_id", "nama", "nim", "alat", "jumlah", "waktu_pinjam", "status"])
    rows = []
    for loan in st.session_state.loans:
        rows.append({
            "loan_id": loan["loan_id"],
            "nama": loan["nama"],
            "nim": loan["nim"],
            "alat": ", ".join([f'{k} x{v}' for k, v in loan["items"].items()]),
            "jumlah": sum(loan["items"].values()),
            "waktu_pinjam": loan["waktu_pinjam"],
            "status": loan["status"],
        })
    return pd.DataFrame(rows)

def returns_df():
    if not st.session_state.returns:
        return pd.DataFrame(columns=["return_id", "loan_id", "nama", "alat", "jumlah", "waktu_kembali", "kondisi"])
    rows = []
    for r in st.session_state.returns:
        rows.append({
            "return_id": r["return_id"],
            "loan_id": r["loan_id"],
            "nama": r["nama"],
            "alat": ", ".join([f'{k} x{v}' for k, v in r["items"].items()]),
            "jumlah": sum(r["items"].values()),
            "waktu_kembali": r["waktu_kembali"],
            "kondisi": r["kondisi"],
        })
    return pd.DataFrame(rows)

def damages_df():
    if not st.session_state.damages:
        return pd.DataFrame(columns=["damage_id", "tanggal", "nama", "alat", "jumlah", "kondisi", "keterangan"])
    rows = []
    for d in st.session_state.damages:
        rows.append({
            "damage_id": d["damage_id"],
            "tanggal": d["tanggal"],
            "nama": d["nama"],
            "alat": d["alat"],
            "jumlah": d["jumlah"],
            "kondisi": d["kondisi"],
            "keterangan": d["keterangan"],
        })
    return pd.DataFrame(rows)

login_form()
if not st.session_state.logged_in:
    st.warning("Silakan login untuk melihat dan mengelola data.")
    st.stop()

st.sidebar.success(f"Login sebagai: {st.session_state.username_login}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username_login = ""
    st.rerun()

st.sidebar.title("Menu")
page = st.sidebar.radio("Pilih halaman", ["Dashboard", "Peminjaman", "Pengembalian", "Log", "Edukasi", "Pengaturan"])

if page == "Dashboard":
    st.title("Logbook Digital Praktikum Titrimetri")
    st.markdown("Ringkasan stok alat dan aktivitas terkini.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Stok Alat (tersedia / total)")
        inv_table = pd.DataFrame([
            {"alat": k, "available": v["available"], "total": v["total"]}
            for k, v in st.session_state.inventory.items()
        ])
        st.dataframe(inv_table, use_container_width=True)
    with col2:
        st.subheader("Aktivitas Terakhir")
        recent_loans = loans_df().sort_values("waktu_pinjam", ascending=False).head(5)
        recent_returns = returns_df().sort_values("waktu_kembali", ascending=False).head(5)
        st.markdown("Peminjaman terbaru")
        st.dataframe(recent_loans, use_container_width=True)
        st.markdown("Pengembalian terbaru")
        st.dataframe(recent_returns, use_container_width=True)

if page == "Peminjaman":
    st.title("Form Peminjaman Alat")
    with st.form("form_pinjam"):
        nama = st.text_input("Nama lengkap peminjam")
        nim = st.text_input("NIM / ID")
        st.markdown("Pilih alat dan jumlah yang ingin dipinjam:")
        cols = st.columns(3)
        requested = {}
        for i, alat in enumerate(INVENTORY):
            c = cols[i % 3]
            max_av = st.session_state.inventory[alat]["available"]
            qty = c.number_input(f"{alat} (tersedia {max_av})", min_value=0, max_value=max_av, value=0, step=1, key=f"pin_{alat}")
            if qty > 0:
                requested[alat] = int(qty)
        tujuan = st.text_area("Tujuan / Praktikum (opsional)")
        submit = st.form_submit_button("Pinjam")
        if submit:
            if not nama or not nim:
                st.error("Isi nama dan NIM terlebih dahulu.")
            elif not requested:
                st.error("Pilih minimal satu alat dengan jumlah > 0.")
            else:
                ok, msg = check_availability(requested)
                if not ok:
                    st.error(msg)
                else:
                    loan_id = st.session_state.next_loan_id
                    st.session_state.next_loan_id += 1
                    loan = {
                        "loan_id": loan_id,
                        "nama": nama,
                        "nim": nim,
                        "items": requested,
                        "tujuan": tujuan,
                        "waktu_pinjam": now_str(),
                        "status": "dipinjam",
                    }
                    for alat, q in requested.items():
                        st.session_state.inventory[alat]["available"] -= q
                    st.session_state.loans.append(loan)
                    st.success(f"Peminjaman dicatat (ID {loan_id}).")

if page == "Pengembalian":
    st.title("Form Pengembalian Alat")
    with st.form("form_kembali"):
        loan_options = [
            f'{l["loan_id"]} - {l["nama"]} ({l["nim"]}) - {", ".join([f"{k}x{v}" for k, v in l["items"].items()])}'
            for l in st.session_state.loans if l["status"] == "dipinjam"
        ]
        if not loan_options:
            st.info("Tidak ada peminjaman aktif saat ini.")
        else:
            sel = st.selectbox("Pilih peminjaman", options=loan_options)
            selected_id = int(sel.split(" - ")[0])
            loan = next(l for l in st.session_state.loans if l["loan_id"] == selected_id)
            returned = {}
            cols = st.columns(3)
            for i, alat in enumerate(loan["items"].keys()):
                c = cols[i % 3]
                max_return = loan["items"][alat]
                qty = c.number_input(f"{alat} (maks {max_return})", min_value=0, max_value=max_return, value=max_return, step=1, key=f"ret_{selected_id}_{alat}")
                if qty > 0:
                    returned[alat] = int(qty)
            kondisi = st.selectbox("Kondisi alat setelah dikembalikan", ["baik", "rusak ringan", "rusak berat"])
            submit_ret = st.form_submit_button("Kembalikan")
            if submit_ret:
                if not returned:
                    st.error("Pilih minimal satu alat yang dikembalikan.")
                else:
                    for alat, q in returned.items():
                        st.session_state.inventory[alat]["available"] += q
                        loan["items"][alat] -= q
                    if all(v == 0 for v in loan["items"].values()):
                        loan["status"] = "dikembalikan"
                    ret_id = len(st.session_state.returns) + 1
                    st.session_state.returns.append({
                        "return_id": ret_id,
                        "loan_id": selected_id,
                        "nama": loan["nama"],
                        "items": returned,
                        "waktu_kembali": now_str(),
                        "kondisi": kondisi,
                    })
                    st.success(f"Pengembalian dicatat (Return ID {ret_id}).")

if page == "Log":
    st.title("Catatan Peminjaman, Pengembalian, dan Kerusakan")
    tab1, tab2, tab3, tab4 = st.tabs(["Peminjaman", "Pengembalian", "Kerusakan", "Sedang Meminjam"])

    with tab1:
        st.subheader("Peminjaman")
        df_loans = loans_df()
        st.dataframe(df_loans.sort_values("waktu_pinjam", ascending=False), use_container_width=True)

    with tab2:
        st.subheader("Pengembalian")
        df_returns = returns_df()
        st.dataframe(df_returns.sort_values("waktu_kembali", ascending=False), use_container_width=True)

    with tab3:
        st.subheader("Catat Alat Rusak")
        with st.form("form_rusak"):
            nama = st.text_input("Nama pelapor")
            alat_rusak = st.selectbox("Pilih alat yang rusak", INVENTORY)
            jumlah_rusak = st.number_input("Jumlah rusak", min_value=1, max_value=100, value=1, step=1)
            kondisi = st.selectbox("Tingkat kerusakan", ["rusak ringan", "rusak sedang", "rusak berat"])
            keterangan = st.text_area("Keterangan kerusakan")
            submit_rusak = st.form_submit_button("Simpan Kerusakan")
            if submit_rusak:
                damage_id = st.session_state.next_damage_id
                st.session_state.next_damage_id += 1
                st.session_state.damages.append({
                    "damage_id": damage_id,
                    "tanggal": now_str(),
                    "nama": nama if nama else "-",
                    "alat": alat_rusak,
                    "jumlah": int(jumlah_rusak),
                    "kondisi": kondisi,
                    "keterangan": keterangan if keterangan else "-",
                })
                st.success(f"Kerusakan alat berhasil dicatat (ID {damage_id}).")
        st.subheader("Daftar Alat Rusak")
        df_damages = damages_df()
        st.dataframe(df_damages.sort_values("tanggal", ascending=False), use_container_width=True)

    with tab4:
        st.subheader("Teman yang Sedang Meminjam")
        df_loans = loans_df()
        aktif = df_loans[df_loans["status"] == "dipinjam"] if not df_loans.empty else df_loans
        st.dataframe(aktif, use_container_width=True)

if page == "Edukasi":
    st.title("Edukasi Alat Praktikum Titrimetri")
    alat = st.selectbox("Pilih alat", INVENTORY)
    st.subheader(alat)
    descriptions = {
        "labu takar 100 mL": "Botol atau labu ukur untuk menakar volume cairan secara presisi. Gunakan pada permukaan datar, baca meniskus pada garis mata. Cuci bersih setelah digunakan.",
        "buret": "Alat untuk titrasi dengan skala graduasi dan kran di bawah. Pasang dengan klamp, kosongkan udara dari kran sebelum titrasi, dan baca volume di bawah meniskus.",
        "klamp": "Digunakan untuk menjepit buret atau alat pada statif; pastikan terpasang kuat.",
        "erlenmeyer 250 mL": "Wadah reaksi untuk titrasi; bentuk kerucut memudahkan pengadukan tanpa tumpah.",
        "corong kaca": "Untuk pemindahan cairan atau filtrasi; gunakan kertas saring bila diperlukan.",
        "batang pengaduk": "Untuk mengaduk larutan selama titrasi agar reaksi berjalan homogen.",
        "pipet tetes": "Untuk meneteskan indikator atau reagen sedikit demi sedikit; gunakan dengan hati-hati.",
        "kaca arloji": "Untuk menimbang atau menutup bejana kecil; bersihkan setelah penggunaan.",
        "tutup kaca": "Menutup bejana untuk mencegah kontaminasi atau penguapan.",
    }
    st.write(descriptions.get(alat, "Deskripsi tidak tersedia."))

if page == "Pengaturan":
    st.title("Pengaturan Sistem")
    cols = st.columns([2, 1])
    with cols[0]:
        st.subheader("Atur stok tiap alat")
        for alat in INVENTORY:
            val = st.number_input(f"Total {alat}", min_value=0, max_value=100, value=st.session_state.inventory[alat]["total"], key=f"set_{alat}")
            if val != st.session_state.inventory[alat]["total"]:
                diff = val - st.session_state.inventory[alat]["total"]
                st.session_state.inventory[alat]["total"] = int(val)
                st.session_state.inventory[alat]["available"] = max(0, min(st.session_state.inventory[alat]["available"] + diff, int(val)))
    with cols[1]:
        st.subheader("Reset data")
        if st.button("Reset semua log"):
            st.session_state.loans = []
            st.session_state.returns = []
            st.session_state.damages = []
            st.session_state.next_loan_id = 1
            st.session_state.next_damage_id = 1
            for a in st.session_state.inventory:
                st.session_state.inventory[a]["available"] = st.session_state.inventory[a]["total"]
            st.success("Data di-reset.")

