const API_BASE = '/api';

// Load drivers on page load
document.addEventListener('DOMContentLoaded', () => {
    loadDrivers();
});

// Load available drivers
async function loadDrivers() {
    try {
        const response = await fetch(`${API_BASE}/drivers`);
        const result = await response.json();
        
        if (result.success) {
            displayDrivers(result.data);
        }
    } catch (error) {
        console.error('Error loading drivers:', error);
    }
}

// Display drivers
function displayDrivers(drivers) {
    const driversList = document.getElementById('driversList');
    driversList.innerHTML = '';
    
    if (drivers.length === 0) {
        driversList.innerHTML = '<p>Tidak ada driver yang tersedia saat ini.</p>';
        return;
    }
    
    drivers.forEach(driver => {
        const driverCard = document.createElement('div');
        driverCard.className = 'driver-card';
        driverCard.innerHTML = `
            <h3>${driver.name}</h3>
            <div class="rating">⭐ ${driver.rating}</div>
            <p>${driver.phone}</p>
            <span class="status ${driver.status}">${driver.status === 'available' ? 'Tersedia' : 'Sibuk'}</span>
        `;
        driversList.appendChild(driverCard);
    });
}

// Handle booking form submission
document.getElementById('bookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        customer_name: document.getElementById('customerName').value,
        customer_phone: document.getElementById('customerPhone').value,
        pickup: document.getElementById('pickup').value,
        destination: document.getElementById('destination').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/book`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showModal('Booking Berhasil!', `
                <h3>Detail Booking</h3>
                <p><strong>ID Booking:</strong> ${result.data.id}</p>
                <p><strong>Driver:</strong> ${result.data.driver_name}</p>
                <p><strong>No. Driver:</strong> ${result.data.driver_phone}</p>
                <p><strong>Penjemputan:</strong> ${result.data.pickup}</p>
                <p><strong>Tujuan:</strong> ${result.data.destination}</p>
                <p><strong>Estimasi Tarif:</strong> Rp ${result.data.estimated_fare.toLocaleString('id-ID')}</p>
                <p><strong>Status:</strong> ${result.data.status}</p>
            `);
            document.getElementById('bookingForm').reset();
            loadDrivers(); // Refresh drivers list
        } else {
            showModal('Error', `<p>${result.message}</p>`);
        }
    } catch (error) {
        showModal('Error', '<p>Terjadi kesalahan saat memproses booking. Silakan coba lagi.</p>');
        console.error('Error:', error);
    }
});

// Handle track form submission
document.getElementById('trackForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const phone = document.getElementById('trackPhone').value;
    
    try {
        const response = await fetch(`${API_BASE}/bookings?phone=${phone}`);
        const result = await response.json();
        
        if (result.success) {
            displayBookings(result.data);
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
        document.getElementById('bookingResults').innerHTML = 
            '<p>Terjadi kesalahan saat memuat data booking.</p>';
    }
});

// Display bookings
function displayBookings(bookings) {
    const bookingResults = document.getElementById('bookingResults');
    bookingResults.innerHTML = '';
    
    if (bookings.length === 0) {
        bookingResults.innerHTML = '<p>Tidak ada booking ditemukan untuk nomor telepon ini.</p>';
        return;
    }
    
    bookings.forEach(booking => {
        const bookingCard = document.createElement('div');
        bookingCard.className = 'booking-card';
        
        const statusText = {
            'pending': 'Menunggu',
            'completed': 'Selesai',
            'cancelled': 'Dibatalkan'
        };
        
        bookingCard.innerHTML = `
            <h3>Booking #${booking.id}</h3>
            <div class="booking-info">
                <p><strong>Driver:</strong> ${booking.driver_name}</p>
                <p><strong>No. Driver:</strong> ${booking.driver_phone}</p>
                <p><strong>Penjemputan:</strong> ${booking.pickup}</p>
                <p><strong>Tujuan:</strong> ${booking.destination}</p>
                <p><strong>Tarif:</strong> Rp ${booking.estimated_fare.toLocaleString('id-ID')}</p>
                <p><strong>Status:</strong> <span class="booking-status status ${booking.status}">${statusText[booking.status] || booking.status}</span></p>
            </div>
            ${booking.status === 'pending' ? `
                <button onclick="cancelBooking(${booking.id})" class="btn btn-secondary" style="margin-right: 10px;">Batalkan</button>
                <button onclick="completeBooking(${booking.id})" class="btn btn-primary">Selesai</button>
            ` : ''}
        `;
        bookingResults.appendChild(bookingCard);
    });
}

// Cancel booking
async function cancelBooking(bookingId) {
    if (!confirm('Apakah Anda yakin ingin membatalkan booking ini?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/bookings/${bookingId}/cancel`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showModal('Berhasil', '<p>Booking berhasil dibatalkan.</p>');
            const phone = document.getElementById('trackPhone').value;
            if (phone) {
                document.getElementById('trackForm').dispatchEvent(new Event('submit'));
            }
            loadDrivers();
        } else {
            showModal('Error', `<p>${result.message}</p>`);
        }
    } catch (error) {
        showModal('Error', '<p>Terjadi kesalahan saat membatalkan booking.</p>');
        console.error('Error:', error);
    }
}

// Complete booking
async function completeBooking(bookingId) {
    if (!confirm('Tandai booking ini sebagai selesai?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/bookings/${bookingId}/complete`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showModal('Berhasil', '<p>Booking ditandai sebagai selesai.</p>');
            const phone = document.getElementById('trackPhone').value;
            if (phone) {
                document.getElementById('trackForm').dispatchEvent(new Event('submit'));
            }
            loadDrivers();
        } else {
            showModal('Error', `<p>${result.message}</p>`);
        }
    } catch (error) {
        showModal('Error', '<p>Terjadi kesalahan saat menyelesaikan booking.</p>');
        console.error('Error:', error);
    }
}

// Modal functions
function showModal(title, content) {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `<h2>${title}</h2>${content}`;
    modal.style.display = 'block';
}

// Close modal
document.querySelector('.close').addEventListener('click', () => {
    document.getElementById('modal').style.display = 'none';
});

window.addEventListener('click', (e) => {
    const modal = document.getElementById('modal');
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});
