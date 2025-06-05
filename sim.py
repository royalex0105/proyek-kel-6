import streamlit as st
from datetime import datetime
import os
import hashlib
import pandas as pd



# ---------------- Helper Functions ----------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_file(base_filename, username):
    # contoh: pemasukan_user1.csv
    name, ext = os.path.splitext(base_filename)
    return f"{name}_{username}{ext}"

def load_data(base_filename, username):
    filename = get_user_file(base_filename, username)
    if os.path.exists(filename):
        try:
            return pd.read_csv(filename)
        except pd.errors.EmptyDataError:
            # Jika file kosong, buat DataFrame kosong dengan kolom sesuai file yang dipakai
            if "pemasukan" in filename:
                return pd.DataFrame(columns=["Tanggal", "Sumber", "Jumlah", "Metode", "Keterangan", "Username"])
            elif "pengeluaran" in filename:
                return pd.DataFrame(columns=["Tanggal", "Kategori", "Sub Kategori", "Jumlah", "Keterangan", "Metode", "Username"])
            elif "jurnal" in filename:
                return pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan"])
            else:
                return pd.DataFrame()
    else:
        # Jika file belum ada, buat DataFrame kosong dengan kolom sesuai file
        if "pemasukan" in base_filename:
            return pd.DataFrame(columns=["Tanggal", "Sumber", "Jumlah", "Metode", "Keterangan", "Username"])
        elif "pengeluaran" in base_filename:
            return pd.DataFrame(columns=["Tanggal", "Kategori", "Sub Kategori", "Jumlah", "Keterangan", "Metode", "Username"])
        elif "jurnal" in base_filename:
            return pd.DataFrame(columns=["Tanggal", "Akun", "Debit", "Kredit", "Keterangan"])
        else:
            return pd.DataFrame()

def save_data(df, base_filename, username):
    filename = get_user_file(base_filename, username)
    df.to_csv(filename, index=False)

def append_data(data, base_filename, username):
    df = load_data(base_filename, username)
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    save_data(df, base_filename, username)

def buat_jurnal(tanggal, akun_debit, akun_kredit, jumlah, keterangan):
    return [
        {"Tanggal": tanggal, "Akun": akun_debit, "Debit": jumlah, "Kredit": 0, "Keterangan": keterangan},
        {"Tanggal": tanggal, "Akun": akun_kredit, "Debit": 0, "Kredit": jumlah, "Keterangan": keterangan},
    ]

def load_user_accounts():
    if os.path.exists("akun.csv"):
        return pd.read_csv("akun.csv")
    else:
        return pd.DataFrame(columns=["Username", "Password"])

def save_user_accounts(df):
    df.to_csv("akun.csv", index=False)

def register_user(username, password):
    akun_df = load_user_accounts()
    if (akun_df['Username'] == username).any():
        return False  # Username sudah ada
    akun_df = pd.concat([akun_df, pd.DataFrame([{"Username": username, "Password": hash_password(password)}])], ignore_index=True)
    save_user_accounts(akun_df)
    return True

def validate_login(username, password):
    akun_df = load_user_accounts()
    hashed_pw = hash_password(password)
    return ((akun_df['Username'] == username) & (akun_df['Password'] == hashed_pw)).any()

import streamlit as st

# ---------------- Login & Register ----------------

def login_register():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ""

    if st.session_state['logged_in']:
        return True

    st.title("🔐 Login / Daftar Akun")
    
    mode = st.radio("Pilih Mode", ["Login", "Daftar"])
    username = st.text_input("Nama Pengguna")
    password = st.text_input("Kata Sandi", type="password")

    if mode == "Login":
        if st.button("Masuk"):
            if username.strip() == "" or password.strip() == "":
                st.error("Harap isi semua kolom.")
            elif validate_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.success(f"Login berhasil! Selamat datang, {username}.")
                st.rerun()
            else:
                st.error("Username atau password salah.")

    else:  # Daftar
        if st.button("Daftar"):
            if username.strip() == "" or password.strip() == "":
                st.error("Harap isi semua kolom.")
            elif register_user(username, password):
                st.success("Akun berhasil dibuat. Silakan login.")
            else:
                st.error("Username sudah digunakan.")

    st.stop()
    return False


