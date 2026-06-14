import streamlit as st
import pandas as pd
import sqlite3
import json
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
        try:
            items = json.loads(r["items"])
        except:
            try:
                items = eval(r["items"])
            except:
                items = {}
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
        try:
            items = json.loads(r["items"])
        except:
            try:
                items = eval(r["items"])
            except:
                items = {}
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
        color: #059669 !important;
        font-weight: 700;
    }
    .stock-empty {
        color: #dc2626 !important;
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
    .team-table {
        width: 100%;
        border-collapse: collapse;
        background-color: white;
        border-radius: 10px;
        overflow: hidden;
    }
    .team-table th {
        background-color: #0284c7;
        color: white !important;
        text-align: left;
        padding: 10px;
    }
    .team-table td {
        padding: 10px;
        border-bottom: 1px solid #e0f2ff;
        color: #0f4d7f;
    }
    </style>
    """, unsafe_allow_html=True)

apply_bluetheme_style()

st.sidebar.title("Menu Logbook Digital")
page = st.sidebar.radio("Pilih halaman", ["Dashboard", "Peminjaman", "Pengembalian", "Log", "Edukasi", "Pengaturan"])

if page == "Dashboard":
    st.markdown("<h1 class='header-title'>Manajemen Logbook Digital Praktikum Titrimetri</h1>", unsafe_allow_html=True)
    st.markdown("Ringkasan stok alat dan aktivitas terkini.")

    # MENAMPILKAN NAMA PENYUSUN KELOMPOK DI SINI
    st.markdown("""
    <div class="card-box" style="background: rgba(255, 255, 255, 0.95); border-left: 5px solid #0284c7;">
        <div class="card-title" style="font-size: 16px; margin-bottom: 10px;">📋 Tim Penyusun Sistem Logbook:</div>
        <table class="team-table">
            <tr>
                <th>Nama Lengkap</th>
                <th>NIM / ID Anggota</th>
            </tr>
            <tr><td>Anindhya Halwa Ariani</td><td><strong>2560575</strong></td></tr>
            <tr><td>Fikri Fadhilah</td><td><strong>2560633</strong></td></tr>
            <tr><td>Kevin Kalyana Dharma</td><td><strong>2560658</strong></td></tr>
            <tr><td>Nasywaa Rihhadatul Aisya</td><td><strong>2560713</strong></td></tr>
            <tr><td>Siti Azra Alfashahah</td><td><strong>2560783</strong></td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown("<h3 class='section-title'>Stok Alat Saat Ini</h3>", unsafe_allow_html=True)
        inv = get_inventory_df()
        for _, row in inv.iterrows():
            warna = "stock-ok" if int(row["available"]) > 0 else "stock-empty"
            st.markdown(
                f"""
                <div class="card-box">
                    <div class="card-title">{row['alat']}</div>
                    <div class="card-sub {warna}">
                        Tersedia untuk Dipinjam: {int(row['available'])} / {int(row['total'])} unit
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    with col2:
        st.markdown("<h3 class='section-title'>Aktivitas Terakhir</h3>", unsafe_allow_html=True)

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
    with st.form("form_pinjam", clear_on_submit=True):
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

        submit = st.form_submit_button("Konfirmasi Pinjam")
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
                        (nama, nim, json.dumps(requested), tujuan, now_str(), "dipinjam")
                    )
                    conn.commit()
                    conn.close()
                    st.success("Peminjaman berhasil dicatat!")
                    st.rerun()

if page == "Pengembalian":
    st.markdown("<h1 class='section-title'>Form Pengembalian Alat</h1>", unsafe_allow_html=True)
    st.caption(f"Waktu sekarang: {now_str()}")
    
    loans_df = get_loans_df()
    active_loans = loans_df[loans_df["status"] == "dipinjam"]

    if active_loans.empty:
        st.info("Tidak ada peminjaman aktif saat ini.")
    else:
        options = active_loans.apply(
            lambda r: f'{r["loan_id"]} - {r["nama"]} ({r["nim"]}) - {r["alat"]}',
            axis=1
        ).tolist()
        
        sel = st.selectbox("Pilih data peminjaman aktif:", options=options, key="select_pengembalian_aktif")
        selected_id = int(sel.split(" - ")[0])

        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM loans WHERE loan_id = ?", (selected_id,))
        loan_row = cur.fetchone()
        conn.close()

        try:
            items = json.loads(loan_row["items"])
        except:
            try:
                items = eval(loan_row["items"])
            except:
                items = {}

        items = {k: v for k, v in items.items() if v > 0}

        with st.form(f"form_kembali_id_{selected_id}", clear_on_submit=True):
            st.markdown("<div class='form-box'>", unsafe_allow_html=True)
            st.markdown(f"### Detail alat yang harus dikembalikan (ID Peminjaman: {selected_id}):")
            
            returned = {}
            cols = st.columns(3)
            
            for i, alat in enumerate(items.keys()):
                c = cols[i % 3]
                max_return = int(items[alat])
                
                qty = c.number_input(
                    f"{alat} (maks {max_return})",
                    min_value=0,
                    max_value=max_return,
                    value=max_return,
                    step=1,
                    key=f"input_numeric_{selected_id}_{alat}"
                )
                if qty > 0:
                    returned[alat] = int(qty)

            kondisi = st.selectbox("Kondisi alat setelah dikembalikan", ["baik", "rusak ringan", "rusak berat"], key=f"kondisi_{selected_id}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            submit_ret = st.form_submit_button("Konfirmasi Pengembalian")

            if submit_ret:
                if not returned:
                    st.error("Pilih minimal satu alat yang dikembalikan.")
                else:
                    conn = get_conn()
                    cur = conn.cursor()
                    
                    for alat, q in returned.items():
                        cur.execute("UPDATE inventory SET available = available + ? WHERE item_name = ?", (q, alat))
                        if alat in items:
                            items[alat] -= q

                    items = {k: v for k, v in items.items() if v > 0}

                    if not items:
                        cur.execute("UPDATE loans SET status = ? WHERE loan_id = ?", ("dikembalikan", selected_id))
                    else:
                        cur.execute("UPDATE loans SET items = ? WHERE loan_id = ?", (json.dumps(items), selected_id))

                    cur.execute(
                        "INSERT INTO returns (loan_id, nama, items, waktu_kembali, kondisi) VALUES (?, ?, ?, ?, ?)",
                        (selected_id, loan_row["nama"], json.dumps(returned), now_str(), kondisi)
                    )
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Pengembalian untuk transaksi ID {selected_id} berhasil dicatat!")
                    st.rerun()

if page == "Log":
    st.markdown("<h1 class='section-title'>Catatan Peminjaman, Pengembalian, dan Kerusakan</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📋 Peminjaman", "🔄 Pengembalian", "⚠️ Kerusakan Alat"])

    with tab1:
        st.dataframe(get_loans_df(), use_container_width=True)

    with tab2:
        st.dataframe(get_returns_df(), use_container_width=True)

    with tab3:
        with st.form("form_rusak", clear_on_submit=True):
            st.write("### Laporkan Kerusakan Alat Baru")
            nama = st.text_input("Nama pelapor")
            alat_rusak = st.selectbox("Pilih alat yang rusak", INVENTORY)
            jumlah_rusak = st.number_input("Jumlah rusak", min_value=1, max_value=100, value=1, step=1)
            kondisi = st.selectbox("Tingkat kerusakan", ["rusak ringan", "rusak sedang", "rusak berat"])
            keterangan = st.text_area("Keterangan detail kerusakan")
            submit_rusak = st.form_submit_button("Simpan Laporan")

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
                st.success("Kerusakan alat berhasil dicatat, stok otomatis disesuaikan.")
                st.rerun()

        st.write("### Riwayat Kerusakan")
        st.dataframe(get_damages_df(), use_container_width=True)

    st.markdown("### 📥 Ekspor Log Data (Format CSV)")
    df_loans = get_loans_df()
    df_returns = get_returns_df()
    df_damages = get_damages_df()

    col_dl1, col_dl2, col_dl3 = st.columns(3)
    if not df_loans.empty:
        col_dl1.download_button("Unduh CSV Peminjaman", df_loans.to_csv(index=False), file_name="log_peminjaman.csv", mime="text/csv", use_container_width=True)
    if not df_returns.empty:
        col_dl2.download_button("Unduh CSV Pengembalian", df_returns.to_csv(index=False), file_name="log_pengembalian.csv", mime="text/csv", use_container_width=True)
    if not df_damages.empty:
        col_dl3.download_button("Unduh CSV Kerusakan", df_damages.to_csv(index=False), file_name="log_kerusakan.csv", mime="text/csv", use_container_width=True)

if page == "Edukasi":
    st.markdown("<h1 class='section-title'>Edukasi Alat Praktikum Laboratorium</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card-box'>Pilih alat untuk melihat deskripsi singkat, penggunaan, dan tips keselamatan.</div>", unsafe_allow_html=True)
    alat = st.selectbox("Pilih jenis alat:", INVENTORY)
    st.subheader(f"💡 Detail Alat: {alat.title()}")

    descriptions = {
        "labu takar 100 mL": "Alat untuk melarutkan bahan kimia dengan volume presisi tinggi. Gunakan pada permukaan datar dan baca meniskus secara sejajar dengan mata.",
        "buret": "Alat untuk titrasi dengan skala graduasi ketat dan kran di bawah. Pastikan bebas gelembung udara pada ujung buret sebelum dipakai.",
        "klamp": "Digunakan untuk menjepit buret atau alat gelas lain pada statif agar posisinya stabil dan tegak lurus.",
        "erlenmeyer 250 mL": "Wadah penampung larutan analat selama proses titrasi. Bentuk konis memudahkan pengadukan memutar (swirling) tanpa tumpah.",
        "corong kaca": "Untuk membantu memindahkan cairan ke wadah bermulut kecil atau menyangga kertas saring pada filtrasi.",
        "batang pengaduk": "Untuk menghomogenkan larutan padat/cair dan membantu mengalirkan cairan saat penuangan.",
        "pipet tetes": "Untuk mengambil dan meneteskan larutan atau indikator dalam skala kecil (tetesan).",
        "kaca arloji": "Tempat menimbang bahan kimia berupa padatan/kristal atau sebagai penutup gelas piala.",
        "tutup kaca": "Untuk menutup bejana atau labu takar agar larutan di dalamnya terlindung dari kontaminasi udara.",
        "gelas piala 500 mL": "Wadah preparasi untuk menampung, melarutkan, atau memanaskan larutan analat/pereaksi.",
        "gelas piala 100 mL": "Gelas piala ukuran kecil untuk mengambil larutan indikator atau cairan dalam volume sedikit.",
        "pipet volumetrik 25 mL": "Pipet gondok dengan tingkat akurasi tinggi untuk memindahkan tepat 25 mL larutan primer/sekunder.",
        "pipet volumetrik 50 mL": "Pipet gondok dengan tingkat akurasi tinggi untuk memindahkan tepat 50 mL larutan.",
        "bulb": "Karet pengisap (three-way rubber bulb) untuk menyedot larutan berbahaya dengan aman menggunakan pipet volumetrik/Mohr.",
        "kaki 3": "Penyangga besi untuk menahan wadah gelas saat proses pemanasan larutan.",
        "kasa asbes": "Alas perata panas di atas kaki tiga agar gelas kimia tidak retak/pecah terkena api langsung.",
        "bunsen": "Sumber pemanas utama menggunakan bahan bakar gas untuk memanaskan larutan pereaksi.",
        "pipet mohr 10 mL": "Pipet ukur bergraduasi untuk memindahkan larutan dengan volume bervariasi hingga maksimal 10 mL.",
        "statif": "Tiang penyangga utama tempat memasang klamp pemegang buret.",
        "gelas ukur 10 mL": "Mengukur volume cairan dengan tingkat ketelitian menengah (skala kasar) hingga batas 10 mL.",
        "gelas ukur 50 mL": "Mengukur volume cairan dengan tingkat ketelitian menengah hingga batas 50 mL.",
        "tabung reaksi": "Tempat mereaksikan zat kimia dalam skala kualitatif kecil.",
        "rak tabung reaksi": "Tempat meletakkan tabung reaksi agar tetap tegak, tertata raki, dan mencegah risiko pecah.",
    }

    st.markdown("<div class='card-box'>", unsafe_allow_html=True)
    st.write(descriptions.get(alat, "Deskripsi tidak tersedia."))
    st.markdown("</div>", unsafe_allow_html=True)

if page == "Pengaturan":
    st.markdown("<h1 class='section-title'>Pengaturan Sistem Lab</h1>", unsafe_allow_html=True)
    st.markdown("<div class='card-box'>Hanya laboran atau pihak berwenang yang boleh mengubah stok awal alat lab.</div>", unsafe_allow_html=True)

    def password_entered():
        if st.session_state.get("admin_password_input") == ADMIN_PASSWORD:
            st.session_state.settings_unlocked = True
        else:
            st.error("Password salah!")
            st.session_state.settings_unlocked = False

    if not st.session_state.settings_unlocked:
        st.text_input("Masukkan password admin", type="password", key="admin_password_input", on_change=password_entered)
        st.warning("Akses pengaturan terkunci.")
    else:
        st.success("Akses panel kontrol laboran terbuka.")
        inv = get_inventory_df()

        cols = st.columns([2, 1])
        with cols[0]:
            st.markdown("### 🛠️ Perbarui Total Kapasitas Alat")
            with st.form("form_update_stok"):
                updates = {}
                for alat in INVENTORY:
                    row = inv[inv["alat"] == alat]
                    current_total = int(row["total"].iloc[0]) if not row.empty else 5
                    current_avail = int(row["available"].iloc[0]) if not row.empty else 5
                    
                    val = st.number_input(
                        f"Total {alat}",
                        min_value=0,
                        max_value=200,
                        value=current_total,
                        key=f"set_{alat}"
                    )
                    updates[alat] = (val, current_total, current_avail)
                
                btn_save_stok = st.form_submit_button("Simpan Perubahan Stok")
                if btn_save_stok:
                    for alat, (new_total, old_total, old_avail) in updates.items():
                        if new_total != old_total:
                            diff = new_total - old_total
                            new_available = max(0, min(old_avail + diff, new_total))
                            update_inventory_item(alat, new_total, new_available)
                    st.success("Stok inventaris berhasil diperbarui!")
                    st.rerun()

        with cols[1]:
            st.markdown("### 🚨 Zona Bahaya")
            if st.button("Reset Semua Log & Data"):
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("DELETE FROM loans")
                cur.execute("DELETE FROM returns")
                cur.execute("DELETE FROM damages")
                for item in INVENTORY:
                    cur.execute("UPDATE inventory SET total = 5, available = 5 WHERE item_name = ?", (item,))
                conn.commit()
                conn.close()
                st.success("Semua data logbook dan stok telah di-reset ke pengaturan awal!")
                st.rerun()
