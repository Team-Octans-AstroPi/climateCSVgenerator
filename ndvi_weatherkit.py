import requests
import json
from exif import Image
import cv2
import sys
import numpy as np
from fastiecm import fastiecm
from octanscm import octanscm



# Functions used later

def dms_to_dd(dms_coords, gps_ref):
    # Convert exif coordinates (dms) to dd format.

    if gps_ref not in ('N', 'E', 'S', 'W'):
        raise RuntimeError(f'Error: gps_ref does not have a valid value (\'N\', \'E\', \'S\', \'W\'): {gps_ref}')

    d, m, s =  dms_coords
    dd = d + m / 60 + s / 3600
    if gps_ref.upper() in ('S', 'W'):
        return -dd
    elif gps_ref.upper() in ('N', 'E'):
        return dd
    
def contrast_stretch(im):
    # From the Astro Pi NDVI tutorial: https://projects.raspberrypi.org/en/projects/astropi-ndvi
    in_min = np.percentile(im, 5)
    in_max = np.percentile(im, 95)
    
    out_min= 0.0
    out_max = 255.0
    
    out = im - in_min
    out *= ((out_min - out_max) / (in_min - in_max))
    out += in_min
    
    return out

def calc_ndvi(image):
    # From the Astro Pi NDVI tutorial: https://projects.raspberrypi.org/en/projects/astropi-ndvi
    b, g, r = cv2.split(image)
    bottom = (r.astype(float) + b.astype(float))
    
    bottom[bottom==0] = 0.01

    ndvi = (b.astype(float) - r) / bottom
    return ndvi







"""
    ------ WeatherKit Information ------ 
    This requires an Apple Developer Program membership.

    WeatherKit is used to provide temperature and precipitation data of each image.

    This code processes data from Apple Weatherthat may be later modified and used for the model.
    Attribution: https://developer.apple.com/weatherkit/data-source-attribution/
"""

link = "https://weatherkit.apple.com/api/v1/weather/en/{latitude}/{longitude}?dataSets=currentWeather&currentAsOf={time}"
auth = "Bearer [token]" # replace with your JWT token, details here: https://developer.apple.com/documentation/weatherkitrestapi
headers = {
            'User-Agent': 'test',
            'Authorization': auth
          }






"""
    CSV Generator Loop
"""

from pathlib import Path

imagedir = "" # directory where your images are stored

