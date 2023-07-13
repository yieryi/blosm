"""
This file is a part of Blosm addon for Blender.
Copyright (C) 2014-2018 Vladimir Elistratov
prokitektura+support@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import math

# 参考 https://github.com/CesiumGS/cesium/blob/e658f018a8eea3a5278b144655c2b3eded0227fa/packages/engine/Source/Core/WebMercatorProjection.js
class WebMercator:
    semimajorAxis = 6378137.
    oneOverSemimajorAxis = 1/semimajorAxis

    def __init__(self, **kwargs):
        # setting default values
        self.lat = 0. # in degrees
        self.lon = 0. # in degrees
        self.k = 1. # scale factor
        
        for attr in kwargs:
            setattr(self, attr, kwargs[attr])
        self.MaximumLatitude = self.mercatorAngleToGeodeticLatitude(math.pi)
        

    def geodeticLatitudeToMercatorAngle(self,latitude):
         if (latitude > self.MaximumLatitude):
            latitude = self.MaximumLatitude
         elif latitude < -self.MaximumLatitude:
            latitude = -self.MaximumLatitude
            
         sinLatitude = math.sin(latitude)
         return 0.5 * math.log((1.0 + sinLatitude) / (1.0 - sinLatitude))


    def mercatorAngleToGeodeticLatitude(self,mercatorAngle):
        return math.pi*.5 - 2.0 * math.atan(math.exp(-mercatorAngle))


    def fromGeographic(self, lat, lon):
        lat = math.radians(lat)
        lon = math.radians(lon)
        x = self.semimajorAxis * lon
        y =  self.geodeticLatitudeToMercatorAngle(lat) * self.semimajorAxis
        return (x, y, 0.)

    def toGeographic(self, x, y):
        longitude = x * self.oneOverSemimajorAxis
        latitude = self.mercatorAngleToGeodeticLatitude(y * self.oneOverSemimajorAxis  )

        lon = math.degrees(longitude)
        lat = math.degrees(latitude)
        return (lat, lon)