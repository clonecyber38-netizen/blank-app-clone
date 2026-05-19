import streamlit as st

st.title("🎈 MAGALI BELOM MANDI")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st

st.markdown("*magali* itu **males** ***mandi***.")
st.markdown('''
    :red[kita] :orange[semua] :green[gatau] :blue[kenapa] :violet[magali]
    :gray[males] :rainbow[mandi] dan :blue-background[magali] mager.''')
st.markdown("Here's a bouquet FOR magali si males mandi &mdash;\
            :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")

multi = '''mandi lah sebelum di mandikan

biarkan air yg menemuiku
'''
st.markdown(multi)
import streamlit as st

# Mengatur judul halaman aplikasi
st.set_page_config(page_title="Kalkulator Sederhana", page_icon="🧮")

st.title("🧮 Kalkulator Sederhana")
st.write("Silakan masukkan angka dan pilih operasi matematika yang diinginkan.")

st.divider()

# Membuat dua kolom untuk input angka agar tampilan lebih rapi
col1, col2 = st.columns(2)

with col1:
    angka_1 = st.number_input("Masukkan Angka Pertama:", value=0.0, step=1.0)

with col2:
    angka_2 = st.number_input("Masukkan Angka Kedua:", value=0.0, step=1.0)

# Pilihan operasi matematika
operasi = st.selectbox(
    "Pilih Operasi:",
    ("Penjumlahan (+)", "Pengurangan (-)", "Perkalian (×)", "Pembagian (÷)")
)

# Tombol untuk menghitung
if st.button("Hitung", type="primary"):
    hasil = 0
    error_message = None
    
    if operasi == "Penjumlahan (+)":
        hasil = angka_1 + angka_2
    elif operasi == "Pengurangan (-)":
        hasil = angka_1 - angka_2
    elif operasi == "Perkalian (×)":
        hasil = angka_1 * angka_2
    elif operasi == "Pembagian (÷)":
        if angka_2 != 0:
            hasil = angka_1 / angka_2
        else:
            error_message = "Error: Tidak bisa membagi dengan angka nol!"

    # Menampilkan hasil
    st.divider()
    if error_message:
        st.error(error_message)
    else:
        # Menampilkan hasil dengan format box sukses yang menarik
        st.success(f"### Hasil: {hasil}")
