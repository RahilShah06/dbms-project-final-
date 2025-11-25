from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'Rahil@MySQL',
    'database': 'dbms3'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=False):
    """Helper function to execute database queries"""
    conn = get_db_connection()
    if not conn:
        return [] if fetch else None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            if 'SELECT' in query.upper():
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()
        else:
            conn.commit()
            result = None
        
        cursor.close()
        return result or [] if fetch else result
    except Exception as e:
        print(f"Query error: {e}")
        conn.rollback()
        return [] if fetch else None
    finally:
        conn.close()

def get_count(query, params=None):
    """Safe function to get count from database"""
    result = execute_query(query, params, fetch=True)
    return result[0]['total'] if result and len(result) > 0 else 0

# ===== ROUTES =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_role', methods=['POST'])
def select_role():
    role = request.form.get('role')
    if role == 'admin':
        return redirect(url_for('admin_login'))
    elif role == 'host':
        return redirect(url_for('host_login'))
    elif role == 'guest':
        return redirect(url_for('guest_dashboard'))
    return redirect(url_for('index'))

# ===== ADMIN ROUTES =====
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_id = request.form.get('admin_id')
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Verify against Admin table
        admin = execute_query(
            "SELECT * FROM Admin WHERE admin_id=%s AND email=%s", 
            (admin_id, email), 
            fetch=True
        )
        
        if admin:
            session['admin_id'] = admin_id
            session['admin_name'] = admin[0]['name']
            session['role'] = 'admin'
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    # Get counts from database
    total_properties = get_count("SELECT COUNT(*) as total FROM Property")
    total_guests = get_count("SELECT COUNT(*) as total FROM Guest")
    total_hosts = get_count("SELECT COUNT(*) as total FROM Host")
    active_bookings = get_count("SELECT COUNT(*) as total FROM Bookings WHERE Status = 'Confirmed'")
    
    return render_template('admin_dashboard.html',
                         total_properties=total_properties,
                         total_guests=total_guests,
                         total_hosts=total_hosts,
                         active_bookings=active_bookings,
                         admin_name=session.get('admin_name'))

@app.route('/admin/hosts', methods=['GET', 'POST'])
def manage_hosts():
    if 'admin_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            host_id = request.form.get('host_id')
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            join_date = request.form.get('join_date') or datetime.now().strftime('%Y-%m-%d')
            
            try:
                execute_query(
                    "INSERT INTO Host (host_id, name, email, phone, join_date) VALUES (%s, %s, %s, %s, %s)",
                    (host_id, name, email, phone, join_date)
                )
                flash('✅ Host added successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error adding host: {str(e)}', 'error')
                
        elif action == 'update':
            host_id = request.form.get('host_id')
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            try:
                execute_query(
                    "UPDATE Host SET name=%s, email=%s, phone=%s WHERE host_id=%s",
                    (name, email, phone, host_id)
                )
                flash('✅ Host updated successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error updating host: {str(e)}', 'error')
                
        elif action == 'delete':
            host_id = request.form.get('host_id')
            try:
                execute_query("DELETE FROM Host WHERE host_id=%s", (host_id,))
                flash('✅ Host deleted successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error deleting host: {str(e)}', 'error')
                
        return redirect(url_for('manage_hosts'))
        
    hosts = execute_query("SELECT * FROM Host", fetch=True)
    
    # Get property counts for each host
    for host in hosts:
        count = get_count("SELECT COUNT(*) as total FROM Property WHERE host_id=%s", (host['host_id'],))
        host['property_count'] = count
        
    return render_template('manage_hosts.html', hosts=hosts or [], admin_name=session.get('admin_name'))

@app.route('/admin/properties', methods=['GET', 'POST'])
def manage_properties():
    if 'admin_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            type_ = request.form.get('type')
            location = request.form.get('location')
            rating = request.form.get('rating') or 0
            price = request.form.get('price')
            status = request.form.get('status') or 'Available'
            host_id = request.form.get('host_id')
            
            try:
                execute_query(
                    "INSERT INTO Property (Name, Type, Location, Rating, PricePerNight, Status, host_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, type_, location, rating, price, status, host_id)
                )
                flash('✅ Property added successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error adding property: {str(e)}', 'error')
                
        elif action == 'update':
            property_id = request.form.get('property_id')
            name = request.form.get('name')
            type_ = request.form.get('type')
            location = request.form.get('location')
            rating = request.form.get('rating')
            price = request.form.get('price')
            status = request.form.get('status')
            host_id = request.form.get('host_id')
            
            try:
                execute_query(
                    "UPDATE Property SET Name=%s, Type=%s, Location=%s, Rating=%s, PricePerNight=%s, Status=%s, host_id=%s WHERE Property_ID=%s",
                    (name, type_, location, rating, price, status, host_id, property_id)
                )
                flash('✅ Property updated successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error updating property: {str(e)}', 'error')
                
        elif action == 'delete':
            property_id = request.form.get('property_id')
            try:
                execute_query("DELETE FROM Property WHERE Property_ID=%s", (property_id,))
                flash('✅ Property deleted successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error deleting property: {str(e)}', 'error')
                
        return redirect(url_for('manage_properties'))
        
    properties = execute_query("""
        SELECT p.*, h.name as host_name 
        FROM Property p 
        LEFT JOIN Host h ON p.host_id = h.host_id
    """, fetch=True)
    
    hosts = execute_query("SELECT * FROM Host", fetch=True)
    
    return render_template('manage_properties.html', 
                         properties=properties or [], 
                         hosts=hosts or [],
                         admin_name=session.get('admin_name'))