# ---------------- Data Kategori ----------------

kategori_pengeluaran = {
    "Bibit": ["Intani", "Inpari", "Ciherang", "32"],
    "Pupuk": ["Urea", "NPK", "Organik", "Ponska"],
    "Pestisida": ["Debestan", "Ronsa", "Refaton", "Ema", "Plenum"],
    "Alat Tani": ["Sabit", "Cangkul", "Karung"],
    "Tenaga Kerja": ["Upah Harian", "Borongan"],
    "Lainnya": ["Lain-lain"]
}
kategori_pemasukan = {
    "Sumber Pemasukan": ["Penjualan Padi", "Lain-lain"]
}

# ---------------- Fungsi Pemasukan ----------------

def pemasukan():
    st.subheader("Tambah Pemasukan")
    tanggal = st.date_input("Tanggal", datetime.now())
    sumber = st.selectbox("Sumber Pemasukan", kategori_pemasukan["Sumber Pemasukan"])
    jumlah = st.number_input("Jumlah (Rp)", min_value=0)
    deskripsi = st.text_area("Keterangan (opsional)") 
    metode = st.radio("Metode Penerimaan", ["Tunai", "Transfer", "Piutang", "Pelunasan Piutang"])

    if st.button("✅ Simpan Pemasukan"):
        if not sumber.strip() or jumlah <= 0:
            st.error("Isi data dengan benar.")
            return
        waktu = tanggal.strftime("%Y-%m-%d %H:%M:%S")
        username = st.session_state['username']
        data = {
            "Tanggal": waktu,
            "Sumber": sumber,
            "Jumlah": jumlah,
            "Metode": metode,
            "Keterangan": deskripsi,
            "Username": username
        }
        append_data(data, "pemasukan.csv", username)
        akun_debit = {
            "Tunai": "Kas",
            "Transfer": "Bank",
            "Piutang": "Piutang Dagang",
            "Pelunasan Piutang": "Kas"
        }[metode]
        akun_kredit = "Pendapatan" if metode != "Pelunasan Piutang" else "Piutang Dagang"
        jurnal = buat_jurnal(waktu, akun_debit, akun_kredit, jumlah, sumber)
        for j in jurnal:
            append_data(j, "jurnal.csv", username)
        st.success("✅ Pemasukan berhasil disimpan.")

# ---------------- Fungsi Pengeluaran ----------------

def pengeluaran():
    st.subheader("Tambah Pengeluaran")
    tanggal = st.date_input("Tanggal", datetime.now())
    kategori = st.selectbox("Kategori Utama", list(kategori_pengeluaran.keys()))
    sub_kategori = st.selectbox("Sub Kategori", kategori_pengeluaran[kategori])
    jumlah = st.number_input("Jumlah (Rp)", min_value=0)
    deskripsi = st.text_area("Keterangan (opsional)")
    metode = st.radio("Metode Pembayaran", ["Tunai", "Transfer", "Utang", "Pelunasan Utang"])

    if st.button("✅ Simpan Pengeluaran"):
        if jumlah <= 0:
            st.error("Jumlah tidak boleh 0.")
            return
        waktu = tanggal.strftime("%Y-%m-%d %H:%M:%S")
        username = st.session_state['username']
        data = {
            "Tanggal": waktu,
            "Kategori": kategori,
            "Sub Kategori": sub_kategori,
            "Jumlah": jumlah,
            "Keterangan": deskripsi,
            "Metode": metode,
            "Username": username
        }
        append_data(data, "pengeluaran.csv", username)
        akun_kredit = {
            "Tunai": "Kas",
            "Transfer": "Bank",
            "Utang": "Utang Dagang",
            "Pelunasan Utang": "Kas"
        }[metode]
        akun_debit = sub_kategori if metode != "Pelunasan Utang" else "Utang Dagang"
        jurnal = buat_jurnal(waktu, akun_debit, akun_kredit, jumlah, deskripsi)
        for j in jurnal:
            append_data(j, "jurnal.csv", username)
        st.success("✅ Pengeluaran berhasil disimpan.")

import streamlit as st
from datetime import datetime
import os
import hashlib
import pandas as pd

# ... (kode helper functions sebelumnya tetap sama) ...

