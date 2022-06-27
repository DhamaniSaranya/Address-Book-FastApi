import requests

# for getting the coordinate of particular address, mapquest api is used

# API Secret Key
coordinateApiKey = "zQ85GG9vCz4xzvnERTYULLpsseGstaok"

# API end point with query ?location=
coordinateApi = f"http://www.mapquestapi.com/geocoding/v1/address?key={coordinateApiKey}&location="


# it returns the address information along with coordinates and address 
# It's take 3 parameter and use them as location query for api 

def getCoordinate(name, addressLine, city, state):
    mainCoordinateApi = f" {coordinateApi}{addressLine},{city},{state}"
    r = requests.get(mainCoordinateApi)
    locationData = r.json()["results"][0]["locations"][0]
    return locationData