@app.route('/admin/guests', methods=['GET', 'POST'])
def manage_guests():
    if 'admin_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            joining_date = request.form.get('joining_date') or datetime.now().strftime('%Y-%m-%d')
            
            try:
                execute_query(
                    "INSERT INTO Guest (Name, Email, Phone, JoiningDate) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, joining_date)
                )
                flash('✅ Guest added successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error adding guest: {str(e)}', 'error')
                
        elif action == 'update':
            guest_id = request.form.get('guest_id')
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            try:
                execute_query(
                    "UPDATE Guest SET Name=%s, Email=%s, Phone=%s WHERE Guest_ID=%s",
                    (name, email, phone, guest_id)
                )
                flash('✅ Guest updated successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error updating guest: {str(e)}', 'error')
                
        elif action == 'delete':
            guest_id = request.form.get('guest_id')
            try:
                execute_query("DELETE FROM Guest WHERE Guest_ID=%s", (guest_id,))
                flash('✅ Guest deleted successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error deleting guest: {str(e)}', 'error')
                
        return redirect(url_for('manage_guests'))
        
    guests = execute_query("SELECT * FROM Guest", fetch=True)
    return render_template('manage_guests.html', guests=guests or [], admin_name=session.get('admin_name'))

@app.route('/admin/bookings', methods=['GET', 'POST'])
def manage_bookings():
    if 'admin_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            booking_type = request.form.get('booking_type')
            check_in = request.form.get('check_in')
            check_out = request.form.get('check_out')
            total_price = request.form.get('total_price')
            status = request.form.get('status')
            guest_id = request.form.get('guest_id')
            property_id = request.form.get('property_id')
            
            try:
                execute_query(
                    "INSERT INTO Bookings (BookingType, CheckIn, CheckOut, TotalPrice, Status, Guest_ID, Property_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (booking_type, check_in, check_out, total_price, status, guest_id, property_id)
                )
                flash('✅ Booking added successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error adding booking: {str(e)}', 'error')
        
        elif action == 'update':
            booking_id = request.form.get('booking_id')
            status = request.form.get('status')
            
            try:
                execute_query(
                    "UPDATE Bookings SET Status=%s WHERE Booking_ID=%s",
                    (status, booking_id)
                )
                flash('✅ Booking updated successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error updating booking: {str(e)}', 'error')
            
        elif action == 'delete':
            booking_id = request.form.get('booking_id')
            try:
                execute_query("DELETE FROM Bookings WHERE Booking_ID=%s", (booking_id,))
                flash('✅ Booking deleted successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error deleting booking: {str(e)}', 'error')
        
        return redirect(url_for('manage_bookings'))
    
    # Get all bookings with related information
    bookings = execute_query("""
        SELECT b.*, g.Name as guest_name, p.Name as property_name, h.name as host_name
        FROM Bookings b
        JOIN Guest g ON b.Guest_ID = g.Guest_ID
        JOIN Property p ON b.Property_ID = p.Property_ID
        JOIN Host h ON p.host_id = h.host_id
        ORDER BY b.CheckIn DESC
    """, fetch=True)
    
    properties = execute_query("SELECT Property_ID, Name FROM Property WHERE Status='Available'", fetch=True)
    guests = execute_query("SELECT Guest_ID, Name FROM Guest", fetch=True)
    
    return render_template('manage_bookings.html', 
                         bookings=bookings or [],
                         properties=properties or [],
                         guests=guests or [],
                         admin_name=session.get('admin_name'))

