import random
from datetime import datetime, timedelta
from database import get_connection

#data populated from ChatGpt

def populate_db():
    conn = get_connection()
    cursor = conn.cursor()

    # ---------------- Truncate tables ----------------
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tables = ["Payment", "Tickets", "Schedule", "Attendee_Event", 
              "Event_Guest", "Vendor", "Event", "Attendee", "Guest", "Room"]
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    # ---------------- Rooms ----------------
    rooms = [
        ('Main Hall', 500, 'First Floor'),
        ('Panel Room A', 120, 'Second Floor'),
        ('Panel Room B', 120, 'Second Floor'),
        ('Artist Alley', 200, 'Expo Center'),
        ('Gaming Room', 150, 'Basement')
    ]
    cursor.executemany(
        "INSERT INTO Room (name, capacity, location) VALUES (%s, %s, %s)",
        rooms
    )
    conn.commit()  # commit rooms before vendors

    # ---------------- Guests ----------------
    guests = [
        ('Ayumi Tanaka', 'ayumi@example.com'),
        ('Kenji Nakamura', 'kenji@example.com'),
        ('Mika Suzuki', 'mika@example.com'),
        ('Studio Pixel Team', 'studio.pixel@example.com')
    ]
    cursor.executemany(
        "INSERT INTO Guest (name, contact_info) VALUES (%s, %s)",
        guests
    )

    # ---------------- Vendors ----------------
    vendors = [
        ('Otaku Merch Co.', 'contact@otakumerch.com', 4),
        ('Retro Games Shop', 'sales@retrogames.com', 5),
        ('Manga World', 'info@mangaworld.com', 3),
        ('Food Co', 'food@example.com', 1),
        ('Anime Goods', 'contact@animegoods.com', 2),
        ('Gaming Supplies', 'sales@gamingsupplies.com', 3),
        ('Manga Cafe', 'info@mangacafe.com', 4),
        ('Merch Hub', 'contact@merchhub.com', 5),
        ('Comic World', 'info@comicworld.com', 1),
        ('Toy Universe', 'sales@toyuniverse.com', 2)
    ]
    cursor.executemany(
        "INSERT INTO Vendor (name, contact_info, room_id) VALUES (%s, %s, %s)",
        vendors
    )

    # ---------------- Attendees ----------------
    attendees = [
        ('Alice Chen', 'alice@example.com'),
        ('Brian Lee', 'brian@example.com'),
        ('Carlos Diaz', 'carlos@example.com'),
        ('Diana Park', 'diana@example.com'),
        ('Ethan Nguyen', 'ethan@example.com'),
        ('Fiona Kim', 'fiona@example.com'),
        ('George Li', 'george@example.com'),
        ('Hannah Wong', 'hannah@example.com'),
        ('Ian Chen', 'ian@example.com'),
        ('Julia Park', 'julia@example.com'),
        ('Kevin Tan', 'kevin@example.com'),
        ('Laura Lin', 'laura@example.com'),
        ('Michael Yu', 'michael@example.com'),
        ('Nina Zhao', 'nina@example.com'),
        ('Oscar Choi', 'oscar@example.com'),
        ('Paula Lim', 'paula@example.com'),
        ('Quinn Lee', 'quinn@example.com'),
        ('Ryan Kim', 'ryan@example.com'),
        ('Sophie Wang', 'sophie@example.com'),
        ('Tommy Chen', 'tommy@example.com')
    ]
    cursor.executemany(
        "INSERT INTO Attendee (name, email) VALUES (%s, %s)",
        attendees
    )

    # ---------------- Events ----------------
    events = [
        ('Opening Ceremony', 'Welcome to ACMS', 1, '2025-07-12 09:00:00', '2025-07-12 10:00:00'),
        ('Anime 101 Panel', 'Intro panel for newcomers', 2, '2025-07-12 11:00:00', '2025-07-12 12:00:00'),
        ('Voice Acting Q&A', 'Q&A with voice actors', 2, '2025-07-12 13:00:00', '2025-07-12 14:30:00'),
        ('Indie Game Showcase', 'Demo of indie games', 5, '2025-07-12 15:00:00', '2025-07-12 17:00:00'),
        ('Cosplay Contest', 'Main cosplay competition', 1, '2025-07-13 14:00:00', '2025-07-13 16:00:00')
    ]
    cursor.executemany(
        "INSERT INTO Event (title, description, room_id, start_time, end_time) VALUES (%s, %s, %s, %s, %s)",
        events
    )

    # ---------------- Schedule ----------------
    guest_ids = list(range(1, len(guests)+1))
    event_ids = list(range(1, len(events)+1))
    room_ids = list(range(1, len(rooms)+1))
    schedules = []
    for _ in range(50):  # more schedule entries
        event_id = random.choice(event_ids)
        guest_id = random.choice(guest_ids)
        room_id = random.choice(room_ids)
        start_time = datetime(2025, 7, random.randint(1, 13), random.randint(9, 15))
        end_time = start_time + timedelta(hours=2)
        schedules.append((guest_id, event_id, room_id, start_time.date(), start_time, end_time))
    cursor.executemany(
        "INSERT INTO Schedule (guest_id, event_id, room_id, date, start_time, end_time) VALUES (%s, %s, %s, %s, %s, %s)",
        schedules
    )

    # ---------------- Tickets ----------------
    tickets = []
    for attendee_id in range(1, len(attendees)+1):
        for event_id in event_ids:
            seat_number = f"{random.choice('ABCDE')}{random.randint(1,20)}"
            price = random.choice([50, 75, 100])
            status = random.choice(['reserved', 'paid'])
            tickets.append((attendee_id, event_id, seat_number, price, status))
    cursor.executemany(
        "INSERT INTO Tickets (attendee_id, event_id, seat_number, price, status) VALUES (%s, %s, %s, %s, %s)",
        tickets
    )

    # ---------------- Payments ----------------
    payments = []
    for attendee_id in range(1, len(attendees)+1):
        payments.append((random.choice([50, 75, 100]), 'credit', attendee_id, None))
    for vendor_id in range(1, len(vendors)+1):
        payments.append((random.choice([400, 450, 500]), 'bank_transfer', None, vendor_id))
    cursor.executemany(
        "INSERT INTO Payment (amount, method, attendee_id, vendor_id) VALUES (%s, %s, %s, %s)",
        payments
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Database populated successfully with 20 attendees and 10 vendors!")

if __name__ == "__main__":
    populate_db()
