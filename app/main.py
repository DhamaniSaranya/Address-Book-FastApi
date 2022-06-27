from fastapi import Depends, FastAPI, status, Response, HTTPException
from . import model, schemas
from sqlalchemy.orm import Session
from .databases import SessionLocal, engine
from geopy.distance import geodesic
from .get_Coordinates import getCoordinate
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging


# implementation of logging

file_name = f'log.txt'
logging.basicConfig(filename=file_name, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Creating Fake Data for Authentication in Swagger UI
# User_Name - dhamani
# Password - dhamanis

fake_users_db = {
    "dhamani": {
        "username": "dhamani",
        "full_name": "Dhamani",
        "email": "dhamani@example.com",
        "hashed_password": "fakehasheddhamanis",
        "disabled": False,
    },
}

# Assigning FastApi to app
app = FastAPI()

# For Fake Hashed Password for security of user Details
def fake_hash_password(password: str):
    return "fakehashed" + password

# assigning the tokenUrl to oauth2_scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# creating Base Model for User Details
class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str

# data is stored in DB
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all, this is used for project requirement
    user = get_user(fake_users_db, token)
    return user

# Authentication is implemented
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# if Authentication Fails then it gives Error
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# post login details for new user
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

# gets all the user data
@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


model.Base.metadata.create_all(engine)

def getDb():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# From request body, creating an address

@app.post("/createAddress", status_code=status.HTTP_201_CREATED)
def create_address(req: schemas.Address, res:Response, db :Session = Depends(getDb), current_user: User = Depends(get_current_user)):
    try:
        # ending and leading extra space are removed
        name = req.name.strip()
        addressLine = req.addressLine.strip()
        city = req.city.strip()
        state = req.state.strip()
        postalCode = req.postalCode

        # we get the location and coordinates using mapquest api
        locationData = getCoordinate(name,addressLine, city, state)
        print(locationData)

        # generate new column for address table
        newAddress = model.Address(
            name= name,
            addressLine = addressLine,
            city = city,
            state = state,
            country = locationData["adminArea1"],
            postalCode = postalCode,
            longitude =  locationData["latLng"]["lng"],
            latitude =  locationData["latLng"]["lat"],
            mapUrl = locationData["mapUrl"]
        )

        # adding row to table
        db.add(newAddress)
        db.commit()
        db.refresh(newAddress)

        return {
            "status": "ok",
            "data": newAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# reads all the addresses

@app.get("/readAddressAll", status_code=status.HTTP_200_OK)
def get_all_address(res: Response, db :Session = Depends(getDb), current_user: User = Depends(get_current_user)):
    try:
        # we get all the data from database and then send to user 
        allAddress = db.query(model.Address).all()
        return{
            "status" :"ok",
            "data" : allAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# we get the addresses which are near to the request body address {157 km}

@app.get("/readAddressNearest", status_code=status.HTTP_200_OK)
def get_nearest_address(res: Response, name, addressLine, city, state, db :Session = Depends(getDb), current_user: User = Depends(get_current_user)):
    try:
        # we get the location & coordinate data from mapquest api 
        locationData = getCoordinate(name, addressLine, city, state)
        quaryCoordinate = locationData["latLng"]

        firstCoordinate = (quaryCoordinate["lat"] , quaryCoordinate["lng"])

        allAddress = db.query(model.Address).all()

        someAddress = []

        """
        In here geodesic returning the distance between quary address and all database address,
        If the distance is below 100km than only it's save the address to someAddress list. 

        geodesic is importaed from geopy.distance module

        Here, someAddress will hold all the address that between 100km
        """

        for address in allAddress:
            secondCoordinate = (address.latitude, address.longitude)
            distanceBetween = geodesic(firstCoordinate, secondCoordinate).km
            if distanceBetween <= 100:
                someAddress.append(address)
        

        # send the nearest address data to the user
        return {
            "status": "ok",
            "data" : someAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# It update the address by giving id and request body 

@app.put("/updateAddress/{id}", status_code=status.HTTP_202_ACCEPTED)
def update_address(id, req: schemas.Address, res: Response, db: Session = Depends(getDb), current_user: User = Depends(get_current_user)):
    try:
        # it removes leading and ending extra space 
        name = req.name.strip()
        addressLine = req.addressLine.strip()
        city = req.city.strip()
        state = req.state.strip()
        postalCode = req.postalCode

        # it gets the location & coordinate data from mapquest api 
        locationData = getCoordinate(name, addressLine, city, state)

        newAddress = {
            "name": name,
            "addressLine" : addressLine,
            "city" : city,
            "state" : state,
            "country" : locationData["adminArea1"],
            "postalCode" : postalCode,
            "longitude" :  locationData["latLng"]["lng"],
            "latitude" :  locationData["latLng"]["lat"],
            "mapUrl" : locationData["mapUrl"]
        }

        # updating the address by giving id and query params 
        updatedAddress = db.query(model.Address).filter(model.Address.id == id).update(newAddress)

        # if the data is not found in database 
        if not updatedAddress:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status" : "failed",
                "msg" : f"Address id {id} not found"
            }

        db.commit()

        # if the data got sucessfully updated 
        return {
            "status" : "ok",
            "data" : updatedAddress
        }
    
    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }


# delees the address by giving id 

@app.delete("/deleteAddress/{id}", status_code=status.HTTP_202_ACCEPTED)
def delete_address(id, res: Response, db: Session = Depends(getDb), current_user: User = Depends(get_current_user)):
    try:
        # deleting address from databse by giving id
        deletedAddress = db.query(model.Address).filter(model.Address.id == id).delete(synchronize_session=False)

        # if the data is not found in database 
        if not deletedAddress:
            res.status_code = status.HTTP_404_NOT_FOUND
            return {
                "status" : "failed",
                "msg" : f"Address id {id} not found"
            }
        
        db.commit()

        # if the data got sucessfully deleted 
        return {
            "status" : "ok",
            "data" : deletedAddress
        }

    except Exception as e:
        res.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "status" : "failed",
            "msg" : str(e)
        }
