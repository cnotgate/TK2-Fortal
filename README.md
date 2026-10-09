# Android Mobile Forensics CTF — A Million Rupiah Mistake

![Category](https://img.shields.io/badge/Category-Mobile%20Forensics-blue)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-orange)
![Tool](https://img.shields.io/badge/Primary%20Tool-ALEAPP-brightgreen)
![Evidence Size](https://img.shields.io/badge/Evidence%20Size-~7%20KB-success)

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
├── CTF_PLAN_BLUEPRINT.md  # Blueprint teknis perancangan artefak forensik
├── .gitignore             # Konfigurasi ignore file temporary dan cache
└── README.md              # Dokumentasi utama repositori
```

---

## 🛠️ Informasi Berkas Barang Bukti

- **Nama Berkas:** `evidence.zip`
- **Ukuran:** ~7 KB
- **Format:** Zip Archive berisi struktur direktori Android standar (`data/data/...`, `data/system/...`)
- **Hash SHA-256:**
  ```text
  C15A5374E52F6792D00E15732FB4EF548905E62ED3606E9195297583541D65E1
  ```

### Artefak Android yang Diuji:

1. **SMS & MMS Database:** `data/data/com.android.providers.telephony/databases/mmssms.db`
2. **Chrome History Database:** `data/data/com.android.chrome/app_chrome/Default/History`
3. **Package Manager State:** `data/system/packages.xml` & `data/system/packages.list`
4. **Usage Statistics:** `data/system/usagestats/0/daily/20260928`

---

## 🚀 Cara Menjalankan Investigasi (ALEAPP)

Tantangan ini dirancang agar dapat diselesaikan 100% menggunakan **ALEAPP**.

### 1. Instalasi ALEAPP

```bash
git clone https://github.com/abrignoni/ALEAPP.git
cd ALEAPP
pip install -r requirements.txt
```

### 2. Eksekusi Analisis

Jalankan ALEAPP terhadap `evidence.zip`:

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