for image in Path(imagedir).iterdir():
    with open(image, 'rb') as image_file:
        # Get location data from image exif

        exif_image = Image(image_file)
        latitude = dms_to_dd(exif_image.gps_latitude, exif_image.gps_latitude_ref)
        longitude = dms_to_dd(exif_image.gps_longitude, exif_image.gps_longitude_ref)
        dt = exif_image.datetime.split(" ")
        dt_split = dt[0].split(":")
        dt = dt_split[0] + "-" + dt_split[1] + "-" + dt_split[2]+"T"+dt[1]+"Z"
        
        # Get climate data from climateapi.scottpinkelman.com.
        # This website uses data from the Institute for Veterinary Public Health and the Provincial Government of Carinthia in Austria.

        climate = requests.get("http://climateapi.scottpinkelman.com/api/v1/location/"+str(latitude)+"/"+str(longitude))
        if "Could not find data for the supplied latitude\\/longitude pair. Please double check your values." not in climate.text:
            # This is a land photo which has an attributed climate.

            # Get climate data from the API
            climateJson = climate.json()
            climateId = climateJson['return_values'][0]['koppen_geiger_zone']


            # Send a request to WeatherKit to get temperature & precipitation information.
            req = requests.get(link.format(latitude=latitude, longitude=longitude, time=dt), headers=headers)
            
            print(req.status_code)

            # Get weather data from json
            current_weather = req.json()["currentWeather"]
            temp = current_weather["temperature"]
            precipitationIntensity = current_weather["precipitationIntensity"]


            # NDVI & Plant health computation
            # This part of the code is a modified version of imageSeparationCV2.

            path = str(image)
            imgname = path.split("/")[-1]
            img = cv2.imread(path, cv2.IMREAD_COLOR)
            if img is None:
                sys.exit("Could not read the image. Check the filename and path.")

            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            windowUp = np.array([179, 255, 30])
            windowDown = np.array([0, 0, 0])

            window = cv2.bitwise_and(img, img, mask = cv2.inRange(img, windowDown, windowUp))

            cloudsUp = np.array([179, 80, 255])
            cloudsDown = np.array([0, 0, 185])

            clouds = cv2.bitwise_and(img, img, mask = cv2.inRange(img, cloudsDown, cloudsUp))

            waterUp = np.array([80, 255, 185])
            waterDown = np.array([0, 0, 30])

            water = cv2.bitwise_and(img, img, mask = cv2.inRange(img, waterDown, waterUp))

            waterUp = np.array([179, 55, 90])
            waterDown = np.array([0, 0, 30])

            water = cv2.bitwise_or(water, cv2.bitwise_and(img, img, mask = cv2.inRange(img, waterDown, waterUp)))

            vegetationUp = np.array([179, 255, 255])
            vegetationDown = np.array([30, 20, 55])

            vegetation = cv2.bitwise_and(img, img, mask = cv2.inRange(img, vegetationDown, vegetationUp))


            land = cv2.subtract(img, cv2.add(cv2.add(clouds, water), window))

            toBeColorMapped = contrast_stretch(calc_ndvi(cv2.cvtColor(vegetation, cv2.COLOR_HSV2BGR))).astype(np.uint8)

            ndvicm = cv2.applyColorMap(toBeColorMapped, fastiecm)

            """
                ------------------------------------------- Plant health ------------------------------------------- 
                Using our custom 8-bit colormap inspired from FastieCM, we split the plant health into 8 categories.
                Each category is assigned a specific color of the colormap. Then, for every category,
                we compute how much of the vegetation in the image is in that category. 
                
                Along with the vegetation percentage (how much of the image represents vegetation), 
                this information is stored inside the CSV used to train the climate model.
            """

            octansNDVI = cv2.applyColorMap(toBeColorMapped, octanscm)

            pixels = octansNDVI.size/3
            backgroundPixels = np.count_nonzero((octansNDVI == [255, 255, 255]).all(axis = 2))

            vegetationPixels = pixels - backgroundPixels

            vegetationPercent = str(vegetationPixels/pixels*100)
            plantHealth1 = "0"
            plantHealth2 = "0"
            plantHealth3 = "0"
            plantHealth4 = "0"
            plantHealth5 = "0"
            plantHealth6 = "0"
            plantHealth7 = "0"
            plantHealth8 = "0"

            if vegetationPixels != 0:
                plantHealth1 = str(np.count_nonzero((octansNDVI == [50, 50, 50]).all(axis = 2))/vegetationPixels*100)
                plantHealth2 = str(np.count_nonzero((octansNDVI == [120, 120, 120]).all(axis = 2))/vegetationPixels*100)
                plantHealth3 = str(np.count_nonzero((octansNDVI == [250, 180, 180]).all(axis = 2))/vegetationPixels*100)
                plantHealth4 = str(np.count_nonzero((octansNDVI == [50, 210, 0]).all(axis = 2))/vegetationPixels*100)
                plantHealth5 = str(np.count_nonzero((octansNDVI == [5, 223, 247]).all(axis = 2))/vegetationPixels*100)
                plantHealth6 = str(np.count_nonzero((octansNDVI == [0, 140, 255]).all(axis = 2))/vegetationPixels*100)
                plantHealth7 = str(np.count_nonzero((octansNDVI == [0, 0, 255]).all(axis = 2))/vegetationPixels*100)
                plantHealth8 = str(np.count_nonzero((octansNDVI == [236, 128, 255]).all(axis = 2))/vegetationPixels*100)


            # Add data to CSV
            with open("ndvi-weaatherkit.csv", "a") as csv:
                csv.write("\""+str(image).split("/")[-1]+"\","+str(temp)+","+str(precipitationIntensity)+","+vegetationPercent + "," + str(latitude) + "," + str(longitude) + "," + plantHealth1 + "," +  plantHealth2 + "," +  plantHealth3 + "," +  plantHealth4 + "," +  plantHealth5 + "," +  plantHealth6 + "," +  plantHealth7 + "," +  plantHealth8 + ",\"" +  str(climateId)+"\"\n")
