from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import os
import random

app = Flask(__name__)

# In-memory database (untuk demo, bisa diganti dengan database sesungguhnya)
# Fokus: area dalam kota Cirebon, biker dan order dianggap "unlimited"

BASE_BIKERS = [
    "Alex",
    "Ujang",
    "Dede",
    "Yanto",
    "Sinta",
    "Rina",
    "Dadan",
    "Jaya",
    "Wati",
    "Bowo",
]

bookings = []
booking_id_counter = 1


# =========================
# ROUTE HALAMAN UTAMA
# =========================

@app.route("/", methods=["GET"])
def index():
    """
    Serve file index.html dari root project.
    Vercel akan mengarahkan semua request ke app.py (lihat vercel.json),
    jadi di sini kita handle halaman utama.
    """
    return send_from_directory(".", "index.html")


@app.route("/<path:path>", methods=["GET"])
def static_files(path):
    """
    Serve file statis (CSS, JS, gambar).
    """
    if os.path.exists(path):
        return send_from_directory(".", path)
    # fallback ke index untuk path lain (opsional)
    return send_from_directory(".", "index.html")


# =========================
# API ENDPOINTS (PREFIX /api)
# =========================

@app.route("/api/drivers", methods=["GET"])
def get_drivers():
    """Mendapatkan daftar biker yang tersedia (secara virtual, unlimited)."""
    drivers = []
    # Generate banyak biker virtual agar kelihatan ramai (misal 30)
    for i in range(30):
        base_name = BASE_BIKERS[i % len(BASE_BIKERS)]
        drivers.append({
            "id": i + 1,
            "name": f"{base_name} #{i + 1}",
            "phone": f"08{random.randint(1000000000, 9999999999)}",
            "status": "available",
            "rating": round(random.uniform(4.5, 5.0), 1),
        })

    return jsonify({"success": True, "data": drivers})


@app.route("/api/book", methods=["POST"])
def book_ride():
    """Membuat booking ojek"""
    global booking_id_counter

    data = request.get_json() or {}

    # Tidak perlu nomor HP customer
    required_fields = ["pickup", "destination", "customer_name"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"Field {field} is required"
            }), 400

    # Pilih biker secara random dari daftar virtual (unlimited)
    biker_name = random.choice(BASE_BIKERS)
    driver_phone = f"08{random.randint(1000000000, 9999999999)}"

    distance_km = estimate_distance_km_cirebon(data["pickup"], data["destination"])
    estimated_fare = calculate_fare(distance_km)

    # Buat booking
    booking = {
        "id": booking_id_counter,
        "driver_name": biker_name,
        "driver_phone": driver_phone,
        "pickup": data["pickup"],
        "destination": data["destination"],
        "customer_name": data["customer_name"],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "estimated_fare": estimated_fare,
        "estimated_distance_km": distance_km,
        "city": "Cirebon"
    }

    bookings.append(booking)
    booking_id_counter += 1

    return jsonify({
        "success": True,
        "data": booking
    })


@app.route("/api/bookings", methods=["GET"])
def get_bookings():
    """Mendapatkan daftar booking (bisa difilter by ID booking)."""
    booking_id = request.args.get("id", type=int)

    if booking_id is not None:
        user_bookings = [b for b in bookings if b["id"] == booking_id]
        return jsonify({"success": True, "data": user_bookings})

    return jsonify({
        "success": True,
        "data": bookings
    })


@app.route("/api/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(booking_id):
    """Membatalkan booking"""
    booking = next((b for b in bookings if b["id"] == booking_id), None)

    if not booking:
        return jsonify({
            "success": False,
            "message": "Booking tidak ditemukan"
        }), 404

    if booking["status"] in ("completed", "cancelled"):
        return jsonify({
            "success": False,
            "message": f"Booking sudah {booking['status']}"
        }), 400

    booking["status"] = "cancelled"

    return jsonify({
        "success": True,
        "data": booking
    })


@app.route("/api/bookings/<int:booking_id>/complete", methods=["POST"])
def complete_booking(booking_id):
    """Menyelesaikan booking"""
    booking = next((b for b in bookings if b["id"] == booking_id), None)

    if not booking:
        return jsonify({
            "success": False,
            "message": "Booking tidak ditemukan"
        }), 404

    booking["status"] = "completed"
    booking["completed_at"] = datetime.now().isoformat()

    return jsonify({
        "success": True,
        "data": booking
    })


def estimate_distance_km_cirebon(pickup: str, destination: str) -> int:
    """
    Estimasi jarak dalam kota Cirebon berdasarkan teks lokasi.
    Menghasilkan jarak yang konsisten untuk kombinasi pickup + destination,
    di rentang 2–14 km (jarak wajar dalam kota).
    """
    key = (pickup + destination).lower()
    # Simple deterministic "hash" supaya setiap kombinasi selalu sama
    total = sum(ord(c) for c in key)
    return 2 + (total % 13)  # 2..14 km


def calculate_fare(distance_km: int) -> int:
    """
    Menghitung estimasi tarif berdasarkan jarak dalam kota Cirebon.
    Contoh skema: 5.000 tarif dasar + 3.000/km.
    """
    base_fare = 5000
    per_km = 3000
    return base_fare + int(per_km * max(distance_km, 1))


if __name__ == "__main__":
    app.run(debug=True)
