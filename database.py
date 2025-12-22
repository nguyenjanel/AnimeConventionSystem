import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    database = os.getenv("DB_NAME")

    # Safety check
    if not all([host, user, password, database]):
        raise RuntimeError(
            "Missing DB environment variables. Check your .env file."
        )

    return pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor
    )


def initialize_tables():
    connection = get_connection()
    cursor = connection.cursor()  # no 'with' here

    # Room table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Room (
            room_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            capacity INT NOT NULL,
            location VARCHAR(100) NOT NULL
        )
    """)

    # Attendee table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attendee (
            attendee_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Event table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Event (
            event_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            room_id INT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            FOREIGN KEY (room_id) REFERENCES Room(room_id)
        )
    """)

    # Guest table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Guest (
            guest_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            contact_info TEXT
        )
    """)

    # Vendor table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Vendor (
            vendor_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            contact_info VARCHAR(150) NOT NULL,
            room_id INT NOT NULL,
            FOREIGN KEY (room_id) REFERENCES Room(room_id)
)
    """)

    # Payment table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Payment (
            payment_id INT AUTO_INCREMENT PRIMARY KEY,
            amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
            method VARCHAR(50) NOT NULL,
            attendee_id INT,
            vendor_id INT,
            FOREIGN KEY (attendee_id) REFERENCES Attendee(attendee_id),
            FOREIGN KEY (vendor_id) REFERENCES Vendor(vendor_id)
        )
    """)

    # Schedule table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Schedule (
            schedule_id INT AUTO_INCREMENT PRIMARY KEY,
            guest_id INT NOT NULL,
            event_id INT NOT NULL,
            room_id INT NOT NULL,
            date DATE NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            FOREIGN KEY (guest_id) REFERENCES Guest(guest_id),
            FOREIGN KEY (event_id) REFERENCES Event(event_id),
            FOREIGN KEY (room_id) REFERENCES Room(room_id)
        )
    """)

    # Many-to-many tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attendee_Event (
            attendee_id INT NOT NULL,
            event_id INT NOT NULL,
            registration_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (attendee_id, event_id),
            FOREIGN KEY (attendee_id) REFERENCES Attendee(attendee_id),
            FOREIGN KEY (event_id) REFERENCES Event(event_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Event_Guest (
            event_id INT NOT NULL,
            guest_id INT NOT NULL,
            PRIMARY KEY (event_id, guest_id),
            FOREIGN KEY (event_id) REFERENCES Event(event_id),
            FOREIGN KEY (guest_id) REFERENCES Guest(guest_id)
        )
    """)

    # Tickets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tickets (
            ticket_id INT AUTO_INCREMENT PRIMARY KEY,
            attendee_id INT NOT NULL,
            event_id INT NOT NULL,
            seat_number VARCHAR(10),
            price DECIMAL(10,2) NOT NULL,
            status ENUM('reserved','paid','canceled') DEFAULT 'reserved',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (attendee_id) REFERENCES Attendee(attendee_id),
            FOREIGN KEY (event_id) REFERENCES Event(event_id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()