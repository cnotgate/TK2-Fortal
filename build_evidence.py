#!/usr/bin/env python3
"""
CTF Evidence Generator - Android Mobile Forensics (Medium)
Scenario: The Smishing & Banking Dropper (Anti-Forensics & Cover-up)

This script generates synthetic, authentic Android forensic artifacts formatted
specifically for parsing by ALEAPP (Android Logs Events And Protobuf Parser).
"""

import os
import sys
import shutil
import sqlite3
import datetime
import zipfile

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "build_temp")
OUTPUT_ZIP = os.path.join(BASE_DIR, "evidence.zip")

# Timeline Helpers
def dt_to_ms(dt):
    """Convert datetime (UTC) to epoch milliseconds."""
    return int(dt.timestamp() * 1000)

def dt_to_webkit(dt):
    """Convert datetime (UTC) to WebKit microsecond timestamp (since 1601-01-01)."""
    return int((dt.timestamp() + 11644473600) * 1000000)

def ms_to_hex(ms):
    """Convert millisecond timestamp to lowercase hex string."""
    return hex(int(ms))[2:]

# Incident Timestamps (Ground Truth)
T_PHISH_SMS = datetime.datetime(2026, 9, 28, 9, 15, 22, tzinfo=datetime.timezone.utc)
T_DOWNLOAD_START = datetime.datetime(2026, 9, 28, 9, 17, 35, tzinfo=datetime.timezone.utc)
T_DOWNLOAD_FINISH = datetime.datetime(2026, 9, 28, 9, 17, 45, tzinfo=datetime.timezone.utc)
T_INSTALL = datetime.datetime(2026, 9, 28, 9, 20, 10, tzinfo=datetime.timezone.utc)
T_EXECUTE_RESUME = datetime.datetime(2026, 9, 28, 9, 21, 5, tzinfo=datetime.timezone.utc)
T_EXECUTE_PAUSE = datetime.datetime(2026, 9, 28, 9, 21, 35, tzinfo=datetime.timezone.utc)
T_OTP_INCOMING = datetime.datetime(2026, 9, 28, 9, 25, 30, tzinfo=datetime.timezone.utc)
T_OTP_EXFIL = datetime.datetime(2026, 9, 28, 9, 25, 32, tzinfo=datetime.timezone.utc)

def clean_build_dir():
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
    os.makedirs(BUILD_DIR, exist_ok=True)

