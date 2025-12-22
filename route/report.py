from fastapi import APIRouter, Query, HTTPException
from database import get_connection
from pymysql.cursors import DictCursor
from enum import Enum

router = APIRouter(prefix="/report", tags=["Reports"])

#allow sort options
class SortOptions(str, Enum):
    attendee_name = "attendee_name"
    event_name = "event_name"
    seat_number = "seat_number"
    room_name = "room_name"
    vendor_name = "vendor_name"
    price = "price"
    status = "status"
    start_time = "start_time"

@router.get("/attendee-tickets")
def attendee_ticket_report(
    sort_by: SortOptions = Query(SortOptions.start_time, description="Column to sort by")
):
    """
Generates a detailed report of all tickets purchased by attendees.

This report shows:
- Attendee name
- Event name
- Seat number
- Room name
- Vendor name
- Ticket price and status
- Event start time

The query involves **5 table joins** because:
1. `Attendee` → to get the name of the person who purchased the ticket.
2. `Tickets` → to get ticket-specific information like seat number, price, and status.
3. `Event` → to get event-related details (title and start time).
4. `Room` → to identify which room the event is held in.
5. `Vendor` → to show which vendor is associated with the room (or event).

Each join is necessary to combine relevant information across entities for a comprehensive attendee-ticket report.
"""
    sort_column_map = {
        "attendee_name": "a.name",
        "event_name": "e.title",
        "seat_number": "t.seat_number",
        "room_name": "r.name",
        "vendor_name": "v.name",
        "price": "t.price",
        "status": "t.status",
        "start_time": "e.start_time",
    }

    conn = get_connection()
    try:
        cursor = conn.cursor(DictCursor)
        query = f"""
        SELECT 
            a.name AS attendee_name,
            e.title AS event_name,
            t.seat_number,
            r.name AS room_name,
            v.name AS vendor_name,
            t.price,
            t.status,
            e.start_time
        FROM Attendee a
        JOIN Tickets t ON a.attendee_id = t.attendee_id
        JOIN Event e ON t.event_id = e.event_id
        JOIN Room r ON e.room_id = r.room_id
        JOIN Vendor v ON r.room_id = v.room_id
        ORDER BY {sort_column_map[sort_by]} ASC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))