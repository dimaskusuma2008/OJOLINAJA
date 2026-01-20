# Ojek Online Website

Website aplikasi ojek online yang dibuat dengan Python Flask dan dapat di-deploy ke Vercel.

## Fitur

- 🏍️ Pesan ojek online dengan mudah
- 📍 Input lokasi penjemputan dan tujuan
- 👨‍💼 Daftar driver yang tersedia
- 📱 Lacak status booking berdasarkan nomor telepon
- ✅ Kelola booking (batalkan/selesai)

## Teknologi

- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Vercel

## Cara Deploy ke Vercel

1. Install Vercel CLI (jika belum):
   ```bash
   npm i -g vercel
   ```

2. Login ke Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Atau deploy langsung dari GitHub:
   - Push code ke repository GitHub
   - Import project di Vercel dashboard
   - Vercel akan otomatis mendeteksi konfigurasi Python

## Struktur Project

```
.
├── api/
│   └── index.py          # Flask API endpoints
├── index.html            # Halaman utama
├── styles.css            # Styling
├── script.js             # JavaScript frontend
├── vercel.json           # Konfigurasi Vercel
├── requirements.txt      # Python dependencies
└── README.md             # Dokumentasi
```

## API Endpoints

- `GET /api/drivers` - Mendapatkan daftar driver yang tersedia
- `POST /api/book` - Membuat booking baru
- `GET /api/bookings?phone=xxx` - Mendapatkan booking berdasarkan nomor telepon
- `POST /api/bookings/<id>/cancel` - Membatalkan booking
- `POST /api/bookings/<id>/complete` - Menyelesaikan booking

## Catatan

- Data disimpan dalam memory (tidak persisten)
- Untuk production, disarankan menggunakan database seperti PostgreSQL atau MongoDB
- Pastikan semua dependencies terinstall sebelum deploy
