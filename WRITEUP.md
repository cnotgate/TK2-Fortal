# 🛡️ Official Write-up & Solution Guide: A Million Rupiah Mistake

## CTF Kategori: Android Mobile Forensics (Level: Medium)

Dokumen ini merupakan panduan solusi resmi (_Official Solution Walkthrough_) untuk challenge investigasi **"A Million Rupiah Mistake"**.

---

## 1. Ringkasan Kasus & Rantai Serangan (Attack Chain Overview)

Kasus ini mensimulasikan insiden kejahatan perbankan (_banking trojan / smishing campaign_) yang umum terjadi di Indonesia. Pelaku melancarkan serangan berjenjang dengan taktik anti-forensik:

```
[Attacker +6281299887766]
          │
          │ 1. Kirim SMS Phishing (09:15:22 UTC)
          ▼
   [Ponsel Korban]
          │
          │ 2. Korban klik link -> Chrome unduh APK (09:17:45 UTC)
          ▼
  [Download APK] ───(Pelaku hapus file fisik APK dari folder Download)
          │
          │ 3. Korban pasang APK (09:20:10 UTC)
          ▼
[Malware Terpasang] ───(Sembunyikan ikon launcher via disabled-components)
          │
          │ 4. Malware pertama kali aktif (09:21:05 UTC)
          ▼
   [Bank Resmi] ───> Kirim SMS OTP Rp 15.000.000 (09:25:30 UTC)
          │
          ▼
[Pencegatan Senyap] ───(Malware tandai SMS OTP read=1, redam notifikasi)
          │
          │ 5. Eksfiltrasi Base64 berkedok crash report (09:25:32 UTC)
          ▼
[Attacker +6282133445566]
```

---

## 2. Prosedur Analisis dengan ALEAPP

Peserta dapat memproses berkas barang bukti `evidence.zip` menggunakan tool **ALEAPP**:

### Menggunakan ALEAPP GUI:

1. Jalankan `aleappGUI.exe`.
2. Pada kolom **Input file/folder**: Pilih berkas `evidence.zip`.
3. Pada kolom **Output folder**: Tentukan folder tujuan laporan (misal: folder kosong `ALEAPP_Reports`).
4. Klik tombol **Process**.
5. Setelah selesai, buka berkas `index.html` yang berada di dalam folder laporan yang dihasilkan.

---

## 3. Pembahasan Soal Langkah demi Langkah (Step-by-Step Walkthrough)

### 🔍 Soal 1: Initial Vector (Tautan Muatan Asli)

- **Pertanyaan:**  
  _Korban menerima pesan teks mencurigakan sesaat sebelum insiden terjadi. Berdasarkan analisis tautan pada pesan tersebut, apa URL pengunduhan langsung (direct download link) dari muatan (payload) yang dituju?_

- **Langkah Investigasi:**
  1. Di panel navigasi ALEAPP, buka kategori **SMS & MMS** -> klik **SMS Messages** (`SMS_Messages.html`).
  2. Perhatikan baris pesan masuk (_Type: Received_) pada tanggal **2026-09-28 09:15:22 UTC** dari pengirim `+6281299887766`.
  3. Isi pesan:
     ```text
     [BCA Alert] Terdeteksi upaya login tidak wajar pada akun Anda. Segera amankan & perbarui proteksi m-Banking melalui: https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=
     ```
  4. Analisis URL menunjukkan adanya parameter gerbang `target` yang dikaburkan menggunakan format **Base64**:
     `aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=`
  5. Lakukan _decode_ Base64 (menggunakan CyberChef atau terminal `echo '...' | base64 -d`):
     ```text
     Base64 Decoded: https://bca-mobile-alert.site/BCA2026.apk
     ```

- **Kunci Jawaban:**  
  `https://bca-mobile-alert.site/BCA2026.apk`

---

### 🔍 Soal 2: Dropper Delivery (Waktu Keberhasilan Unduhan)

- **Pertanyaan:**  
  _Kapan (UTC) berkas aplikasi berbahaya tersebut selesai diunduh ke perangkat korban?_

