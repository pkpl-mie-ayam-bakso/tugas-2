# Dokumentasi Implementasi Keamanan & Autentikasi (Anggota 1)

Dokumen ini merinci implementasi teknis untuk fitur Autentikasi dan Pengerasan Keamanan (Security Hardening) pada proyek Tugas 2 PKPL.

## 🛡️ Ringkasan Implementasi Keamanan

Seluruh perubahan didasarkan pada prinsip **Defense in Depth**, memastikan keamanan berlapis mulai dari tingkat jaringan (header), aplikasi (validasi input), hingga data (audit logging).

---

## 1. Autentikasi & Otorisasi (OAuth 2.0 / OIDC)
Sistem menggunakan **OpenID Connect (OIDC)** melalui Google Identity Platform.
- **Handshake Langsung**: Menggunakan provider `google_login` dari `django-allauth` untuk melewati form pendaftaran tambahan, mengurangi permukaan serangan (attack surface).
- **Verifikasi Identitas**: Sesi dibuat hanya setelah Google memberikan token identitas yang valid.
- **Otorisasi Berbasis Email**: Implementasi pengecekan server-side terhadap daftar `ALLOWED_MEMBER_EMAILS` di `settings.py`.

## 2. Validasi Input & Pencegahan Injeksi
Mencegah serangan **XSS** dan manipulasi data melalui form kustomisasi.
- **SiteSettingsForm (`forms.py`)**: Menggantikan pengambilan data manual dengan abstraksi form Django yang aman.
- **Regex Validation**: Menggunakan Regular Expression untuk memvalidasi format kode warna Hex (`#RRGGBB`).
- **Bound Check**: Validasi rentang ukuran font (10px - 32px) untuk mencegah anomali UI atau *UI-based Denial of Service*.

## 3. Audit Logging & Akuntabilitas
Menyediakan jejak audit untuk setiap tindakan sensitif.
- **Model AuditLog**: Menyimpan tipe aksi (`UPDATE`, `VIEW`, `FAILED_AUTH`), email pengguna, timestamp, dan alamat IP.
- **JSON Diff**: Menyimpan perubahan nilai (*old value* vs *new value*) dalam format JSON untuk transparansi penuh.
- **IP Tracking**: Mendukung ekstraksi IP asli di belakang proxy/load balancer melalui header `X-Forwarded-For`.

## 4. Pengerasan Konfigurasi (Hardening)
Mengubah konfigurasi standar Django menjadi konfigurasi siap produksi (Production-Ready).
- **Environment Isolation**: Menggunakan `python-dotenv` untuk memisahkan rahasia (`SECRET_KEY`, `GOOGLE_CLIENT_SECRET`) dari kode sumber.
- **Deployment Checks**: Implementasi logika kondisional di `settings.py` yang memaksa penggunaan HTTPS dan HSTS ketika `DEBUG=False`.
- **Content Security Policy (CSP)**: Menambahkan header CSP untuk membatasi eksekusi skrip pihak ketiga yang tidak terdaftar.

## 5. Proteksi Serangan Web
- **CSRF Protection**: Menambahkan token CSRF pada semua request POST di template `customize.html`.
- **Rate Limiting**: Menggunakan `django-ratelimit` untuk membatasi pengiriman form (20 kali per menit per user) guna mencegah serangan brute-force.
- **Admin Security**: Membatasi akses model `AuditLog` di panel admin menjadi *read-only* dan hanya bisa diakses oleh **Superuser**.

---

## 🚀 Cara Verifikasi Keamanan
Gunakan perintah berikut untuk memastikan semua sistem berfungsi:

1. **System Check**: `python manage.py check --deploy`
2. **Rate Limit Test**: Gunakan loop `curl` untuk mengirim 21 request ke endpoint `/customize/`.
3. **Audit Log Verification**: Cek tabel `main_auditlog` di database setelah melakukan perubahan tampilan.
