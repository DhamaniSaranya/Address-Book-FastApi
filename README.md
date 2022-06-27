# fastapi- Address Book
# Goal
The goal is to demonstrate your existing Python3 skills and how you can create a minimal API using FastAPI

---


# Features
An address book application where API users can create, update and delete addresses.

The user can perform the following operations (CURD) in the below:
- This can retrieve all the data saved in the database
- This can post new address data in the database
- This can retrieve nearest address for specific address (which is present in database) by providing ID from data saved  in database .
    (retrieve the addresses that are within a given distance and location coordinates.)
- This can retrieve nearest address for specific address(which is not present in database) by providing address deatils from data saved in    database. (retrieve the addresses that are within a given distance and location coordinates.)
- This can retrieve data by locate content by searching for specific words or phrases.
- This can create data when address is entered and will get the coordinates for specific address, added to database.
- This can update existed data by ID number provided.
- This can delete existed data by ID number provided.

---

# Installation

1. Clone the repo

2. install all the requirements

   ```bash
   pip install -r requirements.txt
   ```

3. run the server

   ```bash
   uvicorn app.main:app --reload 
   
   ```
   (If you get error in terminal then try another command below)
   ```bash
   py -m uvicorn app.main:app --reload
   ```

4. click the link below
   # http://localhost:8000/docs

# Authentication

I have used Fake Data for Authentication and Authorization.

I have used fastapi.security OAuth2PasswordBearer, OAuth2PasswordRequestForm

# For Authorizing User in Swagger UI
User with the following details can access the address book.

It has no Security, This was done only for project requirement.

User_name -- dhamani 

Password -- dhamanis