- **Langkah Investigasi:**
  1. Di panel navigasi ALEAPP, buka kategori **Chromium** -> klik **Downloads** (`Downloads.html`).
  2. Temukan entri unduhan untuk file APK yang dianalisis:
     - **Tab URL:** `https://bca-sec.link/check?target=aHR0cHM6...`
     - **Target Path:** `/storage/emulated/0/Download/BCA2026.apk`
     - **Start Time:** `2026-09-28 09:17:35+00:00`
     - **End Time:** `2026-09-28 09:17:45+00:00`
     - **Opened?:** `Yes`
  3. Waktu selesai unduh (_End Time_) tercatat pada jam **09:17:45 UTC**.
  4. _Catatan Forensik:_ Meskipun pelaku kemudian menghapus berkas fisik APK dari penyimpanan internal korban, basis data SQLite Chrome (`History`) mencatat riwayat transaksi unduhan secara utuh.

- **Kunci Jawaban:**  
  `2026-09-28 09:17:45`

---

### 🔍 Soal 3: Malware Identity (Identitas Aplikasi Berbahaya)

- **Pertanyaan:**  
  _Setelah berkas diunduh, sebuah aplikasi berbahaya berhasil dipasang di perangkat. Apa nama paket (package name) dari aplikasi tersebut?_

- **Langkah Investigasi:**
  1. Di panel navigasi ALEAPP, buka kategori **Installed Apps** -> klik **package_info** (`package_info.html`).
  2. Telusuri daftar paket aplikasi dan perhatikan kolom **Install Time**.
  3. Aplikasi standar sistem terpasang pada tahun 2023, sedangkan pada tanggal insiden (**2026-09-28 09:20:10 UTC**) terdapat paket baru yang dipasang:
     - **Name:** `com.secupdate.banking.bcamobile`
     - **Code Path:** `/data/app/com.secupdate.banking.bcamobile-X91abF2==`
     - **Install Time:** `2026-09-28 09:20:10+00:00`
  4. Verifikasi izin aplikasi di tab **Permissions** / **Package and Shared User**: aplikasi ini meminta izin kritis `READ_SMS`, `RECEIVE_SMS`, dan `SEND_SMS`.

- **Kunci Jawaban:**  
  `com.secupdate.banking.bcamobile`

---

### 🔍 Soal 4: Execution Time (Waktu Eksekusi Pertama)

- **Pertanyaan:**  
  _Kapan (UTC) aplikasi berbahaya tersebut pertama kali aktif dijalankan oleh pengguna di perangkat?_

- **Langkah Investigasi:**
  1. Di panel navigasi ALEAPP, buka kategori **Usage Stats** -> klik **Usage Stats** (`Usage_Stats.html`).
  2. Filter tabel berdasarkan nama paket `com.secupdate.banking.bcamobile`.
  3. Perhatikan catatan `event-log` yang merekam perpindahan status aktivitas ke latar depan (_foreground_):
     - **Timestamp:** `2026-09-28 09:21:05+00:00`
     - **Event Type:** `ACTIVITY_RESUMED`
     - **Class:** `com.secupdate.banking.bcamobile.AuthActivity`
  4. Ini membuktikan aplikasi pertama kali aktif berinteraksi dengan pengguna pada jam **09:21:05 UTC**.

- **Kunci Jawaban:**  
  `2026-09-28 09:21:05`

---

### 🔍 Soal 5: Compromised OTP (Nilai Transaksi Kritis)

- **Pertanyaan:**  
  _Pelaku berhasil mengeksekusi transaksi ilegal dengan menyusup dan mencuri kode otentikasi perbankan milik korban. Berapa kode OTP yang berhasil dicuri tersebut?_

