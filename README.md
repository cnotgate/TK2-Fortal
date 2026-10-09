# Android Mobile Forensics CTF — A Million Rupiah Mistake

![Category](https://img.shields.io/badge/Category-Mobile%20Forensics-blue)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-orange)
![Tool](https://img.shields.io/badge/Primary%20Tool-ALEAPP-brightgreen)
![Evidence Size](https://img.shields.io/badge/Evidence%20Size-~10%20KB-success)

Tantangan Capture The Flag (CTF) kategori **Digital Forensics & Incident Response (DFIR) / Android Mobile Forensics** tingkat kesulitan **Sedang (Medium)** yang dirancang untuk dianalisis dan diselesaikan secara menyeluruh menggunakan [ALEAPP (Android Logs Events And Protobuf Parser)](https://github.com/abrignoni/ALEAPP).

---

## 📌 Ringkasan Skenario

Korban (**Budi Santoso**) melapor bahwa rekening bank miliknya mengalami transaksi transfer ilegal sebesar Rp 15.000.000 tanpa persetujuannya. Korban bersikukuh bahwa ia tidak pernah memberikan kode One-Time Password (OTP) kepada siapapun, tidak menerima notifikasi pop-up OTP di layar ponselnya, dan tidak melihat adanya aplikasi mencurigakan baru di daftar aplikasi ponselnya.

Investigator DFIR melakukan _triage acquisition_ terhadap partisi data perangkat Android korban (`evidence.zip`). Analis ditugaskan untuk merekonstruksi rantai serangan (_attack chain_), mulai dari vektor smishing awal, pengunduhan dropper perbankan, instalasi dan persistensi malware, hingga metode pencegatan (_interception_) dan eksfiltrasi data otentikasi.

---

## 📂 Struktur Repositori

```text
├── CHALLENGE.md           # Lembar soal resmi untuk peserta CTF
├── WRITEUP.md             # Panduan investigasi lengkap & kunci jawaban resmi (organizer)
├── evidence.zip           # Berkas barang bukti digital (triage artifact) untuk peserta
├── .gitignore             # Konfigurasi ignore file temporary dan cache
└── README.md              # Dokumentasi utama repositori
```

---

## 🛠️ Informasi Berkas Barang Bukti

- **Nama Berkas:** `evidence.zip`
- **Ukuran:** ~10 KB
- **Format:** Zip Archive berisi struktur direktori Android standar (`data/data/...`, `data/system/...`)
- **Hash SHA-256:**
  ```text
  6CF093CCA2B97C5724647BFCD7F3FDCE632361790C8C83A3721D40428D25D440
  ```

### Artefak Android yang Diuji:

1. **SMS & MMS Database:** `data/data/com.android.providers.telephony/databases/mmssms.db`
2. **Chrome History Database:** `data/data/com.android.chrome/app_chrome/Default/History`
3. **Package Manager State:** `data/system/packages.xml` & `data/system/packages.list`
4. **Usage Statistics:** `data/system/usagestats/0/daily/20260928`

---

## 🚀 Cara Menjalankan Investigasi (ALEAPP)

Tantangan ini dirancang agar dapat diselesaikan 100% menggunakan **ALEAPP**.

### 1. Unduh ALEAPP

Silakan unduh rilis terbaru ALEAPP melalui laman resmi berikut:  
👉 **[https://github.com/abrignoni/ALEAPP/releases](https://github.com/abrignoni/ALEAPP/releases)**

Tersedia dua opsi penggunaan:
- **Versi Standalone GUI (`aleappGUI.exe`):** Unduh berkas rilis untuk Windows, lalu jalankan langsung tanpa perlu instalasi dependensi Python.
- **Versi Source Code (CLI / Python):** Unduh source code dari rilis terbaru, pasang dependensi (`pip install -r requirements.txt`), lalu gunakan antarmuka baris perintah (`aleapp.py`).

### 2. Eksekusi Analisis

#### Opsi A: Menggunakan ALEAPP GUI (Rekomendasi)
1. Buka `aleappGUI.exe`.
2. Pada pilihan input, pilih berkas `evidence.zip`.
3. Tentukan folder output tujuan penyimpanan hasil laporan.
4. Klik **Process** dan tunggu hingga selesai.

#### Opsi B: Menggunakan ALEAPP CLI
```bash
python aleapp.py -t zip -i /path/ke/evidence.zip -o /path/ke/output_folder
```

### 3. Tinjau Laporan HTML

Buka berkas `index.html` pada folder hasil keluaran menggunakan browser untuk memeriksa kategori:

- **Chrome -> Chrome Downloads**
- **SMS & MMS -> SMS Messages**
- **Application Interaction -> Usage Stats**
- **Installed Applications -> Package and Shared User / Permissions**

---

## 📜 Lisensi & Penggunaan

Repositori ini dibuat untuk keperluan edukasi, pelatihan keamanan siber, dan kompetisi Capture The Flag (CTF). Bebas dimodifikasi dan diadaptasi untuk platform CTF seperti CTFd, HackTheBox, dsb.
