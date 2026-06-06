import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Manajemen Logbook Digital Praktikum Titrimetri", layout="wide")

DB_FILE = "lab_logbook.db"
ADMIN_PASSWORD = "kelompok 2"
WIB = ZoneInfo("Asia/Jakarta")

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
    "gelas piala 500 mL",
    "gelas piala 100 mL",
    "pipet volumetrik 25 mL",
    "pipet volumetrik 50 mL",
    "bulb",
    "kaki 3",
    "kasa asbes",
    "bunsen",
    "pipet mohr 10 mL",
    "statif",
    "gelas ukur 10 mL",
    "gelas ukur 50 mL",
    "tabung reaksi",
    "rak tabung reaksi",
]

if "settings_unlocked" not in st.session_state:
    st.session_state.settings_unlocked = False

def now_wib():
    return datetime.now(WIB)

def now_str():
    return now_wib().strftime("%Y-%m-%d %H:%M:%S WIB")

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        item_name TEXT PRIMARY KEY,
        total INTEGER NOT NULL,
        available INTEGER NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT NOT NULL,
        nim TEXT NOT NULL,
        items TEXT NOT NULL,
        tujuan TEXT,
        waktu_pinjam TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS returns (
        return_id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER NOT NULL,
        nama TEXT NOT NULL,
        items TEXT NOT NULL,
        waktu_kembali TEXT NOT NULL,
        kondisi TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS damages (
        damage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        tanggal TEXT NOT NULL,
        nama TEXT NOT NULL,
        alat TEXT NOT NULL,
        jumlah INTEGER NOT NULL,
        kondisi TEXT NOT NULL,
        keterangan TEXT NOT NULL
    )
    """)

    for item in INVENTORY:
        cur.execute("SELECT item_name FROM inventory WHERE item_name = ?", (item,))
        if cur.fetchone() is None:
            cur.execute(
                "INSERT INTO inventory (item_name, total, available) VALUES (?, ?, ?)",
                (item, 5, 5)
            )

    conn.commit()
    conn.close()

init_db()

def get_inventory_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT item_name AS alat, total, available FROM inventory ORDER BY item_name", conn)
    conn.close()
    return df

def update_inventory_item(item_name, total, available):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE inventory SET total = ?, available = ? WHERE item_name = ?",
        (int(total), int(available), item_name)
    )
    conn.commit()
    conn.close()

def get_loans_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM loans ORDER BY loan_id DESC", conn)
    conn.close()
    if df.empty:
        return pd.DataFrame(columns=["loan_id", "nama", "nim", "alat", "jumlah", "tujuan", "waktu_pinjam", "status"])
    rows = []
    for _, r in df.iterrows():
        items = eval(r["items"])
        rows.append({
            "loan_id": r["loan_id"],
            "nama": r["nama"],
            "nim": r["nim"],
            "alat": ", ".join([f"{k} x{v}" for k, v in items.items()]),
            "jumlah": sum(items.values()),
            "tujuan": r["tujuan"],
            "waktu_pinjam": r["waktu_pinjam"],
            "status": r["status"],
        })
    return pd.DataFrame(rows)

def get_returns_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM returns ORDER BY return_id DESC", conn)
    conn.close()
    if df.empty:
        return pd.DataFrame(columns=["return_id", "loan_id", "nama", "alat", "jumlah", "waktu_kembali", "kondisi"])
    rows = []
    for _, r in df.iterrows():
        items = eval(r["items"])
        rows.append({
            "return_id": r["return_id"],
            "loan_id": r["loan_id"],
            "nama": r["nama"],
            "alat": ", ".join([f"{k} x{v}" for k, v in items.items()]),
            "jumlah": sum(items.values()),
            "waktu_kembali": r["waktu_kembali"],
            "kondisi": r["kondisi"],
        })
    return pd.DataFrame(rows)

def get_damages_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM damages ORDER BY damage_id DESC", conn)
    conn.close()
    return df

def check_availability(requested):
    conn = get_conn()
    cur = conn.cursor()
    for alat, qty in requested.items():
        cur.execute("SELECT available FROM inventory WHERE item_name = ?", (alat,))
        row = cur.fetchone()
        if row is None:
            conn.close()
            return False, f"Alat '{alat}' tidak dikenal."
        if qty > row["available"]:
            conn.close()
            return False, f"Stok '{alat}' tidak cukup (tersedia {row['available']})."
    conn.close()
    return True, "Ok"

def apply_bluetheme_style():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #e0f2ff 0%, #dbeafe 35%, #bfdbfe 100%);
        color: #0f4d7f !important;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0284c7 0%, #0ea5e9 100%) !important;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    .header-title {
        color: #0369a1;
        font-weight: 800;
        font-size: 32px;
        margin-bottom: 6px;
        text-shadow: 0 2px 6px rgba(165,211,239,0.4);
    }
    .section-title {
        color: #0284c7;
        font-weight: 700;
        font-size: 22px;
        margin-top: 16px;
    }
    .card-box {
        background: rgba(255,255,255,0.85);
        padding: 16px 18px;
        border-radius: 18px;
        border: 1px solid rgba(99,170,253,0.25);
        box-shadow: 0 6px 18px rgba(14,165,233,0.12);
        margin-bottom: 12px;
    }
    .card-title {
        color: #0369a1;
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 6px;
    }
    .card-sub {
        color: #1f2937;
        font-size: 15px;
        margin: 0;
    }
    .stock-ok {
        color: #059669;
        font-weight: 700;
    }
    .stock-empty {
        color: #dc2632;
        font-weight: 700;
    }
    .form-box {
        background: rgba(255,255,255,0.92);
        padding: 18px 20px;
        border-radius: 20px;
        border: 1px solid rgba(99,170,253,0.3);
        box-shadow: 0 8px 24px rgba(14,165,233,0.14);
    }
    .select-box {
        background: #f0f9ff;
        padding: 10px 12px;
        border-radius: 14px;
        border: 1px solid #bae6fd;
        color: #0c4a6e;
    }
    .empty-box {
        background: #fee2e2;
        padding: 10px 12px;
        border-radius: 14px;
        border: 1px solid #fca5a5;
        color: #991b1b;
    }
    .stDataFrame {
        background: rgba(255,255,255,0.92);
        border-radius: 14px;
        padding: 8px;
    }
    .btn-primary button {
        background: linear-gradient(90deg, #0284c7 0%, #0ea5e9 100%) !important;
        color: white !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

apply_bluetheme_style()

st.sidebar.title("Menu Logbook Digital")
page = st.sidebar.radio("Pilih halaman", ["Dashboard", "Peminjaman", "Pengembalian", "Log", "Edukasi", "Pengaturan"])

if page == "Dashboard":
    st.markdown("<h1 class='header-title'>Manajemen Logbook Digital Praktikum Titrimetri</h1>", unsafe_allow_html=True)
    st.markdown("Ringkasan stok alat dan aktivitas terkini.")

    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown("<div class='card-box'><div class='card-title'>Stok Alat</div></div>", unsafe_allow_html=True)
        inv = get_inventory_df()
        for _, row in inv.iterrows():
            warna = "stock-ok" if int(row["available"]) > 0 else "stock-empty"
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="card-title">{row['alat']}</div>
                    <div class="card-sub" class="{warna}">
                        Total: {int(row['available'])} / {int(row['total'])}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("<div class='card-box'><div class='card-title'>Aktivitas Terakhir</div></div>", unsafe_allow_html=True)

        st.markdown("<div class='card-box'><div class='card-title'>📥 Peminjaman terbaru</div></div>", unsafe_allow_html=True)
        loans = get_loans_df().head(5)
        if loans.empty:
            st.info("Belum ada peminjaman.")
        else:
            st.dataframe(loans, use_container_width=True)

        st.markdown("<div class='card-box'><div class='card-title'>📤 Pengembalian terbaru</div></div>", unsafe_allow_html=True)
        returns = get_returns_df().head(5)
        if returns.empty:
            st.info("Belum ada pengembalian.")
        else:
            st.dataframe(returns, use_container_width=True)

if page == "Peminjaman":
    st.markdown("<h1 class='section-title'>Form Peminjaman Alat</h1>", unsafe_allow_html=True)
    st.caption(f"Waktu sekarang: {now_str()}")
    with st.form("form_pinjam", clear_on_submit=False):
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        nama = st.text_input("Nama lengkap")
        nim = st.text_input("NIM / ID")
        tujuan = st.text_area("Tujuan / Praktikum (opsional)")

        st.markdown("### Pilih alat dan jumlah")
        inv = get_inventory_df()
        requested = {}
        cols = st.columns(3)

        for i, alat in enumerate(INVENTORY):
            c = cols[i % 3]
            row = inv[inv["alat"] == alat]
            max_av = int(row["available"].iloc[0]) if not row.empty else 0

            if max_av > 0:
                c.markdown(f"<div class='select-box'><b>{alat}</b><br>Tersedia: {max_av}</div>", unsafe_allow_html=True)
            else:
                c.markdown(f"<div class='empty-box'><b>{alat}</b><br>Stok habis</div>", unsafe_allow_html=True)

            qty = c.number_input(
                f"Jumlah {alat}",
                min_value=0,
                max_value=max_av,
                value=0,
                step=1,
                key=f"pin_{alat}"
            )
            if qty > 0:
                requested[alat] = int(qty)

        st.markdown("</div>", unsafe_allow_html=True)
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
                    conn = get_conn()
                    cur = conn.cursor()
                    for alat, q in requested.items():
                        cur.execute("UPDATE inventory SET available = available - ? WHERE item_name = ?", (q, alat))
                    cur.execute(
                        "INSERT INTO loans (nama, nim, items, tujuan, waktu_pinjam, status) VALUES (?, ?, ?, ?, ?, ?)",
                        (nama, nim, str(requested), tujuan, now_str(), "dipinjam")
                    )
                    conn.commit()
                    conn.close()
                    st.success("Peminjaman dicatat.")
                    st.info("Data peminjaman ini akan terlihat oleh pengguna lain di halaman Log.")

if page == "Pengembalian":
    st.markdown("<h1 class='section-title'>Form Pengembalian Alat</h1>", unsafe_allow_html=True)
    st.caption(f"Waktu sekarang: {now_str()}")
    loans_df = get_loans_df()
    active_loans = loans_df[loans_df["status"] == "dipinjam"]

    if active_loans.empty:
        st.info("Tidak ada peminjaman aktif saat ini.")
    else:
        with st.form("form_kembali", clear_on_submit=False):
            st.markdown("<div class='form-box'>", unsafe_allow_html=True)
            options = active_loans.apply(
                lambda r: f'{r["loan_id"]} - {r["nama"]} ({r["nim"]}) - {r["alat"]}',
                axis=1
            ).tolist()
            sel = st.selectbox("Pilih peminjaman", options=options)
            selected_id = int(sel.split(" - ")[0])

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT * FROM loans WHERE loan_id = ?", (selected_id,))
            loan_row = cur.fetchone()
            conn.close()

            items = eval(loan_row["items"])
            returned = {}
            cols = st.columns(3)
            for i, alat in enumerate(items.keys()):
                c = cols[i % 3]
                max_return = items[alat]
                qty = c.number_input(
                    f"{alat} (maks {max_return})",
                    min_value=0,
                    max_value=max_return,
                    value=max_return,
                    step=1,
                    key=f"ret_{selected_id}_{alat}"
                )
                if qty > 0:
                    returned[alat] = int(qty)

            kondisi = st.selectbox("Kondisi alat setelah dikembalikan", ["baik", "rusak ringan", "rusak berat"])
            st.markdown("</div>", unsafe_allow_html=True)
            submit_ret = st.form_submit_button("Kembalikan")

            if submit_ret:
                if not returned:
                    st.error("Pilih minimal satu alat yang dikembalikan.")
                else:
                    conn = get_conn()
                    cur = conn.cursor()
                    for alat, q in returned.items():
                        cur.execute("UPDATE inventory SET available = available + ? WHERE item_name = ?", (q, alat))
                        items[alat] -= q

                    if all(v == 0 for v in items.values()):
                        cur.execute("UPDATE loans SET status = ? WHERE loan_id = ?", ("dikembalikan", selected_id))
                    else:
                        cur.execute("UPDATE loans SET items = ? WHERE loan_id = ?", (str(items), selected_id))

                    cur.execute(
                        "INSERT INTO returns (loan_id, nama, items, waktu_kembali, kondisi) VALUES (?, ?, ?, ?, ?)",
                        (selected_id, loan_row["nama"], str(returned), now_str(), kondisi)
                    )
                    conn.commit()
                    conn.close()
                    st.success("Pengembalian dicatat.")

if page == "Log":
    st.markdown("<h1 class='section-title'>Catatan Peminjaman, Pengembalian, dan Kerusakan</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Peminjaman", "Pengembalian", "Kerusakan"])

    with tab1:
        st.dataframe(get_loans_df(), use_container_width=True)

    with tab2:
        st.dataframe(get_returns_df(), use_container_width=True)

    with tab3:
        with st.form("form_rusak", clear_on_submit=False):
            nama = st.text_input("Nama pelapor")
            alat_rusak = st.selectbox("Pilih alat yang rusak", INVENTORY)
            jumlah_rusak = st.number_input("Jumlah rusak", min_value=1, max_value=100, value=1, step=1)
            kondisi = st.selectbox("Tingkat kerusakan", ["rusak ringan", "rusak sedang", "rusak berat"])
            keterangan = st.text_area("Keterangan kerusakan")
            submit_rusak = st.form_submit_button("Simpan Kerusakan")

            if submit_rusak:
                conn = get_conn()
                cur = conn.cursor()

                cur.execute("SELECT available FROM inventory WHERE item_name = ?", (alat_rusak,))
                row = cur.fetchone()
                available_now = row["available"] if row else 0
                jumlah_simpan = min(int(jumlah_rusak), available_now)

                cur.execute(
                    "INSERT INTO damages (tanggal, nama, alat, jumlah, kondisi, keterangan) VALUES (?, ?, ?, ?, ?, ?)",
                    (now_str(), nama if nama else "-", alat_rusak, jumlah_simpan, kondisi, keterangan if keterangan else "-")
                )

                cur.execute(
                    "UPDATE inventory SET available = available - ? WHERE item_name = ?",
                    (jumlah_simpan, alat_rusak)
                )

                conn.commit()
                conn.close()
                st.success("Kerusakan alat berhasil dicatat, stok di Dashboard sudah berkurang.")
                st.rerun()

        st.dataframe(get_damages_df(), use_container_width=True)

    st.markdown("### Ekspor log")
    df_loans = get_loans_df()
    df_returns = get_returns_df()
    df_damages = get_damages_df()

    if not df_loans.empty:
        st.download_button("Unduh CSV Peminjaman", df_loans.to_csv(index=False), file_name="log_peminjaman.csv", mime="text/csv")
    if not df_returns.empty:
        st.download_button("Unduh CSV Pengembalian", df_returns.to_csv(index=False), file_name="log_pengembalian.csv", mime="text/csv")
    if not df_damages.empty:
        st.download_button("Unduh CSV Kerusakan", df_damages.to_csv(index=False), file_name="log_kerusakan.csv", mime="text/csv")

if page == "Edukasi":
    st.markdown("<h1 class='section-title'>Edukasi Alat Praktikum Laboratorium</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card-box'>Pilih alat untuk melihat deskripsi singkat, penggunaan, dan tips keselamatan.</div>", unsafe_allow_html=True)
    alat = st.selectbox("Pilih alat", INVENTORY)
    st.subheader(alat)

    descriptions = {
        "labu takar 100 mL": "Alat untuk melarutkan bahan kimia. Gunakan pada permukaan datar dan baca meniskus atau tanda tera yang sejajar dengan mata.",
        "buret": "Alat untuk titrasi dengan skala graduasi dan kran di bawah. Pastikan bebas gelembung udara sebelum dipakai.",
        "klamp": "Digunakan untuk menjepit buret atau alat lain pada statif agar stabil.",
        "erlenmeyer 250 mL": "Wadah reaksi untuk titrasi. Bentuknya memudahkan pengadukan dan proses titrasi tanpa mudah tumpah.",
        "corong kaca": "Untuk memindahkan cairan atau filtrasi.",
        "batang pengaduk": "Untuk mengaduk larutan agar homogen dan menyeka.",
        "pipet tetes": "Untuk meneteskan larutan dalam jumlah kecil.",
        "kaca arloji": "Untuk menimbang sampel kecil atau menutup bejana.",
        "tutup kaca": "Untuk menutup bejana agar tidak terkontaminasi dan alas menimbang bahan kimia padatan.",
        "gelas piala 500 mL": "Gelas piala berukuran 500 mL untuk menampung, mencampur, atau memanaskan larutan.",
        "gelas piala 100 mL": "Gelas piala kecil untuk volume larutan yang lebih sedikit.",
        "pipet volumetrik 25 mL": "Pipet untuk mengambil volume tetap 25 mL secara sangat presisi.",
        "pipet volumetrik 50 mL": "Pipet untuk mengambil volume tetap 50 mL secara sangat presisi.",
        "bulb": "Karet pengisap untuk membantu mengisi pipet tanpa mulut.",
        "kaki 3": "Penyangga logam untuk pemanasan dengan bunsen.",
        "kasa asbes": "Kasa untuk meratakan panas saat pemanasan.",
        "bunsen": "Pembakar gas untuk pemanasan laboratorium.",
        "pipet mohr 10 mL": "Pipet ukur untuk mengambil volume hingga 10 mL secara bertahap.",
        "statif": "Stand untuk menjepit buret, corong, atau alat lain.",
        "gelas ukur 10 mL": "Gelas ukur kecil untuk mengukur volume sampai 10 mL.",
        "gelas ukur 50 mL": "Gelas ukur untuk volume sampai 50 mL.",
        "tabung reaksi": "Wadah reaksi skala kecil.",
        "rak tabung reaksi": "Tempat meletakkan tabung reaksi agar tegak dan aman.",
    }

    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.write(descriptions.get(alat, "Deskripsi tidak tersedia."))
    st.markdown("</div>", unsafe_allow_html=True)

if page == "Pengaturan":
    st.markdown("<h1 class='section-title'>Pengaturan Sistem</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card-box'>Hanya pihak lab yang boleh mengubah jumlah alat. Masukkan password untuk membuka akses.</div>", unsafe_allow_html=True)

    def password_entered():
        if st.session_state.get("admin_password_input") == ADMIN_PASSWORD:
            st.session_state.settings_unlocked = True
            del st.session_state["admin_password_input"]
        else:
            st.session_state.settings_unlocked = False

    if not st.session_state.settings_unlocked:
        st.text_input("Masukkan password admin", type="password", key="admin_password_input", on_change=password_entered)
        st.warning("Akses pengaturan terkunci.")
    else:
        st.success("Akses pengaturan berhasil dibuka.")
        inv = get_inventory_df()

        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("<div class='card-box'><div class='card-title'>Atur stok tiap alat</div></div>", unsafe_allow_html=True)
            for alat in INVENTORY:
                row = inv[inv["alat"] == alat]
                current_total = int(row["total"].iloc[0]) if not row.empty else 0
                current_avail = int(row["available"].iloc[0]) if not row.empty else 0
                val = st.number_input(
                    f"Total {alat}",
                    min_value=0,
                    max_value=100,
                    value=current_total,
                    key=f"set_{alat}"
                )
                if val != current_total:
                    diff = int(val) - current_total
                    new_available = max(0, min(current_avail + diff, int(val)))
                    update_inventory_item(alat, int(val), new_available)

        with cols[1]:
            st.markdown("<div class='card-box'><div class='card-title'>Reset data</div></div>", unsafe_allow_html=True)
            if st.button("Reset semua log"):
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM loans")
                cur.execute("DELETE FROM returns")
                cur.execute("DELETE FROM damages")
                for item in INVENTORY:
                    cur.execute("UPDATE inventory SET total = 5, available = 5 WHERE item_name = ?", (item,))
                conn.commit()
                conn.close()
                st.success("Data di-reset.")
