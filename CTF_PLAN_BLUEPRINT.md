# 📋 Blueprint CTF: Android Mobile Forensics (Level: Medium)
## Kasus: *A Million Rupiah Mistake*

Dokumen ini merupakan perencanaan teknis komprehensif untuk challenge CTF kategori **Android Mobile Forensics** tingkat kesulitan **Sedang (Medium)**, yang diselesaikan menggunakan tool **ALEAPP (Android Logs Events And Protobuf Parser)**.

---

## 1. Narasi Kasus (Case Scenario)

> **Judul Kasus:** A Million Rupiah Mistake  
> **Nama Korban:** Budi Santoso (`+6281311223344`)  
> **Model Perangkat:** Google Pixel (Android OS)  
> **Tanggal Kejadian:** 28 September 2026 (UTC)  
> 
> **Latar Belakang:**  
> Pada pagi hari tanggal 28 September 2026, korban menerima SMS pemberitahuan yang tampak meyakinkan mengenai pembaruan keamanan perbankan. Korban mengeklik tautan pada SMS yang mengarah ke pengunduhan berkas APK.
> 
> Namun setelah instalasi, **korban merasa curiga karena tidak ada ikon aplikasi baru yang muncul di beranda/app drawer ponselnya**. Bahkan, korban tidak pernah melihat SMS masuk ataupun notifikasi kode OTP dari bank. Beberapa menit kemudian, korban mendapati melalui ATM bahwa saldo rekeningnya telah terkuras habis sebesar Rp 15.000.000.
> 
> **Taktik Pelaku (Anti-Forensics & Cover-up):**  
> Investigasi awal menunjukkan bahwa pelaku berusaha keras **menutupi perbuatannya** melalui beberapa teknik:
> 1. **Penyembunyian Tautan Asli:** Tautan phishing dibungkus gateway dengan parameter URL terenkode Base64.
> 2. **Penghapusan Berkas APK (File Cleanup):** Setelah APK dipasang, berkas installer APK di folder Download sengaja dihapus agar tidak terdeteksi oleh korban maupun antivirus lokal.
> 3. **Penyembunyian Ikon (Stealth Icon Hiding):** Malware sengaja menonaktifkan komponen peluncur (`disabled-components` pada launcher activity) sehingga aplikasi berjalan tanpa jejak visual di layar korban.
> 4. **Pencegatan Diam-diam (Silent SMS Interception):** SMS OTP dari bank langsung ditandai telah dibaca (`read=1`, `seen=0`) dan notifikasinya diredam agar korban tidak sadar.
> 5. **Penyamaran Pesan Eksfiltrasi (Camouflage Traffic):** Malware mengirimkan hasil curian OTP ke nomor penyerang dengan menyamar sebagai laporan galat sistem (`[SYS_CRASH_REPORT]`) berisi string Base64.

---

## 2. Timeline Kronologis Insiden (Ground Truth) & Titik Obfuscation / Cover-up

| Waktu (UTC) | Fase Insiden | Deskripsi Kejadian & Upaya Penyamaran Pelaku | Artefak Forensik | Lokasi File Sistem |
| :--- | :--- | :--- | :--- | :--- |
| **09:15:22** | **Initial Vector (Smishing)** | Korban menerima SMS spoofing (`+6281299887766`). URL memuat parameter `target` terenkode **Base64**: <br>`https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=` | `mmssms.db` (tabel `sms`) | `/data/user_de/0/com.android.providers.telephony/databases/mmssms.db` |
| **09:17:45** | **Dropper Delivery** | Chrome mengunduh file APK: `https://bca-mobile-alert.site/BCA2026.apk`. *(Catatan forensik: Pelaku kemudian menghapus file fisik APK dari penyimpanan setelah instalasi)* | Chrome `History` (tabel `downloads` & `urls`) | `/data/data/com.android.chrome/app_chrome/Default/History` |
| **09:20:10** | **Installation & Icon Hiding** | Korban memasang APK. Paket `com.secupdate.banking.bcamobile` terpasang, lalu malware segera **menonaktifkan launcher activity** (`MainActivity`) agar ikonnya hilang dari layar | `packages.xml` (`disabled-components`) | `/data/system/packages.xml` |
| **09:21:05** | **Malware Execution** | Aplikasi berjalan di background/foreground pertama kali | `usagestats` (event-log) | `/data/system/usagestats/0/daily/` |
| **09:25:30** | **Silent Interception** | Bank resmi (`BANK_CENTRAL` / `14000`) mengirim SMS OTP transfer Rp 15.000.000: `849201`. Malware langsung meredam notifikasi dan menandai pesan | `mmssms.db` (sms incoming, status read) | `/data/user_de/0/com.android.providers.telephony/databases/mmssms.db` |
| **09:25:32** | **Camouflaged Exfiltration** | Malware meneruskan kode OTP ke penyerang (`+6282133445566`) dengan menyamar sebagai laporan crash sistem palsu: <br>`[SYS_CRASH_REPORT]::eyJ2aWN0aW0iOiIrNjI4MTMxMTIyMzM0NCIsIm90cCI6Ijg0OTIwMSIsInR4X2lkIjoiVFgtODkwMjMifQ==` | `mmssms.db` (sms outgoing) | `/data/user_de/0/com.android.providers.telephony/databases/mmssms.db` |

