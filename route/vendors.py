from fastapi import APIRouter, HTTPException
from model.vendor_models import VendorCreate, VendorUpdate
from database import get_connection

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.post("/")
def create_vendor(vendor: VendorCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT room_id FROM Room WHERE room_id = %s",
                (vendor.room_id,)
            )
            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Room {vendor.room_id} does not exist"
                )
            
            sql = "INSERT INTO Vendor (name, contact_info, room_id) VALUES (%s, %s, %s)"
            cursor.execute(sql, (vendor.name, vendor.contact_info, vendor.room_id))
        conn.commit()
        return {"message": "Vendor created successfully"}
    finally:
        conn.close()


@router.get("/")
def get_vendors():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Vendor")
            return cursor.fetchall()
    finally:
        conn.close()


@router.put("/{vendor_id}")
def update_vendor(vendor_id: int, vendor: VendorUpdate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            updates = []
            values = []
            if vendor.name is not None:
                updates.append("name=%s")
                values.append(vendor.name)
            if vendor.contact_info is not None:
                updates.append("contact_info=%s")
                values.append(vendor.contact_info)
            if vendor.room_id is not None:
                updates.append("room_id=%s")
                values.append(vendor.room_id)

            if not updates:
                raise HTTPException(status_code=400, detail="No fields provided for update")

            values.append(vendor_id)
            sql = f"UPDATE Vendor SET {', '.join(updates)} WHERE vendor_id=%s"
            cursor.execute(sql, tuple(values))
        conn.commit()
        return {"message": "Vendor updated successfully"}
    finally:
        conn.close()


@router.delete("/{vendor_id}")
def delete_vendor(vendor_id: int):
    """
    Delete a vendor AND any related payments in ONE transaction.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # 1) Check vendor exists
        cursor.execute(
            "SELECT vendor_id FROM Vendor WHERE vendor_id = %s",
            (vendor_id,),
        )
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Vendor not found")

        # 2) Delete payments for this vendor (child table)
        cursor.execute(
            "DELETE FROM Payment WHERE vendor_id = %s",
            (vendor_id,),
        )

        # 3) Delete vendor
        cursor.execute(
            "DELETE FROM Vendor WHERE vendor_id = %s",
            (vendor_id,),
        )

        conn.commit()
        return {"message": f"Vendor {vendor_id} and related payments deleted successfully"}

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