# ---------------- Fungsi Hapus Transaksi (diperbarui) ----------------

def hapus_transaksi():
    st.subheader("Hapus Transaksi")
    username = st.session_state['username']
    transaksi_type = st.radio("Jenis Transaksi", ["Pemasukan", "Pengeluaran"])
    
    if transaksi_type == "Pemasukan":
        df = load_data("pemasukan.csv", username)
        file_type = "pemasukan"
    else:
        df = load_data("pengeluaran.csv", username)
        file_type = "pengeluaran"
    
    if df.empty:
        st.warning("Tidak ada data transaksi.")
        return
    
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df = df.sort_values('Tanggal', ascending=False)
    
    st.dataframe(df.style.format({
        'Tanggal': lambda x: x.strftime('%Y-%m-%d'),
        'Jumlah': 'Rp {:.0f}'.format
    }), height=400)
    
    index_to_delete = st.selectbox("Pilih nomor transaksi yang akan dihapus", df.index)
    
    if st.button("🗑️ Hapus Transaksi"):
        if hapus_transaksi(file_type, index_to_delete, username):
            st.success("Transaksi berhasil dihapus!")
            st.rerun()
        else:
            st.error("Gagal menghapus transaksi.")

# ---------------- Fungsi Laporan (diperbarui) ----------------