# ===== GUEST ROUTES =====
@app.route('/guest/dashboard')
def guest_dashboard():
    # Guest is now anonymous until they book
    guest_id = session.get('guest_id')
    guest_name = None
    my_bookings = 0
    
    if guest_id:
        guest_data = execute_query("SELECT * FROM Guest WHERE Guest_ID=%s", (guest_id,), fetch=True)
        if guest_data:
            guest_name = guest_data[0]['Name']
            my_bookings = get_count("SELECT COUNT(*) as total FROM Bookings WHERE Guest_ID=%s", (guest_id,))
    
    properties_available = get_count("SELECT COUNT(*) as total FROM Property WHERE Status='Available'")
    
    return render_template('guest_dashboard.html',
                         guest_name=guest_name,
                         my_bookings=my_bookings,
                         properties_available=properties_available)

@app.route('/book/<property_id>', methods=['GET', 'POST'])
def book_property(property_id):
    if request.method == 'POST':
        # Get Guest Details
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Get Booking Details
        booking_type = request.form.get('booking_type')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        
        # Validate dates
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if check_in_date < today:
            flash('❌ Check-in date cannot be in the past.', 'error')
            return redirect(url_for('book_property', property_id=property_id))
            
        if check_in_date >= check_out_date:
            flash('❌ Check-out date must be after check-in date.', 'error')
            return redirect(url_for('book_property', property_id=property_id))
        
        try:
            # Calculate Total Price
            property_data = execute_query("SELECT PricePerNight FROM Property WHERE Property_ID=%s", (property_id,), fetch=True)
            if not property_data:
                flash('Property not found', 'error')
                return redirect(url_for('guest_dashboard'))
                
            price_per_night = float(property_data[0]['PricePerNight'])
            days = (check_out_date - check_in_date).days
            total_price = price_per_night * days
            
            # Check if guest exists
            existing_guest = execute_query("SELECT Guest_ID FROM Guest WHERE Email=%s", (email,), fetch=True)
            
            if existing_guest:
                guest_id = existing_guest[0]['Guest_ID']
            else:
                # Create new guest
                execute_query(
                    "INSERT INTO Guest (Name, Email, Phone, JoiningDate) VALUES (%s, %s, %s, CURDATE())",
                    (name, email, phone)
                )
                # Get the new Guest ID
                new_guest = execute_query("SELECT Guest_ID FROM Guest WHERE Email=%s", (email,), fetch=True)
                guest_id = new_guest[0]['Guest_ID']
            
            # Store in session
            session['guest_id'] = guest_id
            
            # Create Booking
            execute_query(
                "INSERT INTO Bookings (BookingType, CheckIn, CheckOut, TotalPrice, Status, Guest_ID, Property_ID) VALUES (%s, %s, %s, %s, 'Confirmed', %s, %s)",
                (booking_type, check_in, check_out, total_price, guest_id, property_id)
            )
            flash('🎉 Booking confirmed successfully!', 'success')
            return redirect(url_for('guest_dashboard'))
            
        except Exception as e:
            flash(f'❌ Error creating booking: {str(e)}', 'error')
    
    property_data = execute_query("""
        SELECT p.*, h.name as host_name, h.phone as host_phone
        FROM Property p 
        JOIN Host h ON p.host_id = h.host_id
        WHERE p.Property_ID = %s
    """, (property_id,), fetch=True)
    
    if not property_data:
        flash('Property not found', 'error')
        return redirect(url_for('guest_dashboard'))
    
    property_info = property_data[0]
    
    # Pre-fill guest info if in session
    guest_info = {}
    if 'guest_id' in session:
        guest_data = execute_query("SELECT * FROM Guest WHERE Guest_ID=%s", (session['guest_id'],), fetch=True)
        if guest_data:
            guest_info = guest_data[0]
    
    return render_template('book_property.html',
                         property={
                             'Name': property_info.get('Name'),
                             'Type': property_info.get('Type'),
                             'Location': property_info.get('Location'),
                             'Rating': float(property_info.get('Rating') or 0),
                             'PricePerNight': float(property_info.get('PricePerNight') or 0),
                             'owner_name': property_info.get('host_name'),
                             'owner_phone': property_info.get('host_phone')
                         },
                         guest=guest_info)

# ===== HOST ROUTES =====
@app.route('/host/login', methods=['GET', 'POST'])
def host_login():
    if request.method == 'POST':
        host_id = request.form.get('host_id')
        email = request.form.get('email')
        
        host = execute_query("SELECT * FROM Host WHERE host_id=%s AND email=%s", (host_id, email), fetch=True)
        
        if host:
            session['host_id'] = host_id
            session['host_name'] = host[0]['name']
            session['role'] = 'host'
            flash('Login successful!', 'success')
            return redirect(url_for('host_dashboard'))
        else:
            flash('Invalid credentials', 'error')
            
    return render_template('host_login.html')

