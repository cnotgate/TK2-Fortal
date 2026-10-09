---
marp: true
theme: default
paginate: true
header: "A Million Rupiah Mistake — Solution Walkthrough"
footer: "Digital Forensics & Incident Response (DFIR) | ALEAPP"
---

# 📱 🛡️ A Million Rupiah Mistake
### Official Solution & Forensic Walkthrough
**Android Mobile Forensics CTF (Level: Medium)**

- **Target Tool:** ALEAPP (Android Logs Events And Protobuf Parser)
- **Barang Bukti:** `evidence.zip`
- **Format Jawaban:** Nilai forensik langsung (Tanpa format `FLAG{}`)

---

## 📖 1. Latar Belakang Kasus & Misteri

### Profil Insiden:
- **Korban:** Budi Santoso (`+6281311223344`)
- **Kerugian:** Transfer ilegal **Rp 15.000.000**
- **Kejadian:** 28 September 2026

### Tiga Misteri yang Membingungkan Korban:
1. **Tidak Ada Ikon Baru:** Merasa tidak ada aplikasi mencurigakan yang terpasang di launcher/app drawer.
2. **Tidak Ada Notifikasi SMS:** Korban tidak pernah melihat pop-up SMS OTP dari bank.
3. **Tidak Pernah Memberikan OTP:** Korban bersikukuh tidak pernah berinteraksi membagikan kode otentikasi.

---

## ⛓️ 2. Rantai Serangan Pelaku (Attack Chain)

```text
[1. Smishing SMS] (09:15 UTC) -> Mengandung link jebakan Base64
       │
[2. Unduh Dropper] (09:17 UTC) -> Chrome unduh BCA2026.apk
       │
[3. Instalasi] (09:20 UTC) -> Ikon disembunyikan via <disabled-components>
       │
[4. Eksekusi Pertama] (09:21 UTC) -> com.secupdate.banking.bcamobile aktif
       │
[5. Intersepsi OTP] (09:25 UTC) -> SMS bank ditandai read=1, seen=0 (senyap)
       │
[6. Eksfiltrasi] (09:25 UTC) -> SMS keluar berkedok [SYS_CRASH_REPORT]
```

---

## 🛠️ 3. Prosedur Eksekusi ALEAPP

1. Unduh ALEAPP dari rilis resmi:
   👉 **`https://github.com/abrignoni/ALEAPP/releases`**
2. Jalankan **`aleappGUI.exe`**.
3. Pilih berkas barang bukti `evidence.zip` sebagai **Input**.
4. Tentukan folder tujuan laporan sebagai **Output**.
5. Klik tombol **Process** dan buka `index.html`.

### 4 Artefak Kunci:
- `SMS_Messages.html` (`mmssms.db`)
- `Downloads.html` (`History`)
- `package_info.html` (`packages.xml`)
- `Usage_Stats.html` (`daily/20260928`)

---

## 🔍 Soal 1: Melacak URL Muatan Asli

### Pemeriksaan Artefak: `SMS_Messages.html`
- SMS masuk dari `+6281299887766` pada **2026-09-28 09:15:22 UTC**:
  ```text
  [BCA Alert] ... https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=
  ```

### Analisis Obfuscation (Base64 Decode):
- Parameter `target` di-decode:
  ```bash
  echo 'aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=' | base64 -d
  ```

**Kunci Jawaban Resmi:**
```text
https://bca-mobile-alert.site/BCA2026.apk
```

---

## 🔍 Soal 2: Waktu Keberhasilan Unduhan

### Pemeriksaan Artefak: `Downloads.html`
- Buka tabel Chrome Downloads:
  - **Target Path:** `/storage/emulated/0/Download/BCA2026.apk`
  - **Start Time:** `2026-09-28 09:17:35+00:00`
  - **End Time:** `2026-09-28 09:17:45+00:00`
  - **Opened?:** `Yes`

### Catatan Forensik:
Meskipun pelaku menghapus berkas fisik APK dari penyimpanan korban, catatan transaksi di database SQLite Chrome (`History`) tetap permanen.

**Kunci Jawaban Resmi:**
```text
2026-09-28 09:17:45
```

---

## 🔍 Soal 3: Identifikasi Malware & Anti-Forensik

### Pemeriksaan Artefak: `package_info.html`
- Aplikasi resmi (`com.bca`, `com.whatsapp`) terpasang sejak tahun 2024.
- Paket baru terpasang pada waktu insiden (**2026-09-28 09:20:10 UTC**):
  - **Nama Paket:** `com.secupdate.banking.bcamobile`
  - **Izin Berbahaya:** `READ_SMS`, `RECEIVE_SMS`, `SEND_SMS`

