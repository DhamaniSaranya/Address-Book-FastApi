from .databases import Base
from sqlalchemy import Column, Integer, Float, String


# A table is created for database
# Initilizing and validating all the table columns in database

class Address(Base):
    
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    name= Column(String)
    addressLine = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    postalCode = Column(Integer)
    longitude = Column(Float)
    latitude = Column(Float)
    mapUrl = Column(String)