@app.route('/host/dashboard')
def host_dashboard():
    if 'host_id' not in session or session.get('role') != 'host':
        return redirect(url_for('host_login'))
        
    host_id = session['host_id']
    host_name = session['host_name']
    
    my_properties = get_count("SELECT COUNT(*) as total FROM Property WHERE host_id=%s", (host_id,))
    active_bookings = get_count("""
        SELECT COUNT(*) as total 
        FROM Bookings b 
        JOIN Property p ON b.Property_ID = p.Property_ID 
        WHERE p.host_id = %s AND b.Status = 'Confirmed'
    """, (host_id,))
    
    total_revenue_result = execute_query("""
        SELECT SUM(b.TotalPrice) as revenue 
        FROM Bookings b 
        JOIN Property p ON b.Property_ID = p.Property_ID 
        WHERE p.host_id = %s AND b.Status = 'Confirmed'
    """, (host_id,), fetch=True)
    total_revenue = total_revenue_result[0]['revenue'] if total_revenue_result and len(total_revenue_result) > 0 and total_revenue_result[0]['revenue'] else 0
    
    return render_template('host_dashboard.html',
                         host_name=host_name,
                         host_id=host_id,
                         my_properties=my_properties,
                         active_bookings=active_bookings,
                         total_revenue=total_revenue)

@app.route('/host/properties', methods=['GET', 'POST'])
def host_properties():
    if 'host_id' not in session or session.get('role') != 'host':
        return redirect(url_for('host_login'))
        
    host_id = session['host_id']
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form.get('name')
            type_ = request.form.get('type')
            location = request.form.get('location')
            rating = request.form.get('rating') or 0
            price = request.form.get('price')
            status = request.form.get('status') or 'Available'
            
            try:
                execute_query(
                    "INSERT INTO Property (Name, Type, Location, Rating, PricePerNight, Status, host_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (name, type_, location, rating, price, status, host_id)
                )
                flash('✅ Property added successfully!', 'success')
            except Exception as e:
                flash(f'❌ Error adding property: {str(e)}', 'error')
                
        elif action == 'update':
            property_id = request.form.get('property_id')
            name = request.form.get('name')
            type_ = request.form.get('type')
            location = request.form.get('location')
            rating = request.form.get('rating')
            price = request.form.get('price')
            status = request.form.get('status')
            
            # Verify ownership
            prop = execute_query("SELECT * FROM Property WHERE Property_ID=%s AND host_id=%s", (property_id, host_id), fetch=True)
            if not prop:
                flash('❌ Unauthorized or Property not found', 'error')
            else:
                try:
                    execute_query(
                        "UPDATE Property SET Name=%s, Type=%s, Location=%s, Rating=%s, PricePerNight=%s, Status=%s WHERE Property_ID=%s",
                        (name, type_, location, rating, price, status, property_id)
                    )
                    flash('✅ Property updated successfully!', 'success')
                except Exception as e:
                    flash(f'❌ Error updating property: {str(e)}', 'error')
                
        elif action == 'delete':
            property_id = request.form.get('property_id')
            # Verify ownership
            prop = execute_query("SELECT * FROM Property WHERE Property_ID=%s AND host_id=%s", (property_id, host_id), fetch=True)
            if not prop:
                flash('❌ Unauthorized or Property not found', 'error')
            else:
                try:
                    execute_query("DELETE FROM Property WHERE Property_ID=%s", (property_id,))
                    flash('✅ Property deleted successfully!', 'success')
                except Exception as e:
                    flash(f'❌ Error deleting property: {str(e)}', 'error')
                    
        return redirect(url_for('host_properties'))
    
    properties = execute_query("SELECT * FROM Property WHERE host_id=%s", (host_id,), fetch=True)
    return render_template('host_properties.html', properties=properties or [], host_name=session['host_name'])

@app.route('/host/logout')
def host_logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ===== API ROUTES =====
@app.route('/api/properties')
def api_properties():
    try:
        properties = execute_query("""
            SELECT p.*, h.name as host_name, h.phone as host_phone
            FROM Property p 
            JOIN Host h ON p.host_id = h.host_id
            WHERE p.Status = 'Available'
            ORDER BY p.Rating DESC
        """, fetch=True) or []
        
        return jsonify(properties)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify([])

@app.route('/api/bookings')
def api_bookings():
    try:
        guest_id = session.get('guest_id')
        if not guest_id:
            return jsonify([])
            
        bookings = execute_query("""
            SELECT b.*, p.Name as property_name, p.Location, p.Type
            FROM Bookings b
            JOIN Property p ON b.Property_ID = p.Property_ID
            WHERE b.Guest_ID = %s
            ORDER BY b.CheckIn DESC
        """, (guest_id,), fetch=True) or []
        
        return jsonify(bookings)
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify([])

if __name__ == '__main__':
    print("🚀 Starting Property Management System...")
    print("📊 Access at: http://localhost:5000")
    app.run(debug=True, port=5000)