from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory database (untuk demo, bisa diganti dengan database sesungguhnya)
drivers = [
    {"id": 1, "name": "Budi Santoso", "phone": "081234567890", "status": "available", "rating": 4.8, "location": {"lat": -6.2088, "lng": 106.8456}},
    {"id": 2, "name": "Ahmad Rizki", "phone": "081234567891", "status": "available", "rating": 4.9, "location": {"lat": -6.2146, "lng": 106.8451}},
    {"id": 3, "name": "Siti Nurhaliza", "phone": "081234567892", "status": "busy", "rating": 4.7, "location": {"lat": -6.2000, "lng": 106.8500}},
]

bookings = []
booking_id_counter = 1

# Catatan:
# Di Vercel, semua request ke /api/... akan di-route ke file ini (lihat vercel.json).
# Supaya endpoint cocok dengan frontend (yang memanggil /api/drivers, /api/book, dst),
# maka route Flask TIDAK pakai prefix /api lagi, cukup /drivers, /book, /bookings, dll.

@app.route('/drivers', methods=['GET'])
def get_drivers():
    """Mendapatkan daftar driver yang tersedia"""
    available_drivers = [d for d in drivers if d['status'] == 'available']
    return jsonify({
        "success": True,
        "data": available_drivers
    })

@app.route('/book', methods=['POST'])
def book_ride():
    """Membuat booking ojek"""
    global booking_id_counter
    
    data = request.get_json()
    
    required_fields = ['pickup', 'destination', 'customer_name', 'customer_phone']
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "message": f"Field {field} is required"
            }), 400
    
    # Cari driver yang tersedia
    available_driver = None
    for driver in drivers:
        if driver['status'] == 'available':
            available_driver = driver
            break
    
    if not available_driver:
        return jsonify({
            "success": False,
            "message": "Tidak ada driver yang tersedia saat ini"
        }), 400
    
    # Buat booking
    booking = {
        "id": booking_id_counter,
        "driver_id": available_driver['id'],
        "driver_name": available_driver['name'],
        "driver_phone": available_driver['phone'],
        "pickup": data['pickup'],
        "destination": data['destination'],
        "customer_name": data['customer_name'],
        "customer_phone": data['customer_phone'],
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "estimated_fare": calculate_fare(data['pickup'], data['destination'])
    }
    
    bookings.append(booking)
    booking_id_counter += 1
    
    # Update status driver menjadi busy
    available_driver['status'] = 'busy'
    
    return jsonify({
        "success": True,
        "data": booking
    })

@app.route('/bookings', methods=['GET'])
def get_bookings():
    """Mendapatkan daftar booking"""
    phone = request.args.get('phone')
    
    if phone:
        user_bookings = [b for b in bookings if b['customer_phone'] == phone]
        return jsonify({
            "success": True,
            "data": user_bookings
        })
    
    return jsonify({
        "success": True,
        "data": bookings
    })

@app.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Membatalkan booking"""
    booking = next((b for b in bookings if b['id'] == booking_id), None)
    
    if not booking:
        return jsonify({
            "success": False,
            "message": "Booking tidak ditemukan"
        }), 404
    
    if booking['status'] == 'completed' or booking['status'] == 'cancelled':
        return jsonify({
            "success": False,
            "message": f"Booking sudah {booking['status']}"
        }), 400
    
    booking['status'] = 'cancelled'
    
    # Kembalikan driver ke status available
    driver = next((d for d in drivers if d['id'] == booking['driver_id']), None)
    if driver:
        driver['status'] = 'available'
    
    return jsonify({
        "success": True,
        "data": booking
    })

@app.route('/bookings/<int:booking_id>/complete', methods=['POST'])
def complete_booking(booking_id):
    """Menyelesaikan booking"""
    booking = next((b for b in bookings if b['id'] == booking_id), None)
    
    if not booking:
        return jsonify({
            "success": False,
            "message": "Booking tidak ditemukan"
        }), 404
    
    booking['status'] = 'completed'
    booking['completed_at'] = datetime.now().isoformat()
    
    # Kembalikan driver ke status available
    driver = next((d for d in drivers if d['id'] == booking['driver_id']), None)
    if driver:
        driver['status'] = 'available'
    
    return jsonify({
        "success": True,
        "data": booking
    })

def calculate_fare(pickup, destination):
    """Menghitung estimasi tarif (simplified)"""
    # Untuk demo, menggunakan tarif tetap
    base_fare = 10000
    distance_fare = 2000  # per km (simulated)
    return base_fare + (distance_fare * 5)  # Assume 5km distance

if __name__ == '__main__':
    app.run(debug=True)
