from fastapi import APIRouter, HTTPException
from model.schedule_models import ScheduleCreate
from database import get_connection

router = APIRouter(prefix="/schedules", tags=["Schedules"])

@router.post("/")
def create_schedule(schedule: ScheduleCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # NOTE: use backticks so `date`, `start_time`, etc. don't cause syntax issues
            sql = """
            INSERT INTO `Schedule` (`event_id`, `room_id`, `guest_id`, `date`, `start_time`, `end_time`) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    schedule.event_id,
                    schedule.room_id,
                    schedule.guest_id,
                    schedule.date,
                    schedule.start_time,
                    schedule.end_time,
                )
            )
        conn.commit()
        return {"message": "Schedule entry created successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {e}")

    finally:
        conn.close()

@router.get("/")
def get_schedules():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Schedule")
            return cursor.fetchall()
    finally:
        conn.close()
#read by schedule id
@router.get("/{schedule_id}")
def get_schedule(schedule_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Schedule WHERE schedule_id = %s", (schedule_id,))
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Schedule not found")
            return result
    finally:
        conn.close()

@router.put("/{schedule_id}")
def update_schedule(schedule_id: int, schedule: ScheduleCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE Schedule 
            SET event_id=%s, room_id=%s, guest_id=%s, date=%s, start_time=%s, end_time=%s
            WHERE schedule_id=%s
            """
            cursor.execute(sql, (
                schedule.event_id, schedule.room_id, schedule.guest_id,
                schedule.date, schedule.start_time, schedule.end_time, schedule_id
            ))
        conn.commit()
        return {"message": "Schedule updated successfully"}
    finally:
        conn.close()

@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Schedule WHERE schedule_id=%s", (schedule_id,))
        conn.commit()
        return {"message": "Schedule deleted successfully"}
    finally:
        conn.close()

@router.get("/by-date/{query_date}")
def get_schedules_by_date(query_date: str):
    """Return all schedules on a specific date (YYYY-MM-DD)."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Schedule WHERE date = %s", (query_date,))
            return cursor.fetchall()
    finally:
        conn.close()

@router.get("/by-room/{room_id}")
def get_schedules_by_room(room_id: int):
    """Return all schedules for a specific room."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Schedule WHERE room_id = %s", (room_id,))
            return cursor.fetchall()
    finally:
        conn.close()

@router.get("/by-guest/{guest_id}")
def get_schedules_by_guest(guest_id: int):
    """Return all schedules for a specific guest."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Schedule WHERE guest_id = %s", (guest_id,))
            return cursor.fetchall()
    finally:
        conn.close()