def laporan():
    import plotly.express as px
    st.header("📊 Laporan Keuangan")
    username = st.session_state['username']

    col1, col2 = st.columns(2)
    with col1:
        mulai = st.date_input("Tanggal Mulai", datetime.now().replace(day=1))
    with col2:
        akhir = st.date_input("Tanggal Akhir", datetime.now())

    pemasukan_df = load_data("pemasukan.csv", username)
    pengeluaran_df = load_data("pengeluaran.csv", username)
    jurnal_df = load_data("jurnal.csv", username)

    # Konversi tanggal
    for df in [pemasukan_df, pengeluaran_df, jurnal_df]:
        if not df.empty and "Tanggal" in df.columns:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"], errors='coerce')

    # Filter berdasarkan tanggal
    pemasukan_df = pemasukan_df[(pemasukan_df['Tanggal'] >= pd.to_datetime(mulai)) & 
                               (pemasukan_df['Tanggal'] <= pd.to_datetime(akhir))]
    pengeluaran_df = pengeluaran_df[(pengeluaran_df['Tanggal'] >= pd.to_datetime(mulai)) & 
                                   (pengeluaran_df['Tanggal'] <= pd.to_datetime(akhir))]
    jurnal_df = jurnal_df[(jurnal_df['Tanggal'] >= pd.to_datetime(mulai)) & 
                          (jurnal_df['Tanggal'] <= pd.to_datetime(akhir))]

    tabs = st.tabs(["Ringkasan", "Jurnal Umum", "Buku Besar", "Laba Rugi", "Neraca"])
    
    with tabs[0]:
        st.subheader("Ringkasan Keuangan")
        
        total_pemasukan = pemasukan_df['Jumlah'].sum() if not pemasukan_df.empty else 0
        total_pengeluaran = pengeluaran_df['Jumlah'].sum() if not pengeluaran_df.empty else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Pemasukan", f"Rp {total_pemasukan:,.0f}")
        col2.metric("Total Pengeluaran", f"Rp {total_pengeluaran:,.0f}")
        col3.metric("Saldo Bersih", f"Rp {total_pemasukan - total_pengeluaran:,.0f}", 
                   delta=f"{((total_pemasukan - total_pengeluaran)/total_pemasukan*100 if total_pemasukan>0 else 0):.1f}%")
        
        if total_pemasukan > 0 or total_pengeluaran > 0:
            df_sum = pd.DataFrame({
                'Kategori': ['Pemasukan', 'Pengeluaran'],
                'Jumlah': [total_pemasukan, total_pengeluaran]
            })
            fig = px.pie(df_sum, values='Jumlah', names='Kategori', title='Komposisi Pemasukan dan Pengeluaran')
            st.plotly_chart(fig)
            
            # Grafik trend bulanan
            if not pemasukan_df.empty and not pengeluaran_df.empty:
                monthly_data = pd.concat([
                    pemasukan_df.groupby(pd.Grouper(key='Tanggal', freq='M'))['Jumlah'].sum().rename('Pemasukan'),
                    pengeluaran_df.groupby(pd.Grouper(key='Tanggal', freq='M'))['Jumlah'].sum().rename('Pengeluaran')
                ], axis=1).fillna(0)
                
                monthly_data.index = monthly_data.index.strftime('%Y-%m')
                fig = px.bar(monthly_data, barmode='group', title='Trend Bulanan')
                st.plotly_chart(fig)

    with tabs[1]:
        st.subheader("Jurnal Umum")
        if not jurnal_df.empty:
            jurnal_df['Tanggal'] = jurnal_df['Tanggal'].dt.strftime('%Y-%m-%d')
            st.dataframe(jurnal_df.style.format({
                'Debit': 'Rp {:.0f}'.format,
                'Kredit': 'Rp {:.0f}'.format
            }), height=600)
        else:
            st.warning("Tidak ada data jurnal pada periode ini.")

    with tabs[2]:
        st.subheader("Buku Besar")
        if not jurnal_df.empty:
            akun_list = jurnal_df['Akun'].unique()
            selected_akun = st.selectbox("Pilih Akun", akun_list)
            
            df_akun = jurnal_df[jurnal_df['Akun'] == selected_akun].copy()
            df_akun = df_akun.sort_values("Tanggal")
            df_akun['Saldo'] = df_akun['Debit'] - df_akun['Kredit']
            df_akun['Saldo Akumulatif'] = df_akun['Saldo'].cumsum()
            
            st.dataframe(df_akun.style.format({
                'Debit': 'Rp {:.0f}'.format,
                'Kredit': 'Rp {:.0f}'.format,
                'Saldo': 'Rp {:.0f}'.format,
                'Saldo Akumulatif': 'Rp {:.0f}'.format
            }), height=400)
        else:
            st.warning("Tidak ada data jurnal pada periode ini.")

    with tabs[3]:
        st.subheader("Laporan Laba Rugi")
        if not jurnal_df.empty:
            # Hitung pendapatan
            pendapatan = jurnal_df[jurnal_df['Akun'] == 'Pendapatan']['Kredit'].sum()
            
            # Hitung beban (semua akun selain Kas, Bank, Piutang, Utang, Pendapatan)
            akun_beban = [akun for akun in jurnal_df['Akun'].unique() 
                         if akun not in ['Kas', 'Bank', 'Piutang Dagang', 'Utang Dagang', 'Pendapatan']]
            beban = jurnal_df[jurnal_df['Akun'].isin(akun_beban)]['Debit'].sum()
            
            laba_rugi = pendapatan - beban
            
            # Buat tabel laba rugi
            lr_data = [
                {"Keterangan": "Pendapatan", "Jumlah": pendapatan},
                {"Keterangan": "Beban", "Jumlah": beban},
                {"Keterangan": "Laba (Rugi)", "Jumlah": laba_rugi}
            ]
            lr_df = pd.DataFrame(lr_data)
            
            st.dataframe(lr_df.style.format({
                'Jumlah': 'Rp {:.0f}'.format
            }), height=200)
            
            # Tampilkan metrik
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Pendapatan", f"Rp {pendapatan:,.0f}")
            col2.metric("Total Beban", f"Rp {beban:,.0f}")
            col3.metric("Laba (Rugi) Bersih", f"Rp {laba_rugi:,.0f}", 
                       delta_color="inverse" if laba_rugi < 0 else "normal")
        else:
            st.warning("Tidak ada data jurnal pada periode ini.")

    with tabs[4]:
        st.subheader("Neraca")
        if not jurnal_df.empty:
            # Hitung aktiva
            kas = jurnal_df[jurnal_df['Akun'] == 'Kas']['Debit'].sum() - jurnal_df[jurnal_df['Akun'] == 'Kas']['Kredit'].sum()
            bank = jurnal_df[jurnal_df['Akun'] == 'Bank']['Debit'].sum() - jurnal_df[jurnal_df['Akun'] == 'Bank']['Kredit'].sum()
            piutang = jurnal_df[jurnal_df['Akun'] == 'Piutang Dagang']['Debit'].sum() - jurnal_df[jurnal_df['Akun'] == 'Piutang Dagang']['Kredit'].sum()
            total_aktiva = kas + bank + piutang
            
            # Hitung kewajiban
            utang = jurnal_df[jurnal_df['Akun'] == 'Utang Dagang']['Kredit'].sum() - jurnal_df[jurnal_df['Akun'] == 'Utang Dagang']['Debit'].sum()
            total_kewajiban = utang
            
            # Hitung ekuitas (dari laba rugi)
            pendapatan = jurnal_df[jurnal_df['Akun'] == 'Pendapatan']['Kredit'].sum()
            beban = jurnal_df[~jurnal_df['Akun'].isin(['Kas', 'Bank', 'Piutang Dagang', 'Utang Dagang', 'Pendapatan'])]['Debit'].sum()
            ekuitas = pendapatan - beban
            
            # Buat tabel neraca
            neraca_data = [
                {"Keterangan": "AKTIVA", "Jumlah": ""},
                {"Keterangan": "- Kas", "Jumlah": kas},
                {"Keterangan": "- Bank", "Jumlah": bank},
                {"Keterangan": "- Piutang Dagang", "Jumlah": piutang},
                {"Keterangan": "Total Aktiva", "Jumlah": total_aktiva},
                {"Keterangan": "", "Jumlah": ""},
                {"Keterangan": "KEWAJIBAN", "Jumlah": ""},
                {"Keterangan": "- Utang Dagang", "Jumlah": utang},
                {"Keterangan": "Total Kewajiban", "Jumlah": total_kewajiban},
                {"Keterangan": "", "Jumlah": ""},
                {"Keterangan": "EKUITAS", "Jumlah": ""},
                {"Keterangan": "- Laba (Rugi) Bersih", "Jumlah": ekuitas},
                {"Keterangan": "Total Ekuitas", "Jumlah": ekuitas},
                {"Keterangan": "", "Jumlah": ""},
                {"Keterangan": "TOTAL KEWAJIBAN + EKUITAS", "Jumlah": total_kewajiban + ekuitas}
            ]
            neraca_df = pd.DataFrame(neraca_data)
            
            st.dataframe(neraca_df.style.format({
                'Jumlah': lambda x: 'Rp {:.0f}'.format(x) if isinstance(x, (int, float)) else x
            }), height=600)
            
            # Validasi neraca
            if abs(total_aktiva - (total_kewajiban + ekuitas)) > 1:  # Toleransi 1 rupiah
                st.error("⚠️ Neraca tidak balance! Harap periksa data transaksi Anda.")
        else:
            st.warning("Tidak ada data jurnal pada periode ini.")

