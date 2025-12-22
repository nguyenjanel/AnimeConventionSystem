from fastapi import APIRouter, HTTPException
from model.event_models import EventCreate, EventRead, EventUpdate
from database import get_connection

router = APIRouter(prefix="/events", tags=["Events"])

# CREATE
@router.post("/")
def create_event(event: EventCreate):
    """
    Creates Event and checks
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:

            # Check if room exists
            cursor.execute("SELECT room_id FROM Room WHERE room_id = %s", (event.room_id,))
            room_exists = cursor.fetchone()
            if not room_exists:
                return {"error": "Room does not exist"}

            # Check if room is free
            conflict_query = """
                SELECT event_id FROM Event
                WHERE room_id = %s
                AND (
                    (start_time <= %s AND end_time > %s) OR
                    (start_time < %s AND end_time >= %s) OR
                    (%s <= start_time AND %s >= end_time)
                )
            """

            cursor.execute(conflict_query, (
                event.room_id,
                event.start_time, event.start_time,
                event.end_time, event.end_time,
                event.start_time, event.end_time
            ))

            conflict = cursor.fetchone()
            if conflict:
                return {"error": "Room is already booked during this time"}

            # Insert the event
            insert_sql = """
                INSERT INTO Event (title, description, room_id, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_sql, (
                event.title,
                event.description,
                event.room_id,
                event.start_time,
                event.end_time
            ))

        # Commit when all checks succeed
        conn.commit()
        return {"message": "Event created successfully"}

    except Exception as e:
        conn.rollback()
        return {"error": str(e)}

    finally:
        conn.close()

# Read one
@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Event WHERE event_id = %s", (event_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Event not found")
            return result
    finally:
        conn.close()

@router.get("/")
def get_all_events():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Event")
            results = cursor.fetchall()  
            return results
    finally:
        conn.close()

@router.get("/room/{room_id}", response_model=list[EventRead])
def get_events_by_room(room_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:

            # Fetch all events for a room
            cursor.execute("SELECT * FROM Event WHERE room_id = %s", (room_id,))
            results = cursor.fetchall()

            if not results:
                raise HTTPException(status_code=404, detail="No events found for this room")

            return results

    finally:
        conn.close()
# Update
@router.put("/{event_id}", response_model=EventRead)
def update_event(event_id: int, event: EventUpdate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check if event exists
            cursor.execute("SELECT * FROM Event WHERE event_id = %s", (event_id,))
            existing = cursor.fetchone()
            if not existing:
                raise HTTPException(status_code=404, detail="Event not found")

            fields_to_update = []
            values = []

            if event.title is not None:
                fields_to_update.append("title = %s")
                values.append(event.title)

            if event.description is not None:
                fields_to_update.append("description = %s")
                values.append(event.description)

            if event.room_id is not None:
                fields_to_update.append("room_id = %s")
                values.append(event.room_id)

            if event.start_time is not None:
                fields_to_update.append("start_time = %s")
                values.append(event.start_time)

            if event.end_time is not None:
                fields_to_update.append("end_time = %s")
                values.append(event.end_time)

            if not fields_to_update:
                raise HTTPException(status_code=400, detail="No valid fields to update")

            sql = "UPDATE Event SET " + ", ".join(fields_to_update) + " WHERE event_id = %s"
            values.append(event_id)

            cursor.execute(sql, tuple(values))
            conn.commit()

            # Return the updated row
            cursor.execute("SELECT * FROM Event WHERE event_id = %s", (event_id,))
            updated = cursor.fetchone()
            return updated
    finally:
        conn.close()


# Delete
@router.delete("/{event_id}")
def delete_event(event_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Delete tickets for this event
            cursor.execute("DELETE FROM Tickets WHERE event_id = %s", (event_id,))
            # Delete schedules for this event
            cursor.execute("DELETE FROM Schedule WHERE event_id = %s", (event_id,))
            cursor.execute("DELETE FROM Event WHERE event_id = %s", (event_id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Event not found")

        conn.commit()
        return {"detail": "Event deleted"}
    finally:
        conn.close()