- **Langkah Investigasi:**
  1. Di panel navigasi ALEAPP, kembali ke tab **SMS Messages** (`SMS_Messages.html`).
  2. Temukan pesan masuk resmi dari pihak bank pada **2026-09-28 09:25:30 UTC**:
     - **Address:** `BANK_CENTRAL`
     - **Body:**
       ```text
       PERINGATAN! JANGAN BERIKAN KODE INI KEPADA SIAPAPUN. Kode OTP transaksi transfer Rp 15.000.000 ke rekening 8872192831 adalah 849201. Berlaku 5 menit.
       ```
  3. Peserta juga dapat memvalidasinya melalui SMS keluar yang dikirim oleh malware 2 detik setelahnya (**09:25:32 UTC**):
     - **Body:**
       ```text
       [SYS_CRASH_REPORT]::eyJ2aWN0aW0iOiIrNjI4MTMxMTIyMzM0NCIsIm90cCI6Ijg0OTIwMSIsInR4X2lkIjoiVFgtODkwMjMifQ==
       ```
  4. Lakukan _decode_ Base64 terhadap payload JSON:
     ```json
     { "victim": "+6281311223344", "otp": "849201", "tx_id": "TX-89023" }
     ```
  5. Nilai kode OTP yang dicuri adalah **849201**.

- **Kunci Jawaban:**  
  `849201`

---

### 🔍 Soal 6: Exfiltration Destination (Tujuan Eksfiltrasi Data)

- **Pertanyaan:**  
  _Ke nomor telepon mana data otentikasi hasil pencurian tersebut dikirimkan oleh malware?_

- **Langkah Investigasi:**
  1. Pada tab **SMS Messages** (`SMS_Messages.html`), periksa pesan keluar (_Type: Sent_) pada **2026-09-28 09:25:32 UTC**.
  2. Perhatikan kolom **Address** penerima pesan laporan palsu tersebut.
  3. Nomor telepon penerima yang tercatat adalah `+6282133445566`.

- **Kunci Jawaban:**  
  `+6282133445566`

---

## 4. Tinjauan Anti-Forensik & Jawaban Misteri Kasus

Berikut adalah penjelasan teknis mengapa korban tidak menyadari peretasan terjadi:

1. **Mengapa korban tidak melihat ikon aplikasi perbankan baru?**
   - Di dalam berkas `packages.xml`, malware mendaftarkan komponen peluncur utamanya ke dalam tag `<disabled-components>`:
     ```xml
     <disabled-components>
         <item name="com.secupdate.banking.bcamobile.MainActivity" />
     </disabled-components>
     ```
   - Fitur ini menyembunyikan ikon dari _Android Launcher / App Drawer_, sehingga malware berjalan secara senyap sebagai layanan latar belakang (_background service_).

2. **Mengapa korban tidak melihat notifikasi SMS OTP di layar ponsel?**
   - Di basis data `mmssms.db`, pesan dari bank memiliki nilai `read = 1` dan `seen = 0`.
   - Malware memanfaatkan izin `RECEIVE_SMS` dengan prioritas tinggi (_high broadcast priority_) untuk mencegat pesan secara instan sebelum notifikasi visual dirender ke layar pengguna.

3. **Bagaimana eksfiltrasi disamarkan?**
   - Malware tidak mengirimkan format teks vulgar ("OTP: 849201"), melainkan membungkusnya dalam format menyerupai laporan galat sistem Android:
     `[SYS_CRASH_REPORT]::<base64_json>`
   - Hal ini bertujuan untuk mengelabui pemeriksaan sekilas pada log SMS.

---

## 5. Ringkasan Kunci Jawaban Resmi

|  No   | Fokus Investigasi        | Format Jawaban        | Kunci Jawaban Resmi                         |
| :---: | :----------------------- | :-------------------- | :------------------------------------------ |
| **1** | Initial Vector           | URL Lengkap           | `https://bca-mobile-alert.site/BCA2026.apk` |
| **2** | Dropper Delivery         | `YYYY-MM-DD HH:MM:SS` | `2026-09-28 09:17:45`                       |
| **3** | Malware Identity         | String nama paket     | `com.secupdate.banking.bcamobile`           |
| **4** | Execution Time           | `YYYY-MM-DD HH:MM:SS` | `2026-09-28 09:21:05`                       |
| **5** | Compromised OTP          | 6 Digit Angka         | `849201`                                    |
| **6** | Exfiltration Destination | Nomor Internasional   | `+6282133445566`                            |
