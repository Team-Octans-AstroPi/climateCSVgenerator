import os

path = "" # Folder where sorted land images are stored

# map lands
land_images = os.listdir(path)
land_map = {}

for land_type in land_images:
    try:
        land_files = os.listdir(os.path.join(path, land_type))
        #print(land_type)
        for photo in land_files:
            # Add the photo name to the map with the land type
            land_map[photo] = land_type
    except:
        pass

landmap = {}

#print(land_map)

with open("ndvi-weatherkit-clouds.csv", 'r') as initialCSV:
    initialCSV.readline()
    for i in range(1, 479):
        line = initialCSV.readline()[:-1]
        file = line.split(",")[0].replace("\"", "")
        try:
            land_type = land_map[file]
            with open("ndvi-weatherkit-clouds-lands.csv", 'a') as newCSV:
                newCSV.write(line + ",\"" + land_type + "\"\n")
        except:
            with open("ndvi-weatherkit-clouds-lands.csv", 'a') as newCSV:
                newCSV.write(line + ",\"none\"\n")