# ---------------- UI Utama (diperbarui) ----------------

def main():
    st.set_page_config(layout="wide", page_title="Aplikasi Keuangan Petani", page_icon="🌾")
   
    # Logo kecil di header (ganti dengan URL/logo sendiri jika ada)
    st.sidebar.title("🌾 Menu Utama")
    
    logged_in = login_register()
    if not logged_in:
        return
    
    menu = st.sidebar.radio("Navigasi", ["Beranda", "Pemasukan", "Pengeluaran", "Hapus Transaksi", "Laporan", "Logout"])

    if menu == "Beranda":
        st.title(f"Selamat datang, {st.session_state['username']}!")
        st.markdown("""
        <style>
        .welcome-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        </style>
        <div class="welcome-box">
            <h3>Aplikasi Keuangan untuk Petani</h3>
            <p>Fitur lengkap untuk mengelola keuangan usaha tani Anda:</p>
            <ul>
                <li>📥 Tambah pemasukan dan pengeluaran</li>
                <li>📖 Jurnal umum otomatis</li>
                <li>📊 Buku besar dan laporan keuangan</li>
                <li>💰 Laporan laba rugi dan neraca</li>
                <li>🗑️ Manajemen transaksi</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("Gunakan menu di sebelah kiri untuk navigasi.")

    elif menu == "Pemasukan":
        pemasukan()

    elif menu == "Pengeluaran":
        pengeluaran()
        
    elif menu == "Hapus Transaksi":
        hapus_transaksi()

    elif menu == "Laporan":
        laporan()

    elif menu == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.success("Anda telah berhasil logout.")
        st.rerun()

if __name__ == "__main__":
    main()
