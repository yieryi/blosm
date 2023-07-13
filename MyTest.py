import math;



semimajorAxis = 6378137.
oneOverSemimajorAxis = 1/semimajorAxis
import math;



semimajorAxis = 6378137.
oneOverSemimajorAxis = 1/semimajorAxis

def mercatorAngleToGeodeticLatitude(mercatorAngle):
    return math.pi*.5 - 2.0 * math.atan(math.exp(-mercatorAngle))


MaximumLatitude= mercatorAngleToGeodeticLatitude(math.pi)

def geodeticLatitudeToMercatorAngle(latitude):
     if (latitude > MaximumLatitude):
        latitude = MaximumLatitude
     elif latitude < -MaximumLatitude:
        latitude = -MaximumLatitude
        
     sinLatitude = math.sin(latitude)
     return 0.5 * math.log((1.0 + sinLatitude) / (1.0 - sinLatitude))

def fromGeographic( lat, lon):
    lat = math.radians(lat)
    lon = math.radians(lon)
    x = semimajorAxis * lon
    y =  geodeticLatitudeToMercatorAngle(lat) * semimajorAxis
    return (x, y, 0.)

def toGeographic( x, y):
    longitude = x * oneOverSemimajorAxis
    latitude = mercatorAngleToGeodeticLatitude(y * oneOverSemimajorAxis  )

    lon = math.degrees(longitude)
    lat = math.degrees(latitude)
    return (lat, lon)

fromgeo=fromGeographic(30.0232637,120.1947212)
togeo=toGeographic(13380015.16247251,3506540.5287997983)
print(togeo)