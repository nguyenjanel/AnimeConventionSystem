from fastapi import APIRouter, HTTPException
from typing import List
from model.attendees_models import (
    AttendeeCreate,
    AttendeeUpdate,
    AttendeeResponse,
    MoveRegistrationRequest,
)
from database import get_connection

router = APIRouter(prefix="/attendees", tags=["Attendees"])


# Create attendee
@router.post("/", response_model=AttendeeResponse)
def create_attendee(attendee: AttendeeCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Insert without the  ticket_type
            sql = """
                INSERT INTO Attendee (name, email, registration_date)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(sql, (attendee.name, attendee.email))
            conn.commit()

            new_id = cursor.lastrowid

            # Fetch the new row
            cursor.execute(
                """
                SELECT attendee_id, name, email, registration_date
                FROM Attendee
                WHERE attendee_id = %s
                """,
                (new_id,),
            )
            row = cursor.fetchone()

        return row
    finally:
        conn.close()


# Read all attendees
@router.get("/", response_model=List[AttendeeResponse])
def get_attendees():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT attendee_id, name, email, registration_date FROM Attendee"
            )
            result = cursor.fetchall()  
        return result
    finally:
        conn.close()


# Update attendee
@router.put("/{attendee_id}")
def update_attendee(attendee_id: int, attendee: AttendeeUpdate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Check attendee exists
            cursor.execute(
                "SELECT attendee_id FROM Attendee WHERE attendee_id = %s",
                (attendee_id,),
            )
            if cursor.fetchone() is None:
                raise HTTPException(status_code=404, detail="Attendee not found")

            fields_to_update = []
            values = []

            if attendee.name is not None:
                fields_to_update.append("name = %s")
                values.append(attendee.name)

            if attendee.email is not None:
                fields_to_update.append("email = %s")
                values.append(attendee.email)

            if not fields_to_update:
                raise HTTPException(
                    status_code=400, detail="No valid fields to update"
                )

            sql = (
                "UPDATE Attendee SET "
                + ", ".join(fields_to_update)
                + " WHERE attendee_id = %s"
            )
            values.append(attendee_id)

            cursor.execute(sql, tuple(values))

        conn.commit()
        return {"message": "Attendee updated successfully"}
    finally:
        conn.close()


# Delete attendee
@router.delete("/{attendee_id}")
def delete_attendee(attendee_id: int):
    """
    Delete an attendee AND all related records 
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check attendee exists
        cursor.execute(
            "SELECT attendee_id FROM Attendee WHERE attendee_id = %s",
            (attendee_id,),
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Attendee not found")

        # Delete rows that reference this attendee
        cursor.execute(
            "DELETE FROM Tickets WHERE attendee_id = %s",
            (attendee_id,),
        )
        cursor.execute(
            "DELETE FROM Attendee_Event WHERE attendee_id = %s",
            (attendee_id,),
        )
        cursor.execute(
            "DELETE FROM Payment WHERE attendee_id = %s",
            (attendee_id,),
        )

        # Now delete the attendee
        cursor.execute(
            "DELETE FROM Attendee WHERE attendee_id = %s",
            (attendee_id,),
        )

        conn.commit()
        return {"message": f"Attendee {attendee_id} and related data deleted successfully"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()



@router.post("/{attendee_id}/move-registration")
def move_registration(attendee_id: int, move: MoveRegistrationRequest):
    """
    Move an attendee's registration from one event to another.

    Steps
      1) Load old ticket and verify it belongs to this attendee.
      2) Check new event exists and has capacity.
      3) Check new seat is not taken.
      4) Delete old ticket.
      5) Insert new ticket.
      6) Update Attendee_Event join table.
      7) Insert a payment adjustment if the price changed.
      8) Commit rollback on any error.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Load old ticket and verify ownership
        cursor.execute(
            """
            SELECT ticket_id, attendee_id, event_id, price, seat_number
            FROM Tickets
            WHERE ticket_id = %s
            """,
            (move.old_ticket_id,),
        )
        old_ticket = cursor.fetchone()
        if not old_ticket:
            raise HTTPException(status_code=404, detail="Old ticket not found")

        if old_ticket["attendee_id"] != attendee_id:
            raise HTTPException(
                status_code=400,
                detail="Ticket does not belong to this attendee",
            )

        old_event_id = old_ticket["event_id"]
        old_price = float(old_ticket["price"])

        # Check new event exists and capacity
        cursor.execute(
            """
            SELECT r.capacity, COUNT(t.ticket_id) AS tickets_sold
            FROM Event e
            JOIN Room r ON e.room_id = r.room_id
            LEFT JOIN Tickets t ON e.event_id = t.event_id
            WHERE e.event_id = %s
            GROUP BY r.capacity
            """,
            (move.new_event_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="New event not found")

        available_seats = row["capacity"] - row["tickets_sold"]
        if available_seats <= 0:
            raise HTTPException(
                status_code=400,
                detail="No seats available for the new event",
            )

        # Check new seat is not already taken
        cursor.execute(
            """
            SELECT ticket_id
            FROM Tickets
            WHERE event_id = %s AND seat_number = %s
            """,
            (move.new_event_id, move.new_seat_number),
        )
        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail=f"Seat {move.new_seat_number} is already taken for this event",
            )

        # Delete old ticket
        cursor.execute(
            "DELETE FROM Tickets WHERE ticket_id = %s",
            (move.old_ticket_id,),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Old ticket not found on delete")

        # Insert new ticket
        cursor.execute(
            """
            INSERT INTO Tickets (attendee_id, event_id, seat_number, price, status)
            VALUES (%s, %s, %s, %s, 'reserved')
            """,
            (attendee_id, move.new_event_id, move.new_seat_number, move.new_price),
        )
        new_ticket_id = cursor.lastrowid

        # Update Attendee_Event join table
        # Remove old event registration
        cursor.execute(
            """
            DELETE FROM Attendee_Event
            WHERE attendee_id = %s AND event_id = %s
            """,
            (attendee_id, old_event_id),
        )
        #  Add new event registration
        cursor.execute(
            """
            INSERT INTO Attendee_Event (attendee_id, event_id, registration_date)
            VALUES (%s, %s, NOW())
            """,
            (attendee_id, move.new_event_id),
        )

        # Payment adjustment if price changed
        price_diff = float(move.new_price) - old_price
        if price_diff != 0:
            # positive is if attendee owes more and negative is a refund
            method = "adjustment_charge" if price_diff > 0 else "adjustment_refund"
            cursor.execute(
                """
                INSERT INTO Payment (amount, method, attendee_id, vendor_id)
                VALUES (%s, %s, %s, NULL)
                """,
                (abs(price_diff), method, attendee_id),
            )

        # Commit the whole transaction
        conn.commit()

        # Fetch the new ticket to return
        cursor.execute(
            "SELECT * FROM Tickets WHERE ticket_id = %s",
            (new_ticket_id,),
        )
        new_ticket = cursor.fetchone()

        return {
            "status": "success",
            "old_ticket_id": move.old_ticket_id,
            "old_event_id": old_event_id,
            "new_ticket": new_ticket,
            "price_difference": price_diff,
        }

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()