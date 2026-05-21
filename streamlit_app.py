import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Logbook Digital Praktikum Titrimetri", layout="wide")

# Daftar alat yang tersedia
INVENTORY = [
    "labu takar 100 mL",
    "buret",
    "clamp",
    "erlenmeyer 250 mL",
    "corong kaca",
    "batang pengaduk",
    "pipet tetes",
    "kaca arloji",
    "tutup kaca",
]

# Inisialisasi session state untuk menyimpan data
if "inventory" not in st.session_state:
    # Simpan stok awal (misal tiap alat 5 unit) dan ID sederhana
    st.session_state.inventory = {a: {"total": 5, "available": 5} for a in INVENTORY}
if "loans" not in st.session_state:
    st.session_state.loans = []  # daftar dict peminjaman
if "returns" not in st.session_state:
    st.session_state.returns = []  # daftar dict pengembalian
if "next_loan_id" not in st.session_state:
    st.session_state.next_loan_id = 1

# Util: format waktu sekarang
def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Util: cek ketersediaan
def check_availability(requested):
    """
    requested: dict alat -> jumlah
    returns (ok: bool, message: str)
    """
    for alat, qty in requested.items():
        if qty <= 0:
            return False, f"Jumlah untuk '{alat}' harus > 0."
        if alat not in st.session_state.inventory:
            return False, f"Alat '{alat}' tidak dikenal."
        if qty > st.session_state.inventory[alat]["available"]:
            return False, f"Stok '{alat}' tidak cukup (tersedia {st.session_state.inventory[alat]['available']})."
    return True, "Ok"

# Util: buat DataFrame log
def loans_df():
    if not st.session_state.loans:
        return pd.DataFrame(columns=["loan_id","nama","nim","alat","jumlah","waktu_pinjam","status"])
    rows = []
    for loan in st.session_state.loans:
        rows.append({
            "loan_id": loan["loan_id"],
            "nama": loan["nama"],
            "nim": loan["nim"],
            "alat": ", ".join([f'{k} x{v}' for k,v in loan["items"].items()]),
            "jumlah": sum(loan["items"].values()),
            "waktu_pinjam": loan["waktu_pinjam"],
            "status": loan["status"],
        })
    return pd.DataFrame(rows)

def returns_df():
    if not st.session_state.returns:
        return pd.DataFrame(columns=["return_id","loan_id","nama","alat","jumlah","waktu_kembali","kondisi"])
    rows = []
    for r in st.session_state.returns:
        rows.append({
            "return_id": r["return_id"],
            "loan_id": r["loan_id"],
            "nama": r["nama"],
            "alat": ", ".join([f'{k} x{v}' for k,v in r["items"].items()]),
            "jumlah": sum(r["items"].values()),
            "waktu_kembali": r["waktu_kembali"],
            "kondisi": r["kondisi"],
        })
    return pd.DataFrame(rows)

# Sidebar: menu
st.sidebar.title("Menu")
page = st.sidebar.radio("Pilih halaman", ["Dashboard", "Peminjaman", "Pengembalian", "Log", "Edukasi", "Pengaturan"])

# Dashboard
if page == "Dashboard":
    st.title("Logbook Digital Praktikum Titrimetri")
    st.markdown("Ringkasan stok alat dan aktivitas terkini.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Stok Alat (tersedia / total)")
        inv_table = pd.DataFrame([
            {"alat": k, "available": v["available"], "total": v["total"]}
            for k,v in st.session_state.inventory.items()
        ])
        st.table(inv_table.set_index("alat"))
    with col2:
        st.subheader("Aktivitas Terakhir")
        recent_loans = loans_df().sort_values("waktu_pinjam", ascending=False).head(5)
        recent_returns = returns_df().sort_values("waktu_kembali", ascending=False).head(5)
        st.markdown("Peminjaman terbaru")
        st.table(recent_loans if not recent_loans.empty else pd.DataFrame(["Belum ada peminjaman"]))
        st.markdown("Pengembalian terbaru")
        st.table(recent_returns if not recent_returns.empty else pd.DataFrame(["Belum ada pengembalian"]))

# Peminjaman
if page == "Peminjaman":
    st.title("Form Peminjaman Alat")
    with st.form("form_pinjam"):
        nama = st.text_input("Nama lengkap")
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
                    # kurangi stok
                    for alat, q in requested.items():
                        st.session_state.inventory[alat]["available"] -= q
                    st.session_state.loans.append(loan)
                    st.success(f"Peminjaman dicatat (ID {loan_id}).")
                    st.info("Catat ID peminjaman untuk pengembalian nanti.")