def create_telephony_artifacts():
    """Generates mmssms.db in /data/user_de/0/com.android.providers.telephony/databases/"""
    db_dir = os.path.join(BUILD_DIR, "data", "user_de", "0", "com.android.providers.telephony", "databases")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "mmssms.db")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE sms (
        _id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id INTEGER,
        address TEXT,
        person INTEGER,
        date INTEGER,
        date_sent INTEGER DEFAULT 0,
        protocol INTEGER,
        read INTEGER DEFAULT 0,
        status INTEGER DEFAULT -1,
        type INTEGER,
        reply_path_present INTEGER,
        subject TEXT,
        body TEXT,
        service_center TEXT,
        locked INTEGER DEFAULT 0,
        sub_id INTEGER DEFAULT -1,
        error_code INTEGER DEFAULT 0,
        creator TEXT,
        seen INTEGER DEFAULT 0
    );
    """)

    # Background Noise Messages
    sms_entries = [
        # Normal chat with colleague
        (1, "+6281122334455", None, dt_to_ms(datetime.datetime(2026, 9, 27, 8, 30, 0, tzinfo=datetime.timezone.utc)),
         dt_to_ms(datetime.datetime(2026, 9, 27, 8, 29, 50, tzinfo=datetime.timezone.utc)), 0, 1, -1, 1, 0, None,
         "Pagi Mas Budi, nanti siang jadi meeting dengan tim finance?", "+6281100000", 0, 1, 0, "com.google.android.apps.messaging", 1),
        
        (1, "+6281122334455", None, dt_to_ms(datetime.datetime(2026, 9, 27, 8, 35, 12, tzinfo=datetime.timezone.utc)),
         0, 0, 1, -1, 2, 0, None,
         "Siap Mas, nanti jam 1 siang di ruang rapat lt 3 ya.", "+6281100000", 0, 1, 0, "com.google.android.apps.messaging", 1),

        # Telkomsel promo
        (2, "TELKOMSEL", None, dt_to_ms(datetime.datetime(2026, 9, 27, 14, 10, 0, tzinfo=datetime.timezone.utc)),
         dt_to_ms(datetime.datetime(2026, 9, 27, 14, 9, 50, tzinfo=datetime.timezone.utc)), 0, 1, -1, 1, 0, None,
         "Nikmati Kuota Internet MAX 35GB hanya Rp 75rb. Aktifkan sekarang di MyTelkomsel atau hubungi *363#.", "+6281100000", 0, 1, 0, "com.google.android.apps.messaging", 1),

        # WhatsApp OTP Verification
        (3, "WhatsApp", None, dt_to_ms(datetime.datetime(2026, 9, 27, 19, 4, 15, tzinfo=datetime.timezone.utc)),
         dt_to_ms(datetime.datetime(2026, 9, 27, 19, 4, 10, tzinfo=datetime.timezone.utc)), 0, 1, -1, 1, 0, None,
         "Your WhatsApp code: 312-895. Do not share this code with anyone.", "+6281100000", 0, 1, 0, "com.google.android.apps.messaging", 1),

        # ---------------- INCIDENT MESSAGES ----------------
        # 1. Phishing Initial Vector (Received)
        (4, "+6281299887766", None, dt_to_ms(T_PHISH_SMS),
         dt_to_ms(datetime.datetime(2026, 9, 28, 9, 15, 15, tzinfo=datetime.timezone.utc)), 0, 1, -1, 1, 0, None,
         "[BCA Alert] Terdeteksi upaya login tidak wajar pada akun Anda. Segera amankan & perbarui proteksi m-Banking melalui: https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=",
         "+6281100000", 0, 1, 0, "com.google.android.apps.messaging", 1),

        # 2. Bank Official Transaction OTP (Received - Suppressed by malware: read=1, seen=0)
        (5, "BANK_CENTRAL", None, dt_to_ms(T_OTP_INCOMING),
         dt_to_ms(datetime.datetime(2026, 9, 28, 9, 25, 28, tzinfo=datetime.timezone.utc)), 0, 1, -1, 1, 0, None,
         "PERINGATAN! JANGAN BERIKAN KODE INI KEPADA SIAPAPUN. Kode OTP transaksi transfer Rp 15.000.000 ke rekening 8872192831 adalah 849201. Berlaku 5 menit.",
         "+6281100000", 0, 1, 0, "com.google.android.apps.messaging", 0),

        # 3. Exfiltrated OTP SMS (Sent - Disguised as Fake System Crash Report with Base64 JSON)
        (6, "+6282133445566", None, dt_to_ms(T_OTP_EXFIL),
         0, 0, 1, -1, 2, 0, None,
         "[SYS_CRASH_REPORT]::eyJ2aWN0aW0iOiIrNjI4MTMxMTIyMzM0NCIsIm90cCI6Ijg0OTIwMSIsInR4X2lkIjoiVFgtODkwMjMifQ==",
         "+6281100000", 0, 1, 0, "com.secupdate.banking.bcamobile", 1),
    ]

    cur.executemany("""
    INSERT INTO sms (thread_id, address, person, date, date_sent, protocol, read, status, type, reply_path_present, subject, body, service_center, locked, sub_id, error_code, creator, seen)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sms_entries)

    conn.commit()
    conn.close()
    print("[+] Created mmssms.db with authentic SMS messages")