---

## 3. Rangkaian Pertanyaan Investigasi (Investigative & Subtle Prompts)

Pertanyaan dirancang secara realistis layaknya tugas analis DFIR profesional, **tanpa membocorkan nama file sistem, jenis encoding, maupun kata kunci payload**. Peserta harus menganalisis artefak dan menarik kesimpulan sendiri menggunakan ALEAPP:

### 🔍 Pertanyaan 1: Tautan Muatan Asli (Direct Payload URL)
- **Pertanyaan:**  
  *Korban menerima pesan teks mencurigakan sesaat sebelum insiden terjadi. Berdasarkan analisis tautan pada pesan tersebut, apa URL pengunduhan langsung (*direct download link*) dari muatan (*payload*) yang dituju?*
- **Format Jawaban:** URL lengkap (contoh: `https://...`)
- **Kunci Jawaban:** `https://bca-mobile-alert.site/BCA2026.apk`
- **Behind the Scenes (Investigasi):** Peserta memeriksa pesan SMS, menemukan URL gerbang phishing `https://bca-sec.link/check?target=aHR0cHM6...`, menyadari adanya parameter terenkode, dan mendecode Base64 untuk mendapatkan URL langsung.

---

### 🔍 Pertanyaan 2: Waktu Keberhasilan Unduhan (Download Timestamp)
- **Pertanyaan:**  
  *Kapan (UTC) berkas aplikasi berbahaya tersebut selesai diunduh ke perangkat korban?*
- **Format Jawaban:** `YYYY-MM-DD HH:MM:SS`
- **Kunci Jawaban:** `2026-09-28 09:17:45`
- **Behind the Scenes (Investigasi):** Meskipun berkas APK dihapus dari folder Download oleh pelaku, peserta menelusuri riwayat unduhan peramban di ALEAPP untuk menemukan timestamp unduhannya.

---

### 🔍 Pertanyaan 3: Identitas Aplikasi Berbahaya (Malware Package Name)
- **Pertanyaan:**  
  *Setelah berkas diunduh, sebuah aplikasi berbahaya berhasil dipasang di perangkat. Apa nama paket (*package name*) dari aplikasi tersebut?*
- **Format Jawaban:** Plain string nama paket
- **Kunci Jawaban:** `com.secupdate.banking.bcamobile`
- **Behind the Scenes (Investigasi):** Peserta mencari aplikasi yang diinstal pada timeline insiden di daftar paket aplikasi ALEAPP.

---

### 🔍 Pertanyaan 4: Waktu Eksekusi Pertama (First Execution Timestamp)
- **Pertanyaan:**  
  *Kapan (UTC) aplikasi berbahaya tersebut pertama kali aktif dijalankan oleh pengguna di perangkat?*
- **Format Jawaban:** `YYYY-MM-DD HH:MM:SS`
- **Kunci Jawaban:** `2026-09-28 09:21:05`
- **Behind the Scenes (Investigasi):** Peserta menganalisis log interaksi dan penggunaan aplikasi (UsageStats / Recent Activity) di ALEAPP untuk menentukan waktu pertama aplikasi berada di status *resumed/active*.

