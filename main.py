from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection, initialize_tables

#import all routers
from route import attendees, vendors, payments, schedules, events, guest, rooms, tickets, report

app = FastAPI(title="Anime Convention Management System (ACMS)")

#include routers
app.include_router(attendees.router)
app.include_router(vendors.router)
app.include_router(payments.router)
app.include_router(schedules.router)
app.include_router(events.router)     
app.include_router(guest.router)
app.include_router(rooms.router)
app.include_router(tickets.router)
app.include_router(report.router)

#root/default endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the ACMS API!"}

