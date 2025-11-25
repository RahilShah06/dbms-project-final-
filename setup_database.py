import mysql.connector

# Database configuration (connect to MySQL server, not specific DB yet)
config = {
    'host': 'localhost',
    'user': 'root', 
    'password': 'Rahil@MySQL',
}

def setup_database():
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        print("🔌 Connected to MySQL server")
        
        # Create Database
        cursor.execute("DROP DATABASE IF EXISTS dbms3")
        cursor.execute("CREATE DATABASE dbms3")
        cursor.execute("USE dbms3")
        print("✅ Database 'dbms3' created and selected")
        
        # Create Tables
        tables = [
            """CREATE TABLE Host (
                host_id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(15) UNIQUE NOT NULL,
                join_date DATE
            )""",
            """CREATE TABLE Property (
                Property_ID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(100) NOT NULL,
                Type VARCHAR(50),
                Location VARCHAR(100),
                Rating DECIMAL(3,2),
                PricePerNight DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                Status ENUM('Available', 'Booked', 'Closed'),
                host_id VARCHAR(10),
                FOREIGN KEY (host_id) REFERENCES Host(host_id) ON DELETE CASCADE
            )""",
            """CREATE TABLE Guest (
                Guest_ID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(100) NOT NULL,
                Email VARCHAR(100) UNIQUE NOT NULL,
                Phone VARCHAR(15) UNIQUE NOT NULL,
                JoiningDate DATE
            )""",
            """CREATE TABLE Bookings (
                Booking_ID INT PRIMARY KEY AUTO_INCREMENT,
                BookingType ENUM('Online', 'Offline'),
                CheckIn DATE,
                CheckOut DATE,
                TotalPrice DECIMAL(10,2),
                Status ENUM('Confirmed', 'Pending', 'Cancelled'),
                Guest_ID INT,
                Property_ID INT,
                FOREIGN KEY (Guest_ID) REFERENCES Guest(Guest_ID) ON DELETE CASCADE,
                FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
            )""",
            """CREATE TABLE Admin (
                admin_id VARCHAR(10) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                host_id VARCHAR(10),
                FOREIGN KEY (host_id) REFERENCES Host(host_id) ON DELETE SET NULL
            )""",
            """CREATE TABLE Attractions (
                Attraction_ID INT PRIMARY KEY AUTO_INCREMENT,
                Attraction_Name VARCHAR(100),
                Distance DECIMAL(5,2),
                Property_ID INT,
                FOREIGN KEY (Property_ID) REFERENCES Property(Property_ID) ON DELETE CASCADE
            )""",
            """CREATE TABLE Payments (
                PaymentID INT PRIMARY KEY AUTO_INCREMENT,
                Method ENUM('Cash', 'Card', 'UPI', 'Online'),
                Amount DECIMAL(10,2),
                Status ENUM('Completed', 'Pending', 'Failed'),
                Booking_ID INT,
                FOREIGN KEY (Booking_ID) REFERENCES Bookings(Booking_ID) ON DELETE CASCADE
            )""",
            """CREATE TABLE Invoices (
                InvoiceID INT PRIMARY KEY AUTO_INCREMENT,
                InvoiceNO VARCHAR(50) UNIQUE,
                IssuedDate DATE,
                SubTotal DECIMAL(10,2),
                Taxes DECIMAL(10,2),
                Discount DECIMAL(10,2),
                Total DECIMAL(10,2),
                Status ENUM('Paid', 'Pending'),
                Booking_ID INT,
                FOREIGN KEY (Booking_ID) REFERENCES Bookings(Booking_ID) ON DELETE CASCADE
            )""",
            """CREATE TABLE Management (
                TicketID INT PRIMARY KEY AUTO_INCREMENT,
                GuestID INT,
                IssueStatus ENUM('Open', 'In Progress', 'Closed'),
                CreatedAt DATE,
                Description TEXT,
                FOREIGN KEY (GuestID) REFERENCES Guest(Guest_ID) ON DELETE CASCADE
            )"""
        ]
        
        for table in tables:
            cursor.execute(table)
        print("✅ Tables created")
        
        # Insert Data
        # Host
        cursor.executemany(
            "INSERT INTO Host (host_id, name, email, phone, join_date) VALUES (%s, %s, %s, %s, %s)",
            [
                ('H001', 'Raj Sharma', 'raj.sharma@host.com', '9876543210', '2023-01-15'),
                ('H002', 'Priya Singh', 'priya.singh@host.com', '9876543211', '2023-02-20'),
                ('H003', 'Amit Verma', 'amit.verma@host.com', '9876543212', '2023-03-10'),
                ('H004', 'Sneha Joshi', 'sneha.joshi@host.com', '9876543213', '2023-04-15'),
                ('H005', 'Vikram Malhotra', 'vikram.malhotra@host.com', '9876543214', '2023-05-20')
            ]
        )
        
        # Admin
        cursor.executemany(
            "INSERT INTO Admin (admin_id, name, email, host_id) VALUES (%s, %s, %s, %s)",
            [
                ('A001', 'Neha Patel', 'neha.patel@admin.com', 'H001'),
                ('A002', 'Vikram Singh', 'vikram.singh@admin.com', 'H002'),
                ('A003', 'Swati Deshmukh', 'swati.deshmukh@admin.com', 'H003'),
                ('A004', 'Kunal Thakur', 'kunal.thakur@admin.com', 'H004'),
                ('A005', 'Aisha Khan', 'aisha.khan@admin.com', 'H005')
            ]
        )
        
        # Property
        cursor.executemany(
            "INSERT INTO Property (Name, Type, Location, Rating, PricePerNight, Status, host_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [
                ('Sea View Villa', 'Villa', 'Goa', 4.5, 5000.00, 'Available', 'H001'),
                ('Mountain Cottage', 'Cottage', 'Shimla', 4.8, 3500.00, 'Available', 'H002'),
                ('City Apartment', 'Apartment', 'Mumbai', 4.2, 4000.00, 'Booked', 'H003'),
                ('Beach Resort', 'Resort', 'Goa', 4.9, 8000.00, 'Available', 'H001'),
                ('Luxury Villa', 'Villa', 'Bangalore', 4.7, 6000.00, 'Available', 'H004'),
                ('Hilltop Bungalow', 'Bungalow', 'Darjeeling', 4.6, 4500.00, 'Available', 'H005'),
                ('Lakeview House', 'House', 'Udaipur', 4.3, 5500.00, 'Available', 'H002'),
                ('Garden Apartment', 'Apartment', 'Pune', 4.4, 3000.00, 'Available', 'H003')
            ]
        )
        
        # Guest
        cursor.executemany(
            "INSERT INTO Guest (Name, Email, Phone, JoiningDate) VALUES (%s, %s, %s, %s)",
            [
                ('John Doe', 'john.doe@email.com', '9876543215', '2024-01-10'),
                ('Jane Smith', 'jane.smith@email.com', '9876543216', '2024-02-15'),
                ('Bob Wilson', 'bob.wilson@email.com', '9876543217', '2024-03-20'),
                ('Alice Brown', 'alice.brown@email.com', '9876543218', '2024-04-25'),
                ('Charlie Davis', 'charlie.davis@email.com', '9876543219', '2024-05-30'),
                ('Diana Evans', 'diana.evans@email.com', '9876543220', '2024-06-05')
            ]
        )
        
        # Bookings
        cursor.executemany(
            "INSERT INTO Bookings (BookingType, CheckIn, CheckOut, TotalPrice, Status, Guest_ID, Property_ID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            [
                ('Online', '2024-06-01', '2024-06-05', 20000.00, 'Confirmed', 1, 1),
                ('Offline', '2024-06-10', '2024-06-12', 12000.00, 'Pending', 2, 2),
                ('Online', '2024-07-01', '2024-07-07', 35000.00, 'Confirmed', 3, 3),
                ('Online', '2024-08-15', '2024-08-20', 28000.00, 'Confirmed', 4, 4),
                ('Offline', '2024-09-01', '2024-09-05', 18000.00, 'Pending', 5, 5),
                ('Online', '2024-10-10', '2024-10-15', 22000.00, 'Confirmed', 6, 6)
            ]
        )
        print("✅ Data inserted")
        
        # Triggers
        triggers = [
            """CREATE TRIGGER validate_property_rating_insert
            BEFORE INSERT ON Property
            FOR EACH ROW
            BEGIN
                IF NEW.Rating > 5 THEN
                    SET NEW.Rating = 5;
                ELSEIF NEW.Rating < 0 THEN
                    SET NEW.Rating = 0;
                END IF;
            END""",
            
            """CREATE TRIGGER validate_property_rating_update
            BEFORE UPDATE ON Property
            FOR EACH ROW
            BEGIN
                IF NEW.Rating > 5 THEN
                    SET NEW.Rating = 5;
                ELSEIF NEW.Rating < 0 THEN
                    SET NEW.Rating = 0;
                END IF;
            END""",
            
            """CREATE TRIGGER validate_booking_dates
            BEFORE INSERT ON Bookings
            FOR EACH ROW
            BEGIN
                IF NEW.CheckIn >= NEW.CheckOut THEN
                    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Check-in date must be before check-out date.';
                END IF;
            END""",
            
            """CREATE TRIGGER update_property_status_on_booking
            AFTER INSERT ON Bookings
            FOR EACH ROW
            BEGIN
                IF NEW.Status = 'Confirmed' THEN
                    UPDATE Property SET Status = 'Booked' WHERE Property_ID = NEW.Property_ID;
                END IF;
            END""",
            
            """CREATE TRIGGER update_property_status_on_booking_update
            AFTER UPDATE ON Bookings
            FOR EACH ROW
            BEGIN
                IF NEW.Status = 'Cancelled' AND OLD.Status != 'Cancelled' THEN
                    UPDATE Property SET Status = 'Available' WHERE Property_ID = NEW.Property_ID;
                ELSEIF NEW.Status = 'Confirmed' AND OLD.Status != 'Confirmed' THEN
                    UPDATE Property SET Status = 'Booked' WHERE Property_ID = NEW.Property_ID;
                END IF;
            END"""
        ]
        
        for trigger in triggers:
            try:
                cursor.execute(trigger)
            except Exception as e:
                print(f"⚠️ Trigger warning: {e}")
                
        print("✅ Triggers created")
        
        conn.commit()
        cursor.close()
        conn.close()
        print("🎉 Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    setup_database()