---

### 🔍 Pertanyaan 5: Nilai Transaksi Kritis (Compromised OTP Code)
- **Pertanyaan:**  
  *Pelaku berhasil mengeksekusi transaksi ilegal dengan menyusup dan mencuri kode otentikasi perbankan milik korban. Berapa kode OTP yang berhasil dicuri tersebut?*
- **Format Jawaban:** 6 digit angka kode OTP
- **Kunci Jawaban:** `849201`
- **Behind the Scenes (Investigasi):** Peserta menemukan SMS OTP masuk dari bank resmi, atau meneliti lalu lintas SMS keluar yang mencurigakan, menemukan pesan berkedok crash report, dan mendecode payload Base64 untuk mengekstrak OTP.

---

### 🔍 Pertanyaan 6: Tujuan Eksfiltrasi Data (Exfiltration Destination)
- **Pertanyaan:**  
  *Ke nomor telepon mana data otentikasi hasil pencurian tersebut dikirimkan oleh malware?*
- **Format Jawaban:** Nomor telepon lengkap dengan kode negara (contoh: `+62...`)
- **Kunci Jawaban:** `+6282133445566`
- **Behind the Scenes (Investigasi):** Peserta melacak nomor penerima dari transmisi SMS rahasia yang dikirimkan oleh malware di background.

---

## 4. Rincian Teknis Pembuatan Bukti (Technical Build Plan)

Kita akan membuat script Python otomatis (`build_evidence.py`) yang mengenerate struktur direktori Android standar beserta database riil dan mengompresinya menjadi `evidence.zip`:

### A. Struktur Berkas yang Dibuat:
```text
evidence/
├── data/
│   ├── data/
│   │   └── com.android.chrome/
│   │       └── app_chrome/
│   │           └── Default/
│   │               └── History            (SQLite: urls, visits, downloads)
│   ├── system/
│   │   ├── packages.xml                   (XML: package list & granted perms)
│   │   ├── packages.list                  (Plaintext: UID mapping)
│   │   └── usagestats/
│   │       └── 0/
│   │           └── daily/
│   │               └── 1790589600000      (XML usagestats: packages & event-log)
│   └── user_de/
│       └── 0/
│           └── com.android.providers.telephony/
│               └── databases/
│                   └── mmssms.db          (SQLite: sms table incoming/outgoing)
```

### B. Otentisitas Data (Noise & Realisme):
Agar challenge tidak terasa kosong atau "buatan kasar", generator akan menyisipkan:
1. **SMS Percakapan Normal:** Pesan dari keluarga, promo Telkomsel/Indosat, kode verifikasi WhatsApp normal.
2. **Riwayat Browsing Normal:** Akses ke Google, Detik.com, Tokopedia, YouTube sebelum insiden terjadi.
3. **Aplikasi Bawaan:** Paket-paket standar Google Pixel (`com.android.chrome`, `com.google.android.apps.messaging`, `com.google.android.dialer`, launcher).
4. **UsageStats Normal:** Log interaksi dengan aplikasi telepon, launcher, dan browser.

---

## 5. Rencana Deliverables (Hasil Akhir untuk Pengguna)

Setelah perencanaan ini disetujui, deliverables yang akan kita hasilkan:
1. **`build_evidence.py`**: Script generator bukti forensik yang *reproducible*.
2. **`evidence.zip`**: Arsip bukti forensik Android siap pakai untuk peserta CTF.
3. **Uji Validasi ALEAPP**: Pengujian langsung menggunakan `aleappGUI` untuk memastikan semua tab HTML dan data ter-render sempurna tanpa bug.
4. **`CHALLENGE.md`**: Deskripsi challenge siap dipasang di platform CTF (CTFd / Google Form / LMS kuliah).
5. **`WRITEUP.md`**: Panduan investigasi lengkap (Official Solution Walkthrough) dengan tangkapan layar / langkah-langkah detail di ALEAPP untuk dosen/asisten lab atau peserta.

