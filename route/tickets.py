from fastapi import APIRouter, HTTPException
from typing import List
from model.ticket_models import Ticket, TicketCreate, TicketUpdate, TicketTransactionCreate
from database import get_connection
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("/", response_model=List[Ticket])
def get_tickets():
    conn = get_connection()
    try:
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM Tickets")
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket_by_ticket_id(ticket_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor() 
        cursor.execute("SELECT * FROM Tickets WHERE ticket_id=%s", (ticket_id,))
        ticket = cursor.fetchone()
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@router.put("/{ticket_id}", response_model=TicketUpdate)
def update_ticket(ticket_id: int, ticket: TicketUpdate):
    """
    Update the Ticket

    Price > 0

    Status: reserved, paid, canceled
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fields = []
        values = []

        if ticket.attendee_id is not None:
            if ticket.attendee_id is not None:
                cursor.execute("SELECT attendee_id FROM Attendees WHERE attendee_id=%s", (ticket.attendee_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Attendee {ticket.attendee_id} does not exist")
            fields.append("attendee_id=%s")
            values.append(ticket.attendee_id)
        if ticket.event_id is not None:
            if ticket.event_id is not None:
                cursor.execute("SELECT event_id FROM Event WHERE event_id=%s", (ticket.event_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail=f"Event {ticket.event_id} does not exist")
            fields.append("event_id=%s")
            values.append(ticket.event_id)
        if ticket.seat_number is not None:
            fields.append("seat_number=%s")
            values.append(ticket.seat_number)
        if ticket.price is not None:
            fields.append("price=%s")
            values.append(ticket.price)
        if ticket.status is not None:
            fields.append("status=%s")
            values.append(ticket.status)

        if not fields:
            raise HTTPException(status_code=400, detail="No fields provided to update")

        sql = f"UPDATE Tickets SET {', '.join(fields)} WHERE ticket_id=%s"
        values.append(ticket_id)
        cursor.execute(sql, tuple(values))
        conn.commit()

        cursor.execute("SELECT * FROM Tickets WHERE ticket_id=%s", (ticket_id,))
        updated_ticket = cursor.fetchone()
        if not updated_ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return updated_ticket

    finally:
        cursor.close()
        conn.close()


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Tickets WHERE ticket_id=%s", (ticket_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        conn.commit()
        return {"status": "success", "message": f"Ticket {ticket_id} deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


# creating a new ticket but only if the seat isn’t already taken
@router.post("/create-transaction")
def create_ticket_transaction(ticket: TicketTransactionCreate):
    """
    Create a new ticket for an event 

    This endpoint performs multiple checks within a single transaction:

    1. Checks if the requested seat is already taken for the event.
    2. Verifies that the event’s room has available seats.
    3. Inserts the new ticket if all checks pass.

    **Transaction and Rollback:**
    All operations are wrapped in a database transaction. If any of the checks fail (e.g., seat already taken, no available seats, or event not found), an exception is raised and the transaction is rolled back. This ensures that **partial updates are not applied**, and the database remains in a consistent state.

    On successful completion, the transaction is committed and the newly created ticket is returned.
    """

    conn = get_connection()
    cursor = conn.cursor()  
    try:
        # check if the seat is already taken for this event
        cursor.execute(
            """
            SELECT * FROM Tickets
            WHERE event_id=%s AND seat_number=%s
            """,
            (ticket.event_id, ticket.seat_number),
        )
        if cursor.fetchone():
            raise Exception(f"Seat {ticket.seat_number} is already taken for this event.")

        # check if the event’s room has available seats
        cursor.execute(
            """
            SELECT r.capacity, COUNT(t.ticket_id) AS tickets_sold
            FROM Event e
            JOIN Room r ON e.room_id = r.room_id
            LEFT JOIN Tickets t ON e.event_id = t.event_id
            WHERE e.event_id=%s
            GROUP BY r.capacity
            """,
            (ticket.event_id,),
        )
        row = cursor.fetchone()
        if not row:
            raise Exception("Event not found.")

        available_seats = row["capacity"] - row["tickets_sold"]
        if available_seats <= 0:
            raise Exception("No seats available for this event.")

        # insert the new ticket
        cursor.execute(
            """
            INSERT INTO Tickets (attendee_id, event_id, seat_number, price, status)
            VALUES (%s, %s, %s, %s, 'reserved')
            """,
            (ticket.attendee_id, ticket.event_id, ticket.seat_number, ticket.price),
        )

        # commit the transaction
        conn.commit()

        # fetch and return the newly created ticket
        cursor.execute("SELECT * FROM Tickets WHERE ticket_id=%s", (cursor.lastrowid,))
        new_ticket = cursor.fetchone()
        return {"status": "success", "ticket": new_ticket}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()
