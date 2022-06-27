from pydantic import BaseModel

# create an request model using Basemodel imported from pydantic
class Address(BaseModel):
    name: str
    addressLine: str 
    city: str 
    state: str
    postalCode: int