def create_chrome_artifacts():
    """Generates Chrome History database in /data/data/com.android.chrome/app_chrome/Default/"""
    db_dir = os.path.join(BUILD_DIR, "data", "data", "com.android.chrome", "app_chrome", "Default")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "History")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create tables needed by ALEAPP get_chrome and get_chromeDownloads
    cur.execute("""
    CREATE TABLE urls (
        id INTEGER PRIMARY KEY,
        url LONGVARCHAR,
        title LONGVARCHAR,
        visit_count INTEGER DEFAULT 0 NOT NULL,
        typed_count INTEGER DEFAULT 0 NOT NULL,
        last_visit_time INTEGER NOT NULL,
        hidden INTEGER DEFAULT 0 NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE visits (
        id INTEGER PRIMARY KEY,
        url INTEGER NOT NULL,
        visit_time INTEGER NOT NULL,
        from_visit INTEGER,
        transition INTEGER DEFAULT 0 NOT NULL,
        segment_id INTEGER,
        visit_duration INTEGER DEFAULT 0 NOT NULL,
        incremented_visit_count INTEGER DEFAULT 1 NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE downloads (
        id INTEGER PRIMARY KEY,
        guid VARCHAR NOT NULL,
        current_path LONGVARCHAR NOT NULL,
        target_path LONGVARCHAR NOT NULL,
        start_time INTEGER NOT NULL,
        received_bytes INTEGER NOT NULL,
        total_bytes INTEGER NOT NULL,
        state INTEGER NOT NULL,
        danger_type INTEGER NOT NULL,
        interrupt_reason INTEGER NOT NULL,
        hash BLOB NOT NULL,
        end_time INTEGER NOT NULL,
        opened INTEGER NOT NULL,
        last_access_time INTEGER NOT NULL,
        transient INTEGER NOT NULL,
        referrer VARCHAR NOT NULL,
        site_url VARCHAR NOT NULL,
        tab_url VARCHAR NOT NULL,
        tab_referrer_url VARCHAR NOT NULL,
        http_method VARCHAR NOT NULL,
        by_ext_id VARCHAR NOT NULL,
        by_ext_name VARCHAR NOT NULL,
        etag VARCHAR NOT NULL,
        last_modified VARCHAR NOT NULL,
        mime_type VARCHAR NOT NULL,
        original_mime_type VARCHAR NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE downloads_url_chains (
        id INTEGER NOT NULL,
        chain_index INTEGER NOT NULL,
        url LONGVARCHAR NOT NULL,
        PRIMARY KEY (id, chain_index)
    );
    """)

    cur.execute("""
    CREATE TABLE keyword_search_terms (
        keyword_id INTEGER NOT NULL,
        url_id INTEGER NOT NULL,
        lower_term LONGVARCHAR NOT NULL,
        term LONGVARCHAR NOT NULL
    );
    """)

    # Populate Normal History
    urls_data = [
        (1, "https://www.google.com", "Google", 12, 5, dt_to_webkit(datetime.datetime(2026, 9, 28, 8, 10, 0, tzinfo=datetime.timezone.utc)), 0),
        (2, "https://news.detik.com/berita", "detikNews - Berita Terkini dan Terpopuler Hari Ini", 3, 1, dt_to_webkit(datetime.datetime(2026, 9, 28, 8, 15, 30, tzinfo=datetime.timezone.utc)), 0),
        (3, "https://www.tokopedia.com", "Tokopedia - Jual Beli Online Mudah & Terpercaya", 5, 2, dt_to_webkit(datetime.datetime(2026, 9, 28, 8, 45, 0, tzinfo=datetime.timezone.utc)), 0),
        # Phishing Gateway Navigation
        (4, "https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=", "BCA Security Verification Gateway", 1, 1, dt_to_webkit(T_PHISH_SMS), 0),
        # Direct Download Redirection Target
        (5, "https://bca-mobile-alert.site/BCA2026.apk", "BCA Mobile Security Patch 2026", 1, 0, dt_to_webkit(T_DOWNLOAD_START), 0),
    ]

    cur.executemany("INSERT INTO urls VALUES (?, ?, ?, ?, ?, ?, ?)", urls_data)

    visits_data = [
        (1, 1, dt_to_webkit(datetime.datetime(2026, 9, 28, 8, 10, 0, tzinfo=datetime.timezone.utc)), 0, 805306368, 1, 45, 1),
        (2, 2, dt_to_webkit(datetime.datetime(2026, 9, 28, 8, 15, 30, tzinfo=datetime.timezone.utc)), 1, 805306368, 2, 120, 1),
        (3, 3, dt_to_webkit(datetime.datetime(2026, 9, 28, 8, 45, 0, tzinfo=datetime.timezone.utc)), 0, 805306368, 3, 300, 1),
        (4, 4, dt_to_webkit(T_PHISH_SMS), 0, 805306368, 4, 15, 1),
        (5, 5, dt_to_webkit(T_DOWNLOAD_START), 4, 805306368, 5, 10, 1),
    ]

    cur.executemany("INSERT INTO visits VALUES (?, ?, ?, ?, ?, ?, ?, ?)", visits_data)

    # Downloads table entry
    # Note: Target Path shows the APK that was downloaded. In real life, perpetrator deletes it from storage,
    # but the download entry in Chrome History database persists permanently!
    download_entry = (
        1,
        "4a796e83-e182-4217-bfd2-b88301cfa9e3",
        "/storage/emulated/0/Download/BCA2026.apk",
        "/storage/emulated/0/Download/BCA2026.apk",
        dt_to_webkit(T_DOWNLOAD_START),
        8452100,
        8452100,
        1, # State = 1 (COMPLETE)
        0, # Danger type = 0 (NOT_DANGEROUS)
        0, # Interrupt reason = 0 (NONE)
        b"\x3a\x91\xf8\x2b\x6c\x09\x12\x44\xae\x81\x55\x33\xdd\xaa\x12\x04",
        dt_to_webkit(T_DOWNLOAD_FINISH),
        1, # Opened = 1 (Yes)
        dt_to_webkit(T_DOWNLOAD_FINISH),
        0,
        "https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=",
        "https://bca-mobile-alert.site/BCA2026.apk",
        "https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=",
        "",
        "GET",
        "",
        "",
        'W/"80f5c4-645"',
        "Sun, 28 Sep 2026 09:17:45 GMT",
        "application/vnd.android.package-archive",
        "application/vnd.android.package-archive"
    )

    cur.execute("""
    INSERT INTO downloads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, download_entry)

    # Download URL chains
    cur.execute("INSERT INTO downloads_url_chains VALUES (1, 0, ?)", ("https://bca-sec.link/check?target=aHR0cHM6Ly9iY2EtbW9iaWxlLWFsZXJ0LnNpdGUvQkNBMjAyNi5hcGs=",))
    cur.execute("INSERT INTO downloads_url_chains VALUES (1, 1, ?)", ("https://bca-mobile-alert.site/BCA2026.apk",))

    conn.commit()
    conn.close()
    print("[+] Created Chrome History with download records")

def create_system_packages_artifacts():
    """Generates packages.xml and packages.list in /data/system/"""
    sys_dir = os.path.join(BUILD_DIR, "data", "system")
    os.makedirs(sys_dir, exist_ok=True)

    install_time_hex = ms_to_hex(dt_to_ms(T_INSTALL))

    packages_xml_content = f"""<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<packages>
    <version volumeUuid="" sdkVersion="28" databaseVersion="3" fingerprint="google/walleye/walleye:9/PQ3A.190801.002/5670241:user/release-keys" />
    <permission-trees />
    <permissions>
        <item name="android.permission.INTERNET" package="android" protection="1" />
        <item name="android.permission.READ_SMS" package="android" protection="1" />
        <item name="android.permission.RECEIVE_SMS" package="android" protection="1" />
        <item name="android.permission.SEND_SMS" package="android" protection="1" />
        <item name="android.permission.FOREGROUND_SERVICE" package="android" protection="0" />
        <item name="android.permission.RECEIVE_BOOT_COMPLETED" package="android" protection="1" />
    </permissions>

    <!-- Standard Google Apps -->
    <package name="com.android.chrome" codePath="/data/app/com.android.chrome-1" primaryCpuAbi="arm64-v8a" publicFlags="805846596" privateFlags="0" ft="18aaf000000" it="18aaf000000" ut="18aaf000000" version="410310534" userId="10042">
        <sigs count="1" schemeVersion="2">
            <cert index="0" />
        </sigs>
        <perms>
            <item name="android.permission.INTERNET" granted="true" flags="0" />
        </perms>
    </package>

    <package name="com.google.android.apps.messaging" codePath="/data/app/com.google.android.apps.messaging-1" primaryCpuAbi="arm64-v8a" publicFlags="805846596" privateFlags="0" ft="18aaf000000" it="18aaf000000" ut="18aaf000000" version="20260901" userId="10055">
        <sigs count="1" schemeVersion="2">
            <cert index="1" />
        </sigs>
        <perms>
            <item name="android.permission.READ_SMS" granted="true" flags="0" />
            <item name="android.permission.RECEIVE_SMS" granted="true" flags="0" />
            <item name="android.permission.SEND_SMS" granted="true" flags="0" />
        </perms>
    </package>

    <package name="com.google.android.apps.nexuslauncher" codePath="/system/priv-app/NexusLauncherPrebuilt" primaryCpuAbi="arm64-v8a" publicFlags="805846596" privateFlags="0" ft="18aaf000000" it="18aaf000000" ut="18aaf000000" version="9" userId="10012">
        <sigs count="1" schemeVersion="2">
            <cert index="2" />
        </sigs>
        <perms />
    </package>

    <!-- MALWARE PACKAGE (With disabled launcher component for stealth icon hiding) -->
    <package name="com.secupdate.banking.bcamobile" codePath="/data/app/com.secupdate.banking.bcamobile-X91abF2==" primaryCpuAbi="arm64-v8a" publicFlags="805846596" privateFlags="0" ft="{install_time_hex}" it="{install_time_hex}" ut="{install_time_hex}" version="104" userId="10145">
        <sigs count="1" schemeVersion="2">
            <cert index="9" />
        </sigs>
        <perms>
            <item name="android.permission.INTERNET" granted="true" flags="0" />
            <item name="android.permission.READ_SMS" granted="true" flags="0" />
            <item name="android.permission.RECEIVE_SMS" granted="true" flags="0" />
            <item name="android.permission.SEND_SMS" granted="true" flags="0" />
            <item name="android.permission.RECEIVE_BOOT_COMPLETED" granted="true" flags="0" />
            <item name="android.permission.FOREGROUND_SERVICE" granted="true" flags="0" />
        </perms>
        <!-- Stealth Cover-Up: Disabling launcher component so icon disappears from home screen -->
        <disabled-components>
            <item name="com.secupdate.banking.bcamobile.MainActivity" />
        </disabled-components>
    </package>
</packages>
"""

    packages_xml_path = os.path.join(sys_dir, "packages.xml")
    with open(packages_xml_path, "w", encoding="utf-8") as f:
        f.write(packages_xml_content)

    packages_list_content = """com.android.chrome 10042 0 /data/user/0/com.android.chrome default:targetSdkVersion=28 3003
com.google.android.apps.messaging 10055 0 /data/user/0/com.google.android.apps.messaging default:targetSdkVersion=28 3003
com.google.android.apps.nexuslauncher 10012 0 /data/user/0/com.google.android.apps.nexuslauncher default:targetSdkVersion=28 none
com.secupdate.banking.bcamobile 10145 0 /data/user/0/com.secupdate.banking.bcamobile default:targetSdkVersion=28 3003
"""
    packages_list_path = os.path.join(sys_dir, "packages.list")
    with open(packages_list_path, "w", encoding="utf-8") as f:
        f.write(packages_list_content)

    print("[+] Created packages.xml and packages.list")

def create_usagestats_artifacts():
    """Generates usagestats XML file in /data/system/usagestats/0/daily/"""
    usagestats_dir = os.path.join(BUILD_DIR, "data", "system", "usagestats", "0")
    daily_dir = os.path.join(usagestats_dir, "daily")
    os.makedirs(daily_dir, exist_ok=True)

    # version file (Android 9)
    version_file = os.path.join(usagestats_dir, "version")
    with open(version_file, "wb") as f:
        f.write(b"3\n9;REL;6736742\n")

    # Base timestamp of file: 2026-09-28 07:20:00 UTC = 1790580000000
    base_file_time = 1790580000000
    target_exec_ms = dt_to_ms(T_EXECUTE_RESUME) # 1790587265000 (09:21:05 UTC)
    target_pause_ms = dt_to_ms(T_EXECUTE_PAUSE)  # 1790587295000 (09:21:35 UTC)

    offset_resume = target_exec_ms - base_file_time # 7265000 ms
    offset_pause = target_pause_ms - base_file_time   # 7295000 ms

    # Pre-incident offsets for background events
    offset_launcher_start = 3600000 # 08:20:00 UTC
    offset_chrome_resume = 6900000  # 09:15:00 UTC
    offset_chrome_pause = 7100000   # 09:18:20 UTC

    usagestats_xml = f"""<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<usagestats version="1" endTime="8000000">
    <packages>
        <package lastTimeActive="{offset_launcher_start}" package="com.google.android.apps.nexuslauncher" timeActive="120000" lastEvent="2" />
        <package lastTimeActive="{offset_chrome_pause}" package="com.android.chrome" timeActive="200000" lastEvent="2" />
        <package lastTimeActive="{offset_pause}" package="com.secupdate.banking.bcamobile" timeActive="30000" lastEvent="2" appLaunchCount="1" />
    </packages>
    <configurations>
        <config lastTimeActive="1000" timeActive="7000000" />
    </configurations>
    <event-log>
        <!-- Launcher active in morning -->
        <event time="{offset_launcher_start}" package="com.google.android.apps.nexuslauncher" class="com.google.android.apps.nexuslauncher.NexusLauncherActivity" flags="0" type="1" />
        <event time="{offset_launcher_start + 10000}" package="com.google.android.apps.nexuslauncher" class="com.google.android.apps.nexuslauncher.NexusLauncherActivity" flags="0" type="2" />

        <!-- Chrome opened to view phishing link & download APK -->
        <event time="{offset_chrome_resume}" package="com.android.chrome" class="org.chromium.chrome.browser.ChromeTabbedActivity" flags="0" type="1" />
        <event time="{offset_chrome_pause}" package="com.android.chrome" class="org.chromium.chrome.browser.ChromeTabbedActivity" flags="0" type="2" />

        <!-- MALWARE FIRST EXECUTION EVENT (ACTIVITY_RESUMED = 1) at 2026-09-28 09:21:05 UTC -->
        <event time="{offset_resume}" package="com.secupdate.banking.bcamobile" class="com.secupdate.banking.bcamobile.AuthActivity" flags="0" type="1" />
        <event time="{offset_pause}" package="com.secupdate.banking.bcamobile" class="com.secupdate.banking.bcamobile.AuthActivity" flags="0" type="2" />
    </event-log>
</usagestats>
"""

    stat_file = os.path.join(daily_dir, str(base_file_time))
    with open(stat_file, "w", encoding="utf-8") as f:
        f.write(usagestats_xml)

    print(f"[+] Created usagestats daily file with execution offset {offset_resume} ({T_EXECUTE_RESUME} UTC)")

def pack_to_zip():
    """Packs the build_temp directory contents into evidence.zip including explicit directory entries."""
    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(BUILD_DIR):
            for d in dirs:
                dir_full = os.path.join(root, d)
                rel_dir = os.path.relpath(dir_full, BUILD_DIR).replace("\\", "/") + "/"
                z.write(dir_full, rel_dir)
            for f in files:
                abs_path = os.path.join(root, f)
                rel_path = os.path.relpath(abs_path, BUILD_DIR)
                zip_path = rel_path.replace("\\", "/")
                z.write(abs_path, zip_path)

    zip_size = os.path.getsize(OUTPUT_ZIP)
    print(f"[SUCCESS] Successfully created evidence archive: {OUTPUT_ZIP} ({zip_size} bytes)")

def main():
    print("=" * 60)
    print("Building CTF Forensic Evidence for ALEAPP...")
    print("=" * 60)
    clean_build_dir()
    create_telephony_artifacts()
    create_chrome_artifacts()
    create_system_packages_artifacts()
    create_usagestats_artifacts()
    pack_to_zip()
    print("=" * 60)
    print("Build complete! Evidence is ready for ALEAPP analysis.")
    print("=" * 60)

if __name__ == "__main__":
    main()
