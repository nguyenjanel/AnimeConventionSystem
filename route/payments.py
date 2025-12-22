from fastapi import APIRouter, HTTPException
from model.payment_models import PaymentCreate
from model.payment_models import PaymentCreate, PaymentResponse
from database import get_connection

router = APIRouter(prefix="/payments", tags=["Payments"])


# create payment
@router.post("/", response_model=PaymentResponse)
def create_payment(payment: PaymentCreate):
    """
    Create a new payment record. 

    Each payment must be associated with **either** an attendee **or** a vendor, but not both. 
    - If `attendee_id` is provided, the payment is for an attendee.  
    - If `vendor_id` is provided, the payment is for a vendor.  

    The endpoint validates that exactly one of these IDs is set and will raise an error if this rule is violated.
    """
    # Validate that exactly one of attendee_id or vendor_id is provided
    if (payment.attendee_id is None and payment.vendor_id is None) or \
       (payment.attendee_id is not None and payment.vendor_id is not None):
        raise HTTPException(
            status_code=400,
            detail="Payment must be for either an attendee or a vendor, not both or neither."
        )

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO Payment (amount, method, attendee_id, vendor_id) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(
                sql,
                (
                    payment.amount,
                    payment.method,
                    payment.attendee_id,
                    payment.vendor_id,
                ),
            )
            conn.commit()
            payment_id = cursor.lastrowid

        # Return a PaymentResponse-compatible dict
        return {
            "payment_id": payment_id,
            "amount": payment.amount,
            "method": payment.method,
            "attendee_id": payment.attendee_id,
            "vendor_id": payment.vendor_id,
        }
    finally:
        conn.close()


# read all payments
@router.get("/", response_model=list[PaymentResponse])
def get_payments():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT payment_id, amount, method, attendee_id, vendor_id
                FROM Payment
                """
            )
            rows = cursor.fetchall()
            return rows
    finally:
        conn.close()