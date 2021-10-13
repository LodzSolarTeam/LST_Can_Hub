class Gps:
    dateDay = bytearray(1)
    dateMonth = bytearray(1)
    dateYear = bytearray(2)
    timeHour = bytearray(1)
    timeMin = bytearray(1)
    timeSec = bytearray(1)
    latitude = bytearray(8)  # double
    latitudeDirection = bytearray(1)
    longitude = bytearray(8)  # double
    longitudeDirection = bytearray(1)
    altitude = bytearray(8)  # double
    speedKnots = bytearray(8)  # double
    speedKilometers = bytearray(8)  # double
    satellitesNumber = bytearray(1)
    quality = bytearray(1)