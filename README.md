# Anime Convention Management System (ACMS)

## Project Overview
The **Anime Convention Management System (ACMS)** is a backend, database-driven application designed to manage the core operations of an anime convention. The system supports managing attendees, events, rooms, tickets, vendors, guests, schedules, and payments through a RESTful API.

This project was built to demonstrate **relational database design**, **BCNF normalization**, **SQL querying**, **transactions**, and **data validation** using a modern backend stack.

---

## Technologies Used

- **FastAPI** – Backend web framework for building REST APIs  
- **MySQL** – Relational database used to store and manage convention data  
- **PyMySQL** – Python connector for MySQL  
- **Pydantic** – Data validation and request/response modeling  
- **Swagger UI** – Automatically generated interactive API documentation  

## Database Design

The system uses **8+ normalized tables** in **BCNF**, including:

- `Attendee`
- `Event`
- `Room`
- `Ticket`
- `Payment`
- `Vendor`
- `Guest`
- `Schedule`

Relationships are enforced using **primary keys**, **foreign keys**, and **constraints** to maintain data integrity.

---

## Key Features

### CRUD Operations
- Create, read, update, and delete attendees, events, rooms, tickets, vendors, and payments.
