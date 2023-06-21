import os

path = "" # Folder where sorted cloud images are stored

# map clouds
clouds = os.listdir(path)
cloud_map = {}

for cloud_type in clouds:
    try:
        cloud_files = os.listdir(os.path.join(path, cloud_type))
        #print(cloud_type)
        for photo in cloud_files:
            # Add the photo name to the map with the cloud type
            cloud_map[photo] = cloud_type
    except:
        pass

cloudmap = {}

#print(cloud_map)

with open("ndvi-weatherkit.csv", 'r') as initialCSV:
    initialCSV.readline()
    for i in range(1, 481):
        line = initialCSV.readline()[:-1]
        file = line.split(",")[0].replace("\"", "")
        try:
            cloud_type = cloud_map[file]
            with open("ndvi-weatherkit-clouds.csv", 'a') as newCSV:
                newCSV.write(line + ",\"" + cloud_type + "\"\n")
        except:
            with open("ndvi-weatherkit-clouds.csv", 'a') as newCSV:
                newCSV.write(line + ",\"none\"\n")