from fastapi import APIRouter, HTTPException
from model.guest_models import GuestCreate, Guest
from database import get_connection

router = APIRouter(prefix="/guests", tags=["Guests"])


# Create guest
@router.post("/", response_model=Guest)
def create_guest(guest: GuestCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Guest (name, contact_info)
                VALUES (%s, %s)
            """
            cursor.execute(
                sql,
                (
                    guest.name,
                    guest.contact_info,
                ),
            )
            conn.commit()
            guest_id = cursor.lastrowid

        return {
            "guest_id": guest_id,
            "name": guest.name,
            "contact_info": guest.contact_info,
        }
    finally:
        conn.close()


# Read all guests
@router.get("/", response_model=list[Guest])
def get_guests():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT guest_id, name, contact_info
                FROM Guest
                """
            )
            rows = cursor.fetchall()
            return rows
    finally:
        conn.close()


# Read one guest
@router.get("/{guest_id}", response_model=Guest)
def get_guest(guest_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT guest_id, name, contact_info
                FROM Guest
                WHERE guest_id = %s
                """,
                (guest_id,),
            )
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Guest not found")

            return row
    finally:
        conn.close()

# Update guest
@router.put("/{guest_id}", response_model=Guest)
def update_guest(guest_id: int, guest: GuestCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check guest exists
            cursor.execute(
                "SELECT guest_id FROM Guest WHERE guest_id = %s",
                (guest_id,),
            )
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Guest not found")

            # Full update of name and contact information
            sql = """
                UPDATE Guest
                SET name = %s,
                    contact_info = %s
                WHERE guest_id = %s
            """
            cursor.execute(
                sql,
                (
                    guest.name,
                    guest.contact_info,
                    guest_id,
                ),
            )
            conn.commit()

            # Return updated row
            cursor.execute(
                """
                SELECT guest_id, name, contact_info
                FROM Guest
                WHERE guest_id = %s
                """,
                (guest_id,),
            )
            updated = cursor.fetchone()
            return updated
    finally:
        conn.close()

# Delete guest
@router.delete("/{guest_id}")
def delete_guest(guest_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Make sure the guest exists
            cursor.execute(
                "SELECT guest_id FROM Guest WHERE guest_id = %s",
                (guest_id,),
            )
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Guest not found")

            # Delete related rows first 
            cursor.execute(
                "DELETE FROM Schedule WHERE guest_id = %s",
                (guest_id,),
            )

            # Delete the guest
            cursor.execute(
                "DELETE FROM Guest WHERE guest_id = %s",
                (guest_id,),
            )

        conn.commit()
        return {"detail": "Guest and related records deleted"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        conn.close()