### Trik Anti-Forensik (Mengapa Ikon Tidak Muncul?):
Di `packages.xml`, komponen peluncur dinonaktifkan:
```xml
<disabled-components>
    <item name="com.secupdate.banking.bcamobile.MainActivity" />
</disabled-components>
```

**Kunci Jawaban Resmi:**
```text
com.secupdate.banking.bcamobile
```

---

## 🔍 Soal 4: Waktu Eksekusi Pertama

### Pemeriksaan Artefak: `Usage_Stats.html`
- Filter tabel berdasarkan nama paket `com.secupdate.banking.bcamobile`:
  - **Timestamp:** `2026-09-28 09:21:05+00:00`
  - **Usage Type:** `event-log`
  - **Event Type:** `ACTIVITY_RESUMED` (Type 1)
  - **Class:** `com.secupdate.banking.bcamobile.AuthActivity`

### Makna Forensik:
Aplikasi berpindah ke latar depan (*foreground*) dan pertama kali aktif dijalankan oleh pengguna pada jam **09:21:05 UTC**.

**Kunci Jawaban Resmi:**
```text
2026-09-28 09:21:05
```

---

## 🔍 Soal 5: Kode OTP yang Berhasil Dicuri

### Pemeriksaan Artefak: `SMS_Messages.html`
1. **SMS Masuk Bank (09:25:30 UTC):**
   ```text
   PERINGATAN! JANGAN BERIKAN KODE INI KEPADA SIAPAPUN. Kode OTP transaksi transfer 
   Rp 15.000.000 ke rekening 8872192831 adalah 849201. Berlaku 5 menit.
   ```
   *Catatan:* Status `read=1, seen=0` (dicegat instan oleh malware).

2. **SMS Keluar Malware (09:25:32 UTC):**
   ```text
   [SYS_CRASH_REPORT]::eyJ2aWN0aW0iOiIrNjI4MTMxMTIyMzM0NCIsIm90cCI6Ijg0OTIwMSIsInR4X2lkIjoiVFgtODkwMjMifQ==
   ```
   *Base64 Decoded:* `{"victim":"+6281311223344","otp":"849201","tx_id":"TX-89023"}`

**Kunci Jawaban Resmi:**
```text
849201
```

---

## 🔍 Soal 6: Tujuan Eksfiltrasi Data

### Pemeriksaan Artefak: `SMS_Messages.html`
- Periksa detail pesan keluar (*Type: Sent*) pada jam **09:25:32 UTC**:
  - **Date:** `2026-09-28 09:25:32+00:00`
  - **Address:** `+6282133445566`
  - **Creator:** `com.secupdate.banking.bcamobile`

### Penyamaran:
Malware menyamarkan teks sebagai `[SYS_CRASH_REPORT]` untuk mengelabui pemeriksaan manual.

**Kunci Jawaban Resmi:**
```text
+6282133445566
```

---

## 🎯 Ringkasan Kunci Jawaban Resmi

| No | Fokus Investigasi | Format Jawaban | Kunci Jawaban Resmi |
| :---: | :--- | :--- | :--- |
| **1** | Initial Vector (Payload URL) | URL Lengkap | `https://bca-mobile-alert.site/BCA2026.apk` |
| **2** | Dropper Delivery Time | `YYYY-MM-DD HH:MM:SS` | `2026-09-28 09:17:45` |
| **3** | Malware Identity | Nama paket string | `com.secupdate.banking.bcamobile` |
| **4** | First Execution Time | `YYYY-MM-DD HH:MM:SS` | `2026-09-28 09:21:05` |
| **5** | Compromised OTP | 6 Digit Angka | `849201` |
| **6** | Exfiltration Phone Number | Nomor Internasional | `+6282133445566` |

---

## 💡 Kesimpulan & Pelajaran Forensik (Takeaways)

1. **Anti-Forensics Tidak Menghapus Segala Jejak:**
   Penghapusan berkas installer fisik (APK) gagal menghilangkan riwayat transaksi download di SQLite Chrome.
2. **Korelasi Multi-Artefak adalah Kunci:**
   SMS (Vektor & Eksfiltrasi) + Chrome History (Download) + Packages XML (Manifest & Status Ikon) + UsageStats (Timeline Eksekusi).
3. **Keandalan ALEAPP:**
   ALEAPP mampu membedah format database SQLite, XML sistem, dan protobuf daily log secara cepat, terstruktur, dan terstandarisasi.
