# 📱 CTF Challenge: Jejak SMS Berujung Petaka (The Smishing & Banking Dropper)

- **Kategori:** Mobile Forensics (Android)
- **Tingkat Kesulitan:** Medium
- **Tool Rekomendasi:** [ALEAPP (Android Logs Events And Protobuf Parser)](https://github.com/abrignoni/ALEAPP), CyberChef / Decoder
- **Berkas Bukti:** `evidence.zip`
- **SHA-256 Checksum:** `C15A5374E52F6792D00E15732FB4EF548905E62ED3606E9195297583541D65E1`

---

## 📖 Narasi Kasus (Scenario)

Pada pagi hari tanggal 28 September 2026, **Budi Santoso**, seorang nasabah perbankan, menerima sebuah pesan teks mendesak di ponsel Android miliknya yang mengabarkan adanya aktivitas login mencurigakan. Panik dan khawatir rekeningnya diblokir, korban mengikuti petunjuk pada pesan tersebut untuk memperbarui sistem proteksi perbankannya.

Namun setelah mengunduh dan memasang berkas yang diarahkan, korban heran karena **tidak ada ikon aplikasi baru** yang muncul di layar utama maupun _app drawer_ ponselnya. Korban mengira proses instalasi gagal dan melanjutkan aktivitasnya seperti biasa.

Beberapa menit kemudian, tanpa pernah melihat adanya notifikasi transaksi masuk di layar, korban mendapati melalui ATM bahwa saldo rekeningnya telah berkurang drastis sebesar **Rp 15.000.000**. Korban langsung melapor ke kepolisian dan menyerahkan ponselnya kepada analis forensik digital untuk diteliti.

Sebagai analis DFIR, tugas Anda adalah melakukan analisis forensik terhadap citra sistem perangkat korban menggunakan **ALEAPP**, mengungkap taktik penyamaran yang digunakan pelaku, merekonstruksi alur serangan (_attack chain_), dan menjawab rangkaian pertanyaan investigasi berikut.

---

## 🔍 Pertanyaan Investigasi (Investigation Questions)

> **Catatan Format Pengiriman:**  
> Jawaban tidak menggunakan format pembungkus flag (tanpa `FLAG{...}`). Masukkan jawaban sesuai dengan format yang diminta pada masing-masing butir soal secara presisi.

### 1. Initial Vector (Tautan Muatan Asli)

Korban menerima pesan teks mencurigakan sesaat sebelum insiden terjadi. Berdasarkan analisis tautan pada pesan tersebut, apa URL pengunduhan langsung (_direct download link_) dari muatan (_payload_) yang dituju?

- **Format:** URL lengkap (termasuk protokol, contoh: `https://domain.com/path/file.apk`)

---

### 2. Dropper Delivery (Waktu Keberhasilan Unduhan)

Kapan (UTC) berkas aplikasi berbahaya tersebut selesai diunduh ke perangkat korban?

- **Format:** `YYYY-MM-DD HH:MM:SS` (contoh: `2026-01-15 14:30:25`)

---

### 3. Malware Identity (Identitas Aplikasi Berbahaya)

Setelah berkas diunduh, sebuah aplikasi berbahaya berhasil dipasang di perangkat. Apa nama paket (_package name_) dari aplikasi tersebut?

- **Format:** String nama paket lengkap (contoh: `com.example.appname`)

---

### 4. Execution Time (Waktu Eksekusi Pertama)

Kapan (UTC) aplikasi berbahaya tersebut pertama kali aktif dijalankan oleh pengguna di perangkat?

- **Format:** `YYYY-MM-DD HH:MM:SS` (contoh: `2026-01-15 14:30:25`)

---

### 5. Compromised OTP (Nilai Transaksi Kritis)

Pelaku berhasil mengeksekusi transaksi ilegal dengan menyusup dan mencuri kode otentikasi perbankan milik korban. Berapa kode OTP yang berhasil dicuri tersebut?

- **Format:** 6 digit angka (contoh: `123456`)

---

### 6. Exfiltration Destination (Tujuan Eksfiltrasi Data)

Ke nomor telepon mana data otentikasi hasil pencurian tersebut dikirimkan oleh malware?

- **Format:** Nomor telepon internasional lengkap dengan tanda tambah (contoh: `+6281234567890`)

---

## 💡 Petunjuk Investigasi (Hints)

1. Periksa riwayat komunikasi teks masuk dan keluar untuk memahami interaksi awal korban dan jalur komunikasi malware.
2. Pelaku kejahatan siber sering kali menggunakan teknik _gateway redirection_ dan pengaburan _encoding_ untuk menyamarkan tautan langsung file APK berbahaya.
3. Meskipun pelaku menghapus berkas fisik APK setelah instalasi, basis data peramban mencatat riwayat unduhan secara permanen.
4. Perhatikan waktu aktivitas aplikasi pada log interaksi sistem (_system logs & usage events_) untuk mengetahui kapan proses aplikasi berpindah ke status aktif (_resumed_).
