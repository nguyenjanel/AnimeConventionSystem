from fastapi import APIRouter, HTTPException
from model.room_models import RoomCreate, RoomUpdate
from database import get_connection

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/")
def create_room(room: RoomCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            #check for duplicate room name
            cursor.execute("SELECT room_id FROM Room WHERE name=%s", (room.name,))
            if cursor.fetchone():
                return {"error": f"A room with the name '{room.name}' already exists."}

            #insert the new room
            sql = """
            INSERT INTO Room (name, capacity, location)
            VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (room.name, room.capacity, room.location))

        conn.commit()
        return {"message": "Room created successfully"}
    finally:
        conn.close()


@router.get("/")
def get_rooms():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Room")
            return cursor.fetchall()
    finally:
        conn.close()


@router.put("/{room_id}")
def update_room(room_id: int, room: RoomUpdate):
    """
    Partially update a room. Prevents duplicate room names.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            #check for duplicate room name if name is being updated
            if room.name is not None:
                cursor.execute(
                    "SELECT room_id FROM Room WHERE name=%s AND room_id!=%s",
                    (room.name, room_id)
                )
                if cursor.fetchone():
                    return {"error": f"A room with the name '{room.name}' already exists."}

            fields = []
            values = []

            if room.name is not None:
                fields.append("name=%s")
                values.append(room.name)
            if room.capacity is not None:
                fields.append("capacity=%s")
                values.append(room.capacity)
            if room.location is not None:
                fields.append("location=%s")
                values.append(room.location)

            if not fields:
                return {"error": "No fields provided to update."}

            sql = f"UPDATE Room SET {', '.join(fields)} WHERE room_id=%s"
            values.append(room_id)
            cursor.execute(sql, tuple(values))

        conn.commit()
        return {"message": "Room updated successfully"}
    finally:
        conn.close()


@router.delete("/{room_id}")
def delete_room(room_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Room WHERE room_id=%s", (room_id,))
        conn.commit()
        return {"message": "Room deleted successfully"}
    finally:
        conn.close()