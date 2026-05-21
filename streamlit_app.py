import streamlit as st
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Logbook Digital Praktikum Titrimetri", layout="wide")

# Daftar alat yang tersedia
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
            "re
            