# Pengembalian
if page == "Pengembalian":
    st.title("Form Pengembalian Alat")
    with st.form("form_kembali"):
        st.markdown("Pilih ID peminjaman yang akan dikembalikan:")
        loan_options = [f'{l["loan_id"]} - {l["nama"]} ({l["nim"]}) - {", ".join([f"{k}x{v}" for k,v in l["items"].items()])}' for l in st.session_state.loans if l["status"]=="dipinjam"]
        if not loan_options:
            st.info("Tidak ada peminjaman aktif saat ini.")
        else:
            sel = st.selectbox("Pilih peminjaman", options=loan_options)
            selected_id = int(sel.split(" - ")[0])
            loan = next(l for l in st.session_state.loans if l["loan_id"]==selected_id)
            st.markdown("Jika hanya sebagian dikembalikan, masukkan jumlah yang dikembalikan per alat.")
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
                    # update stok dan catat pengembalian
                    for alat, q in returned.items():
                        st.session_state.inventory[alat]["available"] += q
                        loan["items"][alat] -= q
                    # jika semua item sudah 0, tandai selesai
                    if all(v == 0 for v in loan["items"].values()):
                        loan["status"] = "dikembalikan"
                    # catat log pengembalian
                    ret_id = len(st.session_state.returns) + 1
                    ret = {
                        "return_id": ret_id,
                        "loan_id": selected_id,
                        "nama": loan["nama"],
                        "items": returned,
                        "waktu_kembali": now_str(),
                        "kondisi": kondisi,
                    }
                    st.session_state.returns.append(ret)
                    st.success(f"Pengembalian dicatat (Return ID {ret_id}).")

# Log
if page == "Log":
    st.title("Catatan Peminjaman & Pengembalian")
    st.subheader("Peminjaman")
    df_loans = loans_df()
    st.dataframe(df_loans.sort_values("waktu_pinjam", ascending=False), use_container_width=True)
    st.subheader("Pengembalian")
    df_returns = returns_df()
    st.dataframe(df_returns.sort_values("waktu_kembali", ascending=False), use_container_width=True)
    st.markdown("Ekspor log:")
    buffer = io.StringIO()
    df_all = pd.concat([df_loans, df_returns.rename(columns={"return_id":"loan_id","waktu_kembali":"waktu_pinjam","kondisi":"status"})], sort=False, ignore_index=True)
    if not df_all.empty:
        st.download_button("Unduh CSV (semua log)", df_all.to_csv(index=False), file_name="logbook_all.csv", mime="text/csv")

# Edukasi
if page == "Edukasi":
    st.title("Edukasi Alat Praktikum Titrimetri")
    st.markdown("Pilih alat untuk melihat deskripsi singkat, penggunaan, dan tips keselamatan.")
    alat = st.selectbox("Pilih alat", INVENTORY)
    st.subheader(alat)
    descriptions = {
        "labu takar 100 mL": (
            "Botol atau labu ukur untuk menakar volume cairan secara presisi. " 
            "Gunakan pada permukaan datar, baca meniskus pada garis mata. "
            "Cuci bersih setelah digunakan."
        ),
        "buret": (
            "Alat untuk titrasi dengan skala graduasi dan kran di bawah. " 
            "Pasang dengan klamp, kosongkan udara dari kran sebelum titrasi, dan baca volume di bawah meniskus."
        ),
        "klamp": "Digunakan untuk menjepit buret atau alat pada statif; pastikan terpasang kuat.",
        "erlenmeyer 250 mL": "Wadah reaksi untuk titrasi; bentuk kerucut memudahkan pengadukan tanpa tumpah.",
        "corong kaca": "Untuk pemindahan cairan atau filtrasi; gunakan kertas saring bila diperlukan.",
        "batang pengaduk": "Untuk mengaduk larutan selama titrasi agar reaksi berjalan homogen.",
        "pipet tetes": "Untuk meneteskan indikator atau reagen sedikit demi sedikit; gunakan dengan hati-hati.",
        "kaca arloji": "Untuk menimbang atau menutup bejana kecil; bersihkan setelah penggunaan.",
        "tutup kaca": "Menutup bejana untuk mencegah kontaminasi atau penguapan.",
    }
    tips = {
        "labu takar 100 mL": ["Jangan gunakan untuk pemindahan kasar; gunakan pipet atau corong bila perlu.", "Jaga garis ukur tetap bersih."],
        "buret": ["Bilas buret dengan larutan yang akan digunakan sebelum titrasi.", "Periksa kebocoran kran sebelum mulai."],
        "erlenmeyer 250 mL": ["Pegang di bagian bawah saat menuang untuk stabilitas."],
    }
    st.write(descriptions.get(alat, "Deskripsi tidak tersedia."))
    if alat in tips:
        st.markdown("Tips:")
        for t in tips[alat]:
            st.write(f"- {t}")

# Pengaturan
if page == "Pengaturan":
    st.title("Pengaturan Sistem (Sederhana)")
    st.markdown("Atur stok awal atau reset data (hati-hati).")
    cols = st.columns([2,1])
    with cols[0]:
        st.subheader("Atur stok tiap alat")
        for alat in INVENTORY:
            val = st.number_input(f"Total {alat}", min_value=0, max_value=100, value=st.session_state.inventory[alat]["total"], key=f"set_{alat}")
            if val != st.session_state.inventory[alat]["total"]:
                # ubah total dan adjust available proporsional (jika available > new total set = new total)
                diff = val - st.session_state.inventory[alat]["total"]
                st.session_state.inventory[alat]["total"] = int(val)
                st.session_state.inventory[alat]["available"] = max(0, min(st.session_state.inventory[alat]["available"] + diff, int(val)))
    with cols[1]:
        st.subheader("Reset data")
        if st.button("Reset semua log (jangan asal klik)"):
            st.session_state.loans = []
            st.session_state.returns = []
            st.session_state.next_loan_id = 1
            for a in st.session_state.inventory:
                st.session_state.inventory[a]["available"] = st.session_state.inventory[a]["total"]
            st.success("Data di-reset.")
            
